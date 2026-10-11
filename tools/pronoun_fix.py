"""Gendered pronoun fix (after phase 3).

The game fills [buffer1..3] with him/her, he/she, his/her taken from tiny fragment strings
(checkgender + bufferstring subroutines). The Italian had 'lui'/'lei'/'suo'/'di lei' there,
giving 'Prendi lui!', 'portare lui qui', 'la mamma di suo'.
Fix: object/possessive fragments become the clitics 'lo'/'la', glued to the verb in the
sentences ('Prendi[buffer1]!' -> 'Prendilo!' / 'Prendila!'); possessives Italian does not
need are dropped (DROP: removing a [buffer] token is harmless for the game).
Subject fragments (he/she -> lui/lei) stay.

  python out/pronoun_fix.py SRC DST      (run after dlg_tools apply, before build.sh)"""
import json, sys, collections, re
sys.path.insert(0, '.')
sys.path.insert(0, 'out')
import eng_tools as ET

A = '{B4}'
E = '\\.'
W = '\\CC0818'

FRAG = {
    'tbl_gendered_dialogue_fragments_00013_789224': 'lo',   # him  (sub 0x1E6E06A b0, sub 0x1E8A141 b1)
    'tbl_gendered_dialogue_fragments_00016_78922E': 'la',   # her  (same, plus sub 0x1E8A141 b0 possessive)
    'tbl_gendered_dialogue_fragments_00027_7BD7C5': 'lo',   # his  (sub 0x1E8A141 b0)
    'tbl_gendered_dialogue_fragments_00048_1FA764E': 'lo',  # him  (subs 0x1E709DB / 0x1EAB8FD b0)
    'scr_1FA7652': 'la',                                    # her  (same, plus 0x1EAB8FD b2)
    'tbl_gendered_dialogue_fragments_00049_1FA7656': 'lo',  # his  (sub 0x1EAB8FD b2)
}

