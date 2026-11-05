"""Aplica las mejoras al index.html original con reemplazos exactos (falla si algo no coincide)."""
import re, sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()

def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        sys.exit(f'ERROR: esperado {count} coincidencia(s), hay {n}: {old[:80]!r}')
    s = s.replace(old, new)

def rep_re(pat, new):
    global s
    s2, n = re.subn(pat, lambda m: new, s, count=1, flags=re.S)
    if n != 1: sys.exit(f'ERROR regex: {pat[:80]}')
    s = s2

# ── 1. CSS nuevo ──
rep('</style>', r'''
/* ══════════ IMÁGENES DE PRODUCTO ══════════ */
.pimg{width:100%;height:100%;object-fit:contain;background:#fff;padding:8px;display:block;}
.prod-img.has-photo{background:#fff;}
.prod-img.has-photo .prod-img-label{display:none;}
.ph-fallback{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;width:100%;height:100%;background:radial-gradient(circle at 30% 20%,#fbf7ea,#ece7da);color:#9a937f;}
.ph-fallback svg{width:38px;height:38px;opacity:.45;}
.ph-fallback small{font-size:10px;letter-spacing:1.4px;text-transform:uppercase;}
.prod-card .prod-img,.prod-card .prod-name{cursor:pointer;}
.prod-card .prod-name:hover{text-decoration:underline;text-decoration-color:var(--dorado);}
.pch-img .pimg{padding:14px;}
/* ══════════ FICHA DE PRODUCTO ══════════ */
.pd-box{max-width:720px;display:grid;grid-template-columns:1fr 1fr;gap:26px;padding:30px;}
.pd-media{aspect-ratio:1;border-radius:16px;overflow:hidden;border:1.5px solid var(--borde);background:#fff;}
.pd-credit{font-size:10px;color:var(--gris-text);margin-top:6px;line-height:1.4;}
.pd-cat{font-size:11px;letter-spacing:2px;text-transform:uppercase;color:var(--dorado);font-weight:700;margin-bottom:6px;}
.pd-name{font-family:'Playfair Display',serif;color:var(--azul-dark);font-size:26px;line-height:1.2;margin-bottom:8px;padding-right:30px;}
.pd-sub{color:#444;font-size:14px;line-height:1.6;margin-bottom:14px;}
.pd-meta{font-size:13px;color:var(--gris-text);margin-bottom:6px;}
.pd-meta b{color:#222;}
.pd-price{font-size:15px;margin:14px 0;padding:12px 14px;background:var(--gris-bg);border-radius:12px;}
.pd-buy{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-top:8px;}
.pd-buy .btn-checkout{flex:1;min-width:160px;}
.pd-ask{display:block;text-align:center;margin-top:10px;font-size:13px;color:#128c4a;font-weight:600;}
@media(max-width:640px){.pd-box{grid-template-columns:1fr;padding:22px 18px;}.pd-media{max-height:260px;}}
/* ══════════ CHAT: VOZ E IMÁGENES ══════════ */
.lt-card-ic.ph{overflow:hidden;background:#fff;border:1px solid #eee;cursor:pointer;}
.lt-card-ic.ph img{width:100%;height:100%;object-fit:contain;}
.lt-card-tx b{cursor:pointer;}
.lt-bubble .lt-replay{background:none;border:none;cursor:pointer;font-size:13px;color:var(--gris-text);padding:2px 0 0;margin-top:6px;display:inline-flex;gap:4px;align-items:center;}
.lt-bubble .lt-replay:hover{color:var(--azul);}
.lt-bubble.err{background:#fff6f6;border-color:#f3c9c9;}
.lt-done-card{margin-top:8px;background:#eafaf1;border:1px solid #bfe9d0;border-radius:12px;padding:8px 10px;font-size:13px;color:#16653b;}
#lt-ai-mic{width:38px;height:38px;border-radius:12px;border:1.5px solid #e2e0d8;background:#fff;color:var(--azul);cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;transition:all .2s;position:relative;}
#lt-ai-mic svg{width:18px;height:18px;}
#lt-ai-mic:hover{border-color:var(--azul);}
#lt-ai-mic.rec{background:var(--error);border-color:var(--error);color:#fff;animation:micPulse 1.2s infinite;}
#lt-ai-mic.busy{opacity:.6;cursor:progress;}
#lt-ai-mic[hidden]{display:none;}
@keyframes micPulse{0%{box-shadow:0 0 0 0 rgba(217,54,54,.45);}100%{box-shadow:0 0 0 12px rgba(217,54,54,0);}}
.lt-voice-hint{font-size:12px;color:var(--error);text-align:center;margin-top:6px;min-height:0;}
.lt-voice-hint:empty{display:none;}
.lt-ai-icon-btn.on{background:var(--dorado);color:var(--azul-dark);}
.lt-ai-context.basic i{background:#e0a100;}
</style>''')

