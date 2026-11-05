# Pruebas de interfaz en navegador real (Chromium headless). Requiere servidores en 3201 (IA simulada) y 3202 (sin IA).
import json, sys
from playwright.sync_api import sync_playwright

R = []
def t(name, fn):
    try: fn(); R.append(('✅', name))
    except Exception as e: R.append(('❌', f'{name} → {str(e)[:200]}'))

# Simula el micrófono (reconocimiento de voz) y registra lo que se habla, porque headless no tiene audio.
STUBS = """
window.__spoken = [];
class FakeSR { constructor(){ this.lang=''; } start(){ window.__srLang = this.lang; setTimeout(()=>{ this.onstart&&this.onstart();
  const r=[{0:{transcript:window.__sayNext||'hola'},isFinal:true,length:1}]; this.onresult&&this.onresult({results:r}); this.onend&&this.onend(); },50);} stop(){} abort(){} }
window.SpeechRecognition = FakeSR; window.webkitSpeechRecognition = FakeSR;
const realSS = window.speechSynthesis;
Object.defineProperty(window,'speechSynthesis',{value:{ speak(u){ window.__spoken.push({t:u.text,lang:u.lang}); setTimeout(()=>{u.onstart&&u.onstart(); u.onend&&u.onend();},5);}, cancel(){}, getVoices(){ return [{name:'Google español de Estados Unidos',lang:'es-US'},{name:'Paulina',lang:'es-MX'}]; }, onvoiceschanged:null }});
"""