T = {
    # --- intro: laboratorio della Luce della Rovina
    'scr_1F2CBDA': '§Presto, scienziato!⏎Che fai lì impalato?¶Prendi[buffer1]!',
    'scr_1F2CC17': '§Ora stendi[buffer1] e rinchiudi[buffer1]⏎nel magazzino!¶Zefiro andrà su tutte le furie quando⏎lo saprà' + E,
    'scr_1F2CC7E': '[buffer3] non si sveglia, Hoopa.',
    'scr_1F2CD70': '§E sei stato tu a portar[buffer1] qui?',
    'scr_1F2CDA7': 'Non so perché [buffer1] volessi qui, ma sei stato una seccatura continua da quando ti ho trovato su quella spiaggia l' + A + 'anno scorso!¶Non sarò il tuo vero \\qocustode\\qc, ma ora sono il tuo Allenatore!¶E come tuo Allenatore, ti ordino di smetterla con queste bambinate' + E + W + ' SUBITO!',
    'scr_1F2CEC8': 'Ora che ci penso, potrei sfruttare la cosa a mio vantaggio' + E,
    'scr_1F2CB2D': 'Reclute',
    'scr_1F2E221': 'Il primo, il ragazzo coi capelli rossi, non ha visto niente di importante.¶L' + A + 'altra persona, invece' + E + '¶Se Fey scopre che [buffer2] ha messo piede nel laboratorio, pretenderà di trasferire tutto nel bel mezzo della nostra operazione.¶Sai bene che non possiamo permetterci di perdere tempo e risorse' + E,
    'scr_1F2F9B9': 'Reclute!¶Uno di voi vada a trattener[buffer1]!',
    # --- Zefiro e Avorio
    'scr_1F32527': 'Presto!¶Prendi[buffer1], subito!',
    'scr_1F32861': 'Oh, Avorio' + E + '¶Come pensiamo di rimetter[buffer1] in riga, se non riesci nemmeno a batter[buffer1] in una semplice lotta?',
    'scr_1F3296E': '[red]Zefiro, non sono sicura che basti Houndoom da solo per batter[buffer1]' + E,
    'scr_1F329AE': 'Dubiti di me, Avorio?¶Houndoom e io siamo più che in grado di far[buffer1] fuori.',
    'scr_1F32EB9': 'Lascia[buffer1] andare, per ora.¶Finché fanno poche apparizioni in pubblico, Fey e Arthur non hanno motivo di parlarsi.¶È difficile che lui glielo dica.',
    'scr_1F3068C': 'Visto, Eulero?¶Direi che quella Medaglia dimostra che [player] sa badare a sé, e anche bene. Possiamo lasciar[buffer1] fare.¶Al momento, noi quattro siamo gli unici a conoscere il vero scopo delle Ombre.¶Avere un altro Allenatore in grado di affrontarle' + E + W + ' capisci sicuramente dove voglio arrivare.',
    # --- Aklove / Ciprian
    'scr_1F3ADE9': 'Ora basta! Levati dalla mia vista.¶Le Ombre sono finite.¶È ora che Borrius veda la luce' + E + W + ' la Luce della Rovina!¶Ah, ma prima' + E + '¶Vedo che l' + A + 'ospite d' + A + 'onore si è degnato di unirsi a noi.¶Reclute, portateme[buffer1].',
    'scr_1F3F468': 'Ciprian, non capisco' + E + '¶Perché [buffer1] stimi tanto?¶[player] non ha fatto altro che intralciarci.¶Cosa ti fa pensare che [buffer2] voglia aiutarci?',
    'scr_1F3932D': 'Signore, [player] sta cercando di farsi strada fin quassù passando per le rovine!',
    'scr_1F45482': 'Manda [player] dal suo amico!',
    # --- Aros e Hoopa
    'scr_1F1194E': 'Ecco perché, amico mio, devi nasconderti.¶Manderò la tua Poké Ball alla deriva, tra le onde' + E + '¶Sarai sicuramente più al sicuro perso in mare che se restassi con me.¶Se mi sbaglio e non succede nulla, ti richiamerò.¶Ma se questa è la nostra ultima volta insieme' + E + '¶Proteggi il sangue del mio sangue, se mai [buffer2] fosse in pericolo.¶E se un giorno qualche malintenzionato cercasse di liberare a forza il tuo vero potere' + E + '¶Allora cerca[buffer1]: saprà proteggerti.¶Addio, mio buon amico.',
    'scr_1F3B920': 'Ci siamo già incrociati un paio di volte.¶Buon sangue non mente: ha il tuo stesso senso della giustizia' + E + '¶Si butta sempre a capofitto, anche quando non è il caso' + E,
    # --- Emboar Neri / Granbull del Terrore / Big Mo
    'scr_1F9DBD7': 'Te lo dico io!¶Nessuno mi aveva mai stracciato come ha fatto [buffer2]!¶Ho perfino ribattezzato gli Emboar Neri in [player] Neri, per onorar[buffer1]!¶Quindi è ora di ricominciare da capo.¶Io e i [player] Neri ci trasferiamo a Città di Antisis!¶Ho sentito che la vecchia banda che comandava laggiù è stata cacciata dalla città.¶Granbull del Terrore, o roba del genere' + E + '¶Ora quella città è pronta per essere presa dai [player] Neri!¶Gwa ha ha ha!',
    'scr_1F9F6B5': 'Davvero?¶Allora non ci resta che sbatter[buffer1] al tappeto!',
    'scr_1F9F700': 'Chad! Dammi i tuoi Pokémon!¶Voglio stender[buffer1] con la nostra forza combinata!',
    'scr_1FA6CB5': 'Eh?¶È solo una peste!¶Riempiamo[buffer2] di botte e arraffiamo' + E,
    'scr_1FAEE2C': 'Eh? È solo una peste!¶Accidenti, chi va dritto verso un grosso gruppo di persone senza protezione, eh?¶Riempiamo[buffer2] di botte e freghiamoci tutti i soldi!',
    'scr_1FA6E9F': 'Tranquillo, Boss!¶Adesso [buffer1] concio per le feste: [buffer2] piangerà finché la mamma non verrà a prender[buffer3]!',
    'scr_1FA6F85': 'Gah! Brutti zucconi!¶Vi avevo detto di NON sottovalutar[buffer1]!¶E voi che avete fatto? Siete andati a sottovalutar[buffer1]!¶Ma dico io, con tutti gli scagnozzi che ci sono, perché mi sono capitati i più scemi?¶Potrei mandare un babbeo dopo l' + A + 'altro contro questa peste, ma sono sicuro che neanche mille farebbero differenza!¶Vuol dire che i Granbull del Terrore resteranno dei perdenti per sempre' + E + '?',
    'scr_1F9C106': 'Beh, guarda un po' + A + ' chi è passato dalle parole ai fatti!¶Ah ah ah ah! Va bene, un patto è un patto!¶Ti affronterò un' + A + 'altra volta, uno contro uno, con il mio Pokémon migliore!¶Ma non pensare che finirà come l' + A + 'ultima volta!¶Ho guardato tutte le tue lotte, e ormai credo di averti inquadrato per bene.¶Quindi, se pensi di potermi stupire così facilmente' + E + '¶Fatti sotto con tutto quello che hai! Vediamo se il Kingpin ti prende le misure!',
    # --- megacheck 2026-09-30: gendered nouns
    'scr_1EEAD3D': 'Sono sicura che [buffer2] adorerà questa torta.¶Ti prego, prendi questi in cambio del tuo duro lavoro, giovane Allenatore.',
    'scr_1F9CD8C': 'Ci siamo dimenticati di fare un regalo a chi mi ha aiutato!',
    'scr_1FAE9B4': 'Oh, mi ricordo di te!¶Ci hai aiutato nella Palestra di Borgo Dresco!¶Per questo puoi avere questi cinque Revitalizzanti.',
    'scr_8CE9CB': 'Ti do il benvenuto in Pokémon Unbound!¶Prima di iniziare, tieni presente che questo è un fangame senza scopo di lucro.¶Se hai pagato per questo gioco, chiedi subito il rimborso!',
    'scr_1FA20B1': 'Bene, ragazzi! È il momento della resa dei conti!¶Appena la bomba esplode, fategliela vedere ai Ferrothorn Neri!¶Fate sì che si spaventino così tanto da cominciare a chiamarci il Terrore [player]!',
    'scr_1F92746': '[black]La Stampa [green][buffer1][black] è stata aggiunta alla Carta della Frontiera di [player]!',
}
DROP = {'scr_1F3932D', 'scr_1F45482', 'scr_1FAEE2C', 'scr_1F9C106', 'scr_1F1194E', 'scr_1F3B920',
        'scr_1F9CD8C', 'scr_1FAE9B4'}