# ── 2. Destacados: sin fotos genéricas engañosas; se generan desde el catálogo ──
rep_re(r'<div class="grid-prods-home">.*?</article>\s*</div>', '<div class="grid-prods-home" id="featured-grid"></div>')

# ── 3. Testimonios: solo reales, desde CONFIG ──
rep_re(r'<!-- ► IMPORTANTE: reemplaza estos testimonios.*?</section>', '''<!-- Testimonios: se muestran solo si agregas reseñas REALES en CONFIG.testimonios -->
  <section class="testimonial-section" id="testimonios" hidden>
    <div class="section-header reveal">
      <span class="section-eyebrow">— Clientes felices —</span>
      <h2>Lo que dicen nuestros clientes</h2>
      <div class="section-divider"></div>
    </div>
    <div class="testi-grid" id="testi-grid"></div>
  </section>''')

# ── 4. Ficha de producto (modal) ──
rep('<!-- TOAST -->', '''<!-- ══════════════ FICHA DE PRODUCTO ══════════════ -->
<div class="modal-overlay" id="pd-modal" onclick="overlayClose(event,'pd-modal')">
  <div class="modal-box pd-box" role="dialog" aria-modal="true" aria-labelledby="pd-name" id="pd-content"></div>
</div>

<!-- TOAST -->''')

# ── 5. Chat: controles de voz ──
rep('''      <button class="lt-ai-icon-btn" onclick="newLTConversation()"''', '''      <button class="lt-ai-icon-btn" id="lt-voice-toggle" onclick="toggleVoiceReplies()" aria-pressed="false" aria-label="Activar respuestas habladas" title="Respuestas habladas">🔈</button>
      <button class="lt-ai-icon-btn" onclick="newLTConversation()"''')
rep('''      <button type="submit" id="lt-ai-send" aria-label="Enviar mensaje">''', '''      <button type="button" id="lt-ai-mic" onclick="toggleMic()" aria-label="Hablar con el asesor" title="Pulsa para hablar">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="2" width="6" height="12" rx="3"/><path d="M5 10a7 7 0 0 0 14 0"/><line x1="12" y1="17" x2="12" y2="22"/></svg>
      </button>
      <button type="submit" id="lt-ai-send" aria-label="Enviar mensaje">''')
rep('''    <small>Los cálculos son aproximados. Un asesor confirma precios y cantidades.</small>''', '''    <div class="lt-voice-hint" id="lt-voice-hint" role="status"></div>
    <small>Los cálculos son aproximados. Un asesor confirma precios y cantidades.</small>''')
rep('<div class="lt-ai-status"><i></i>Asesor virtual · responde al instante</div>', '<div class="lt-ai-status"><i></i><span id="lt-ai-status-text">Asesor virtual</span></div>')

# ── 6. CONFIG ──
rep("""  aiEndpoint: '',
};""", """  aiEndpoint: '/api/chat',   // Se activa solo si el servidor tiene la IA configurada (ver README)
  apiBase: '',               // Vacío = mismo dominio. Si la tienda y el servidor están en dominios distintos, pon la URL del servidor.

  // Productos destacados en el inicio (ids del catálogo)
  destacados: [1, 7, 14, 63],

  // Testimonios REALES (ej. copiados de tus reseñas de Google). Vacío = la sección no se muestra.
  // { texto:'...', nombre:'...', rol:'...', estrellas:5 }
  testimonios: [],
};""")

