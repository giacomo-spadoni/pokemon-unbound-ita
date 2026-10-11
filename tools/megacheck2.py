"""Second, stricter QA pass (classes of bugs not covered by megacheck.py).
  python out/megacheck2.py JSON > report"""
import json, re, sys, collections
sys.path.insert(0, '.')
sys.path.insert(0, 'out')
import eng_tools as ET

d = json.load(open(sys.argv[1], encoding='utf-8'))
E = d['entries']
order = json.load(open('out/dlg_order.json'))
dead = {order[n] for n in json.load(open('out/dlg_story_dead_ids.json'))}
BS = chr(92)
R = collections.defaultdict(list)
TEXTCATS = {'scripts', 'pointer_texts', 'v7_texts', 'plain_scripts', 'mission_descriptions', 'mission_objectives',
            'item_descriptions', 'move_descriptions', 'ability_descriptions', 'pokedex_descriptions', 'battle_messages'}

# official names EN -> IT (items, moves, abilities)
names = {}
for x in E:
    if x['category'] in ('item_names', 'move_names', 'ability_names') and (x.get('translated') or x.get('translated_fixed')):
        o = x['original'].strip('"')
        t = x.get('translated_fixed') or x['translated']
        if len(o) >= 5 and o != t and not o.isupper():
            names.setdefault(o, set()).add(t)
name_re = re.compile(r'\b(' + '|'.join(sorted(map(re.escape, names), key=len, reverse=True)) + r')\b')


def flat(t):
    return re.sub(r'\s+', ' ', t.replace('{B4}', "'").replace(BS + 'l', ' ').replace(BS + 'p', ' ').replace('\n', ' ')).strip()


COLOR = re.compile(r'\[(black|red|green|blue|white|lightgreen|orange|yellow|grey|gray|darkgrey|lightblue|pink|purple)\]')
ORTHO = [
    (r'\bperchè\b|\bpoichè\b|\bbenchè\b|\baffinchè\b|\bsicchè\b|\bnè\b|\bsè\b(?! stess)', 'accento grave al posto dell acuto (perché, né, sé)'),
    (r"\bpò\b|\bpo\b(?!')", "po' scritto male"),
    (r"\bqual'è\b|\bqual'era\b", "qual è senza apostrofo"),
    (r"\bun'(altro|amico|uomo|allenatore|attimo|attacco|esempio|Uovo|uovo|incontro|oggetto|istante|ospite)\b", "un' davanti a maschile"),
    (r"\bun (amica|altra|avventura|ora|idea|occhiata|esperienza|isola|area|arma|aura|abilità|ottima|altra)\b", "un senza apostrofo davanti a femminile"),
    (r"\b(e'|E')\s", "e' invece di è"),
    (r"\bpiu\b|\bperche\b|\bcosi\b|\bperò\b(?=x)|\bgia\b|\bpuo\b|\bcitta\b|\bpieta\b", "accento mancante"),
    (r"\bPokemon\b|\bPokè|\bPoke Ball\b", "Pokémon/Poké scritto male"),
    (r"\s,|\s\.(?!\.)|\s!|\s\?", None),
    (r"([a-zàèéìòù])\1\1", "lettera tripla"),
    (r"\b(il|lo|la|i|gli|le|un|una|di|a|da|in|con|su|per|tra|fra|e|che)\s+\1\b", "parola ripetuta"),
    (r"\b[Ss]ei\s+(stat[oa])\s+(stat[oa])\b", None),
]
for x in E:
    if x['id'] in dead:
        continue
    t = x.get('translated_fixed') or x.get('translated')
    if not t:
        continue
    o = x['original'].strip('"')
    cat = x['category']
    key = f"{x['id']} [{cat}]"
    ft, fo = flat(t), flat(o)
    # 1 numbers changed
    if cat in TEXTCATS:
        no = sorted(re.findall(r'(?<![\\\w])\d+(?:[.,]\d+)?', re.sub(r'\[[a-z0-9_]+\]|\\[A-Za-z?]+[0-9A-F]*|\\\\[0-9A-F]{2}', ' ', fo)))
        nt = sorted(re.findall(r'(?<![\\\w])\d+(?:[.,]\d+)?', re.sub(r'\[[a-z0-9_]+\]|\\[A-Za-z?]+[0-9A-F]*|\\\\[0-9A-F]{2}', ' ', ft)))
        no = [n.replace(',', '').replace('.', '') for n in no]
        nt = [n.replace(',', '').replace('.', '') for n in nt]
        if no != nt and not (cat == 'pokedex_descriptions'):
            R['1 numeri diversi'].append((key, f'EN {no} IT {nt} | {fo[:160]}', ft[:200]))
    # 2 colour order
    co, ct = COLOR.findall(o), COLOR.findall(t)
    if co != ct and collections.Counter(co) == collections.Counter(ct):
        R['2 colori in ordine diverso'].append((key, f'{co} -> {ct} | {fo[:140]}', ft[:200]))
    elif collections.Counter(co) != collections.Counter(ct):
        R['2b colori diversi'].append((key, f'{co} -> {ct} | {fo[:140]}', ft[:200]))
    # 3 question lost
    if cat in ('scripts', 'v7_texts', 'pointer_texts', 'plain_scripts') and fo.rstrip(' .\\').endswith('?') and not re.search(r'\?[\s\]\\a-z0-9_]*$', ft.rstrip(' .')):
        R['3 domanda diventata affermazione'].append((key, fo[-120:], ft[-160:]))
    # 4 official names in free text
    if cat in TEXTCATS - {'battle_messages'}:
        for m in name_re.finditer(fo):
            en = m.group(1)
            if not any(itn.lower() in ft.lower() for itn in names[en]) and en not in ft:
                R['4 nome ufficiale diverso'].append((key, f'{en} -> {sorted(names[en])} | {fo[:120]}', ft[:200]))
                break
    # 5 orthography
    if cat not in ('trainer_names', 'pokemon_names'):
        for pat, why in ORTHO:
            m = re.search(pat, ft)
            if m and why:
                R['5 ortografia: ' + why].append((key, m.group(0), ft[:200]))
    # 6 empty translations
    if not ft.strip() and fo.strip() and cat not in ('battle_messages',):
        R['6 traduzione vuota'].append((key, fo, repr(t)))
    # 7 name lengths (menus)
    lim = {'item_names': 13, 'move_names': 13, 'ability_names': 17, 'pokemon_names': 11, 'trainer_classes': 13}.get(cat)
    if lim and len(ft) > max(lim, len(fo)):
        R['7 nome troppo lungo per il menu'].append((key, f'{len(ft)} > {lim} | {fo}', ft))
    # 8 line too wide in a multi-line dialogue (pixel width)
    if cat in ('scripts', 'v7_texts', 'plain_scripts') and ET.BREAKS.search(o):
        W = max([ET.px(l.strip()) for l in ET.BREAKS.split(o) if l.strip()] + [0])
        for l in ET.BREAKS.split(t):
            if l.strip() and ET.px(l.strip()) > max(W, 216) + 4:
                R['8 riga più larga del riquadro'].append((key, f'{ET.px(l.strip())}px > {max(W, 216)} | {l.strip()[:80]}', ft[:160]))
                break

for k in sorted(R):
    print(f'\n##### {k}: {len(R[k])}')
    for key, a, b in R[k]:
        print(f'{key}\n   EN {a}\n   IT {b}')
