"""Tools for fitting Italian into the fixed byte slots of in-place pointer_texts.

  python out/eng_tools.py dump <start> [count]   -> print a batch for translation
  python out/eng_tools.py apply SRC DST          -> validate + apply all out/eng_batches/b*.py

Batch files define T = {index: 'italian text'}. Layout in the italian text:
  '¶'  = new text box (paragraph)   (encoded like the original's blank line / \\p)
  lines are wrapped automatically: first break '\\n', following breaks '\\l' (scroll)
Leading/trailing control tokens of the original must be written explicitly if needed;
the original's trailing layout (blank lines) is re-appended automatically."""
import json, re, sys, os, glob, importlib.util
sys.path.insert(0, '.')
sys.path.insert(0, 'out')
from lib.pcs_text import Charmap, decode_pcs
from wrap import px


def norm_rt(t):
    """compare texts across the codec: apostrophe token, layout spelling, spaces"""
    t = t.replace('{B4}', '’').replace(chr(92) + 'p', '\n\n').replace(chr(92) + 'n', '\n')
    return re.sub(r'\s+', ' ', t).strip()

spec = importlib.util.spec_from_file_location('inj', '005_hybrid_injector.py')
INJ = importlib.util.module_from_spec(spec)
spec.loader.exec_module(INJ)
CM = Charmap('it')
BS = chr(92)
BREAKS = re.compile('\n\n|\n|' + re.escape(BS + 'l') + '|' + re.escape(BS + 'p'))
TRAIL = re.compile('(?:\n|' + re.escape(BS + 'l') + '|' + re.escape(BS + 'p') + r'| )+$')
TOKENS = re.compile(r'\\\\[0-9A-F]{2}|\[[a-z0-9_]+\]|\\CC(?:[0-9A-F]{2})+|\\btn[0-9A-F]{2}|\\\?[0-9A-F]{2}|\\q[oc]'
                    r'|\\(?:pk|Po)(?![a-zA-Z])|\\(?:mn|Ke|Bl|Lo|Ck|Lv|sm|sf|au|ad|al|ar)|\{[0-9A-F]{2}\}')

ORDER_FILE = 'out/eng_order.json'


def order():
    if not os.path.exists(ORDER_FILE):
        kinds = json.load(open('out/english_kind.json', encoding='utf-8'))
        prio = {'Unbound': 0, 'altro FireRed': 1, 'decorazioni base segreta': 2, 'parole Chiacchierata (MAIUSC)': 3}
        E = json.load(open('out/it-phase2c.json', encoding='utf-8'))['entries']
        ids = [x['id'] for x in E if x['id'] in kinds and x['category'] == 'pointer_texts']
        pos = {i: k for k, i in enumerate(ids)}
        ids.sort(key=lambda i: (prio[kinds[i]], pos[i]))
        json.dump(ids, open(ORDER_FILE, 'w'))
    return json.load(open(ORDER_FILE))


def tokens(t):
    t = t.replace('{B4}', '’')
    return sorted(m for m in TOKENS.findall(t) if m not in ('{B4}',))


def wrap_width(orig):
    ws = [px(l.strip()) for l in BREAKS.split(orig) if l.strip()]
    return min(max(max(ws, default=0), 150), 216)


def layout(text, orig):
    """wrap italian according to the original's box width; ¶ -> new box"""
    if text.startswith('§'):
        # manual layout: ¶ new box, ⏎ newline, ↓ scroll line; spaces kept as written
        body = text[1:].replace('¶', '\n\n').replace('⏎', '\n').replace('↓', BS + 'l')
        m = TRAIL.search(orig)
        return body + (m.group(0) if m else ''), 240
    multiline = bool(BREAKS.search(orig.rstrip()))
    text = text.rstrip('¶ ')          # trailing layout is always copied from the original
    lead = text[:len(text) - len(text.lstrip(' '))]   # fragments glued after a name keep their space
    text = text.lstrip(' ')
    paras = [p.strip() for p in text.split('¶')]
    out = []
    for p in paras:
        if not multiline and len(paras) == 1:
            out.append(p)
            continue
        W = wrap_width(orig)
        words, lines, cur = p.split(' '), [], ''
        for w_ in words:
            cand = (cur + ' ' + w_) if cur else w_
            if px(cand) <= W:
                cur = cand
            else:
                lines.append(cur)
                cur = w_
        lines.append(cur)
        s = lines[0]
        for k, l in enumerate(lines[1:]):
            s += ('\n' if k == 0 else BS + 'l') + l
        out.append(s)
    body = lead + '\n\n'.join(out)
    m = TRAIL.search(orig)
    return body + (m.group(0) if m else ''), wrap_width(orig)


def dump(start, size=120):
    ids = order()
    E = {x['id']: x for x in json.load(open('out/it-phase2c.json', encoding='utf-8'))['entries']}
    print(f'# da {start}: voci {start}..{min(len(ids), start + size) - 1} di {len(ids)}')
    for n in range(start, min(len(ids), start + size)):
        x = E[ids[n]]
        o = x['original'].strip('"').replace('\n\n', '¶').replace('\n', ' ').replace(BS + 'l', ' ').replace(BS + 'p', '¶')
        t = re.sub(r'\s+', ' ', x['translated'].replace('\n', ' '))
        print(f"{n}|{int(x['byte_length']) - 1}| {o}\n    IT: {t}")


def apply(src, dst):
    ids = order()
    d = json.load(open(src, encoding='utf-8'))
    by = {x['id']: x for x in d['entries']}
    T = {}
    for f in sorted(glob.glob('out/eng_batches/b*.py')):
        ns = {}
        exec(open(f, encoding='utf-8').read(), ns)
        T.update(ns['T'])
    ok = bad = 0
    for n, text in sorted(T.items()):
        x = by[ids[n]]
        orig = x['original'].strip('"')
        final, W = layout(text, orig)
        size = len(INJ.encode_text(CM, final))
        budget = int(x['byte_length'])
        lines = [l for l in BREAKS.split(final) if l.strip()]
        problems = []
        if size > budget:
            problems.append(f'{size}>{budget} byte')
        if tokens(final) != tokens(orig):
            problems.append(f'token {tokens(final)} != {tokens(orig)}')
        # every character must exist in the game font: encode -> decode must round-trip
        back = decode_pcs(INJ.encode_text(CM, final), 0, 4096).text
        if norm_rt(back) != norm_rt(final):
            problems.append(f'carattere non codificabile: {back!r}')
        if any(px(l.strip()) > max(W, 216 if len(lines) == 1 else W) for l in lines) and BREAKS.search(orig.rstrip()):
            problems.append('riga troppo larga')
        if problems:
            bad += 1
            print(f'NO {n} {ids[n]}: {"; ".join(problems)}\n   EN {orig!r}\n   IT {final!r}')
            continue
        x['translated'] = final
        x['translated_fixed'] = final
        x['manual_fix'] = 'fit-in-place'
        ok += 1
    json.dump(d, open(dst, 'w', encoding='utf-8'), ensure_ascii=False)
    print(f'applicate {ok} | da rivedere {bad} | totale voci in lista {len(ids)}')


if __name__ == '__main__':
    if sys.argv[1] == 'dump':
        dump(int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 120)
    else:
        apply(sys.argv[2], sys.argv[3])
