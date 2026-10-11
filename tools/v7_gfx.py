"""v7: Italian text graphics (status icons, ESP/PS labels) patched into the built ROM.
  python out/v7_gfx.py ROM_IN ROM_OUT [--preview out/v7_gfx_preview.png]
Every asset is an LZ77 4bpp blob of the ORIGINAL Unbound ROM. The edited blob is written in place when the new
compressed stream fits the old one, otherwise into verified free space (long 0xFF run) with every aligned
pointer to the old blob redirected."""
import sys, struct
sys.path.insert(0, '.')
from lib.gba_graphics import lz77_decompress, lz77_compress, decode_4bpp_tiles, encode_4bpp_tiles

ORIG = open('rom/unbound.gba', 'rb').read()
FU = open('out/red_usa.gba', 'rb').read()
FI = open('out/red_ita.gba', 'rb').read()


def lz_len(rom, a):
    """length in bytes of the LZ77 stream at a (header included)"""
    size = int.from_bytes(rom[a + 1:a + 4], 'little')
    i, out = a + 4, 0
    while out < size:
        flags = rom[i]; i += 1
        for b in range(8):
            if out >= size:
                break
            if flags & (0x80 >> b):
                n = (rom[i] >> 4) + 3
                i += 2
                out += n
            else:
                i += 1
                out += 1
    return i - a


def load(rom, a, w):
    d = lz77_decompress(rom, a)
    n = len(d) // 32
    h = (n + w - 1) // w
    return decode_4bpp_tiles(d, w, h), len(d), h


def status_sheet(unb_addr, usa_addr, ita_addr):
    """copy the Italian letters of each 32x8 icon, mapped onto Unbound's own colours"""
    g, size, _ = load(ORIG, unb_addr, 32)
    gu, _, _ = load(FU, usa_addr, 32)
    gi, _, _ = load(FI, ita_addr, 32)
    for k in range(7):
        xs = range(k * 32, k * 32 + 32)
        diff = [(x, y) for y in range(8) for x in xs if gu[y][x] != gi[y][x]]
        if not diff:
            continue
        x0, x1 = min(x for x, _ in diff), max(x for x, _ in diff)
        y0, y1 = min(y for _, y in diff), max(y for _, y in diff)
        votes = {}
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                votes.setdefault(gu[y][x], {}).setdefault(g[y][x], 0)
                votes[gu[y][x]][g[y][x]] += 1
        m = {u: max(v, key=v.get) for u, v in votes.items()}
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if gi[y][x] in m:
                    g[y][x] = m[gi[y][x]]
    return g, size


def stamp(g, x0, y0, rows, colours):
    for dy, r in enumerate(rows):
        for dx, ch in enumerate(r):
            if ch != ' ':
                g[y0 + dy][x0 + dx] = colours[ch]


def exp_bar():                     # "EXP" -> "ESP"  (3x5 glyphs, C=12 letter, D=13 shade)
    g, size, _ = load(ORIG, 0xE9B3F0, 12)
    stamp(g, 79, 1, ['CCD', 'C..', 'DCD', '..C', 'DCC'], {'C': 12, 'D': 13, '.': 0})
    return g, size


def hp_bar():                      # "HP" -> "PS"  (outlined 7-wide glyphs, F=15 outline, 4=fill)
    g, size, _ = load(ORIG, 0xE9B4B8, 12)
    for y in range(0, 6):
        for x in range(73, 86):
            g[y][x] = 0
    P = ['.FFFFF.', 'F44444F', 'F44F44F', 'F44444F', 'F44FFF.', '.FF....']
    S = ['.FFFFF.', 'F44444F', 'F44FFF.', '.FFF44F', 'F44444F', '.FFFFF.']
    col = {'F': 15, '4': 4, '.': None}
    for x0, glyph in ((73, P), (79, S)):
        for dy, r in enumerate(glyph):
            for dx, ch in enumerate(r):
                if col[ch] is not None:
                    g[dy][x0 + dx] = col[ch]
    return g, size


def healthbox():                   # "HP" -> "PS" inside the battle healthbox (1 = letter, 7 = background)
    g, size, _ = load(ORIG, 0xD1F340, 32)
    P = ['11111', '11711', '11111', '11777']
    S = ['11111', '11777', '77711', '11111']
    stamp(g, 162, 3, P, {'1': 1, '7': 7})
    stamp(g, 168, 3, S, {'1': 1, '7': 7})
    return g, size


