// Extrae CATS y RAW del HTML original a data/catalog.json SIN modificar ids, nombres ni descripciones.
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
const grab = name => { const m = src.match(new RegExp('const ' + name + ' = (\\[[\\s\\S]*?\\n\\]);')); if (!m) throw new Error(name); return Function('return ' + m[1])(); };
const CATS = grab('CATS'), RAW = grab('RAW');
const cats = CATS.map(({id,label,sub}) => ({id,label,sub}));
const productos = RAW.map(([id,cat,nombre,sub,u,precio]) => ({id,cat,nombre,sub,u:u||'unidad',precio:precio||null,marca:null,referencia:null}));
// Marca solo cuando aparece literalmente en el nombre (no se inventa)
const MARCAS = ['Argos','San Marcos','Tequendama','Sika','Supermastick','Santa Fe','Corona','Perfiacero','Metaldeck'];
productos.forEach(p => { const m = MARCAS.find(b => p.nombre.includes(b)); if (m) p.marca = m; });
fs.writeFileSync('data/catalog.json', JSON.stringify({version:1, actualizado:new Date().toISOString().slice(0,10), categorias:cats, productos}, null, 1));
console.log(cats.length, 'categorías,', productos.length, 'productos,', productos.filter(p=>p.marca).length, 'con marca,', productos.filter(p=>p.precio).length, 'con precio');
