const fs = require('fs');
const path = require('path');
const root = __dirname;
const meta = JSON.parse(fs.readFileSync(path.join(root, '_chapter_meta.json'), 'utf8'));
const lines = fs.readFileSync(path.join(root, '原文', '原文.txt'), 'utf8').split(/\r?\n/);
const outDir = path.join(root, '_chapter_slices');
fs.mkdirSync(outDir, { recursive: true });
for (let i = 0; i < meta.rows.length; i++) {
  const r = meta.rows[i];
  const start = r.start - 1;
  const end = i < meta.rows.length - 1 ? meta.rows[i + 1].start - 2 : lines.length - 1;
  const body = lines.slice(start, end + 1).join('\n');
  const name = String(r.num).padStart(2, '0') + '.txt';
  fs.writeFileSync(path.join(outDir, name), body, 'utf8');
}
console.log('sliced', meta.rows.length, '->', outDir);
