# English still shown through code literal pools / fixed slots too small (out/audit/english_hunter/report.txt B1-B2)
SRC = {
    'v7b_0416C8F': [0x123CBC],                 # "[buffer1] isn't holding anything" (bag Give)
    'v7b_0417032': [0x1251D8],                 # "base stat was raised" (vitamins)
    'tbl_map_names_00108_3EF22E': [0xC4DA0],   # Dehara Dept. special case in GetMapName
}
RELOC = {
    'scr_415D97': 'Ragazza',
    'scr_A4524B': 'Gran Mo',
    'scr_A45270': 'Ciprian',
    'scr_A4526B': 'Yarrow',
    'scr_A4C5FD': 'Provocazione',
    'scr_A4C5DD': 'Inibitore',
}
XP = {
    0x416F9A: ("[buffer1] non è più scottato.[pause]", [0x125100]),
    0x416FED: ("[buffer1] è di nuovo in salute.[pause]", [0x125164]),
    0x417002: ("I PP di [buffer1] sono aumentati.[pause]", [0x1251EC]),
    0x41A16F: ("[player] ha scambiato di posto [buffer1] e [buffer2].", [0x113F7C]),
    0x41E1E9: ("[buffer2] sarà inviato a [buffer1].", [0x514B0, 0x528A0]),
}
