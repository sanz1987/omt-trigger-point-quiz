#!/usr/bin/env python3
"""Build the multi-class quiz site.
- Trigger-point bank is generated from muscles.json (+ img/attribution.json).
- Other classes are parsed from classes/<id>.txt:
    @ Topic name            (starts a topic)
    Question text
    * correct answer
    - wrong answer          (x3)
    E: explanation (source)
  Blocks are separated by blank lines; lines starting with # are comments.
Run: python3 build.py   -> writes index.html and questions.json"""
import json, random, re, hashlib, sys
random.seed(42)
CLASSES = [
 ('trigger', 'OMT II · Trigger point muscles', 'Origins, insertions, actions and nerves of the 52 muscles in the Catalyst University trigger-point slides'),
 ('omt2', 'OMT II · Techniques', 'Trigger-point theory, Mulligan, MET, myofascial release, MLD, scars & burns, cupping'),
 ('trauma', 'Pathology of Trauma', 'Orthopaedic trauma by region, fracture management, imaging'),
 ('biomech', 'Biomechanics', 'Kinematics, kinetics, gait analysis, measurement, posture, knee, hip, spine'),
 ('research', 'Research Methodology', 'Scientific method, PICO, hypotheses, objectives, Research Protocol rules'),
 ('patho1', 'Pathophysiological Foundations I', 'Health & disease, inflammation/fever/pain, clinical history & diagnostics, pharmacology, oncology, haematology, MSK, digestive & endocrine — from the 2025-26 lecture slides'),
]
errors = []

def parse(cid):
    Q, topic = [], 'General'
    txt = open(f'classes/{cid}.txt', encoding='utf-8').read()
    blocks = re.split(r'\n\s*\n', txt)
    for b in blocks:
        lines = [l.rstrip() for l in b.strip().split('\n') if l.strip() and not l.startswith('#')]
        while lines and lines[0].startswith('@'):
            topic = lines.pop(0)[1:].strip()
        if not lines: continue
        q, ok, bad, ex = None, [], [], ''
        for l in lines:
            if l.startswith('* '): ok.append(l[2:].strip())
            elif l.startswith('- '): bad.append(l[2:].strip())
            elif l.startswith('E:'): ex = l[2:].strip()
            elif q is None: q = l.strip()
            else: q += ' ' + l.strip()
        opts = ok + bad
        if len(ok) != 1 or len(bad) < 2 or not q or not ex or len(set(o.lower() for o in opts)) != len(opts):
            errors.append(f'{cid}: bad block: {lines[:2]}'); continue
        qid = cid + '-' + hashlib.md5(q.encode()).hexdigest()[:8]
        Q.append({'id': qid, 'topic': topic, 'q': q, 'options': opts, 'answer': 0, 'explanation': ex})
    return Q

def norm(t):
    return re.sub(r'\s*\(.*?\)','',t).strip().lower()

def trigger():
    M = json.load(open('muscles.json', encoding='utf-8'))
    att = json.load(open('img/attribution.json', encoding='utf-8'))
    ex = {m['id']: set(m.get('x', [])) for m in M}
    for a in list(ex):
        for b in list(ex[a]): ex.setdefault(b, set()).add(a)
    def pool(m, f):
        c = [o for o in M if o['id'] != m['id'] and o['id'] not in ex[m['id']] and o.get(f) and norm(o[f]) != norm(m[f]) and not (f == 'nerve' and (norm(o[f]) in norm(m[f]) or norm(m[f]) in norm(o[f])))]
        s = [o for o in c if o['region'] == m['region']]; t = [o for o in c if o['region'] != m['region']]
        random.shuffle(s); random.shuffle(t); return s + t
    def expl(m):
        e = f"{m['name']} — O: {m['origin']}. I: {m['insertion']}. A: {m['action']}."
        if m.get('nerve'): e += f" N: {m['nerve']}."
        return e + f" (Catalyst slides, p. {m['page']})"
    Q = []
    stems = {'origin': 'What is the origin of {}?', 'insertion': 'Where does {} insert?',
             'action': 'What is the main action of {}?', 'nerve': 'Which nerve innervates {} (per the slides)?'}
    for m in M:
        for f in ('origin', 'insertion', 'action', 'nerve'):
            if not m.get(f): continue
            seen, wrong = {norm(m[f])}, []
            for o in pool(m, f):
                if norm(o[f]) not in seen: seen.add(norm(o[f])); wrong.append(o[f])
                if len(wrong) == 3: break
            if len(wrong) < 3: continue
            Q.append({'id': f"trigger-{m['id']}-{f}", 'topic': m['region'], 'q': stems[f].format(m['name']),
                      'options': [m[f]] + wrong, 'answer': 0, 'explanation': expl(m), 'img': m['id']})
        for f in ('insertion', 'origin'):
            if any(o[f].lower() == m[f].lower() for o in M if o['id'] != m['id']): continue
            wrong = [o['name'] for o in pool(m, f)][:3]
            stem = f"Which muscle inserts on: {m['insertion']}?" if f == 'insertion' else f"Which muscle originates from: {m['origin']}?"
            Q.append({'id': f"trigger-{m['id']}-r{f}", 'topic': m['region'], 'q': stem, 'options': [m['name']] + wrong,
                      'answer': 0, 'explanation': expl(m), 'img': m['id']})
    imgs = {k: v for k, v in att.items()}
    return Q, imgs, M

bank = {'classes': [], 'images': {}}
tq, imgs, M = trigger()
bank['images'] = imgs
for cid, title, desc in CLASSES:
    Q = tq if cid == 'trigger' else parse(cid)
    topics = list(dict.fromkeys(q['topic'] for q in Q))
    bank['classes'].append({'id': cid, 'title': title, 'desc': desc, 'topics': topics, 'questions': Q})
if errors:
    print('\n'.join(errors)); sys.exit(1)
json.dump(bank, open('questions.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
html = open('template.html', encoding='utf-8').read().replace('/*__BANK__*/', json.dumps(bank, ensure_ascii=False).replace('</', '<\\/'))
open('index.html', 'w', encoding='utf-8').write(html)
for c in bank['classes']: print(f"{c['id']:9} {len(c['questions']):4} questions, {len(c['topics'])} topics")
print('images:', len(set(v['file'] for v in imgs.values())), 'files for', len(imgs), 'muscles')
