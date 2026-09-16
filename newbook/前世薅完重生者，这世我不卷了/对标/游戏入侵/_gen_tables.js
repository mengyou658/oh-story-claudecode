const fs = require('fs');
const meta = require('./_chapter_meta.json');
const rows = meta.rows;
let table = '| 章号 | 标题 | 起始行 | 字数 |\n|------|------|--------|------|\n';
for (const r of rows) {
  table += `| ${r.num} | ${r.title} | ${r.start} | ${r.chars} |\n`;
}
let idx = '| 章节 | 标题 | 字数 |\n|------|------|------|\n';
for (const r of rows) {
  idx += `| 第${r.num}章 | ${r.title} | ${r.chars} |\n`;
}
fs.writeFileSync('_boundary_table.md', table, 'utf8');
fs.writeFileSync('_index_table.md', idx, 'utf8');
console.log('ok', rows.length, 'total', meta.total);
