"""Mega check of the Italian translation as it is in the ROM.
  python out/megacheck.py JSON ROM > report.txt"""
import json, struct, sys, re, collections
sys.path.insert(0, '.')
sys.path.insert(0, 'out')
from lib.pcs_text import decode_pcs
import eng_tools as ET

JS, ROM = sys.argv[1], sys.argv[2]
rom = open(ROM, 'rb').read()
E = json.load(open(JS, encoding='utf-8'))['entries']
BS = chr(92)
order = json.load(open('out/dlg_order.json'))
dead = {order[n] for n in json.load(open('out/dlg_story_dead_ids.json'))}
debug = {order[n] for n in json.load(open('out/dlg_debug_ids.json'))}
gl = json.load(open('glossaries/it.json', encoding='utf-8'))['terms']


def rd(x):
    for s in x.get('pointer_sources', []):
        p = struct.unpack_from('<I', rom, int(s, 16))[0]
        if 0x08000000 <= p < 0x0A000000:
            return decode_pcs(rom, p - 0x08000000, 3000).text
    return decode_pcs(rom, int(x['address'], 16), 3000).text


def flat(t):
    t = t.replace('{B4}', '’').replace(BS + 'l', ' ').replace(BS + 'p', ' ').replace(BS + 'n', ' ')
    return re.sub(r'\s+', ' ', t.replace('\n', ' ')).strip().strip('"')


def norm(t):
    return re.sub(r'\s+', '', flat(t))


R = collections.defaultdict(list)
EN_WORDS = re.compile(r"\b(the|you|your|and|with|this|that|what|have|don’t|I’m|it’s|is|are|was|of|to|for|my|me|we|be|will|can|not|just|if|there|here|all|but|get|got|now|who|how|why|from|out|up|on|at|it|an|do|so|no|yes|yeah|they|them|he|she|his|her)\b")
EN_OK = re.compile(r'(Black|Terror|Battle|Light|Ruin|Shadow|Poké|Hip|Waders|Sea|Burglar|Challenge|Road|Kingpin|Boss|Mega|Z-|Max|Frontier|Tower|Circus|Mine|Ring|Show|Room|Park|Dojo|Cube|ADM|KBT)')
DUP_OK = {'ah', 'ha', 'oh', 'eh', 'no', 'sì', 'hoo', 'pa', 'la', 'bla', 'ehi', 'hmm', 'muu', 'toc', 'bip', 'grr', 'ih', 'uh', 'hi', 'he', 'ho', 'bu', 'via', 'ciao', 'presto', 'su', 'dai', 'forza', 'scusa', 'sì,', 'ok', 'bene', 'basta', 'aiuto', 'avanti', 'ahi', 'wow', 'ehm', 'mmm', 'tic', 'tac', 'zzz', 'uuh', 'buu', 'gwa', 'chaw', 'bau', 'miao', 'cip', 'crack', 'bum', 'bang', 'pop', 'hop'}
CALQUE = re.compile(r'\b(fa senso|realizzat[oaie]|realizzare che|supportar\w*|eventualmente|attualmente|lavorare con quest\w|in ordine (di|per)|fare sicuro|essere sicuro di|prendere cura|è tutto su|tipo di|Tipo tipo|chiaramente|onestamente|sai cosa\?|indovina cosa|in effetti no|dopotutto|a proposito di che|immagino di sì|fai la tua mossa|mossa intelligente|colpire la strada|avere un tempo|buon tempo|per favore di|compagno|ragazzo mio|grande tempo|in modo da|assicurati di|a questo punto|tutto sommato|non vedo l.ora)\b', re.I)
glmap = [(t['source'], t['target']) for t in gl if t['source'] != t['target'] and len(t['source']) >= 4]