# megacheck 2026-09-30: more fragments
FRAG.update({
    'scr_415D97': 'Ragazza',                                     # Girl (was 'Lei', next to 'Ragazzo')
    'tbl_gendered_dialogue_fragments_00035_1EEAF9C': 'mio nipote',  # grandson ('la mia [buffer2]' -> '[buffer2]')
    'tbl_gendered_dialogue_fragments_00036_1EEAFA5': 'mio figlio',  # son
    'tbl_gendered_dialogue_fragments_00053_1FA14C2': 'ragazzo',                                    # guy ('Davvero, tipo?')
    'tbl_gendered_dialogue_fragments_00045_1FA17C0': 'amico',                                      # man   ('my man' / 'Bel colpo, uomo!')
    'tbl_gendered_dialogue_fragments_00046_1FA17C8': 'amica',                                      # woman
})

# exact strings (no layout): FD placeholders written with a single backslash showed '0F', '23'...
BB = chr(92) * 2
RAW = {
    'tbl_battle_messages_00310_3FD366': BB + '1C ' + BB + '1D\nvuole sfidarti!',
    'tbl_battle_messages_00332_3FD522': BB + '1C ' + BB + '1D\nha ritirato ' + BB + '00!',
    'tbl_battle_messages_00018_A4B440': BB + '38 Ventoincoda\nè finito!',
    'tbl_battle_messages_00019_A4B460': BB + '38 Fortuncanto\nè finito!',
    'tbl_menu_pokemon_00016_A4E15D': 'Servono [buffer1] Pokémon.',
    # stat messages: whole Italian phrases (the verb after an adverb is suppressed by v7_code.py)
    'tbl_battle_messages_00224_3FCB41': 'sale di molto!',
    'tbl_battle_messages_00226_3FCB50': 'cala a picco!',
    'tbl_battle_messages_00000_883590': 'sale moltissimo!',
    'tbl_battle_messages_00000_A4C603': 'sale moltissimo!',
    'tbl_battle_messages_00001_8835A0': 'cala moltissimo!',
    'tbl_battle_messages_00001_A4C610': 'cala moltissimo!',
}
FIXBS = ['tbl_battle_messages_%s' % k for k in (
    '00000_905690', '00001_9056B4', '00002_905770', '00003_905A30', '00004_905A50', '00005_905C25',
    '00006_905C40', '00007_905E9A', '00009_9064A0', '00010_906520', '00011_906540')]
