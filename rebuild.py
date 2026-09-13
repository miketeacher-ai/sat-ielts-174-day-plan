"""Rebuild words.json + study_plan.json from REAL sources only.
Sources: curated core (125) + sat6000.csv + scholarsnyc CSV + AWL headwords/families.
Validity: english-words dict OR WordNet. Enrichment: sourced def > WordNet.
Difficulty: wordfreq zipf -> 1-5. Quotas: SAT 2200 / IELTS 1300 / Both 1500.
"""
import json, os, csv, re, random, shutil
from collections import Counter

random.seed(60)
BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, 'data')

try:
    from wordfreq import zipf_frequency
    def difficulty(word):
        # Multi-word entries: graded by their hardest token, so common
        # phrases aren't mislabelled C1.
        parts = word.split(' ')
        z = min(zipf_frequency(p, 'en') for p in parts)
        if z >= 5.5: return 1
        if z >= 4.5: return 2
        if z >= 3.5: return 3
        if z >= 2.5: return 4
        return 5
except ImportError:
    def difficulty(word):
        return min(5, max(1, (len(word.replace(' ', '')) + 1) // 3))

_diff_cache = {}
def difficulty_cached(word):
    if word not in _diff_cache:
        _diff_cache[word] = difficulty(word)
    return _diff_cache[word]

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
core = json.load(open(os.path.join(SRC, 'words_core.json')))
sat_src, ielts_src = {}, set()
for e in core:
    w = clean_word(e['word'])
    if w and valid(w):
        sat_src[w] = {'definition': e['definition'], 'pos': e['part_of_speech'],
                      'synonyms': e.get('synonyms', []), 'example': e.get('example', '')}

# ---------- source 2: sat6000.csv ----------
print('parsing sat6000...')
n_raw = 0
n_before = len(sat_src)
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
print('sat6000 kept:', len(sat_src) - n_before, '(scanned', n_raw, ')')

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
# NOTE: awl.json carries headwords/subwords only (no definitions), so it
# determines IELTS/Both *membership*; definitions for IELTS-only words come
# from WordNet in enrich(), falling back to a generic example sentence.
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
THEME_MAP = {
    'noun.food': 'Food & Eating', 'noun.animal': 'Animals', 'noun.plant': 'Plants & Nature',
    'noun.person': 'People & Society', 'noun.group': 'People & Society',
    'noun.artifact': 'Objects & Tools', 'noun.location': 'Places & Travel', 'noun.time': 'Time',
    'noun.quantity': 'Numbers & Amounts', 'noun.attribute': 'Qualities', 'noun.state': 'States & Conditions',
    'noun.event': 'Events', 'noun.cognition': 'Thinking & Learning', 'noun.communication': 'Communication',
    'noun.feeling': 'Emotions', 'noun.motive': 'Motives & Goals', 'noun.possession': 'Money & Belongings',
    'noun.process': 'Processes', 'noun.phenomenon': 'Science & Phenomena', 'noun.substance': 'Materials',
    'noun.body': 'Body & Health', 'noun.relation': 'Relationships',
    'verb.motion': 'Movement & Travel', 'verb.cognition': 'Thinking & Learning',
    'verb.communication': 'Communication', 'verb.emotion': 'Emotions', 'verb.social': 'People & Society',
    'verb.possession': 'Money & Belongings', 'verb.consumption': 'Food & Eating',
    'verb.creation': 'Making & Building', 'verb.competition': 'Competition', 'verb.contact': 'Touch & Contact',
    'verb.perception': 'Senses', 'verb.change': 'Change', 'verb.stative': 'States & Conditions',
    'verb.body': 'Body & Health', 'verb.weather': 'Weather & Nature',
    'adj.all': 'Describing Words', 'adj.pert': 'Describing Words', 'adv.all': 'Manner & Degree',
}

def theme_of(lex):
    return THEME_MAP.get(lex, 'General Academic')

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
    lex = s.lexname() if s else ''
    return {'word': word, 'definition': definition, 'part_of_speech': p,
            'difficulty': difficulty(word), 'synonyms': synonyms,
            'example': example, 'theme': theme_of(lex)}

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
MIN_DIFFICULTY = 3  # B1+ only: drop difficulty 1-2 (A1-B1 core vocabulary)
# Filter BEFORE quota slicing (cached), and track exactly which words are
# consumed, so quota offsets and spill leftovers stay aligned. Shortfalls
# (e.g. a small Both overlap) spill from the other pools and are reported.
# Words with no definition source (no sourced def AND no WordNet synset —
# typically rare AWL subword forms) are dropped: enrich() cannot define them.
from functools import lru_cache

@lru_cache(maxsize=None)
def _has_wn(word):
    return bool(wn.synsets(word.replace(' ', '_')))


def has_definition(w):
    src = sat_src.get(w)
    if src and src.get('definition'):
        return True
    return _has_wn(w)


WORDS = []
consumed = set()
def eligible(pool):
    return [w for w in pool if w not in consumed and difficulty_cached(w) >= MIN_DIFFICULTY and has_definition(w)]
def take(pool, cat, n):
    out = []
    for w in pool:
        if len(out) >= n:
            break
        if w in consumed or difficulty_cached(w) < MIN_DIFFICULTY or not has_definition(w):
            continue
        consumed.add(w)
        out.append((w, sat_src.get(w, {}), cat))
    return out

both_e = eligible(both)
sat_e = eligible(sat_only)
ielts_e = eligible(ielts_only)
picks = take(both_e, 'Both', QUOTA['Both']) + take(sat_e, 'SAT', QUOTA['SAT']) + take(ielts_e, 'IELTS', QUOTA['IELTS'])
got = Counter(cat for _, _, cat in picks)
print('quota fill:', {k: f"{got.get(k, 0)}/{v}" for k, v in QUOTA.items()})
# spill: fill shortfalls from remaining eligible pool
short = 5000 - len(picks)
if short > 0:
    rest = [w for w in sat_e + ielts_e + both_e if w not in consumed]
    for w in rest[:short]:
        consumed.add(w)
        src = sat_src.get(w, {})
        cat = 'Both' if w in ielts_src and w in sat_src else ('IELTS' if w in ielts_src else 'SAT')
        picks.append((w, src, cat))
if len(picks) < 5000:
    print(f"WARNING: pool exhausted at {len(picks)}/5000 (quotas unfillable from sources)")
print('picked:', len(picks))

for w, src, cat in picks:
    e = enrich(w, src)
    e['category'] = cat
    WORDS.append(e)

WORDS.sort(key=lambda e: (e['difficulty'], e['word']))
WORDS_PER_DAY = 30
from collections import defaultdict
by_theme = defaultdict(list)
for e in WORDS:
    by_theme[e.get('theme', 'General Academic')].append(e)
# split large themes into 30-word days; merge slivers (<12) into a mixed pool
chunks = []
mixed = []
for theme in sorted(by_theme):
    lst = by_theme[theme]
    random.shuffle(lst)
    while len(lst) >= WORDS_PER_DAY:
        chunks.append((theme, lst[:WORDS_PER_DAY]))
        lst = lst[WORDS_PER_DAY:]
    if lst:
        if len(lst) >= 12:
            chunks.append((theme, lst))
        else:
            mixed.extend(lst)
random.shuffle(mixed)
mixed_chunks = [mixed[i:i + WORDS_PER_DAY] for i in range(0, len(mixed), WORDS_PER_DAY)]
if mixed_chunks:
    if len(mixed_chunks) > 1 and len(mixed_chunks[-1]) < 12:
        mixed_chunks[-2].extend(mixed_chunks.pop())
    elif len(mixed_chunks) == 1 and len(mixed_chunks[0]) < 12 and chunks:
        chunks[-1][1].extend(mixed_chunks.pop())
    for ch in mixed_chunks:
        chunks.append(('Mixed Academic Practice', ch))
# balance: sliver merges can push a chunk over WORDS_PER_DAY; move overflow
# to the smallest chunk until none exceeds it (a below-cap chunk must exist
# whenever an over-cap one does, since the average is below cap).
_lists = [lst for _, lst in chunks]
while len(_lists) > 1:
    _big = max(range(len(_lists)), key=lambda i: len(_lists[i]))
    _small = min(range(len(_lists)), key=lambda i: len(_lists[i]))
    if len(_lists[_big]) <= WORDS_PER_DAY or len(_lists[_small]) >= WORDS_PER_DAY:
        break
    _lists[_small].append(_lists[_big].pop())
# order days easy -> hard by average difficulty; shuffle word order within each day
def _avgd(c):
    return sum(w['difficulty'] for w in c[1]) / len(c[1])
chunks.sort(key=_avgd)
WORDS = []
THEME_PART = {}
for n, (theme, lst) in enumerate(chunks, start=1):
    part = THEME_PART.get(theme, 0) + 1
    THEME_PART[theme] = part
    random.shuffle(lst)
    for e in lst:
        e['day'] = n
        e['day_theme'] = theme if part == 1 else f"{theme} · Part {part}"
        WORDS.append(e)
NDAYS = len(chunks)
print('days:', NDAYS, '| themes:', len(THEME_PART))

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
def topic_for(day):
    base = TOPICS[(day - 1) % len(TOPICS)]
    rnd = (day - 1) // len(TOPICS)
    return base if rnd == 0 else f"{base} · Round {rnd + 1}"

for day in range(1, NDAYS + 1):
    dw = [w for w in WORDS if w['day'] == day]
    a, b = dw[0], dw[1] if len(dw) > 1 else dw[0]
    ex0 = a['example']
    if a['word'] in ex0.lower():
        q1 = re.sub(re.escape(a['word']), '_____', ex0, count=1, flags=re.I) + f"  (context: {a['definition']})"
    else:
        q1 = f"Choose the word that best completes: 'The results clearly showed _____. (context: {a['definition']})'"
    distract1 = [w['word'] for w in dw[2:5]]
    while len(distract1) < 3:
        distract1.append(random.choice(WORDS)['word'])
    opts1 = [a['word']] + distract1[:3]
    random.shuffle(opts1)
    e1 = {'type': 'fill_in_blank',
          'question': q1,
          'options': opts1,
          'answer': a['word'],
          'explanation': f"'{a['word']}' means: {a['definition']}. Example: {a['example']}"}
    syns = [s for s in b.get('synonyms', []) if s != b['word']]
    if syns:
        correct = syns[0]
    else:
        # no distinct synonym known: quiz on the word's own definition instead
        pool = [w['word'] for w in random.sample(WORDS, 200) if w['word'] != b['word']]
        opts2 = [b['word']] + pool[:3]
        random.shuffle(opts2)
        e2 = {'type': 'definition_match',
              'question': f"Which word means: '{b['definition']}'?",
              'options': opts2,
              'answer': b['word'],
              'explanation': f"'{b['word']}' means: {b['definition']}. Example: {b['example']}"}
        plan.append({'day': day, 'topic': dw[0].get('day_theme') or topic_for(day), 'words': dw, 'exercises': [e1, e2]})
        continue
    pool = [w['word'] for w in random.sample(WORDS, 200) if w['word'] != b['word'] and w['word'] != correct]
    opts3 = [correct] + pool[:3]
    random.shuffle(opts3)
    e2 = {'type': 'synonym_match',
          'question': f"Which word is closest in meaning to '{b['word']}' ({b['definition']})?",
          'options': opts3,
          'answer': correct,
          'explanation': f"'{correct}' shares the meaning of '{b['word']}': {b['definition']}."}
    plan.append({'day': day, 'topic': dw[0].get('day_theme') or topic_for(day), 'words': dw, 'exercises': [e1, e2]})

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

# ---------- hard gates: fail the build instead of shipping bad data ----------
import sys
errors = []
QUOTA_MIN = {'Both': 250, 'SAT': 2000, 'IELTS': 1100}  # floors, not targets
if len(WORDS) != 5000 or len(set(w['word'] for w in WORDS)) != 5000:
    errors.append(f"word count/unique != 5000 (got {len(WORDS)}/{len(set(w['word'] for w in WORDS))})")
for cat, floor in QUOTA_MIN.items():
    if cc.get(cat, 0) < floor:
        errors.append(f"category {cat} below floor {floor}: {cc.get(cat, 0)}")
for w in WORDS:
    for f in ('word', 'definition', 'part_of_speech', 'difficulty', 'synonyms', 'example', 'theme', 'category', 'day'):
        if f not in w or w[f] in (None, ''):
            errors.append(f"word missing {f}: {w.get('word')}")
            break
    if w.get('difficulty') not in (3, 4, 5):
        errors.append(f"difficulty out of B1+ range: {w.get('word')}={w.get('difficulty')}")
day_ids = sorted(d['day'] for d in plan)
if day_ids != list(range(1, len(plan) + 1)):
    errors.append("day ids not contiguous 1..N")
for d in plan:
    if not (12 <= len(d['words']) <= 31):
        errors.append(f"day {d['day']} size {len(d['words'])}")
    if len(d.get('exercises', [])) != 2:
        errors.append(f"day {d['day']} exercises != 2")
by_word = {w['word']: w for w in WORDS}
for d in plan:
    for ex in d['exercises']:
        opts, ans = ex['options'], ex['answer']
        if ans not in opts:
            errors.append(f"day {d['day']} answer missing: {ans}")
        if len(set(opts)) != 4:
            errors.append(f"day {d['day']} options != 4 unique: {opts}")
        if ex['type'] == 'fill_in_blank' and '_____' not in ex['question']:
            errors.append(f"day {d['day']} fill-in has no blank")
        if ex['type'] == 'synonym_match':
            m = re.search(r"meaning to '([^']+)'", ex['question'])
            if m and m.group(1) in by_word:
                syns = set(s for s in by_word[m.group(1)].get('synonyms', []) if s != m.group(1))
                clash = [o for o in opts if o != ans and o in syns]
                if clash:
                    errors.append(f"day {d['day']} ambiguous distractor {clash} for {m.group(1)}")
                if ans == m.group(1):
                    errors.append(f"day {d['day']} synonym answer == word")
if errors:
    print(f"BUILD FAILED with {len(errors)} gate violations (first 20):")
    for e in errors[:20]:
        print(' -', e)
    sys.exit(1)
report = {'total': len(WORDS), 'cats': dict(cc), 'days': len(plan),
          'per_day_min': min(dc.values()), 'per_day_max': max(dc.values()),
          'quota_fill': {k: f"{cc.get(k, 0)}/{v}" for k, v in QUOTA.items()}}
json.dump(report, open(os.path.join(DATA, 'build_report.json'), 'w'), indent=1)
print('BUILD OK:', report)
