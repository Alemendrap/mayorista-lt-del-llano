// Importa fotos ya revisadas a la tienda: WebP 800x800 fondo blanco + registro con licencia y crédito.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),sharp=require('sharp');
const [srcDir, creditsFile] = process.argv.slice(2);
const credits=JSON.parse(fs.readFileSync(creditsFile,'utf8'));
const imgPath='data/images.json'; const images=fs.existsSync(imgPath)?JSON.parse(fs.readFileSync(imgPath)):{};
const cat=JSON.parse(fs.readFileSync('data/catalog.json')).productos;
(async()=>{ const seen=new Set();
 for(const c of credits){
  const p=cat.find(x=>x.id===c.id); if(!p) throw new Error('no existe '+c.id);
  const out=await sharp(path.join(srcDir,c.local)).rotate().resize(800,800,{fit:'contain',background:'#ffffff'}).flatten({background:'#ffffff'}).webp({quality:82}).toBuffer();
  const hash=crypto.createHash('sha1').update(out).digest('hex').slice(0,10); if(seen.has(hash)) throw new Error('duplicada '+c.id); seen.add(hash);
  fs.writeFileSync(`public/img/productos/${c.id}.webp`,out);
  images[c.id]={status:'aprobada',confidence:'media',source:'wikimedia_commons',license:c.licencia,sourceUrl:c.pagina,
    credit:`Foto: ${c.autor} · ${c.licencia} · Wikimedia Commons (foto de referencia)`,file:`${c.id}.webp`,hash,v:1,approvedBy:'propietario (chat 2026-11-05)',updated:new Date().toISOString()};
  console.log(c.id,p.nombre,Math.round(out.length/1024)+'KB');
 }
 fs.writeFileSync(imgPath,JSON.stringify(images,null,1)); require('child_process').execSync('node scripts/embed-images.js',{stdio:'inherit'});
})();
