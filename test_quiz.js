// Quiz generator invariant test: answer in options (once), 4 unique options, no answer==word for synonym_match.
const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');
const src = html.match(/<script>([\s\S]*)<\/script>/)[1];
for (const fn of ['shuffle', 'pickDistractors', 'blankWord', 'escReg', 'makeQuizQ'])
  eval(src.match(new RegExp('function ' + fn + '\\([\\s\\S]*?\\n\\}'))[0]);
const plan = JSON.parse(fs.readFileSync('data/study_plan.json', 'utf8'));
const pool = plan.flatMap(p => p.words);
let bad = 0, types = {};
for (let i = 0; i < 300; i++) {
  const w = pool[Math.floor(Math.random() * pool.length)];
  const syns = (w.synonyms || []).filter(s => s !== w.word);
  const t = syns.length && i % 3 === 0 ? 'synonym_match' : (i % 3 === 1 ? 'definition_match' : 'fill_in_blank');
  const q = makeQuizQ(w, pool, t);
  types[t] = (types[t] || 0) + 1;
  if (!q.options.includes(q.answer)) { console.log('ANSWER MISSING', w.word, t); bad++; }
  if (new Set(q.options).size !== 4) { console.log('DUP OPTS', w.word, t, q.options); bad++; }
  if (t === 'synonym_match' && q.answer === w.word) { console.log('SELF ANSWER', w.word); bad++; }
  if (t === 'synonym_match') {
    const syns = new Set((w.synonyms || []).filter(s => s !== w.word));
    const clash = q.options.filter(o => o !== q.answer && syns.has(o));
    if (clash.length) { console.log('AMBIGUOUS DISTRACTOR', w.word, clash); bad++; }
  }
  if (t === 'fill_in_blank' && !q.q.includes('_____')) { console.log('NO BLANK', w.word); bad++; }
}
console.log('types:', JSON.stringify(types), '| bad:', bad);

// SM-2 scheduling invariants (deterministic clock).
for (const fn of ['srUpdate', 'srDueList'])
  eval(src.match(new RegExp('function ' + fn + '\\([\\s\\S]*?\\n\\}'))[0]);
global.saveProgress = () => {};
srMap = {}; wordObj = { abate: { day: 1 } }; masteredWords = new Set();
const _now = Date.now, T0 = 1700000000000;
Date.now = () => T0;
const srEq = (name, cond) => { if (!cond) { console.log('SR FAIL', name); bad++; } };
srUpdate('ghost', 5);                       // unknown word ignored
srEq('unknown ignored', !srMap.ghost);
srUpdate('abate', 5);
srEq('first pass interval=1', srMap.abate.i === 1 && srMap.abate.n === 1 && srMap.abate.d === T0 + 864e5);
srUpdate('abate', 5);
srEq('second pass interval=6', srMap.abate.i === 6 && srMap.abate.n === 2);
srUpdate('abate', 1);
srEq('fail resets', srMap.abate.n === 0 && srMap.abate.i === 1);
Date.now = () => T0 + 2 * 864e5;
srEq('due after interval', srDueList().includes('abate'));
masteredWords.add('abate');
srEq('mastered excluded', !srDueList().includes('abate'));
Date.now = _now;
process.exit(bad ? 1 : 0);