# english names left in battle (trainer table) and missions
NAMES = {'Zeph': 'Zefiro', 'Ivory': 'Avorio', 'Marlon': 'Ciprian', 'Big Mo': 'Gran Mo', 'Galavan': 'Galvani',
         'Moleman': 'Talpino', 'Krystal': 'Cristal', 'Milo': 'Yarrow'}
REPL = {
    'tbl_mission_objectives_00005_1F56201': [('Dresco Town', 'Borgo Dresco')],
    'tbl_mission_objectives_00008_1F5627F': [('Crater Town', 'Città Cratere')],
    'tbl_mission_objectives_00012_1F56353': [('Blizzard City', 'Città Bufera')],
    'tbl_mission_objectives_00018_1F56482': [('Fallshore City', 'Città di Fallshore')],
    'tbl_mission_objectives_00019_1F564B6': [('Fallshore\nCity', 'Città di\nFallshore')],
    'tbl_mission_objectives_00032_1F56717': [('Dehara City', 'Città di Dehara')],
    'scr_1F0DE88': [(' Coins', ' Gettoni')], 'scr_1F0DE9F': [(' Coins', ' Gettoni')],
    'scr_1F0DEB9': [(' Coins', ' Gettoni')], 'scr_1F0DEE8': [(' Coins', ' Gettoni')],
    'scr_1FA16E3': [('giovane [buffer1]', '[buffer1]')],
}
for i in ('scr_1F9E5F4', 'scr_1F9E745', 'scr_1F9E852', 'scr_1F9EA4F', 'scr_1FA2257'):
    REPL[i] = [('Black Ferrothorn', 'Ferrothorn Neri')]


def fits(x, final):
    size = len(ET.INJ.encode_text(ET.CM, final))
    fixed = bool(x.get('translated_fixed')) or not x.get('pointer_sources') or x.get('no_relocation') or x['category'] == 'pointer_texts'
    return not fixed or size <= int(x['byte_length'])


