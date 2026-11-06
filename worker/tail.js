
// ════════════════ GEMINI ════════════════
const T = t => ({ string: 'STRING', integer: 'INTEGER', number: 'NUMBER', boolean: 'BOOLEAN', array: 'ARRAY', object: 'OBJECT' })[t] || 'STRING';
function toGemini(schema) {
  const o = { type: T(schema.type) };
  if (schema.description) o.description = schema.description;
  if (schema.enum) o.enum = schema.enum;
  if (schema.items) o.items = toGemini(schema.items);
  if (schema.properties) { o.properties = {}; for (const [k, v] of Object.entries(schema.properties)) o.properties[k] = toGemini(v); if (!Object.keys(o.properties).length) delete o.properties; }
  if (schema.required) o.required = schema.required;
  return o;
}
const DECLS = TOOLS.map(t => {
  const d = { name: t.name, description: t.description };
  if (Object.keys(t.input_schema.properties || {}).length) d.parameters = toGemini(t.input_schema);
  return d;
});
const SYSTEM_G = SYSTEM.replace('"LT AI"', '"Asesor LT"');

async function callGemini(env, contents) {
  const model = env.GEMINI_MODEL || 'gemini-flash-latest';
  const base = env.GEMINI_BASE_URL || 'https://generativelanguage.googleapis.com';
  const r = await fetch(`${base}/v1beta/models/${encodeURIComponent(model)}:generateContent`, {
    method: 'POST',
    headers: { 'content-type': 'application/json', 'x-goog-api-key': env.GEMINI_API_KEY },
    body: JSON.stringify({ systemInstruction: { parts: [{ text: SYSTEM_G }] }, contents, tools: [{ functionDeclarations: DECLS }],
      generationConfig: { temperature: 0.4, maxOutputTokens: +(env.MAX_OUTPUT_TOKENS || 800) } }),
    signal: AbortSignal.timeout(40000),
  });
  if (!r.ok) { const e = new Error('gemini ' + r.status); e.status = r.status; e.detail = (await r.text().catch(() => '')).slice(0, 300); throw e; }
  return r.json();
}

async function chat(env, history, cart) {
  const ctx = { shown: new Set(), actions: [], cart: cart.slice(), calc: null };
  const contents = history.map(h => ({ role: h.role === 'assistant' ? 'model' : 'user', parts: [{ text: h.text }] }));
  for (let step = 0; step < 6; step++) {
    const res = await callGemini(env, contents);
    const cand = res.candidates && res.candidates[0];
    const parts = (cand && cand.content && cand.content.parts) || [];
    const calls = parts.filter(p => p.functionCall);
    if (!calls.length) {
      const text = parts.filter(p => p.text && !p.thought).map(p => p.text).join('').trim();
      return { reply: text || 'Perdón, no pude responder eso. ¿Me lo repites con otras palabras o prefieres escribirnos por WhatsApp?', products: [...ctx.shown].slice(0, 8), actions: ctx.actions, calc: ctx.calc };
    }
    contents.push({ role: 'model', parts });   // se devuelven intactas (incluye firmas de razonamiento si las hay)
    contents.push({ role: 'user', parts: calls.map(c => ({ functionResponse: { name: c.functionCall.name, response: runTool(c.functionCall.name, c.functionCall.args || {}, ctx) } })) });
  }
  return { reply: 'Esta consulta necesitó demasiados pasos. ¿La resumimos o te comunico con un asesor por WhatsApp?', products: [...ctx.shown].slice(0, 8), actions: ctx.actions };
}