# ── 7. Catálogo: let + carga desde el servidor (fotos/precios) ──
rep("const PRODUCTOS = RAW.map(([id,cat,nombre,sub,u,precio]) => ({id,cat,catLabel:CAT_LABEL[cat],nombre,sub,u:u||'unidad',precio:precio||null}));",
"""const PRODUCTOS = RAW.map(([id,cat,nombre,sub,u,precio]) => ({id,cat,catLabel:CAT_LABEL[cat],nombre,sub,u:u||'unidad',precio:precio||null,img:null,imgCredit:null,marca:null}));
const API = path => (CONFIG.apiBase || '') + path;
const SERVER = {online:false, ai:false, serverSTT:false};
// Si hay servidor, trae fotos aprobadas, precios y marcas. Nunca borra productos: solo completa datos por id.
async function loadServer(){
  try {
    const h = await fetch(API('/api/health'), {cache:'no-store'}); if (!h.ok) throw 0;
    Object.assign(SERVER, await h.json(), {online:true});
    const r = await fetch(API('/api/catalog')); if (!r.ok) throw 0;
    const data = await r.json();
    data.productos.forEach(sp => { const p = prod(sp.id); if (p) Object.assign(p, {img: sp.img ? API(sp.img) : null, imgCredit: sp.imgCredit, precio: sp.precio || p.precio, marca: sp.marca}); });
  } catch(e) { SERVER.online = false; }
  updateAIStatus(); renderAll();
}
function renderAll(){ renderFeatured(); render(); renderCart(); }""")

# ── 8. Imagen de producto + fallback elegante ──
rep("function imgFallback(img, cat){ const box = img.parentNode; img.remove(); box.insertAdjacentHTML('afterbegin', icon(cat)); }",
"""function imgFallback(img, cat){ const box = img.parentNode; img.remove(); box.classList.remove('has-photo'); box.insertAdjacentHTML('afterbegin', phFallback(cat)); }
const phFallback = cat => `<div class="ph-fallback">${icon(cat, '#8a826c', 1.4)}<small>Foto próximamente</small></div>`;
function prodImg(p){
  return p.img ? `<img class="pimg" src="${esc(p.img)}" alt="${esc(p.nombre)}" loading="lazy" decoding="async" width="400" height="400" onerror="imgFallback(this,'${p.cat}')">` : phFallback(p.cat);
}""")

# ── 9. Tarjetas del catálogo con foto y ficha ──
rep("""      <div class="prod-img">${icon(p.cat)}<span class="prod-img-label">${p.catLabel}</span><div class="prod-cat-tag">${p.catLabel}</div></div>
      <div class="prod-body">
        <h3 class="prod-name">${esc(p.nombre)}</h3>""",
"""      <div class="prod-img ${p.img ? 'has-photo' : ''}" onclick="openProduct(${p.id})" role="button" tabindex="0" aria-label="Ver ficha de ${esc(p.nombre)}" onkeydown="if(event.key==='Enter')openProduct(${p.id})">${prodImg(p)}<div class="prod-cat-tag">${p.catLabel}</div></div>
      <div class="prod-body">
        <h3 class="prod-name" onclick="openProduct(${p.id})">${esc(p.nombre)}</h3>""")
rep("#productos-grid.list-view .prod-img-label,#productos-grid.list-view .prod-cat-tag{display:none;}",
    "#productos-grid.list-view .prod-img-label,#productos-grid.list-view .prod-cat-tag,#productos-grid.list-view .ph-fallback small{display:none;}\n#productos-grid.list-view .pimg{padding:4px;}")
rep(".prod-img{height:140px;width:100%;", ".prod-img{height:170px;width:100%;overflow:hidden;")
rep("  .prod-img{height:100px;}", "  .prod-img{height:130px;}")

# Ordenar por precio solo si existen precios
rep("""    <option value="za">Z → A</option>""", """    <option value="za">Z → A</option>
            <option value="p-asc" data-price hidden>Precio: menor a mayor</option>
            <option value="p-desc" data-price hidden>Precio: mayor a menor</option>""")
