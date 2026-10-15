// Builds the Threads-style weekly review page for @sau21h.
// Usage: node build.js 2026-10-19 [days, default 7]   (run thumbs.ps1 with the same start and days first)
// Reads queue/*.json for the days from the start date, thumbs/<date>/NN.jpg and notes.json
// ({"2026-10-20": ["slide 1: ..."]}), writes sau21h-week-preview.html next to this file.
const fs = require('fs');
const path = require('path');
const dir = __dirname;
const root = path.join(dir, '..', '..');
const start = process.argv[2];
if (!/^\d{4}-\d{2}-\d{2}$/.test(start || '')) { console.error('usage: node build.js YYYY-MM-DD'); process.exit(1); }

const posts = {};
for (const f of fs.readdirSync(path.join(root, 'queue')).filter(f => f.endsWith('.json'))) {
  for (const p of JSON.parse(fs.readFileSync(path.join(root, 'queue', f), 'utf8'))) {
    if (/^\d{4}-\d{2}-\d{2}$/.test(p.date) && p.status !== 'retired') posts[p.date] = p;
  }
}
const notesFile = path.join(dir, 'notes.json');
const notes = fs.existsSync(notesFile) ? JSON.parse(fs.readFileSync(notesFile, 'utf8')) : {};
const DOW = ['Chủ nhật', 'Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7'];
const ddmm = d => d.slice(8, 10) + '/' + d.slice(5, 7);

const days = [];
const nDays = +(process.argv[3] || 7);
for (let i = 0; i < nDays; i++) {
  const t = new Date(start + 'T12:00:00Z'); t.setUTCDate(t.getUTCDate() + i);
  const date = t.toISOString().slice(0, 10);
  const p = posts[date];
  const day = { date, label: DOW[t.getUTCDay()], short: ddmm(date), post: null };
  if (p) {
    const tdir = path.join(dir, 'thumbs', date);
    const slides = fs.existsSync(tdir) ? fs.readdirSync(tdir).filter(f => f.endsWith('.jpg')).sort()
      .map(f => 'data:image/jpeg;base64,' + fs.readFileSync(path.join(tdir, f)).toString('base64')) : [];
    day.post = {
      status: p.status, pillar: p.pillar, hook: p.hook || '',
      threads: [p.caption, p.share].filter(Boolean).join('\n'),
      ig: [p.caption, p.share, p.hashtags].filter(Boolean).join('\n'),
      slides, notes: notes[date] || [],
    };
  }
  days.push(day);
}
const end = days[days.length - 1].short;
const week = { range: days[0].short + ' đến ' + end, built: ddmm(new Date(Date.now() + 7 * 3600e3).toISOString().slice(0, 10)), days };
const tpl = fs.readFileSync(path.join(dir, 'template.html'), 'utf8');
const out = tpl.replace('/*WEEK_DATA*/null', JSON.stringify(week));
fs.writeFileSync(path.join(dir, 'sau21h-week-preview.html'), out);
console.log('sau21h-week-preview.html', (out.length / 1e6).toFixed(2) + ' MB');
