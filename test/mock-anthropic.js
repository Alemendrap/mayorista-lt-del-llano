// Simulador de la API de Anthropic SOLO para pruebas automáticas (reproduce el protocolo de tool use).
// Permite probar el circuito servidor ↔ herramientas ↔ carrito sin gastar créditos.
const http = require('http');
const calls = [];
const srv = http.createServer((req, res) => {
  let b = ''; req.on('data', c => b += c); req.on('end', () => {
    const body = JSON.parse(b); calls.push({ key: req.headers['x-api-key'], body });
    const msgs = body.messages, last = msgs[msgs.length - 1];
    const firstUser = msgs.find(m => m.role === 'user' && typeof m.content === 'string');
    const userText = [...msgs].reverse().find(m => m.role === 'user' && typeof m.content === 'string').content.toLowerCase();
    const send = (content, stop) => { res.setHeader('content-type', 'application/json'); res.end(JSON.stringify({ id: 'm', type: 'message', role: 'assistant', model: body.model, content, stop_reason: stop, usage: { input_tokens: 100, output_tokens: 20 } })); };
    const tr = Array.isArray(last.content) ? last.content.filter(c => c.type === 'tool_result') : [];
    if (userText.includes('error500')) { res.statusCode = 500; return res.end('{"error":"boom"}'); }
    if (userText.includes('inventado')) {
      if (!tr.length) return send([{ type: 'tool_use', id: 't3', name: 'agregar_al_carrito', input: { producto_id: 9999, cantidad: 1 } }], 'tool_use');
      return send([{ type: 'text', text: 'Ese producto no existe en el catálogo: ' + tr[0].content }], 'end_turn');
    }
    if (userText.includes('agrega')) {
      if (!tr.length) return send([{ type: 'tool_use', id: 't1', name: 'buscar_productos', input: { consulta: 'cemento argos' } }], 'tool_use');
      const r = JSON.parse(tr[0].content);
      if (r.resultados) { const id = r.resultados[0].id; return send([{ type: 'tool_use', id: 't2', name: 'agregar_al_carrito', input: { producto_id: id, cantidad: 2 } }], 'tool_use'); }
      if (r.ok) return send([{ type: 'text', text: `Listo, agregué **${r.agregado.cantidad} ${r.agregado.unidad}s** de ${r.agregado.producto}.` }], 'end_turn');
    }
    if (userText.includes('placa')) {
      if (!tr.length) return send([{ type: 'tool_use', id: 't4', name: 'calcular_materiales', input: { tipo: 'placa_concreto', largo_m: 6, alto_o_ancho_m: 8, espesor_cm: 10 } }], 'tool_use');
      const r = JSON.parse(tr[0].content);
      return send([{ type: 'text', text: `Para ${r.area_m2} m² necesitas unos ${r.resultados[0].cantidad} bultos de cemento.` }], 'end_turn');
    }
    send([{ type: 'text', text: 'Hola, ¿en qué te ayudo? (turnos recibidos: ' + msgs.length + ')' }], 'end_turn');
  });
});
module.exports = { srv, calls };
if (require.main === module) srv.listen(4010, () => console.log('mock 4010'));
