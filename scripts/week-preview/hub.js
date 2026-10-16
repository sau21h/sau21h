// Writes week.json + avatar.jpg here in the Content Hub format (see 1. Business/0. Content Hub/build.js).
// Usage: node hub.js 2026-10-16 [days, default 10]   (run thumbs.ps1 with the same start and days first)
// Queue status -> Hub status: review -> Draft (waiting for Trung), approved -> Approved, posted -> Posted.
// Posts still in draft (not rendered) are left out. Post id = S21-<date>; thumbs/<date>/NN.jpg are the slides.
// Hub decisions are synced back by Claude: approved -> queue status "approved", skip -> "retired",
// fix -> re-roll or edit per the note, status stays "review".
const fs = require('fs');
const path = require('path');
const dir = __dirname;
const root = path.join(dir, '..', '..');
const start = process.argv[2];
if (!/^\d{4}-\d{2}-\d{2}$/.test(start || '')) { console.error('usage: node hub.js YYYY-MM-DD [days]'); process.exit(1); }
const nDays = +(process.argv[3] || 10);

const posts = {};
for (const f of fs.readdirSync(path.join(root, 'queue')).filter(f => f.endsWith('.json'))) {
  for (const p of JSON.parse(fs.readFileSync(path.join(root, 'queue', f), 'utf8'))) {
    if (/^\d{4}-\d{2}-\d{2}$/.test(p.date) && p.status !== 'retired') posts[p.date] = p;
  }
}
const notesFile = path.join(dir, 'notes.json');
const notes = fs.existsSync(notesFile) ? JSON.parse(fs.readFileSync(notesFile, 'utf8')) : {};
const DOW = ['Chủ nhật', 'Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7'];
const STATUS = { review: 'Draft', approved: 'Approved', posted: 'Posted' };
const ddmm = d => d.slice(8, 10) + '/' + d.slice(5, 7);

const days = [];
for (let i = 0; i < nDays; i++) {
  const t = new Date(start + 'T12:00:00Z'); t.setUTCDate(t.getUTCDate() + i);
  const date = t.toISOString().slice(0, 10);
  const p = posts[date];
  if (!p || !STATUS[p.status]) continue;
  days.push({ label: DOW[t.getUTCDay()], date: ddmm(date), posts: [{
    key: date, time: '21:00', status: STATUS[p.status], id: 'S21-' + date.replace(/-/g, ''),
    topic: p.hook || p.pillar || '', kind: p.pillar || '',
    caption: [p.caption, p.share, p.hashtags].filter(Boolean).join('\n'),
    notes: [...(notes[date] || []), 'Threads đăng cùng caption nhưng không có #sau21h.'],
  }] });
}
const week = { range: days.length ? days[0].date + ' đến ' + days[days.length - 1].date : '', days };
fs.writeFileSync(path.join(dir, 'week.json'), JSON.stringify(week, null, 2));
const av = path.join(root, 'posts', 'profile', 'avatar_A.jpg');
if (fs.existsSync(av)) fs.copyFileSync(av, path.join(dir, 'avatar.jpg'));
console.log('week.json', days.length, 'days', week.range);
