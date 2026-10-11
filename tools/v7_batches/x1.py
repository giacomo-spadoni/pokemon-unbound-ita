# v7b: English strings found by romscan2 (reachable by script commands / tables) that were never extracted.
# X = {address: Italian text}  (same notation as t*.py: @XX battle buffers, … ellipsis, ¶ new box)
# R = {entry id: Italian text}  rewrites of existing entries (layout + token check)
X = {
    0x1A52DD: "[player] trova [buffer1] [buffer2]!",
    0x1A63E8: "[player] trova [buffer2]!¶Contiene [buffer1].",
    0xA4D82B: "[player] trova [buffer1] [buffer2]!",
    0xA4D84B: "Hai ottenuto [buffer2]!¶Contiene [buffer1].",
    0x1A5690: "[player] consegna [buffer1].",
    0x416C8F: "[buffer1] non tiene nessuno strumento.[pause]",
    0x417032: "La statistica base [buffer2] di [buffer1] è aumentata.[pause]",
    0x41ADFF: "[player] ha riposato comodamente a casa.",
    0x7710F1: "Hai ricevuto [buffer1]!",
    0x7C67A0: "[player] riceve $4.000!",
    0x7D4845: "[blue]Funziona! Funziona davvero!",
    0x7F16B6: "Recluta 3: [blue]Ricevuto! Siamo salvi!",
    0x7F5158: "[blue]Questa è la mia vendetta!",
    0x7419B7: "Ben fatto.¶Mi hai rallegrato un po' la giornata.",
    0x8CF522: "una Pepita",
    0x8CF554: "il Cromamuleto",
    0x1F07353: "un Catalogo Allenatori",
    0x1F07382: "una Latiasite",
    0x1F0738E: "un Cromamuleto",
    0xA377A6: "@13 non riesce a ingranare!",
    0xA3787F: "@13 ha perquisito @11 e ha trovato @16!",
    0xA444EA: "in una tempesta di sabbia!",
    0xA444FA: "sotto la grandine!",
    0xA4AD51: "@16 di @10 è bruciata!",
    0xA4B0C9: "@10 si avvolge in una nebbia protettiva!",
    0xA4E276: "[buffer1] ti adora! [buffer2] di base è sceso![pause]",
    0xA4E406: "Ora [buffer1] può usare il Gigamax![pause]",
    0xA4E41F: "[buffer1] non può più usare il Gigamax.[pause]",
    0x1F12E80: "Ho perso perché sono ancora mezzo addormentato.",
    0x1F31CEF: "Mi dispiace, signor Ciprian!",
    0x1F3DE39: "No…¶Non di nuovo…",
    0x1F4AA46: "Ovviamente, non mi ha mostrato niente che non sapessi già.",
    0x1F82C88: "l'Uovo raro",
    0x1F8D227: "Minatore",
    0x1FA91BD: "Non è servito a molto…",
    0x1F0DD4B: "strumento",
}
X_DROP = set()
R = {
    # lists that lost one-item-per-line in the starting translation
    'scr_7EB7D2': "§1F: Sportello servizi⏎2F: Mercato degli Allenatori↓3F: Zona Evoluzione↓4F: Angolo MT↓5F: Scatola delle medicine↓6F: Doni di Wiseman",
    'scr_1F71777': "§1F: Sportello servizi⏎2F: Mercato degli Allenatori↓3F: Zona Evoluzione↓4F: Angolo MT↓5F: Scatola delle medicine↓6F: Doni di Wiseman",
    'scr_1EEAF4D': "§10 Baccacedro↓10 Baccaprugna↓2 Baccalighia↓2 Baccapane↓5 Latte Mumu",
}
