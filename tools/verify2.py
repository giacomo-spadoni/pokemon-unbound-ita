import json, struct, sys, re, collections
sys.path.insert(0, '.')
from lib.pcs_text import decode_pcs

BASE, NEW, JSON_NEW = sys.argv[1], sys.argv[2], sys.argv[3]
rb = open(BASE, 'rb').read()
rn = open(NEW, 'rb').read()
E = json.load(open(JSON_NEW, encoding='utf-8'))['entries']
BS = chr(92)


def rd(rom, x):
    for s in x.get('pointer_sources', []):
        p = struct.unpack_from('<I', rom, int(s, 16))[0]
        if 0x08000000 <= p < 0x0A000000:
            return decode_pcs(rom, p - 0x08000000, 2048).text
    return decode_pcs(rom, int(x['address'], 16), 2048).text


def norm(t):
    t = t.replace('{B4}', '’').replace(BS + BS + 'n', '').replace(BS + 'n', '')
    return re.sub(r'\s+', '', t.replace('"', ''))


def words(t):
    return len(re.findall(r'[A-Za-zÀ-ú]{3,}', t))


def status(rom, x):
    exp = x.get('translated_fixed') or x.get('translated') or ''
    got = rd(rom, x)
    if norm(got) == norm(exp):
        return 'ok'
    if norm(got) == norm(x['original']):
        return 'english'
    return 'other'


c = collections.Counter()
regress = []
for x in E:
    if not x.get('translated') or words(x['translated']) < 2:
        continue
    try:
        sb, sn = status(rb, x), status(rn, x)
    except Exception:
        continue
    c[(sb, sn)] += 1
    if sb == 'ok' and sn != 'ok':
        regress.append((x['id'], x['category'], sn))
print('(base -> nuova):')
for k, v in sorted(c.items()):
    print('  ', k, v)
print('testi tradotti nella base ma NON nella nuova:', len(regress))
for r in regress[:15]:
    print('  ', r)
gain = [k for k in c if k[0] != 'ok' and k[1] == 'ok']
print('testi non tradotti nella base ma tradotti nella nuova:', sum(c[k] for k in gain))