def extra(by):
    bad = 0
    for i, t in RAW.items():
        x = by[i]
        if not fits(x, t):
            print('NO', i, 'spazio fisso', repr(t))
            bad += 1
            continue
        x['translated'] = t
        if x.get('translated_fixed'):
            x['translated_fixed'] = t
        x['manual_fix'] = 'megacheck'
    for i in FIXBS:
        x = by[i]
        t = re.sub('(?<!' + re.escape(chr(92)) + ')' + re.escape(chr(92)) + '([0-9A-F]{2})', lambda m: BB + m.group(1), x['translated'])
        assert sorted(re.findall(re.escape(BB) + '([0-9A-F]{2})', t)) == sorted(re.findall(re.escape(BB) + '([0-9A-F]{2})', x['original'])), i
        x['translated'] = t
        x['manual_fix'] = 'megacheck'
    n = 0
    for x in by.values():
        if x['category'] == 'trainer_names' and x['original'].strip('"') in NAMES:
            t = NAMES[x['original'].strip('"')]
            if fits(x, t):
                x['translated'] = t
                if x.get('translated_fixed'):
                    x['translated_fixed'] = t
                x['manual_fix'] = 'megacheck'
                n += 1
    for i, pairs in REPL.items():
        x = by[i]
        t = x.get('translated_fixed') or x['translated']
        for a, b in pairs:
            if a in t:
                t = t.replace(a, b)
                continue
            # the words may be split by a line break: keep the break between the new words
            pa = '(' + ')('.join(re.escape(w) for w in a.split(' ')) + ')'
            pa = pa.replace(')(', ')(\\s+|' + re.escape(chr(92)) + 'l)(')
            wb = b.split(' ')
            assert re.search(pa, t) and len(wb) == 2, (i, a)
            t = re.sub(pa, lambda m: wb[0] + m.group(2) + wb[1], t)
        if not fits(x, t):
            print('NO', i, 'spazio fisso', repr(t))
            bad += 1
            continue
        x['translated'] = t
        if x.get('translated_fixed'):
            x['translated_fixed'] = t
        x['manual_fix'] = 'megacheck'
    print(f'megacheck: grezzi {len(RAW)} | segnaposti {len(FIXBS)} | nomi allenatori {n} | sostituzioni {len(REPL)} | da rivedere {bad}')
    flex(by)


# v7: player addressed in the masculine -> neutral. Whole text is flattened, edited and wrapped again.
FLEX = {
    'scr_19F217': [('Sei stato a pescare?', 'Hai provato a pescare?')],
    'scr_1A5B4A': [('sei un vero amico!', 'sei un tesoro!')],
    'scr_753675': [('Sei sceso dalla montagna?', 'Vieni giù dalla montagna?')],
    'scr_1F61AC4': [('Sei sceso dalla montagna?', 'Vieni giù dalla montagna?')],
    'scr_1EE3151': [('Sei tornato!', 'Eccoti di nuovo!')],
    'scr_1EFC612': [('se sei riuscito ad arrivare', 'se hai potuto arrivare')],
    'scr_1EFC6F4': [('se sei riuscito ad arrivare', 'se hai potuto arrivare')],
    'scr_1F49264': [('da dove sei venuto!', 'da dove vieni!')],
    'scr_1F9E3FB': [('da dove sei venuto!', 'da dove vieni!')],
    'scr_1F86991': [('quello che sei venuto a fare', 'quello per cui sei qui')],
    'scr_1F877ED': [('alla fine sei arrivato,', 'alla fine eccoti qui,')],
    'scr_1F9E745': [('Sei arrivato giusto in tempo,', 'Arrivi giusto in tempo,')],
    'scr_1F9F3A3': [('Sei pronto a riprovarci,', 'Te la senti di riprovarci,')],
    'scr_1F7C123': [('sei un vero campione.', 'hai la stoffa del campione.')],
    'scr_1F5405D': [('che tu sia venuto fin qui!', 'di vederti qui!')],
    'scr_1F540CF': [('Sono commosso che tu sia venuto fin qui,', 'Mi commuove vederti qui,')],
    'scr_1F4D924': [('che sei venuto qui', 'che sei qui')],
    'scr_1EF4CFC': [('sei disposto a separarti', 'vuoi separarti')],
    'scr_1EF4F91': [('sei disposto a cedere', 'vuoi cedere')],
    'scr_1EF83B9': [("sei un vero maestro dell{B4}allevamento.", "l{B4}allevamento non ha più segreti per te.")],
    'scr_1EF84A1': [("sei un vero maestro dell{B4}allevamento.", "l{B4}allevamento non ha più segreti per te.")],
    'scr_1F98B99': [('se sei interessato a fare acquisti', 'se ti interessa fare acquisti')],
    'scr_1F740D9': [('sarai sicuro di ottenere', 'otterrai di sicuro')],
    'scr_1F823C3': [('Sarai il nuovo arrivato nella nostra sfida giornaliera?', 'Vuoi partecipare alla nostra sfida giornaliera?')],
    'scr_1FA6CEC': [('Quel ragazzo sembra terribilmente familiare', 'Quella faccia mi sembra terribilmente familiare'),
                    ('sei quel piccolo teppista che si è immischiato', 'sei quella peste che si è immischiata'),
                    ('sei andato a disturbare i miei ragazzi', 'hai dato fastidio ai miei ragazzi')],
    'scr_1F33067': [('un [buffer1] che esce', 'qualcuno che esce'), ('sei stato rapito?', 'ti hanno rapito?')],
}
FLEX_DROP = {'scr_1F33067'}


