"""v7: Pokédex in metres / kilograms + Italian labels (FireRed code reused by Unbound).
  python out/v7_code.py ROM_IN ROM_OUT
Height (FireRed DexScreen_PrintMonHeight body at 0x1058F6, Unbound only hooks the species conversion):
  x = height_dm*10000/254 -> x = height_dm*10 (= cm); feet = x/120 -> metres = x/100; the "*120" shift sequence
  becomes movs r0,#100 / muls r0,r6; inches = (x - m*100)/10 = decimetre digit.
  Printed  m ' i/10 i%10 "   ->   m , d <space> m     (i/1 = d, i%1 = 0 + ' ')
Weight: lbs*100 = w_hg*100000/4536 -> w_hg*10 (= kg*100), decimal point -> comma, "lbs." -> "kg".
Every patched spot is checked against the original bytes first."""
import sys, struct
sys.path.insert(0, '.')
sys.path.insert(0, 'out')

PATCHES = [  # (address, original bytes, new bytes, what)
    (0x10597C, struct.pack('<I', 10000), struct.pack('<I', 10), 'altezza: 10000 -> 10'),
    (0x105926, bytes([0xFE, 0x21]), bytes([0x01, 0x21]), 'altezza: /254 -> /1'),
    (0x10593C, bytes([0x78, 0x21]), bytes([0x64, 0x21]), 'altezza: /120 -> /100'),
    (0x105944, bytes([0x30, 0x01, 0x80, 0x1B, 0xC0, 0x00]),
     bytes([0x64, 0x20, 0x70, 0x43, 0xC0, 0x46]), 'altezza: r6*120 -> movs r0,#100; muls r0,r6; nop'),
    (0x10599C, bytes([0xB4, 0x20]), bytes([0xB8, 0x20]), "altezza: ' -> ,"),
    (0x1059A6, bytes([0x0A, 0x21]), bytes([0x01, 0x21]), 'altezza: i/10 -> i/1'),
    (0x1059B4, bytes([0x0A, 0x21]), bytes([0x01, 0x21]), 'altezza: i%10 -> i%1'),
    (0x1059BA, bytes([0xA1, 0x30]), bytes([0x00, 0x30]), "altezza: cifra -> spazio"),
    (0x1059C2, bytes([0xB2, 0x20]), bytes([0xE1, 0x20]), 'altezza: " -> m'),
    (0x1059DC, bytes([0xB4, 0x20]), bytes([0xB8, 0x20]), "altezza sconosciuta: ' -> ,"),
    (0x1059F0, bytes([0xB2, 0x20]), bytes([0xE1, 0x20]), 'altezza sconosciuta: " -> m'),
    (0x105AD0, struct.pack('<I', 100000), struct.pack('<I', 10), 'peso: *100000 -> *10'),
    (0x105AD4, struct.pack('<I', 4536), struct.pack('<I', 1), 'peso: /4536 -> /1'),
    (0x105BA6, bytes([0xAD, 0x20]), bytes([0xB8, 0x20]), 'peso: . -> ,'),
    (0x105BDC, bytes([0xAD, 0x20]), bytes([0xB8, 0x20]), 'peso sconosciuto: . -> ,'),
    # Stat messages: CFRU writes [adverb][verb] into gBattleTextBuff2 ("sharply " + "rose!"). Italian uses whole
    # phrases ("sale di molto!"), so after an adverb r4 becomes 0xFF: FireRed then writes the verb entry with type
    # 0xFF = B_BUFF_EOS and the verb is never expanded (r4 is reloaded right after, 0x27F2C / 0x27FA6).
    (0x8834CC, bytes([0x08, 0xD0]), bytes([0x06, 0xD0]), 'cala: beq harshly -> nuovo blocco'),
    (0x8834D2, bytes.fromhex('5c70852098700120d870042204e05c70d3209870dc700422'),
     bytes.fromhex('5c70852098700120' '03e0' '5c70d32098700020' 'd8700422ff24'), 'cala: dopo l avverbio niente verbo'),
    (0x88351A, bytes([0x08, 0xD0]), bytes([0x06, 0xD0]), 'sale: beq sharply -> nuovo blocco'),
    (0x883520, bytes.fromhex('5c70862098700120d870042204e05c70d1209870dc700422'),
     bytes.fromhex('5c70862098700120' '03e0' '5c70d12098700020' 'd8700422ff24'), 'sale: dopo l avverbio niente verbo'),
]
# label strings: literal-pool word -> new Italian text (written to vetted free space)
LABELS = [(0x105978, 0x08415F98, 'Alt.'), (0x105CAC, 0x08415F9B, 'Peso'), (0x105CA8, 0x08415FA0, 'kg')]


def main(src, dst):
    import eng_tools as ET
    from v7_gfx import free_block
    rom = bytearray(open(src, 'rb').read())
    orig = open('rom/unbound.gba', 'rb').read()
    for a, old, new, what in PATCHES:
        assert orig[a:a + len(old)] == old, f'0x{a:X} originale diverso ({what})'
        assert rom[a:a + len(old)] == old, f'0x{a:X} già modificato nella build ({what})'
        rom[a:a + len(new)] = new
        print(f'0x{a:X} {what}')
    blob = b''
    for _, _, text in LABELS:
        blob += ET.INJ.encode_text(ET.CM, text)
    dest = free_block(rom, len(blob))
    assert dest > 0
    rom[dest:dest + len(blob)] = blob
    off = dest
    for lit, old_ptr, text in LABELS:
        assert struct.unpack_from('<I', rom, lit)[0] == old_ptr, f'letterale 0x{lit:X} inatteso'
        refs = [i for i in range(0, len(rom) - 3, 4) if struct.unpack_from('<I', rom, i)[0] == old_ptr]
        for r in refs:
            rom[r:r + 4] = struct.pack('<I', off + 0x08000000)
        print(f'etichetta {text!r} a 0x{off:X} ({len(refs)} riferimenti)')
        off += len(ET.INJ.encode_text(ET.CM, text))
    open(dst, 'wb').write(rom)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