rep("""  if (currentSort === 'za') list.sort((a, b) => b.nombre.localeCompare(a.nombre, 'es'));""",
"""  if (currentSort === 'za') list.sort((a, b) => b.nombre.localeCompare(a.nombre, 'es'));
  if (currentSort === 'p-asc') list.sort((a, b) => (a.precio ?? Infinity) - (b.precio ?? Infinity));
  if (currentSort === 'p-desc') list.sort((a, b) => (b.precio ?? -1) - (a.precio ?? -1));""")
rep("""function render(){
  const list = filtered();""", """function render(){
  document.querySelectorAll('[data-price]').forEach(o => o.hidden = !PRODUCTOS.some(p => p.precio));
  const list = filtered();""")

# ── 10. Destacados, testimonios y ficha ──
rep("function resetFilter(){", r"""function renderFeatured(){
  $('#featured-grid').innerHTML = CONFIG.destacados.map(prod).filter(Boolean).map((p, i) => `
    <article class="prod-card-home reveal visible">
      <div class="pch-img" onclick="openProduct(${p.id})" style="cursor:pointer">${prodImg(p)}${i === 0 ? '<span class="pch-badge">Más vendido</span>' : ''}</div>
      <div class="pch-body">
        <div class="pch-cat">${esc(p.catLabel)}</div>
        <h3 class="pch-name">${esc(p.nombre)}</h3>
        <p class="pch-desc">${esc(p.sub)}</p>
        <div class="pch-footer"><div class="pch-price">${p.precio ? fmtCOP(p.precio) + ' / ' + p.u : 'Precio a cotizar'}</div><button class="btn-add-home" onclick="addToCart(${p.id})">+ Agregar</button></div>
      </div>
    </article>`).join('');
}
function renderTestimonials(){
  const T = CONFIG.testimonios || [];
  $('#testimonios').hidden = !T.length;
  $('#testi-grid').innerHTML = T.map(t => { const n = Math.max(1, Math.min(5, t.estrellas || 5)); return `
    <div class="testi-card reveal"><div class="testi-stars" aria-label="${n} de 5 estrellas">${'★'.repeat(n)}${'☆'.repeat(5 - n)}</div>
      <p class="testi-text">"${esc(t.texto)}"</p>
      <div class="testi-author"><div class="testi-avatar">${esc(String(t.nombre || '?').split(' ').map(w => w[0]).slice(0, 2).join(''))}</div><div class="testi-info"><div class="name">${esc(t.nombre)}</div><div class="role">${esc(t.rol || '')}</div></div></div>
    </div>`; }).join('');
}
function openProduct(id){
  const p = prod(id); if (!p) return;
  const rel = PRODUCTOS.filter(x => x.cat === p.cat && x.id !== p.id).slice(0, 0);
  $('#pd-content').innerHTML = `
    <button class="modal-close" onclick="closeModal('pd-modal')" aria-label="Cerrar">✕</button>
    <div><div class="pd-media">${prodImg(p)}</div>${p.imgCredit ? `<div class="pd-credit">${esc(p.imgCredit)}</div>` : ''}</div>
    <div>
      <div class="pd-cat">${esc(p.catLabel)}</div>
      <h2 class="pd-name" id="pd-name">${esc(p.nombre)}</h2>
      <p class="pd-sub">${esc(p.sub)}</p>
      ${p.marca ? `<div class="pd-meta">Marca: <b>${esc(p.marca)}</b></div>` : ''}
      <div class="pd-meta">Se vende por: <b>${esc(p.u)}</b></div>
      <div class="pd-price">${p.precio ? `<b>${fmtCOP(p.precio)}</b> / ${esc(p.u)}` : 'Precio mayorista: <b>a cotizar</b> según volumen. Te lo confirmamos por WhatsApp.'}</div>
      <div class="pd-buy">
        <div class="qty-ctrl"><button class="qty-btn" type="button" onclick="pdQty(-1)" aria-label="Menos">−</button><input class="qty-input" id="pd-qty" type="number" inputmode="numeric" min="1" value="1" aria-label="Cantidad"><button class="qty-btn" type="button" onclick="pdQty(1)" aria-label="Más">+</button></div>
        <button class="btn-checkout" onclick="addToCart(${p.id}, $('#pd-qty').value);closeModal('pd-modal')">Agregar al pedido</button>
      </div>
      <a class="pd-ask" href="${waLink('Hola, quiero información de: ' + p.nombre)}" target="_blank" rel="noopener">💬 Preguntar por este producto</a>
    </div>`;
  openModal('pd-modal');
}
function pdQty(d){ const i = $('#pd-qty'); i.value = Math.max(1, (parseInt(i.value) || 1) + d); }
function resetFilter(){""")

