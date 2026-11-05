// Copia las fotos aprobadas dentro de index.html para que se vean incluso sin servidor (abriendo el archivo).
const fs=require('fs');const images=JSON.parse(fs.readFileSync('data/images.json'));
const map={};for(const [id,i] of Object.entries(images)) if(i.status==='aprobada'&&i.file) map[id]=['img/productos/'+i.file+'?v='+(i.v||1), i.credit||null];
let s=fs.readFileSync('public/index.html','utf8');
const line='const LOCAL_IMG = '+JSON.stringify(map)+'; // generado por scripts/embed-images.js';
s=/const LOCAL_IMG = .*\n/.test(s)?s.replace(/const LOCAL_IMG = .*\n/,line+'\n'):s.replace('const PRODUCTOS = RAW.map(',line+'\nconst PRODUCTOS = RAW.map(');
fs.writeFileSync('public/index.html',s);console.log(Object.keys(map).length,'fotos incrustadas');
