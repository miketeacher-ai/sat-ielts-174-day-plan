// Focus-mode render test (throwaway harness, own source only).
const fs = require('fs');
const html = fs.readFileSync('static/index.html', 'utf8');
const src = html.match(/<script>([\s\S]*)<\/script>/)[1];
for (const fn of ['esc', 'levelLabel', 'renderFocus', 'focusStep'])
  eval(src.match(new RegExp('function ' + fn + '\\([\\s\\S]*?\\n\\}'))[0]);
const plan = JSON.parse(fs.readFileSync('data/study_plan.json', 'utf8'));
studyPlan = plan; currentDay = 1; masteredWords = new Set(); focus = null;
global.document = { getElementById: () => global.__el || (global.__el = { innerHTML: '' }), querySelector: () => null };
global.window = { scrollTo: () => {} };
focus = { words: plan[0].words.slice(0, 3), i: 0, flipped: false, shuffled: false };
renderFocus();
const h = global.__el.innerHTML;
console.log('word shown:', h.includes(plan[0].words[0].word));
console.log('counter:', h.includes('Card 1 / 3'));
console.log('level pill:', /B1|B2|C1/.test(h));
console.log('nav wiring:', (h.match(/focusStep\(/g) || []).length === 2);
focusStep(1);
console.log('step works:', global.__el.innerHTML.includes('Card 2 / 3'));