# ── 11. Chat con IA real ──
rep_re(r"/\* --- Conexión opcional con IA real.*?\n}\n\n/\* --- Interfaz del chat --- \*/", r"""/* --- IA real (Claude) a través del servidor. Sin servidor/IA → motor básico local. --- */
function updateAIStatus(){
  const ai = SERVER.online && SERVER.ai && CONFIG.aiEndpoint;
  $('#lt-ai-status-text').textContent = ai ? 'Asesor con IA · en línea' : 'Asesor virtual · modo básico';
  $('#lt-ai-context-text').textContent = ai ? `IA conectada al catálogo · ${PRODUCTOS.length} productos` : `Modo básico (sin IA) · ${PRODUCTOS.length} productos`;
  document.querySelector('.lt-ai-context').classList.toggle('basic', !ai);
  setupMic();
}
function mdLite(t){
  return esc(t).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>').replace(/(^|\n)\s*[-•]\s+(.+)/g, '$1• $2').replace(/\n/g, '<br>');
}
function ltCardsImg(list){
  return `<div class="lt-cards">${list.map(p => `
    <div class="lt-card"><div class="lt-card-ic ${p.img ? 'ph' : ''}" onclick="openProduct(${p.id})">${p.img ? `<img src="${esc(p.img)}" alt="" loading="lazy">` : icon(p.cat)}</div>
      <div class="lt-card-tx"><b onclick="openProduct(${p.id})">${esc(p.nombre)}</b><small>${p.precio ? fmtCOP(p.precio) + ' / ' + esc(p.u) : esc(p.sub) + ' · precio a cotizar'}</small></div>
      <button class="lt-card-add" data-act="add" data-id="${p.id}" data-qty="1" aria-label="Agregar ${esc(p.nombre)}">+ Agregar</button>
    </div>`).join('')}</div>`;
}
async function ltReply(text){
  if (!(SERVER.online && SERVER.ai && CONFIG.aiEndpoint)) return ltLocal(text);
  const msgs = LT.history.filter(h => h.text).slice(-12).map(h => ({role: h.role === 'bot' ? 'assistant' : 'user', text: h.text.slice(0, h.role === 'bot' ? 2500 : 600)}));
  try {
    const r = await fetch(API(CONFIG.aiEndpoint), {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({messages: msgs, cart: cart.map(i => ({id:i.id, qty:i.qty}))})});
    const d = await r.json().catch(() => ({}));
    if (!r.ok){
      if (d.code === 'no_ai'){ SERVER.ai = false; updateAIStatus(); return ltLocal(text); }
      return {err:true, html:`⚠️ ${esc(d.error || 'No pude conectarme con el asesor.')}` + ltActs([['retry', '↻ Reintentar', text], ['wa', '💬 Preguntar por WhatsApp', 'Hola, tengo esta consulta: ' + text, 'wa']])};
    }
    // Ejecuta las acciones REALES en el carrito y confirma solo las que funcionaron
    const done = [];
    (d.actions || []).forEach(a => {
      if (a.type !== 'add_to_cart' || !prod(a.id)) return;
      const before = cart.find(c => c.id === a.id)?.qty || 0;
      addToCart(a.id, a.qty, true);
      const after = cart.find(c => c.id === a.id)?.qty || 0;
      if (after > before) done.push(`${(after - before).toLocaleString('es-CO')} ${plural(prod(a.id).u, after - before)} de ${prod(a.id).nombre}`);
    });
    const shown = (d.products || []).map(sp => prod(sp.id)).filter(Boolean);
    let html = mdLite(d.reply || '');
    if (done.length) html += `<div class="lt-done-card">✅ En tu pedido: ${done.map(esc).join(', ')}</div>` + ltActs(ACT_ORDER());
    else if (shown.length) html += ltCardsImg(shown.slice(0, 6));
    if (d.calc && d.calc.resultados) html += ltActs([['addmany', '➕ Agregar cálculo al pedido', d.calc.resultados.map(x => x.producto_id + ':' + x.cantidad).join(','), 'main']]);
    return {html, text: d.reply || '', speak: d.reply || ''};
  } catch(e) {
    return {err:true, html:`⚠️ Se perdió la conexión con el asesor.` + ltActs([['retry', '↻ Reintentar', text], ['wa', '💬 WhatsApp', 'Hola, tengo esta consulta: ' + text, 'wa']])};
  }
}

/* --- Voz: micrófono (pulsar para hablar) y respuestas habladas --- */
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
const VOICE = {rec:null, recording:false, mediaRec:null, chunks:[], viaVoice:false, on: store.get('lt_voice', false), speaking:false};
function voiceHint(t){ $('#lt-voice-hint').textContent = t || ''; if (t) setTimeout(() => { if ($('#lt-voice-hint').textContent === t) $('#lt-voice-hint').textContent = ''; }, 6000); }
function setupMic(){
  const can = !!SR || (SERVER.serverSTT && !!window.MediaRecorder && !!navigator.mediaDevices);
  $('#lt-ai-mic').title = can ? 'Pulsa para hablar' : 'Tu navegador no permite dictado por voz';
  $('#lt-ai-mic').dataset.can = can ? '1' : '';
}
function micUI(state){ const b = $('#lt-ai-mic'); b.classList.toggle('rec', state === 'rec'); b.classList.toggle('busy', state === 'busy'); b.setAttribute('aria-label', state === 'rec' ? 'Detener grabación' : 'Hablar con el asesor'); }
async function toggleMic(){
  stopSpeaking();
  if (VOICE.recording){ if (VOICE.rec) VOICE.rec.stop(); if (VOICE.mediaRec) VOICE.mediaRec.stop(); return; }
  if (!window.isSecureContext) return voiceHint('El micrófono solo funciona en sitios con https.');
  if (SR) return startBrowserSTT();
  if (SERVER.serverSTT && window.MediaRecorder && navigator.mediaDevices) return startServerSTT();
  voiceHint('Tu navegador no permite dictado por voz. Prueba con Chrome, Edge o Safari, o escribe tu mensaje.');
}
function startBrowserSTT(){
  const rec = new SR(); VOICE.rec = rec;
  rec.lang = 'es-CO'; rec.interimResults = true; rec.continuous = false; rec.maxAlternatives = 1;
  const input = $('#lt-ai-input'); let finalText = '';
  rec.onstart = () => { VOICE.recording = true; micUI('rec'); voiceHint(''); input.placeholder = 'Te escucho…'; };
  rec.onresult = e => { let interim = ''; for (const r of e.results){ if (r.isFinal) finalText = r[0].transcript; else interim += r[0].transcript; } input.value = finalText || interim; autoResize(input); };
  rec.onerror = e => {
    const m = {'not-allowed':'Permiso de micrófono denegado. Actívalo en el candado de la barra de direcciones.', 'service-not-allowed':'Permiso de micrófono denegado.', 'no-speech':'No te escuché. Intenta de nuevo, más cerca del micrófono.', 'audio-capture':'No se encontró un micrófono.', 'network':'El dictado necesita conexión a internet.'};
    voiceHint(m[e.error] || 'No pude usar el micrófono.');
  };
  rec.onend = () => { VOICE.recording = false; VOICE.rec = null; micUI(); input.placeholder = 'Ej: necesito 20 bultos de cemento';
    const t = input.value.trim(); if (t){ VOICE.viaVoice = true; ltSend(); } };
  try { rec.start(); } catch(e) { voiceHint('No pude iniciar el micrófono.'); }
}
async function startServerSTT(){
  let stream;
  try { stream = await navigator.mediaDevices.getUserMedia({audio:true}); }
  catch(e){ return voiceHint(e.name === 'NotAllowedError' ? 'Permiso de micrófono denegado.' : 'No se encontró un micrófono.'); }
  const type = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4', 'audio/ogg'].find(t => MediaRecorder.isTypeSupported?.(t)) || '';
  const mr = new MediaRecorder(stream, type ? {mimeType:type} : undefined); VOICE.mediaRec = mr; VOICE.chunks = [];
  const stopT = setTimeout(() => mr.state === 'recording' && mr.stop(), 30000);
  mr.ondataavailable = e => e.data.size && VOICE.chunks.push(e.data);
  mr.onstop = async () => {
    clearTimeout(stopT); stream.getTracks().forEach(t => t.stop()); VOICE.recording = false; VOICE.mediaRec = null; micUI('busy');
    try {
      const blob = new Blob(VOICE.chunks, {type: mr.mimeType || 'audio/webm'});
      const r = await fetch(API('/api/transcribe'), {method:'POST', headers:{'Content-Type': blob.type.split(';')[0]}, body: blob});
      const d = await r.json();
      if (!r.ok || !d.text) throw new Error(d.error);
      $('#lt-ai-input').value = d.text; VOICE.viaVoice = true; ltSend();
    } catch(e){ voiceHint(e.message || 'No pude transcribir el audio.'); }
    micUI();
  };
  mr.start(); VOICE.recording = true; micUI('rec'); voiceHint('Grabando… toca el micrófono para terminar.');
}
function pickVoice(){
  const vs = speechSynthesis.getVoices().filter(v => /^es/i.test(v.lang));
  const pref = ['es-CO', 'es-419', 'es-US', 'es-MX'];
  for (const l of pref){ const v = vs.find(v => v.lang.replace('_', '-') === l && /natural|google|online|neural/i.test(v.name)) || vs.find(v => v.lang.replace('_', '-') === l); if (v) return v; }
  return vs[0] || null;
}
function speak(text){
  if (!('speechSynthesis' in window) || !text) return;
  stopSpeaking();
  const clean = text.replace(/\*\*/g, '').replace(/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}]/gu, '').replace(/\s*[-•]\s+/g, '. ').replace(/(\d)"/g, '$1 pulgadas').replace(/×/g, ' por ').replace(/\bm²/g, ' metros cuadrados').replace(/\bm³/g, ' metros cúbicos');
  // Se divide en frases: evita que algunos navegadores corten textos largos
  const parts = clean.match(/[^.!?\n]+[.!?]?/g) || [clean];
  const v = pickVoice();
  parts.forEach((ptxt, i) => {
    const u = new SpeechSynthesisUtterance(ptxt.trim()); u.lang = v ? v.lang : 'es-CO'; if (v) u.voice = v; u.rate = 1.02; u.pitch = 1;
    if (i === 0) u.onstart = () => { VOICE.speaking = true; voiceBtn(); };
    if (i === parts.length - 1) u.onend = u.onerror = () => { VOICE.speaking = false; voiceBtn(); };
    speechSynthesis.speak(u);
  });
}
function stopSpeaking(){ if ('speechSynthesis' in window) speechSynthesis.cancel(); VOICE.speaking = false; voiceBtn(); }
function voiceBtn(){
  const b = $('#lt-voice-toggle'); if (!b) return;
  b.textContent = VOICE.speaking ? '⏹' : (VOICE.on ? '🔊' : '🔈');
  b.classList.toggle('on', VOICE.on);
  b.setAttribute('aria-pressed', VOICE.on);
  b.setAttribute('aria-label', VOICE.speaking ? 'Detener respuesta hablada' : (VOICE.on ? 'Desactivar respuestas habladas' : 'Activar respuestas habladas'));
  b.title = b.getAttribute('aria-label');
}
function toggleVoiceReplies(){
  if (VOICE.speaking) return stopSpeaking();
  if (!('speechSynthesis' in window)) return voiceHint('Tu navegador no puede leer respuestas en voz alta.');
  VOICE.on = !VOICE.on; store.set('lt_voice', VOICE.on); voiceBtn();
  voiceHint(VOICE.on ? 'Respuestas habladas activadas.' : 'Respuestas habladas desactivadas.');
}
if ('speechSynthesis' in window) speechSynthesis.onvoiceschanged = () => {};

/* --- Interfaz del chat --- */""")