// ════════════════ SEGURIDAD ════════════════
const buckets = new Map();   // límite por IP dentro de cada instancia (el plan gratis de Gemini pone el tope global)
function rateLimit(key, max, windowMs) {
  const now = Date.now(); const recent = (buckets.get(key) || []).filter(t => now - t < windowMs);
  if (recent.length >= max) { buckets.set(key, recent); return false; }
  recent.push(now); buckets.set(key, recent); if (buckets.size > 5000) buckets.clear(); return true;
}
function validChat(body) {
  if (!body || !Array.isArray(body.messages)) return 'messages requerido';
  const msgs = body.messages.slice(-12);
  if (!msgs.length || msgs[msgs.length - 1].role !== 'user') return 'el último mensaje debe ser del cliente';
  for (const m of msgs) {
    if (!['user', 'assistant'].includes(m.role) || typeof m.text !== 'string' || !m.text.trim()) return 'mensaje inválido';
    if (m.text.length > (m.role === 'user' ? 600 : 2500)) return 'mensaje demasiado largo';
  }
  const cart = Array.isArray(body.cart) ? body.cart.slice(0, 100) : [];
  if (!cart.every(i => byId(i.id) && Number.isInteger(i.qty) && i.qty > 0 && i.qty < 100000)) return 'carrito inválido';
  return null;
}
function cleanHistory(msgs) {
  const out = [];
  for (const m of msgs.slice(-12)) { const text = m.text.trim(); if (out.length && out[out.length - 1].role === m.role) out[out.length - 1].text += '\n' + text; else out.push({ role: m.role, text }); }
  while (out.length && out[0].role !== 'user') out.shift();
  return out;
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const origin = req.headers.get('origin') || '';
    const allowed = (env.ALLOWED_ORIGINS || 'https://alemendrap.github.io').split(',').map(s => s.trim());
    const cors = allowed.includes(origin) ? { 'Access-Control-Allow-Origin': origin, 'Vary': 'Origin', 'Access-Control-Allow-Methods': 'GET,POST', 'Access-Control-Allow-Headers': 'content-type' } : {};
    const json = (obj, status = 200) => new Response(JSON.stringify(obj), { status, headers: { 'content-type': 'application/json; charset=utf-8', 'X-Content-Type-Options': 'nosniff', ...cors } });
    if (origin && !allowed.includes(origin)) return json({ error: 'Origen no permitido' }, 403);
    if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors });

    if (url.pathname === '/api/health') return json({ ok: true, ai: !!env.GEMINI_API_KEY, model: env.GEMINI_API_KEY ? (env.GEMINI_MODEL || 'gemini-flash-latest') : null, proveedor: 'gemini', serverSTT: false, productos: catalog.productos.length });
    if (url.pathname === '/api/catalog') return json({ categorias: catalog.categorias, productos: catalog.productos.map(publicProduct) });
    if (url.pathname === '/api/chat' && req.method === 'POST') {
      if (!env.GEMINI_API_KEY) return json({ error: 'IA no configurada', code: 'no_ai' }, 503);
      const ip = req.headers.get('cf-connecting-ip') || '?';
      if (!rateLimit(ip, +(env.RATE_PER_10MIN || 20), 600e3)) return json({ error: 'Vas muy rápido. Espera unos minutos o escríbenos por WhatsApp.', code: 'rate' }, 429);
      const raw = await req.text(); if (raw.length > 40000) return json({ error: 'Solicitud demasiado grande', code: 'bad_request' }, 413);
      let body; try { body = JSON.parse(raw); } catch (_) { return json({ error: 'JSON inválido', code: 'bad_request' }, 400); }
      const err = validChat(body); if (err) return json({ error: err, code: 'bad_request' }, 400);
      try {
        const out = await chat(env, cleanHistory(body.messages), body.cart || []);
        return json({ reply: out.reply, products: out.products.map(byId).filter(Boolean).map(publicProduct), actions: out.actions, calc: out.calc || null });
      } catch (e) {
        console.error(JSON.stringify({ msg: 'chat_fail', status: e.status, detail: e.detail }));
        if (e.status === 429) return json({ error: 'El asesor virtual alcanzó su límite gratuito por ahora. Escríbenos por WhatsApp y te atendemos.', code: 'budget' }, 503);
        let why = ''; try { why = String(JSON.parse(e.detail).error.message || '').slice(0, 160); } catch (_) {}
        return json({ error: 'El asesor virtual no está disponible en este momento.', code: 'upstream', upstream_status: e.status || null, upstream_reason: why }, 502);
      }
    }
    return json({ error: 'No encontrado' }, 404);
  },
};
