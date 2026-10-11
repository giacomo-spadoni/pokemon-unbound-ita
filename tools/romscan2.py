"""Stricter English finder: every FF-terminated PCS string still referenced by a pointer in the ROM whose words are
English (large word list, also short strings like "[player] found [buffer2]!").
  python out/romscan2.py ROM JSON > out/romscan2.txt"""
import json, re, sys, struct, collections
sys.path.insert(0, '.')
from lib.pcs_text import decode_pcs

rom = open(sys.argv[1], 'rb').read()
EN_WORDS = set("""the a an you your yours he she him her his it its we our they them their i me my mine this that these those
is are was were be been being am do does did done have has had will would can could should shall may might must
found find obtained obtain received receive got get put away pocket bag item items used use using learned learn forgot
forget move moves wants want trying try delete deleted give gave take took fainted faint wild foe enemy opposing ally team
what where when why how who which there here not no yes yeah okay ok please thanks thank sorry hello hi hey welcome
and or but if so because then than too very really just only also again still now already ever never always
of to for from with without into onto about at by on in out up down off over under
sent out come came go went gone back battle battles battling trainer trainers money paid pay won lose lost win
level grew rose fell raised lowered restored healed cured hurt damage effect effects became become turned
can't cannot don't doesn't didn't won't isn't aren't wasn't i'm you're it's that's there's let's i'll you'll
party box pc stored storage sent nickname nicknamed hatched egg eggs evolved evolve evolution stopped
good great nice well done ready wait waiting""".split())
IT_HINT = re.compile(r"[àèéìòù]|\b(il|lo|gli|della|delle|degli|che|non|sono|sei|hai|per|con|una|uno|questo|questa|anche|più|ancora)\b", re.I)
LET = set(range(0xA1, 0xF0)) | {0x00, 0xB4, 0xB0, 0xAB, 0xAC, 0xAD, 0xAE, 0xB8, 0xFE, 0xFD, 0xFA, 0xFB, 0xFC, 0x1B, 0x1A}

# all pointer values in the ROM (aligned + unaligned) -> set of targets
targets = set()
data = rom
for i in range(0, len(data) - 3):
    if data[i + 3] in (0x08, 0x09) and data[i + 2] <= 0xFF:
        v = int.from_bytes(data[i:i + 4], 'little') - 0x08000000
        if 0 <= v < len(rom):
            targets.add(v)
out = []
i = 0
n = len(rom)
while i < n:
    if rom[i] == 0xFF:
        i += 1
        continue
    j = rom.find(b'\xff', i)
    if j == -1:
        break
    seg = rom[i:j]
    if 3 <= len(seg) <= 1200 and i in targets and sum(b in LET for b in seg) / len(seg) > 0.9:
        t = decode_pcs(rom, i, len(seg) + 1).text
        clean = re.sub(r'\[[a-z0-9_]+\]|\\[A-Za-z?]+[0-9A-F]*|\\\\[0-9A-F]{2}', ' ', t)
        words = re.findall(r"[A-Za-z’']+", clean)
        en = [w for w in words if w.lower().replace('’', "'") in EN_WORDS]
        if en and len(en) >= max(1, len(words) // 3) and not IT_HINT.search(clean):
            out.append((i, t, en))
    i = j + 1
print('stringhe con puntatore che sembrano inglesi:', len(out))
for a, t, en in out:
    print(f'0x{a:07X} {t[:150]!r}')
