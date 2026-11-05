// Pruebas del servidor: node test/api.test.js
const assert = require('assert');
const { spawn } = require('child_process');
const fs = require('fs'), path = require('path');
const sharp = require('sharp');
const { srv, calls } = require('./mock-anthropic');
const ROOT = path.join(__dirname, '..');
const KEY = 'sk-ant-TEST-ESTA-CLAVE-NUNCA-DEBE-SALIR', ADMIN = 'admin-token-de-prueba-123456';
const results = [];
const t = async (name, fn) => { try { await fn(); results.push(['✅', name]); } catch (e) { results.push(['❌', name + ' → ' + e.message]); } };
const startServer = (port, env) => new Promise(res => {
  const p = spawn('node', ['server.js'], { cwd: ROOT, env: { ...process.env, PORT: port, ...env } });
  p.stdout.on('data', d => { if (String(d).includes('listo')) res(p); });
  p.stderr.on('data', d => process.stderr.write(d));
});

(async () => {
  const imagesBackup = fs.existsSync(path.join(ROOT, 'data/images.json')) ? fs.readFileSync(path.join(ROOT, 'data/images.json')) : null;
  await new Promise(r => srv.listen(4010, r));
  const A = await startServer(3101, { ANTHROPIC_API_KEY: KEY, ANTHROPIC_BASE_URL: 'http://127.0.0.1:4010', ADMIN_TOKEN: ADMIN, RATE_PER_10MIN: '8' });
  const B = await startServer(3102, { ANTHROPIC_API_KEY: '', ADMIN_TOKEN: '' });
  const U = 'http://127.0.0.1:3101';
  const post = (url, body, h = {}) => fetch(url, { method: 'POST', headers: { 'content-type': 'application/json', ...h }, body: JSON.stringify(body) });

  await t('Catálogo: 132 productos, ids y nombres idénticos al original', async () => {
    const d = await (await fetch(U + '/api/catalog')).json();
    const html = fs.readFileSync(path.join(ROOT, 'backup/lt_uwu_original_2026-11-05.html'), 'utf8');
    const RAW = Function('return ' + html.match(/const RAW = (\[[\s\S]*?\n\]);/)[1])();
    assert.strictEqual(d.productos.length, RAW.length);
    RAW.forEach(([id, cat, nombre, sub]) => { const p = d.productos.find(x => x.id === id); assert(p && p.nombre === nombre && p.sub === sub && p.cat === cat, 'difiere ' + id); });
  });
  await t('Health informa IA activa sin revelar la clave', async () => {
    const txt = await (await fetch(U + '/api/health')).text();
    assert(JSON.parse(txt).ai === true); assert(!txt.includes(KEY));
  });
  await t('La clave no aparece en ningún archivo público', async () => {
    for (const f of ['/', '/admin.html', '/api/catalog']) assert(!(await (await fetch(U + f)).text()).includes(KEY), f);
    const pub = fs.readdirSync(path.join(ROOT, 'public')).filter(f => f.endsWith('.html')).map(f => fs.readFileSync(path.join(ROOT, 'public', f), 'utf8')).join('');
    assert(!/sk-ant-|sk-proj-|ANTHROPIC_API_KEY\s*[:=]\s*['"]sk/.test(pub));
  });
  await t('IA: "agrega 2 bultos de cemento argos" → busca, agrega id 1 ×2 por herramienta', async () => {
    const r = await post(U + '/api/chat', { messages: [{ role: 'user', text: 'agrega 2 bultos de cemento argos' }], cart: [] });
    const d = await r.json(); assert.strictEqual(r.status, 200, JSON.stringify(d));
    assert.deepStrictEqual(d.actions, [{ type: 'add_to_cart', id: 1, qty: 2 }]);
    assert(d.reply.includes('Cemento Argos')); assert(d.products.some(p => p.id === 1));
    const c = calls[calls.length - 1];
    assert.strictEqual(c.key, KEY); assert(c.body.tools.length === 6); assert(c.body.system[0].text.includes('Nunca inventes'));
  });
  await t('IA: producto inexistente → la herramienta lo rechaza, sin acción en carrito', async () => {
    const d = await (await post(U + '/api/chat', { messages: [{ role: 'user', text: 'agrega algo inventado' }], cart: [] })).json();
    assert.deepStrictEqual(d.actions, []); assert(d.reply.includes('inexistente'));
  });
  await t('IA: calculadora determinística (placa 6×8×10 cm → 34 bultos)', async () => {
    const d = await (await post(U + '/api/chat', { messages: [{ role: 'user', text: 'placa de 6 x 8' }], cart: [] })).json();
    assert(d.reply.includes('34 bultos'), d.reply); assert(d.calc.resultados[0].cantidad === 34);
  });
  await t('IA: conserva contexto (historial enviado al modelo)', async () => {
    await post(U + '/api/chat', { messages: [{ role: 'user', text: 'hola' }, { role: 'assistant', text: 'Hola' }, { role: 'user', text: 'y para un baño?' }], cart: [] });
    assert.strictEqual(calls[calls.length - 1].body.messages.length, 3);
  });
  await t('Validación: rechaza mensajes de 601+ caracteres y carritos con ids falsos', async () => {
    assert.strictEqual((await post(U + '/api/chat', { messages: [{ role: 'user', text: 'x'.repeat(601) }] })).status, 400);
    assert.strictEqual((await post(U + '/api/chat', { messages: [{ role: 'user', text: 'hola' }], cart: [{ id: 9999, qty: 1 }] })).status, 400);
  });
  await t('Error del proveedor → 502 con mensaje amable (sin detalles internos)', async () => {
    const r = await post(U + '/api/chat', { messages: [{ role: 'user', text: 'error500' }] }); const d = await r.json();
    assert.strictEqual(r.status, 502); assert(!JSON.stringify(d).includes('boom'));
  });
  await t('CORS: bloquea otros dominios', async () => {
    assert.strictEqual((await post(U + '/api/chat', { messages: [{ role: 'user', text: 'hola' }] }, { origin: 'https://sitio-malicioso.com' })).status, 403);
  });
  await t('Límite por usuario: responde 429 al superar el máximo', async () => {
    let last; for (let i = 0; i < 6; i++) last = await post(U + '/api/chat', { messages: [{ role: 'user', text: 'hola' }] });
    assert.strictEqual(last.status, 429);
  });
  await t('Sin clave de IA → 503 no_ai (la página usa modo básico)', async () => {
    const r = await post('http://127.0.0.1:3102/api/chat', { messages: [{ role: 'user', text: 'hola' }] });
    assert.strictEqual(r.status, 503); assert.strictEqual((await r.json()).code, 'no_ai');
  });
  await t('Admin: sin token → 401; sin ADMIN_TOKEN configurado → 503', async () => {
    assert.strictEqual((await fetch(U + '/api/admin/images')).status, 401);
    assert.strictEqual((await fetch('http://127.0.0.1:3102/api/admin/images', { headers: { authorization: 'Bearer x' } })).status, 503);
  });
  const H = { authorization: 'Bearer ' + ADMIN };
  await t('Admin: subir foto → WebP 800×800 centrada, publicada en el catálogo', async () => {
    const png = await sharp({ create: { width: 1200, height: 600, channels: 3, background: '#c00' } }).png().toBuffer();
    const r = await post(U + '/api/admin/upload', { id: 63, dataUrl: 'data:image/png;base64,' + png.toString('base64') }, H);
    const d = await r.json(); assert.strictEqual(r.status, 200, JSON.stringify(d));
    const meta = await sharp(path.join(ROOT, 'public/img/productos/63.webp')).metadata();
    assert(meta.format === 'webp' && meta.width === 800 && meta.height === 800);
    const p = (await (await fetch(U + '/api/catalog')).json()).productos.find(x => x.id === 63);
    assert(p.img && p.img.startsWith('/img/productos/63.webp'));
    assert.strictEqual((await fetch(U + p.img)).status, 200);
  });
  await t('Admin: la misma foto no se puede asignar a otro producto', async () => {
    const png = await sharp({ create: { width: 1200, height: 600, channels: 3, background: '#c00' } }).png().toBuffer();
    const r = await post(U + '/api/admin/upload', { id: 64, dataUrl: 'data:image/png;base64,' + png.toString('base64') }, H);
    assert.strictEqual(r.status, 400); assert((await r.json()).error.includes('Tubo Sanitario 4'));
  });
  await t('Admin: cobertura y retiro de foto', async () => {
    let d = await (await fetch(U + '/api/admin/images', { headers: H })).json(); const base = d.con_imagen; assert(d.rows.find(r => r.id === 63).status === 'aprobada');
    await post(U + '/api/admin/reject', { id: 63 }, H);
    d = await (await fetch(U + '/api/admin/images', { headers: H })).json(); assert.strictEqual(d.con_imagen, base - 1);
  });
  await t('Admin: Wikimedia Commons (sugerencias) — depende de red externa', async () => {
    const r = await post(U + '/api/admin/suggest', { id: 14 }, H);
    if (r.status === 502) throw new Error('NO PROBADO AQUÍ: este entorno no tiene salida a commons.wikimedia.org (502 controlado)');
  });
  A.kill(); B.kill(); srv.close();
  if (imagesBackup) fs.writeFileSync(path.join(ROOT, 'data/images.json'), imagesBackup); else fs.rmSync(path.join(ROOT, 'data/images.json'), { force: true });
  console.log(results.map(r => r.join(' ')).join('\n'));
  console.log(`\n${results.filter(r => r[0] === '✅').length}/${results.length} pruebas OK`);
})();
