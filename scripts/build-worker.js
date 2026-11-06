// Genera worker/worker.js (un solo archivo para pegar en Cloudflare) reutilizando la lógica de server.js.
const fs = require('fs');
const srv = fs.readFileSync('server.js', 'utf8');
const a = srv.indexOf('const catLabel = id =>'), b = srv.indexOf('async function callClaude');
if (a < 0 || b < 0) throw new Error('no se encontró el bloque de lógica en server.js');
const catalog = JSON.parse(fs.readFileSync('data/catalog.json', 'utf8'));
const imgs = JSON.parse(fs.readFileSync('data/images.json', 'utf8'));
const slim = {}; for (const [k, v] of Object.entries(imgs)) if (v.status === 'aprobada') slim[k] = { status: v.status, file: v.file, v: v.v, credit: v.credit || null };
const out = fs.readFileSync('worker/head.js', 'utf8').replace('__CATALOG__', JSON.stringify(catalog)).replace('__IMAGES__', JSON.stringify(slim))
  + '\n' + srv.slice(a, b) + fs.readFileSync('worker/tail.js', 'utf8');
fs.writeFileSync('worker/worker.js', out);
console.log('worker/worker.js', Math.round(out.length / 1024) + ' KB');
