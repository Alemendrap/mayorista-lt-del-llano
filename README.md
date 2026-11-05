# Mayorista LT del Llano — tienda con asesor de IA

## Qué hay en esta carpeta

| Ruta | Qué es |
|---|---|
| `public/index.html` | La tienda (tu página, mejorada). Funciona incluso abierta como archivo suelto, pero la IA y las fotos necesitan el servidor. |
| `public/admin.html` | Panel de fotos del catálogo (protegido con clave). Se abre en `tudominio.com/admin`. |
| `server.js` | Servidor: IA conectada al catálogo, voz, panel de fotos, límites de seguridad. |
| `data/catalog.json` | **Tu catálogo** (132 productos, mismos ids, nombres y descripciones del original). Aquí agregas precios. |
| `data/images.json` | Se crea solo: qué foto tiene cada producto, su origen, licencia y nivel de confianza. |
| `public/img/productos/` | Fotos optimizadas (WebP 800×800). |
| `backup/` | Copia intacta de tu página original. |
| `test/` | Pruebas automáticas. |

## Ponerla en línea (unos 20 minutos)

Necesitas un hosting que ejecute **Node.js 20+ con disco persistente** (las fotos se guardan en disco). Opciones: Railway, Render (con "Persistent Disk"), o un VPS (DigitalOcean, Hostinger VPS). Un hosting solo de HTML (Netlify, GitHub Pages) **no** sirve para la IA.

1. Sube esta carpeta (sin `node_modules` ni `.env`) a GitHub o al hosting.
2. Comando de instalación: `npm install` · Comando de inicio: `npm start`.
3. En el panel del hosting, sección **Variables de entorno**, crea (ver `.env.example`):
   - `ANTHROPIC_API_KEY` → créala en https://console.anthropic.com (requiere cargar saldo).
   - `ADMIN_TOKEN` → una clave larga inventada por ti (mín. 16 caracteres).
   - `TRUST_PROXY=1`.
   - Opcional: `OPENAI_API_KEY` para dictado por voz en Firefox.
4. Si usas Render/Railway, monta el disco persistente en la carpeta del proyecto para `data/` y `public/img/`.
5. Abre `tudominio.com`: el chat debe decir **"Asesor con IA · en línea"**. Si dice "modo básico", la clave no está configurada.
6. Pon tu `logo.png` y `qr-pago.png` dentro de `public/`.

En tu computador: `npm install`, crea `.env` a partir de `.env.example`, y `npm start` → http://localhost:3000

## Agregar precios, marcas o referencias

Edita `data/catalog.json` (el servidor lo recarga solo). Ejemplo:
```json
{"id":1,"cat":"cementos","nombre":"Cemento Argos x 50 kg","sub":"Bulto 50 kg · Uso estructural","u":"bulto","precio":32000,"marca":"Argos","referencia":"ARG-50"}
```
Con precio, la tienda muestra el valor, el carrito calcula el total, aparece el orden por precio y la IA puede citarlo. Sin precio, todo dice "a cotizar" y la IA no inventa valores.

## Fotos de productos

En `/admin`: **Subir foto** (lo más confiable: foto propia o la que te entregue tu proveedor con permiso) o **Sugerencias** (busca en Wikimedia Commons solo imágenes con licencia libre; tú apruebas cada una y el crédito al autor se muestra en la ficha). Nada se publica sin tu aprobación. El panel muestra la cobertura y exporta un reporte CSV.

Para fotos oficiales de marca (Argos, Sika, Corona…), pídelas al asesor comercial de cada marca: los distribuidores suelen recibir el material con permiso de uso.

## Costos

- **IA (Anthropic):** se cobra por tokens. Cada mensaje usa ~2 a 4 llamadas al modelo (por las consultas al catálogo). El texto de instrucciones se guarda en caché para abaratarlo. Tope diario configurable con `DAILY_AI_LIMIT`. Precios: https://www.anthropic.com/pricing
- **Voz:** el dictado (Chrome, Edge, Safari) y la lectura en voz alta usan el navegador del cliente: **gratis**. Solo `OPENAI_API_KEY` (opcional) tiene costo por minuto de audio.
- **Hosting:** según el proveedor.

## Pruebas

`npm test` (servidor, con una API de IA simulada) y `python3 test/ui_test.py` (navegador, con los servidores corriendo en 3201/3202).
