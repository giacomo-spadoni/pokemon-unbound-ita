"""Every trainerbattle (0x5C) in a ROM: decode all its text pointers, flag English ones.
  python out/audit/trainer_scan.py ROM > out/audit/trainer_scan.txt"""
import sys, re, collections
sys.path.insert(0, '.')
from lib.pcs_text import decode_pcs

rom = open(sys.argv[1], 'rb').read()
orig = open('rom/unbound.gba', 'rb').read()
EN = set("""the you your i me my we our is are was were be been am do does did have has had will would can could
should what where when why how who this that there here not no yes just so but and or if of to for from with
at on in out up it it's i'm you're don't can't won't let's get got go going come came battle battles trainer
trainers pokemon pokémon win won lose lost beat strong stronger weak best good great nice wow huh hey oh ah
again too very really still now never always time think know want need see look like gonna wanna yeah okay
please thanks sorry well right way man guy girl kid""".split())
IT = re.compile(r"[àèéìòù]|\b(il|lo|gli|della|che|non|sono|sei|hai|per|con|una|uno|questo|questa|anche|più|mi|ti|ho|ma|di)\b", re.I)
LET = set(range(0xA1, 0xF0)) | {0x00, 0xB4, 0xB0, 0xAB, 0xAC, 0xAD, 0xAE, 0xB8, 0xFE, 0xFD, 0xFA, 0xFB, 0xFC, 0x1B}


def text_at(r, p):
    if not (0 <= p < len(r)):
        return None
    j = r.find(b'\xff', p, p + 1500)
    if j == -1 or j - p < 2:
        return None
    seg = r[p:j]
    if sum(b in LET for b in seg) / len(seg) < 0.9:
        return None
    return decode_pcs(r, p, j - p + 1).text


seen = {}
n_tb = 0
i = rom.find(b'\x5c')
while i != -1:
    t = rom[i + 1] if i + 1 < len(rom) else 99
    if t <= 0x0C:
        texts = []
        for k in range(6, 34, 4):
            for off in (k,):
                w = int.from_bytes(rom[i + off:i + off + 4], 'little')
                if 0x08000000 <= w < 0x0A000000:
                    s = text_at(rom, w - 0x08000000)
                    if s:
                        texts.append((i + off, w - 0x08000000, s))
        # need at least one text right at +6 or +10 to accept as a real trainerbattle
        if texts and texts[0][0] in (i + 6, i + 10):
            n_tb += 1
            for src, p, s in texts:
                seen.setdefault(p, (src, s))
    i = rom.find(b'\x5c', i + 1)

eng = []
for p, (src, s) in seen.items():
    clean = re.sub(r'\[[a-z0-9_]+\]|\\[A-Za-z?.]+[0-9A-F]*|\\\\[0-9A-F]{2}', ' ', s)
    words = re.findall(r"[A-Za-z’']+", clean)
    en = [w for w in words if w.lower().replace('’', "'") in EN]
    if words and len(en) >= max(1, len(words) // 4) and not IT.search(clean):
        eng.append((src, p, s))
print('trainerbattle', n_tb, 'testi', len(seen), 'inglesi', len(eng))
for src, p, s in sorted(eng):
    print(f'src 0x{src:07X} txt 0x{p:07X} {s[:160]!r}')