def flex(by):
    BSL = chr(92)
    ok = bad = 0
    for i, pairs in FLEX.items():
        x = by[i]
        orig = x['original'].strip('"')
        cur = x.get('translated_fixed') or x['translated']
        flat = cur.replace(BSL + 'p', '¶').replace('\n\n', '¶').replace('\n', ' ').replace(BSL + 'l', ' ')
        flat = re.sub(' *¶ *', '¶', re.sub('  +', ' ', flat))
        for a, b in pairs:
            pat = r'\s*'.join(re.escape(w) for w in a.split(' '))
            pat = pat.replace(r'\s*', r'[ ¶]+')
            assert re.search(pat, flat), (i, a)
            flat = re.sub(pat, lambda m: b, flat, count=1)
        final, W = ET.layout(flat, orig)
        p = []
        tf, to = collections.Counter(ET.tokens(final)), collections.Counter(ET.tokens(orig))
        if (tf - to) if i in FLEX_DROP else (tf != to):
            p.append(f'token {dict(tf)} / {dict(to)}')
        if any(ET.px(l.strip()) > W for l in ET.BREAKS.split(final) if l.strip()) and ET.BREAKS.search(orig.rstrip()):
            p.append('riga troppo larga')
        if x.get('translated_fixed') or not x.get('pointer_sources'):
            p.append('spazio fisso')
        if p:
            bad += 1
            print('NO', i, '; '.join(p), repr(final))
            continue
        x['translated'] = final
        x['manual_fix'] = 'v7-neutral'
        ok += 1
    print(f'forme neutre: {ok} ok, {bad} da rivedere')


def main(src, dst):
    d = json.load(open(src, encoding='utf-8'))
    by = {x['id']: x for x in d['entries']}
    bad = 0
    for i, t in FRAG.items():
        by[i]['translated'] = t
        by[i]['manual_fix'] = 'pronoun-fix'
    for i, text in T.items():
        x = by[i]
        orig = x['original'].strip('"')
        final, Wd = ET.layout(text, orig)
        p = []
        if i in DROP:
            if collections.Counter(ET.tokens(final)) - collections.Counter(ET.tokens(orig)):
                p.append(f'token in più {ET.tokens(final)} / {ET.tokens(orig)}')
        elif ET.tokens(final) != ET.tokens(orig):
            p.append(f'token {ET.tokens(final)} != {ET.tokens(orig)}')
        back = ET.decode_pcs(ET.INJ.encode_text(ET.CM, final), 0, 4096).text
        if ET.norm_rt(back) != ET.norm_rt(final):
            p.append(f'carattere non codificabile: {back!r}')
        if any(ET.px(l.strip()) > Wd for l in ET.BREAKS.split(final) if l.strip()):
            p.append('riga troppo larga')
        if x.get('translated_fixed') or not x.get('pointer_sources'):
            p.append('spazio fisso')
        if p:
            bad += 1
            print('NO', i, '; '.join(p), repr(final))
            continue
        x['translated'] = final
        x['manual_fix'] = 'pronoun-fix'
    extra(by)
    json.dump(d, open(dst, 'w', encoding='utf-8'), ensure_ascii=False)
    print(f'frammenti {len(FRAG)} | dialoghi {len(T) - bad} ok, {bad} da rivedere')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