def back_button():                 # "B Back" -> "B Esci" (1 = letter fill, C = outline)
    g, size, _ = load(ORIG, 0xACA968, 4)
    for y in range(8):
        for x in range(9, 32):
            g[y][x] = 0
    glyphs = [(10, ['111', '1  ', '11 ', '1  ', '1  ', '111'], 1),
              (14, [' 11', '1  ', '  1', '11 '], 3),
              (18, [' 11', '1  ', '1  ', ' 11'], 3),
              (22, ['1', ' ', '1', '1', '1', '1'], 1)]
    fill = set()
    for x0, rows, y0 in glyphs:
        for dy, r in enumerate(rows):
            for dx, ch in enumerate(r):
                if ch == '1':
                    fill.add((x0 + dx, y0 + dy))
    for (x, y) in fill:
        for nx in (x - 1, x, x + 1):
            for ny in (y - 1, y, y + 1):
                if 9 <= nx < 32 and 0 <= ny < 8 and (nx, ny) not in fill:
                    g[ny][nx] = 12
    for (x, y) in fill:
        g[y][x] = 1
    return g, size


def presents():                    # "PRESENTS" -> "PRESENTA"
    g, size, _ = load(ORIG, 0xEF3828, 8)
    A = ['.55555.', '55...55', '66...66', '5555555', '66...66', '55...55']
    for dy, r in enumerate(A):
        for dx, ch in enumerate(r):
            g[dy][56 + dx] = 0 if ch == '.' else int(ch)
    return g, size


# Only assets referenced by the game (FireRed copies at 0xE9BF48 / 0xE82EA0 / 0xD1F340 have no pointer left).
ASSETS = [
    (0xB1E11C, 32, lambda: status_sheet(0xB1E11C, 0xE9BF48, 0xE9BF5C)),
    (0xE9B3F0, 12, exp_bar),
    (0xE9B4B8, 12, hp_bar),
    (0xACA968, 4, back_button),
    (0xEF3828, 8, presents),
]


def free_block(rom, need):
    """FF space inside the injector's vetted free ranges (lib/unbound_free_space.py), 64-byte margins."""
    from lib.unbound_free_space import VETTED_FREE_SPACE_RANGES
    run = bytes([0xFF]) * (need + 128)
    for lo, hi in VETTED_FREE_SPACE_RANGES:
        i = rom.find(run, lo, hi)
        if i != -1:
            return (i + 64 + 3) // 4 * 4
    return -1


def main(src, dst, preview=None):
    rom = bytearray(open(src, 'rb').read())
    grids = []
    for addr, w, fn in ASSETS:
        assert rom[addr:addr + 16] == ORIG[addr:addr + 16], f'asset 0x{addr:X} già modificato'
        g, size = fn()
        h = len(g) // 8
        data = encode_4bpp_tiles(g, w, h)[:size]
        comp = lz77_compress(data, vram_safe=True)
        assert lz77_decompress(comp, 0) == data
        old = lz_len(ORIG, addr)
        if len(comp) <= old:
            rom[addr:addr + len(comp)] = comp
            where = 'sul posto'
        else:
            dest = free_block(rom, len(comp))
            assert dest > 0
            rom[dest:dest + len(comp)] = comp
            p_old = struct.pack('<I', addr + 0x08000000)
            refs = [i for i in range(0, len(rom) - 3, 4) if rom[i:i + 4] == p_old]
            assert refs, f'nessun puntatore a 0x{addr:X}'
            for r in refs:
                rom[r:r + 4] = struct.pack('<I', dest + 0x08000000)
            where = f'spostato a 0x{dest:X} ({len(refs)} puntatori)'
        print(f'0x{addr:X}: {len(comp)} byte (prima {old}) {where}')
        grids.append((addr, g))
    open(dst, 'wb').write(rom)
    if preview:
        from PIL import Image
        rows = []
        for addr, g in grids:
            go, _, _ = load(ORIG, addr, len(g[0]) // 8)
            for gg in (go, g):
                im = Image.new('L', (len(gg[0]), len(gg)))
                im.putdata([v * 17 for row in gg for v in row])
                rows.append(im.crop((0, 0, min(im.width, 256), min(im.height, 32))))
        W, H = 256, sum(r.height + 2 for r in rows)
        s = Image.new('L', (W, H), 40)
        y = 0
        for r in rows:
            s.paste(r, (0, y)); y += r.height + 2
        s.resize((W * 3, H * 3), Image.NEAREST).save(preview)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[4] if len(sys.argv) > 4 and sys.argv[3] == '--preview' else None)
