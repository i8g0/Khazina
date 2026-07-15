import fs from "fs";
import path from "path";

function walk(dir, files = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full, files);
    else if (entry.name.endsWith(".js")) files.push(full);
  }
  return files;
}

const serverDir = ".next/server";
const files = walk(serverDir);
let reactModuleIds = new Set();
let useContextHits = 0;

for (const file of files) {
  const content = fs.readFileSync(file, "utf8");
  if (!content.includes("useContext")) continue;
  useContextHits++;
  for (const match of content.matchAll(/react@19\.2\.7/g)) {
    reactModuleIds.add(file);
  }
}

console.log("files with useContext:", useContextHits);
console.log("files mentioning react@19.2.7:", reactModuleIds.size);

const chunk875 = fs.readFileSync(".next/server/chunks/875.js", "utf8");
const reactDefs = [...chunk875.matchAll(/ReactSharedInternals/g)];
console.log("ReactSharedInternals in 875:", reactDefs.length);

const modules = [...chunk875.matchAll(/\/\* (\d+) \*\//g)].length;
console.log("webpack modules in 875:", modules);
