"""Rebuild words.json + study_plan.json from REAL sources only.
Sources: curated core (125) + sat6000.csv + scholarsnyc CSV + AWL headwords/families.
Validity: english-words dict OR WordNet. Enrichment: sourced def > WordNet.
Difficulty: wordfreq zipf -> 1-5. Quotas: SAT 2200 / IELTS 1300 / Both 1500.
"""
import json, os, csv, re, random, shutil
from collections import Counter

random.seed(60)
BASE = os.getcwd()
DATA = os.path.join(BASE, 'data')

try:
    from wordfreq import zipf_frequency
    def difficulty(word):
        z = zipf_frequency(word, 'en')
        if z >= 5.5: return 1
        if z >= 4.5: return 2
        if z >= 3.5: return 3
        if z >= 2.5: return 4
        return 5
except ImportError:
    def difficulty(word):
        return min(5, max(1, (len(word) + 1) // 3))

from nltk.corpus import wordnet as wn

POSMAP = {'n': 'noun', 'v': 'verb', 'a': 'adj', 's': 'adj', 'r': 'adv',
          'noun': 'noun', 'verb': 'verb', 'adjective': 'adj', 'adverb': 'adv',
          'adj': 'adj', 'adv': 'adv'}

def clean_word(w):
    w = (w or '').strip().lower().replace('_', ' ')
    if not re.fullmatch(r"[a-z]+(?: [a-z]+)?", w):
        return None
    if not (3 <= len(w.replace(' ', '')) <= 18):
        return None
    return w

# ---------- load validity dict ----------
print('loading english dict...')
SRC = os.path.join(DATA, 'sources')
eng = set(json.load(open(os.path.join(SRC, 'eng_dict.json'))).keys())
print('dict size:', len(eng))

def valid(w):
    key = w.replace(' ', '')
    return key in eng or bool(wn.synsets(w.replace(' ', '_')))

# ---------- source 1: curated core ----------
core = json.load(open(os.path.join(DATA, 'words_core.json')))
sat_src, ielts_src = {}, set()
for e in core:
    w = clean_word(e['word'])
    if w and valid(w):
        sat_src[w] = {'definition': e['definition'], 'pos': e['part_of_speech'],
                      'synonyms': e.get('synonyms', []), 'example': e.get('example', '')}

# ---------- source 2: sat6000.csv ----------
print('parsing sat6000...')
n_raw = 0
with open(os.path.join(SRC, 'sat6000.csv'), encoding='utf-8', errors='ignore') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('Index|'):
            continue
        parts = line.split('|')
        if len(parts) < 4:
            continue
        w = clean_word(parts[1])
        if not w or w in sat_src:
            continue
        n_raw += 1
        if not valid(w):
            continue
        sat_src[w] = {'definition': parts[2].strip().capitalize(),
                      'pos': POSMAP.get(parts[3].strip().lower(), ''),
                      'synonyms': [], 'example': ''}
print('sat6000 kept:', len(sat_src) - len(core), '(scanned', n_raw, ')')

# ---------- source 3: scholarsnyc (word,pos,def,example) ----------
print('parsing scholarsnyc...')
with open(os.path.join(SRC, 'sat_words.csv'), encoding='utf-8', errors='ignore') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) < 5:
            continue
        w = clean_word(row[1])
        if not w or w in sat_src or not valid(w):
            continue
        sat_src[w] = {'definition': row[3].strip().capitalize(),
                      'pos': POSMAP.get(row[2].strip().lower(), ''),
                      'synonyms': [], 'example': row[4].strip()}
print('sat total:', len(sat_src))

# ---------- source 4: AWL headwords + families ----------
awl = json.load(open(os.path.join(SRC, 'awl.json')))
for sub, heads in awl.items():
    if not isinstance(heads, dict):
        continue
    for head, info in heads.items():
        for w in [head] + (info.get('subwords') or []):
            w = clean_word(w)
            if w and valid(w):
                ielts_src.add(w)
print('awl valid words:', len(ielts_src))

# ---------- build final pool ----------
def enrich(word, src):
    syns = wn.synsets(word.replace(' ', '_'))
    pos = (src.get('pos') or '').lower()
    wn_pos = {'noun': 'n', 'verb': 'v', 'adj': 'a', 'adv': 'r'}.get(pos)
    s = None
    if syns:
        if wn_pos:
            cands = [x for x in syns if x.pos() == wn_pos]
            if cands:
                syns = cands
        # rank: attested usage + commonality over raw order (avoids obscure first senses)
        syns = sorted(syns, key=lambda x: (1 if x.examples() else 0, len(x.lemmas())), reverse=True)
        s = syns[0]
    definition = src.get('definition') or (s.definition().capitalize() if s else '')
    synonyms = list(src.get('synonyms') or [])
    if s:
        # answer-quality synonyms only: same synset + similar_tos (same POS by construction).
        # also_sees/hypernyms are too loose and produce wrong answers.
        extra = []
        for x in [s] + s.similar_tos():
            for l in x.lemmas():
                name = l.name().replace('_', ' ').lower()
                if name != word and name not in synonyms and name not in extra and ' ' not in name:
                    extra.append(name)
            if len(synonyms) + len(extra) >= 3:
                break
        synonyms = (synonyms + extra)[:3]
    if not synonyms:
        synonyms = [word]
    example = src.get('example') or ''
    if not example and s and s.examples():
        example = s.examples()[0].capitalize()
    if not example:
        example = f"Students should understand the word '{word}' for the exam."
    p = pos if pos in ('noun', 'verb', 'adj', 'adv') else POSMAP.get(s.pos(), 'noun') if s else 'noun'
    return {'word': word, 'definition': definition, 'part_of_speech': p,
            'difficulty': difficulty(word), 'synonyms': synonyms,
            'example': example}

both = sorted(set(sat_src) & ielts_src)
sat_only = sorted(set(sat_src) - ielts_src)
ielts_only = sorted(set(ielts_src) - set(sat_src))
print('both:', len(both), 'sat_only:', len(sat_only), 'ielts_only:', len(ielts_only))

# even coverage: shuffle (seeded) so picks aren't alphabet-biased
random.shuffle(both)
random.shuffle(sat_only)
# IELTS: headwords first (stronger entries), shuffled within groups
heads = set()
for sub, hd in awl.items():
    if isinstance(hd, dict):
        heads.update(k.lower() for k in hd.keys())
ielts_head = [w for w in ielts_only if w in heads]
ielts_rest = [w for w in ielts_only if w not in heads]
random.shuffle(ielts_head)
random.shuffle(ielts_rest)
ielts_only = ielts_head + ielts_rest

QUOTA = {'Both': 1500, 'SAT': 2200, 'IELTS': 1300}
WORDS = []
def take(words, cat, n):
    out = []
    for w in words:
        if len(out) >= n:
            break
        src = sat_src.get(w, {})
        out.append((w, src, cat))
    return out

picks = take(both, 'Both', QUOTA['Both']) + take(sat_only, 'SAT', QUOTA['SAT']) + take(ielts_only, 'IELTS', QUOTA['IELTS'])
# spill: fill shortfalls from remaining pool
used = {w for w, _, _ in picks}
short = 5000 - len(picks)
if short > 0:
    rest = [w for w in list(sat_only[QUOTA['SAT']:]) + list(ielts_only[QUOTA['IELTS']:]) + list(both[QUOTA['Both']:]) if w not in used]
    for w in rest[:short]:
        src = sat_src.get(w, {})
        cat = 'Both' if w in ielts_src and w in sat_src else ('IELTS' if w in ielts_src else 'SAT')
        picks.append((w, src, cat))
print('picked:', len(picks))

for w, src, cat in picks:
    e = enrich(w, src)
    e['category'] = cat
    WORDS.append(e)

WORDS.sort(key=lambda e: (e['difficulty'], e['word']))
for i, e in enumerate(WORDS):
    e['day'] = (i % 60) + 1
WORDS.sort(key=lambda e: (e['day'], e['difficulty'], e['word']))

# ---------- exercises ----------
TOPICS = ["Core Academic Vocabulary", "Root Words & Affixes", "Synonym Families",
    "Word Formation", "Context Clues", "Academic Writing", "Test Strategies",
    "Formal Language", "Negation Prefixes", "Direction Prefixes", "Time & Order",
    "Degree & Intensity", "Quantity & Number", "Noun Suffixes", "Verb Suffixes",
    "Adjective Suffixes", "Latin Roots: Action", "Latin Roots: Thought",
    "Latin Roots: Senses", "Greek Roots: Science", "Greek Roots: Life",
    "Greek Roots: Language", "High-Frequency SAT", "IELTS Academic Topics",
    "Environment", "Technology", "Health & Medicine", "Economics",
    "Education", "Law & Justice", "Philosophy & Ethics", "History & Culture",
    "Arts & Literature", "Media & Communication", "Science Methods",
    "Data & Statistics", "Social Science", "Psychology", "Politics & Government",
    "Engineering", "Mathematics", "Physics & Chemistry", "Biology",
    "Earth & Space", "Computing & IT", "Business & Finance", "Marketing",
    "Healthcare", "Legal Terms", "Ethics Review", "Comprehensive Review",
    "Mixed Practice 1", "Mixed Practice 2", "Mixed Practice 3", "Mixed Practice 4",
    "Timed Drill 1", "Timed Drill 2", "Final Review A", "Final Review B",
    "Consolidation", "Practice Test"]

plan = []
for day in range(1, 61):
    dw = [w for w in WORDS if w['day'] == day]
    a, b = dw[0], dw[1] if len(dw) > 1 else dw[0]
    exs = [a['example'] if a['word'] in a['example'].lower() else f"The results clearly showed {a['word']}."]
    q1 = re.sub(re.escape(a['word']), '_____', exs[0], count=1, flags=re.I) if a['word'] in exs[0].lower() else f"Choose the word that best completes: 'The results clearly showed _____. (context: {a['definition']})'"
    distract1 = [w['word'] for w in dw[2:5]]
    while len(distract1) < 3:
        distract1.append(random.choice(WORDS)['word'])
    e1 = {'type': 'fill_in_blank',
          'question': f"{q1}  (context: {a['definition']})",
          'options': sorted([a['word']] + distract1[:3], key=lambda x: random.random()),
          'answer': a['word'],
          'explanation': f"'{a['word']}' means: {a['definition']}. Example: {a['example']}"}
    syns = [s for s in b.get('synonyms', []) if s != b['word']]
    if syns:
        correct = syns[0]
    else:
        # no distinct synonym known: quiz on the word's own definition instead
        pool = [w['word'] for w in random.sample(WORDS, 200) if w['word'] != b['word']]
        e2 = {'type': 'definition_match',
              'question': f"Which word means: '{b['definition']}'?",
              'options': sorted([b['word']] + pool[:3], key=lambda x: random.random()),
              'answer': b['word'],
              'explanation': f"'{b['word']}' means: {b['definition']}. Example: {b['example']}"}
        plan.append({'day': day, 'topic': TOPICS[(day - 1) % len(TOPICS)], 'words': dw, 'exercises': [e1, e2]})
        continue
    pool = [w['word'] for w in random.sample(WORDS, 200) if w['word'] != b['word'] and w['word'] != correct]
    e2 = {'type': 'synonym_match',
          'question': f"Which word is closest in meaning to '{b['word']}' ({b['definition']})?",
          'options': sorted([correct] + pool[:3], key=lambda x: random.random()),
          'answer': correct,
          'explanation': f"'{correct}' shares the meaning of '{b['word']}': {b['definition']}."}
    plan.append({'day': day, 'topic': TOPICS[(day - 1) % len(TOPICS)], 'words': dw, 'exercises': [e1, e2]})

# ---------- save (backup old) ----------
for fn in ('words.json', 'study_plan.json'):
    p = os.path.join(DATA, fn)
    if os.path.exists(p):
        shutil.copy(p, p + '.v1bak')
json.dump(WORDS, open(os.path.join(DATA, 'words.json'), 'w'), indent=1)
json.dump(plan, open(os.path.join(DATA, 'study_plan.json'), 'w'), indent=1)

cc = Counter(w['category'] for w in WORDS)
dc = Counter(w['day'] for w in WORDS)
print('total:', len(WORDS), 'unique:', len(set(w['word'] for w in WORDS)))
print('cats:', dict(cc))
print('per-day min/max:', min(dc.values()), max(dc.values()))
print('avg difficulty:', round(sum(w['difficulty'] for w in WORDS) / len(WORDS), 2))
print('sample ielts:', [w['word'] for w in WORDS if w['category'] == 'IELTS'][:8])
