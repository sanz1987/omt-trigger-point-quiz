#!/usr/bin/env python3
"""Build questions.json + index.html from muscles.json.
Usage: python3 build.py   (edit muscles.json, then re-run)"""
import json, random
random.seed(42)
M = json.load(open('muscles.json'))
byid = {m['id']: m for m in M}
# symmetric exclusion lists
ex = {m['id']: set(m.get('x', [])) for m in M}
for a in list(ex):
    for b in list(ex[a]):
        ex.setdefault(b, set()).add(a)
LBL = {'origin': 'origin', 'insertion': 'insertion', 'action': 'action'}

def pool(m, field):
    cands = [o for o in M if o['id'] != m['id'] and o['id'] not in ex[m['id']] and o[field] != m[field]]
    same = [o for o in cands if o['region'] == m['region']]
    other = [o for o in cands if o['region'] != m['region']]
    random.shuffle(same); random.shuffle(other)
    return same + other

def expl(m):
    return f"{m['name']} — O: {m['origin']}. I: {m['insertion']}. A: {m['action']}."

Q = []
for m in M:
    for f in ('origin', 'insertion', 'action'):
        seen, wrong = {m[f]}, []
        for o in pool(m, f):
            if o[f] not in seen:
                seen.add(o[f]); wrong.append(o[f])
            if len(wrong) == 3: break
        stem = {'origin': f"What is the origin of {m['name']}?",
                'insertion': f"Where does {m['name']} insert?",
                'action': f"What is the main action of {m['name']}?"}[f]
        Q.append({'muscle': m['id'], 'region': m['region'], 'type': f, 'q': stem,
                  'options': [m[f]] + wrong, 'answer': 0, 'explanation': expl(m)})
    for f in ('insertion', 'origin'):
        # reverse: only if no other muscle shares this exact text
        if any(o[f] == m[f] for o in M if o['id'] != m['id']): continue
        wrong = [o['name'] for o in pool(m, f)][:3]
        stem = (f"Which muscle inserts on: {m['insertion']}?" if f == 'insertion'
                else f"Which muscle originates from: {m['origin']}?")
        Q.append({'muscle': m['id'], 'region': m['region'], 'type': f, 'q': stem,
                  'options': [m['name']] + wrong, 'answer': 0, 'explanation': expl(m)})
for i, q in enumerate(Q): q['id'] = i
bank = {'muscles': [{k: m[k] for k in ('id', 'name', 'region')} for m in M], 'questions': Q}
json.dump(bank, open('questions.json', 'w'), indent=1, ensure_ascii=False)
html = open('template.html', encoding='utf-8').read().replace('/*__BANK__*/', json.dumps(bank, ensure_ascii=False).replace('</', '<\\/'))
open('index.html', 'w', encoding='utf-8').write(html)
from collections import Counter
c = Counter(q['muscle'] for q in Q)
print(len(M), 'muscles,', len(Q), 'questions; min per muscle', min(c.values()))