# ltAdd guarda texto del bot y agrega botón "escuchar"
rep("""function ltAppend(role, html){
  const m = document.createElement('div');
  m.className = 'lt-msg ' + role;
  m.innerHTML = `<div class="lt-bubble">${html}</div>`;""", """function ltAppend(role, html, speakText, err){
  const m = document.createElement('div');
  m.className = 'lt-msg ' + role;
  const replay = role === 'bot' && speakText && 'speechSynthesis' in window ? `<br><button type="button" class="lt-replay" data-act="speak" data-arg="${esc(speakText)}" aria-label="Escuchar respuesta">🔊 Escuchar</button>` : '';
  m.innerHTML = `<div class="lt-bubble${err ? ' err' : ''}">${html}${replay}</div>`;""")
rep("""function ltAdd(role, html, text){
  ltAppend(role, html);
  LT.history.push({role, html, text: text || ''});""", """function ltAdd(role, html, text, speakText, err){
  ltAppend(role, html, speakText, err);
  LT.history.push({role, html, text: text || '', speak: speakText || ''});""")
rep("""  typing.remove();
  ltAdd('bot', res.html);""", """  typing.remove();
  const sp = res.speak || (res.html || '').replace(/<(ul|table|div)[\\s\\S]*$/i, '').replace(/<[^>]+>/g, ' ').replace(/\\s+/g, ' ').trim();
  ltAdd('bot', res.html, res.text || '', res.err ? '' : sp, res.err);
  if (!res.err && (VOICE.on || VOICE.viaVoice)) speak(sp);
  VOICE.viaVoice = false;""")
