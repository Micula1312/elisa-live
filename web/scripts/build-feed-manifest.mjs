import { readdir, writeFile, mkdir } from "node:fs/promises";
import { join, relative, extname } from "node:path";

const root=join(process.cwd(),"public","feed");
const allowed=new Set([".jpg",".jpeg",".png",".webp",".gif",".avif"]);
const files=[];

async function walk(dir){
  let entries=[];
  try{entries=await readdir(dir,{withFileTypes:true})}
  catch(err){
    if(err.code==="ENOENT"){await mkdir(root,{recursive:true});return}
    throw err;
  }
  for(const entry of entries){
    if(entry.name==="manifest.json"||entry.name.startsWith("."))continue;
    const full=join(dir,entry.name);
    if(entry.isDirectory())await walk(full);
    else if(allowed.has(extname(entry.name).toLowerCase()))
      files.push(relative(root,full).replaceAll("\\","/"));
  }
}
await walk(root);
// Stable shuffle by filename hash: varied visually, deterministic between rehearsals.
const hash=s=>[...s].reduce((h,ch)=>((h*31+ch.charCodeAt(0))>>>0),2166136261);
files.sort((a,b)=>hash(a)-hash(b));
await writeFile(join(root,"manifest.json"),JSON.stringify(files,null,2)+"\n");
console.log(`[ELISA] feed manifest: ${files.length} images`);
