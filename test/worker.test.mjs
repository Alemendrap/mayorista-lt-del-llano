// Prueba el Worker de Gemini con un simulador del protocolo de Gemini (functionCall/functionResponse).
import http from 'node:http';
import assert from 'node:assert';
import worker from '../worker/worker.js';
const seen = [];
const mock = http.createServer((req, res) => { let b = ''; req.on('data', c => b += c); req.on('end', () => {
  const body = JSON.parse(b); seen.push({ key: req.headers['x-goog-api-key'], body, url: req.url });
  const last = body.contents[body.contents.length - 1];
  const userText = [...body.contents].reverse().find(c => c.role === 'user' && c.parts[0].text)?.parts[0].text || '';
  const fr = last.parts.filter(p => p.functionResponse);
  const send = parts => { res.setHeader('content-type', 'application/json'); res.end(JSON.stringify({ candidates: [{ content: { role: 'model', parts } }] })); };
  if (userText.includes('limite')) { res.statusCode = 429; return res.end('{}'); }
  if (userText.includes('agrega')) {
    if (!fr.length) return send([{ functionCall: { name: 'buscar_productos', args: { consulta: 'cemento argos' } }, thoughtSignature: 'abc' }]);
    const r = fr[0].functionResponse.response;
    if (r.resultados) return send([{ functionCall: { name: 'agregar_al_carrito', args: { producto_id: r.resultados[0].id, cantidad: 2 } } }]);
    return send([{ text: `Listo, agregué ${r.agregado.cantidad} de ${r.agregado.producto}.` }]);
  }
  send([{ text: 'Hola, ¿qué vas a construir?' }]);
}); });
await new Promise(r => mock.listen(4020, r));
const env = { GEMINI_API_KEY: 'AIza-TEST', GEMINI_BASE_URL: 'http://127.0.0.1:4020' };
const O = 'https://alemendrap.github.io';
const call = (path, body, origin = O, e = env) => worker.fetch(new Request('https://w.example' + path, body ? { method: 'POST', headers: { origin, 'content-type': 'application/json' }, body: JSON.stringify(body) } : { headers: { origin } }), e);
const R = []; const t = async (n, f) => { try { await f(); R.push('✅ ' + n); } catch (e) { R.push('❌ ' + n + ' → ' + e.message); } };
await t('health: IA activa, sin revelar clave', async () => { const x = await (await call('/api/health')).text(); assert(JSON.parse(x).ai); assert(!x.includes('AIza')); });
await t('chat: busca y agrega 2 Cemento Argos (id 1) con herramientas', async () => {
  const r = await call('/api/chat', { messages: [{ role: 'user', text: 'agrega 2 bultos de cemento argos' }], cart: [] }); const d = await r.json();
  assert.strictEqual(r.status, 200, JSON.stringify(d)); assert.deepStrictEqual(d.actions, [{ type: 'add_to_cart', id: 1, qty: 2 }]); assert(d.reply.includes('Cemento Argos'));
  const last = seen[seen.length - 1];
  assert.strictEqual(last.key, 'AIza-TEST'); assert(last.url.includes('gemini-flash-lite-latest')); assert(last.body.tools[0].functionDeclarations.length === 6);
  assert(seen[1].body.contents[1].parts[0].thoughtSignature === 'abc', 'firma devuelta');
  assert(last.body.contents[last.body.contents.length - 1].role === 'user');
});
await t('CORS: bloquea otro dominio', async () => assert.strictEqual((await call('/api/chat', { messages: [{ role: 'user', text: 'hola' }] }, 'https://malo.com')).status, 403));
await t('CORS: permite la tienda', async () => assert.strictEqual((await call('/api/health')).headers.get('access-control-allow-origin'), O));
await t('validación: mensaje largo → 400', async () => assert.strictEqual((await call('/api/chat', { messages: [{ role: 'user', text: 'x'.repeat(601) }] })).status, 400));
await t('límite gratis de Gemini (429) → mensaje amable', async () => { const r = await call('/api/chat', { messages: [{ role: 'user', text: 'limite' }] }); assert.strictEqual(r.status, 503); assert.strictEqual((await r.json()).code, 'budget'); });
await t('sin clave → no_ai (la tienda queda en modo básico)', async () => assert.strictEqual((await (await call('/api/chat', { messages: [{ role: 'user', text: 'hola' }] }, O, {})).json()).code, 'no_ai'));
mock.close(); console.log(R.join('\n'));
