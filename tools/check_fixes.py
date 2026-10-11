"""Validate proposed fixes WITHOUT building.   (run from the project root)
  python out/audit/check_fixes.py FILE.py        validate R / X dicts of a proposal file
  python out/audit/check_fixes.py show ID [ID..] print EN, current IT (as injected) and IT in R-notation
  python out/audit/check_fixes.py addr 0xADDR    decode the ORIGINAL ROM string at ADDR + its safe script/table refs

Proposal file format (Python, write it with the Write tool, never via shell heredoc):
  R = {'scr_187B5D': "Testo italiano¶secondo riquadro"}    # rewrite an existing entry (by id)
  X = {0x1A52DD: "[player] trova [buffer1]!"}             # new string never extracted (by ORIGINAL ROM address)
  NOTE = {'scr_187B5D': 'why'}                              # optional, one line per fix
Notation: plain Italian; '¶' = new box (lines are wrapped automatically to the original box width);
'§' prefix = manual layout ('⏎' newline, '↓' scroll line, '¶' new box); [player] [buffer1] [rival] [blue] ... as in the
original; @XX = battle buffer \\\\XX ; @?XX @CCxx.. @qo @qc = single-backslash codes; '…' = game ellipsis \\. ;
"'" apostrophe. Any other control code: write it literally with an escaped backslash (e.g. "\\\\au" in Python source).
Every control token of the English original must appear the same number of times."""
import json, sys, re, collections
sys.path.insert(0, '.')
sys.path.insert(0, 'out')
import eng_tools as ET
from v7_apply import expand
from lib.pcs_text import decode_pcs

BS = chr(92)
D = None


def db():
    global D
    if D is None:
        D = {x['id']: x for x in json.load(open('out/it-v7.json', encoding='utf-8'))['entries']}
    return D


def cur(x):
    return x.get('translated_fixed') or x.get('translated') or ''


def notation(t):
    t = t.replace('{B4}', "'").replace(BS + '.', '…')
    t = re.sub(re.escape(BS) * 2 + '([0-9A-F]{2})', r'@\1', t)
    t = re.sub(re.escape(BS) + r'(\?[0-9A-F]{2}|CC(?:[0-9A-F]{2})+|q[oc])', r'@\1', t)
    t = t.replace('\n\n', '¶').replace(BS + 'p', '¶')
    t = re.sub('\n|' + re.escape(BS + 'l'), ' ', t)
    return re.sub(' +', ' ', t).strip()


def enc_len(t):
    return len(ET.INJ.encode_text(ET.CM, t))


ROM = None


def rom():
    global ROM
    if ROM is None:
        ROM = open('rom/unbound.gba', 'rb').read()
    return ROM


def refs(a):
    r = rom()
    pat = (a + 0x08000000).to_bytes(4, 'little')
    out, i = [], r.find(pat)
    while i != -1:
        s = i
        kind = None
        if r[s - 2:s] == b'\x0f\x00':
            kind = 'loadpointer'
        elif r[s - 1] == 0x67:
            kind = 'preparemsg'
        elif r[s - 2] == 0x85 and r[s - 1] < 0x10:
            kind = 'bufferstring'
        elif r[s - 5] == 0xFA and r[s - 2:s] == b'\x03\x02':
            kind = 'battle-script FA'
        elif any(r[s - k] == 0x5C and r[s - k + 1] <= 0x0C for k in range(6, 34, 2)):
            kind = 'trainerbattle'
        elif s % 4 == 0 and any(int.from_bytes(r[s + o:s + o + 4], 'little') >> 24 in (8, 9) for o in (-4, 4)):
            kind = 'aligned table/literal'
        out.append((s, kind))
        i = r.find(pat, i + 1)
    return out


def check(path):
    ns = {}
    exec(open(path, encoding='utf-8').read(), ns)
    bad = 0
    for eid, text in ns.get('R', {}).items():
        x = db().get(eid)
        if not x:
            print('ERR', eid, 'id inesistente'); bad += 1; continue
        orig = x['original'][1:-1]
        try:
            final, W = ET.layout(expand(text), orig)
        except AssertionError as e:
            print('ERR', eid, e); bad += 1; continue
        p = []
        to, tf = collections.Counter(ET.tokens(orig)), collections.Counter(ET.tokens(final))
        if to != tf:
            p.append(f'token {dict(tf)} != originale {dict(to)}')
        back = decode_pcs(ET.INJ.encode_text(ET.CM, final), 0, 4096).text
        if ET.norm_rt(back) != ET.norm_rt(final):
            p.append('carattere non codificabile')
        wide = [l for l in ET.BREAKS.split(final) if l.strip() and ET.px(l.strip()) > max(W, 216)]
        if wide and not text.startswith('§'):
            p.append(f'riga larga {wide}')
        fixed = x.get('translated_fixed') or x.get('no_relocation') or x['category'] == 'pointer_texts' or not x.get('pointer_sources')
        if fixed and enc_len(final) > x['byte_length']:
            p.append(f'slot fisso: {enc_len(final)} byte > {x["byte_length"]}')
        print('ERR' if p else 'OK ', eid, '; '.join(p), '\n     ', repr(final))
        bad += bool(p)
    for a, text in ns.get('X', {}).items():
        orig = decode_pcs(rom(), a, 2048).text
        rs = [k for s, k in refs(a) if k]
        final, W = ET.layout(expand(text), orig)
        p = []
        if not rs:
            p.append('nessun riferimento sicuro (script/tabella) -> non iniettabile')
        if collections.Counter(ET.tokens(orig)) != collections.Counter(ET.tokens(final)):
            p.append(f'token {ET.tokens(final)} != {ET.tokens(orig)}')
        back = decode_pcs(ET.INJ.encode_text(ET.CM, final), 0, 4096).text
        if ET.norm_rt(back) != ET.norm_rt(final):
            p.append('carattere non codificabile')
        print('ERR' if p else 'OK ', hex(a), rs, '; '.join(p), '\n      EN', repr(orig), '\n      IT', repr(final))
        bad += bool(p)
    print('errori:', bad)


if __name__ == '__main__':
    if sys.argv[1] == 'show':
        for eid in sys.argv[2:]:
            x = db()[eid]
            print(eid, x['category'], 'addr', x['address'], 'len', x['byte_length'], 'fixed' if x.get('translated_fixed') else '',
                  'no_reloc' if x.get('no_relocation') else '', 'srcs', x.get('pointer_sources', [])[:6])
            print('  EN ', repr(x['original']))
            print('  IT ', repr(cur(x)))
            print('  R= ', repr(notation(cur(x))))
    elif sys.argv[1] == 'addr':
        a = int(sys.argv[2], 16)
        print(repr(decode_pcs(rom(), a, 2048).text))
        for s, k in refs(a):
            print('  ref 0x%X %s' % (s, k))
    else:
        check(sys.argv[1])