with sync_playwright() as pw:
    b = pw.chromium.launch()
    ctx = b.new_context(viewport={'width': 1366, 'height': 900}, locale='es-CO')
    ctx.add_init_script(STUBS)
    page = ctx.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    # logo.png aún no existe en el proyecto y este entorno no tiene salida a Google Fonts: se ignoran
    page.on('response', lambda r: r.status >= 400 and 'logo.png' not in r.url and errors.append(f'{r.status} {r.url}'))
    page.goto('http://localhost:3201/#catalogo'); page.wait_for_timeout(800)

    t('Catálogo muestra los 132 productos', lambda: (lambda n: n == 132 or (_ for _ in ()).throw(Exception(n)))(page.locator('#productos-grid .prod-card').count()))
    t('19 fotos aprobadas visibles; el resto con respaldo elegante', lambda: (lambda n: n == 132 - 19 or (_ for _ in ()).throw(Exception(n)))(page.locator('#productos-grid .ph-fallback').count()))
    def busq():
        page.fill('#main-search', 'varilla media pulgada'); page.wait_for_timeout(200)
        names = page.locator('#productos-grid .prod-name').all_inner_texts()
        page.fill('#main-search', ''); page.wait_for_timeout(100)
        assert names == ['Varilla 1/2"'], names
    t('Búsqueda con medida hablada ("varilla media pulgada")', busq)
    def ficha():
        page.locator('#productos-grid .prod-name', has_text='Varilla 3/8"').first.click(); page.wait_for_timeout(300)
        assert page.locator('#pd-modal.open').count() == 1
        page.fill('#pd-qty', '25'); page.click('#pd-content .btn-checkout'); page.wait_for_timeout(300)
        assert json.loads(page.evaluate("localStorage.getItem('lt_cart')")) == [{'id': 15, 'qty': 25}]
    t('Ficha de producto abre y agrega cantidad al carrito (persistente)', ficha)

    page.goto('http://localhost:3201/'); page.wait_for_timeout(800)
    def featured():
        assert page.locator('#featured-grid .prod-card-home').count() == 4
        assert 'unsplash' not in page.inner_html('#featured-grid')
        assert page.locator('#testimonios').is_hidden()
    t('Destacados sin fotos engañosas; testimonios inventados ocultos', featured)

    def ai_cart():
        page.click('#lt-ai-launcher'); page.wait_for_timeout(300)
        assert 'IA' in page.inner_text('#lt-ai-status-text'), page.inner_text('#lt-ai-status-text')
        page.fill('#lt-ai-input', 'agrega 2 bultos de cemento argos'); page.click('#lt-ai-send')
        page.wait_for_selector('.lt-done-card', timeout=8000)
        cart = json.loads(page.evaluate("localStorage.getItem('lt_cart')"))
        assert {'id': 1, 'qty': 2} in cart, cart
        assert page.inner_text('#cart-count') == '2'
    t('Chat IA: agrega 2 bultos de Cemento Argos al carrito real y lo confirma', ai_cart)

    def voice():
        page.evaluate("window.__sayNext='placa de 6 x 8'; window.__spoken=[]")
        n = page.locator('.lt-msg.bot').count()
        page.click('#lt-ai-mic'); page.wait_for_function(f"document.querySelectorAll('.lt-msg.bot').length > {n} && !document.querySelector('.lt-typing')", timeout=8000)
        page.wait_for_timeout(400)
        assert page.evaluate('window.__srLang') == 'es-CO', 'lang'
        assert '34 bultos' in page.locator('.lt-msg.bot').last.inner_text(), page.locator('.lt-msg.bot').last.inner_text()
        spoken = page.evaluate('window.__spoken')
        assert spoken and spoken[0]['lang'].startswith('es'), spoken
        assert page.locator('.lt-msg.bot').last.locator('[data-act=addmany]').count() == 1, 'addmany'
    t('Voz: micrófono (es-CO) → IA → respuesta hablada en español + botón agregar cálculo', voice)

    def tts_toggle():
        page.click('#lt-voice-toggle'); assert page.get_attribute('#lt-voice-toggle', 'aria-pressed') == 'true'
        page.evaluate("window.__spoken=[]"); page.locator('.lt-replay').last.click(); page.wait_for_timeout(100)
        assert page.evaluate('window.__spoken.length') > 0
    t('Controles de voz: activar respuestas habladas y "Escuchar" de nuevo', tts_toggle)

    def checkout():
        page.click('#lt-ai-launcher'); page.click('.btn-cart'); page.wait_for_timeout(300)
        page.click('.btn-checkout'); page.wait_for_timeout(300)
        assert page.locator('#checkout-modal.open').count() == 1
        assert 'Cemento Argos' in page.inner_text('#co-resumen')
    t('Checkout existente intacto con productos agregados por la IA', checkout)

    # Móvil
    m = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True, locale='es-CO')
    m.add_init_script(STUBS)
    mp = m.new_page(); mp.goto('http://localhost:3201/#catalogo'); mp.wait_for_timeout(800)
    mp.screenshot(path='test/screens/movil-catalogo.png')
    t('Móvil: sin scroll horizontal', lambda: (lambda w: w <= 390 or (_ for _ in ()).throw(Exception(w)))(mp.evaluate('document.documentElement.scrollWidth')))
    mp.click('#lt-ai-launcher'); mp.wait_for_timeout(300)
    mp.fill('#lt-ai-input', 'agrega 2 bultos de cemento argos'); mp.click('#lt-ai-send'); mp.wait_for_selector('.lt-done-card', timeout=8000)
    mp.screenshot(path='test/screens/movil-chat.png')
    t('Móvil: chat a pantalla completa con micrófono visible', lambda: (lambda bb: bb['width'] >= 380 and mp.is_visible('#lt-ai-mic') or (_ for _ in ()).throw(Exception(bb)))(mp.locator('#lt-ai-chat').bounding_box()))

    # Sin IA configurada → modo básico honesto
    n = b.new_context(viewport={'width': 1366, 'height': 900}); np_ = n.new_page()
    np_.goto('http://localhost:3202/'); np_.wait_for_timeout(800); np_.click('#lt-ai-launcher'); np_.wait_for_timeout(400)
    def basic():
        assert 'modo básico' in np_.inner_text('#lt-ai-status-text')
        np_.fill('#lt-ai-input', 'muro de 5 x 2.4'); np_.click('#lt-ai-send'); np_.wait_for_timeout(1300)
        assert 'bloques' in np_.locator('.lt-msg.bot').last.inner_text().lower()
    t('Sin clave de IA: se indica "modo básico" y el motor local sigue respondiendo', basic)

    # Página abierta sin servidor (archivo suelto) no se rompe
    f = b.new_context().new_page(); ferr = []
    f.on('pageerror', lambda e: ferr.append(str(e)))
    f.goto('file:///home/claude/ltdelllano/public/index.html#catalogo'); f.wait_for_timeout(800)
    t('Abierta como archivo (sin servidor): catálogo y carrito funcionan', lambda: (f.locator('.prod-card').count() == 132 and not ferr) or (_ for _ in ()).throw(Exception(ferr)))

    page.goto('http://localhost:3201/'); page.wait_for_timeout(500); page.screenshot(path='test/screens/escritorio-inicio.png')
    page.goto('http://localhost:3201/#catalogo'); page.wait_for_timeout(500); page.click('#lt-ai-launcher'); page.wait_for_timeout(300); page.screenshot(path='test/screens/escritorio-catalogo-chat.png')
    t('Sin errores de JavaScript en consola', lambda: (not errors) or (_ for _ in ()).throw(Exception(errors[:3])))
    b.close()

print('\n'.join(' '.join(r) for r in R)); print(f"\n{sum(r[0]=='✅' for r in R)}/{len(R)} pruebas de interfaz OK")