cats_seen = collections.Counter()
for x in E:
    if not x.get('translated'):
        continue
    cat = x['category']
    if x['id'] in dead or x['id'] in debug:
        continue
    try:
        got = rd(x)
    except Exception:
        continue
    exp = x.get('translated_fixed') or x['translated']
    o = x['original'].strip('"')
    f, fo = flat(got), flat(o)
    cats_seen[cat] += 1
    key = f"{x['id']} [{cat}]"
    # A. what is in the ROM is not the expected text
    if norm(got) != norm(exp):
        R['A in ROM diverso dal previsto' + (' (inglese)' if norm(got) == norm(o) else '')].append((key, fo, f))
        continue
    if f == fo and len(re.findall(r'[A-Za-z]{3,}', fo)) >= 2 and cat not in ('pokemon_names', 'trainer_names', 'pokedex_species', 'pokedex_form_names'):
        R['B identico all inglese'].append((key, fo, f))
        continue
    # C. English words left
    ens = [w for w in EN_WORDS.findall(re.sub(r'\[[a-z0-9_]+\]|\\[A-Za-z]+[0-9A-F]*', ' ', f)) ]
    if len(ens) >= 3 and not EN_OK.search(f):
        R['C parole inglesi'].append((key, fo, f))
    elif len(ens) >= 2:
        R['C2 parole inglesi (dubbio)'].append((key, fo, f))
    # D. tokens
    if ET.tokens(exp) != ET.tokens(o) and x.get('manual_fix') != 'pronoun-fix':
        miss = collections.Counter(ET.tokens(o)) - collections.Counter(ET.tokens(exp))
        extra = collections.Counter(ET.tokens(exp)) - collections.Counter(ET.tokens(o))
        R['D segnaposto diversi'].append((key, f'mancano {dict(miss)} in più {dict(extra)} | ' + fo, f))
    # E. duplicated words
    for m in re.finditer(r'\b(\w+)[ ,]+\1\b', f, re.I):
        if m.group(1).lower() not in DUP_OK and not m.group(1).isdigit():
            R['E parola ripetuta'].append((key, m.group(0), f))
            break
    # F. spacing / punctuation
    g = re.sub(r'\\[.]', '…', f)
    if re.search(r' [,.!?;:](?!\d)', g) or re.search(r'[a-zà-ù][,;:][A-Za-zÀ-ù]', g) or re.search(r'[a-zà-ù][!?][A-Za-zÀ-ù]', g):
        R['F spazi/punteggiatura'].append((key, fo, f))
    # G. placeholders glued to english plural / articles
    if re.search(r'\[buffer\d\]s\b', f) or re.search(r'\\\\0[0-9A-F]s\b', f):
        R['G plurale inglese su segnaposto'].append((key, fo, f))
    m = re.search(r"\b(il|lo|la|un|uno|una|del|della|al|alla|nel|nella|dal|dalla|questo|questa|quel|quella|tuo|tua|suo|sua|mio|mia)\s+(\[green\])?\[buffer\d\]", f, re.I)
    if m and cat in ('scripts', 'pointer_texts'):
        R['G2 articolo davanti a segnaposto'].append((key, m.group(0) + ' | ' + fo, f))
    # H. glossary: english name left although it has an italian name
    for s, t in glmap:
        if re.search(r'\b' + re.escape(s) + r'\b', f) and t not in f and s not in t:
            R['H nome non tradotto (glossario)'].append((key, f'{s} -> {t}', f))
            break
    # I. strange characters / leftovers
    if re.search(r'[¶§⏎↓{}]|’s\b|\bs’|\\n|\?\?(?!\?)|\s[’]\s', f.replace('???', '')):
        R['I caratteri strani'].append((key, fo, f))
    # J. truncated fixed-space texts
    if (x.get('translated_fixed') or cat == 'pointer_texts') and re.search(r'[.!?…]["’]?$', fo) and not re.search(r'[.!?…»"’\]\)]$|\\\.$', f.strip()):
        R['J forse troncato (spazio fisso)'].append((key, fo, f))
    # K. calques
    m = CALQUE.search(f)
    if m and cat in ('scripts', 'pointer_texts', 'mission_descriptions'):
        R['K possibile calco'].append((key, m.group(0), f))
    # L. mixed tu / Lei
    if cat == 'scripts' and re.search(r'\b(tu|ti|tuo|tua|hai|sei)\b', f) and re.search(r'\b(Lei è|Lei ha|La prego|Sua|Suo|Le serve|La ringrazio|desidera)\b', f):
        R['L tu e Lei mescolati'].append((key, fo, f))

print('voci controllate per categoria:', dict(cats_seen))
for k in sorted(R):
    print(f'\n##### {k}: {len(R[k])}')
    for key, a, b in R[k]:
        print(f'{key}\n   EN {a[:300]}\n   IT {b[:300]}')
