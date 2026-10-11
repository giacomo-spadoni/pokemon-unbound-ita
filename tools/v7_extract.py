"""v7: collect English texts still shown in game that the extractor never found.
Accepted only when EVERY pointer to the text is a safe owner:
  - CFRU battle-script operand  FA <0x0203C020|0x0203E020> <ptr>
  - 4-byte aligned word (pointer table / literal pool)
  - event-script loadpointer    0F 00 <ptr>
Targets inside an existing JSON entry are skipped.
  python out/v7_extract.py JSON  -> out/v7_new.json (entries, untranslated) + out/v7_rejected.txt"""
import json, re, struct, sys, collections
sys.path.insert(0, '.')
from lib.pcs_text import decode_pcs

rom = open('rom/unbound.gba', 'rb').read()
E = json.load(open(sys.argv[1], encoding='utf-8'))['entries']
spans = sorted((int(x['address'], 16), int(x['address'], 16) + int(x.get('byte_length') or 1)) for x in E)
starts = [a for a, _ in spans]
import bisect


def inside(a):
    k = bisect.bisect_right(starts, a) - 1
    return k >= 0 and spans[k][0] <= a < spans[k][1]


FA = (bytes.fromhex('fa20c00302'), bytes.fromhex('fa20e00302'))


def refs(t):
    p = struct.pack('<I', t + 0x08000000)
    out = []
    i = rom.find(p)
    while i != -1:
        out.append(i)
        i = rom.find(p, i + 1)
    return out


def kind(s):
    if rom[s - 5:s] in FA or (rom[s - 5] == 0xFA and rom[s - 2:s] == b'\x03\x02'):
        return 'fa'
    if rom[s - 2:s] == b'\x0f\x00':
        return 'loadpointer'
    if rom[s - 1] == 0x67:
        return 'preparemsg'
    if rom[s - 2] == 0x85 and rom[s - 1] < 0x10:
        return 'bufferstring'
    for k in (6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32):  # trainerbattle (CFRU types up to 0x0F have longer layouts)
        if rom[s - k] == 0x5C and rom[s - k + 1] <= 0x0F:
            return 'trainerbattle'
    if s % 4 == 0:
        return 'aligned'
    return 'unknown'


# candidate targets: FA operands + english strings found by romscan (still referenced)
cands = set()
for pre in FA:
    i = rom.find(pre)
    while i != -1:
        t = struct.unpack_from('<I', rom, i + 5)[0]
        if 0x08000000 <= t < 0x0A000000:
            cands.add(t - 0x08000000)
        i = rom.find(pre, i + 1)
for l in open('out/romscan_live.txt', encoding='utf-8'):
    cands.add(int(l[:9], 16))

EN = re.compile(r"[A-Za-z]{3,}")
new, rej = [], []
for t in sorted(cands):
    if inside(t):
        continue
    r = decode_pcs(rom, t, 2048)
    txt = r.text
    if len(EN.findall(txt)) < 1 or r.byte_length < 3:
        rej.append((t, 'non testo', txt[:60]))
        continue
    srcs = refs(t)
    kinds = [kind(s) for s in srcs]
    if not srcs or 'unknown' in kinds:
        rej.append((t, 'sorgenti ' + ','.join(f'{s:X}:{k}' for s, k in zip(srcs, kinds)), txt[:60]))
        continue
    battle = 'fa' in kinds or 0x880000 <= t < 0xA50000
    new.append({
        'id': 'v7_%07X' % t,
        'category': 'battle_messages' if battle else 'v7_texts',
        'address': '0x%X' % t,
        'pointer_sources': ['0x%X' % s for s in srcs],
        'byte_length': r.byte_length,
        'is_pointer_based': True,
        'table_name': 'v7.' + ('cfruBattle' if battle else 'misc'),
        'original': '"' + txt + '"',
        'source_kinds': sorted(set(kinds)),
    })
json.dump(new, open('out/v7_new.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
with open('out/v7_rejected.txt', 'w', encoding='utf-8') as f:
    for t, why, txt in rej:
        f.write(f'0x{t:07X} | {why} | {txt!r}\n')
print('nuove voci', len(new), collections.Counter(x['category'] for x in new), '| scartate', len(rej),
      collections.Counter(w.split(' ')[0] for _, w, _ in rej))
