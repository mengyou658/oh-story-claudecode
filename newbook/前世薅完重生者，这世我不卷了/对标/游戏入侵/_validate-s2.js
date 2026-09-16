const fs = require('fs');
const path = require('path');
const dir = path.join(__dirname, '章节');
const files = fs.readdirSync(dir).filter(f => /第\d+章_摘要\.md$/.test(f));
files.sort((a, b) => {
  const na = +a.match(/第(\d+)章/)[1];
  const nb = +b.match(/第(\d+)章/)[1];
  return na - nb;
});
const tones = new Set(['紧张','轻松','悲伤','热血','爽','甜','温馨','恐怖','压抑','其他']);
const tags = new Set(['爱情','亲情','友情','权力','金钱','成长','复仇','悬念','搞笑','热血','日常','其他']);
let fail = 0;
const report = [];
for (const f of files) {
  const text = fs.readFileSync(path.join(dir, f), 'utf8');
  const n = (text.match(/^P\d+ /gm) || []).length;
  const toneN = (text.match(/基调：/g) || []).length;
  const descN = (text.match(/^P\d+ [^|]+\|[^|]*\S[^|]*\|[^|]*涉及/gm) || []).length;
  const toneVals = [...text.matchAll(/基调：([^ |\r\n]+)/g)].map(m => m[1]);
  const tagVals = [...text.matchAll(/主题标签[：]?([^ |\r\n]+)/g)].map(m => m[1].replace(/^：/, ''));
  const badTone = toneVals.filter(v => !tones.has(v));
  const badTag = tagVals.filter(v => !tags.has(v));
  const issues = [];
  if (n < 10) issues.push(`Pcount=${n}<10`);
  if (toneN !== n) issues.push(`tone ${toneN}!=${n}`);
  if (descN !== n) issues.push(`desc ${descN}!=${n}`);
  if (badTone.length) issues.push(`badTone=${badTone.join(',')}`);
  if (badTag.length) issues.push(`badTag=${badTag.join(',')}`);
  if (!/\*\*概要\*\*/.test(text)) issues.push('missing概要');
  if (issues.length) {
    fail++;
    report.push(`${f}: ${issues.join('; ')}`);
  }
}
console.log(`files=${files.length} fail=${fail}`);
report.forEach(r => console.log(r));
process.exit(fail ? 1 : 0);