rep("""  if (LT.history.length){ LT.history.forEach(h => ltAppend(h.role, h.html)); setChips(CHIPS_DEFAULT); }""",
    """  if (LT.history.length){ LT.history.forEach(h => ltAppend(h.role, h.html, h.speak)); setChips(CHIPS_DEFAULT); }""")
# Acciones nuevas del chat
rep("""  else if (act === 'hv'){ closeLTChat(); openHVModal(); }""", """  else if (act === 'hv'){ closeLTChat(); openHVModal(); }
  else if (act === 'speak'){ speak(arg); }
  else if (act === 'retry'){ ltSend(arg); }""")
# Cerrar chat detiene voz; Escape cierra ficha (ya cubierto por modal-overlay)
rep("""function closeLTChat(){
  document.body.classList.remove('lt-open');""", """function closeLTChat(){
  stopSpeaking(); if (VOICE.recording){ VOICE.rec?.abort?.(); VOICE.mediaRec?.stop(); }
  document.body.classList.remove('lt-open');""")
# Chips: tocar → si hay IA se envía tal cual
# Inicio
rep("""  buildCategories();
  renderCart();""", """  buildCategories();
  renderFeatured();
  renderTestimonials();
  renderCart();
  voiceBtn(); updateAIStatus();
  loadServer();""")
rep("""  $('#lt-ai-context-text').textContent = `Conectado al catálogo · ${PRODUCTOS.length} productos`;\n""", "")
# Mensaje de bienvenida más útil con voz
rep("""<li>Armar tu pedido y explicarte cómo pagar</li></ul>¿Qué vas a construir?`);""", """<li>Armar tu pedido y explicarte cómo pagar</li></ul>¿Qué vas a construir? También puedes hablarme con el 🎤.`);""")
# SEO/OG: la imagen de vista previa ya no promete un producto
open(p, 'w', encoding='utf-8').write(s)
print('OK', len(s))
