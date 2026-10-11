# Pokémon Unbound — traduzione italiana rivista

Patch italiana **rivista e corretta** per **Pokémon Unbound**, costruita sulla traduzione di
[Simopich/unbound-translator](https://github.com/Simopich/unbound-translator) (patch italiana del 9/9/2026).
Tutto il merito degli strumenti e della prima traduzione va a quel progetto: qui c'è una revisione completa del testo
italiano, fatta giocando su PSP (ARK-5 + TempGBA) e confrontando i testi con quelli ufficiali di Pokémon Rosso Fuoco.

> [!IMPORTANT]
> Questa repository **non contiene la ROM** del gioco. Serve la ROM inglese di Pokémon Unbound con
> MD5 `9cad8e771940e7f7094d13911552cef0`. Non pubblicare ROM o salvataggi.

> [!NOTE]
> La revisione è stata fatta con l'aiuto di un'intelligenza artificiale (Claude), con controlli automatici su tutta la
> ROM e prove in gioco. È una **beta**: se trovi testi strani, apri una segnalazione (Issues).

## Come si installa

1. Scarica [`patch/pokemon-unbound-ita-v7.bps`](patch/pokemon-unbound-ita-v7.bps).
2. Applicala alla ROM **inglese originale** di Unbound (non a una ROM già patchata) con un programma per patch BPS,
   per esempio [Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/) (dal browser) o Flips.
3. Risultato atteso: MD5 `c0b3574868d68f9be0c9be5f8148e30c`, CRC32 `71677A18`.

## Posso continuare la mia partita? Sì

**I salvataggi funzionano con tutte le versioni**: quelli della versione inglese, della patch originale di Simopich e
di tutte le versioni precedenti di questa patch (v4, v5, v6). La patch cambia solo testi e grafica, non i dati di
gioco: il file di salvataggio (`.sav`) non viene toccato e resta compatibile.

Per aggiornare:

1. **Salva dal menu del gioco** (non solo con il salvataggio rapido dell'emulatore).
2. Fai una copia di sicurezza del file `.sav`.
3. Sostituisci la ROM vecchia con quella nuova **tenendo lo stesso nome del file**, così l'emulatore trova lo stesso
   salvataggio.
4. Avvia e carica la partita dal menu del gioco.

> [!WARNING]
> I **save state** dell'emulatore (salvataggi rapidi, es. `.svs`, `.ss0`) fotografano la memoria della ROM vecchia:
> caricati con la nuova possono mostrare testi vecchi o dare problemi. Usa il salvataggio normale del gioco per
> passare da una versione all'altra, poi rifai i save state.

Su PSP con TempGBA: imposta l'aggiornamento del salvataggio su automatico (opzione di backup "Auto"), altrimenti il
`.sav` viene scritto solo quando esci dall'emulatore e spegnendo la console si perde la partita.

## Novità della v7

**Testi inglesi rimasti**
- **Allenatori**: circa 70 frasi di sfida e di sconfitta comparivano ancora in inglese anche se erano tradotte (il gioco
  le raggiungeva da un secondo comando di script mai aggiornato). Corretti oltre 700 riferimenti di questo tipo.
- Oltre 80 testi mai estratti tradotti: "Jack found TM94" → "Jack trova MT94", oggetti trovati/ricevuti, Gigamax,
  tempesta di sabbia, grandine, messaggi degli strumenti ("non tiene nessuno strumento", "I PP sono aumentati"…),
  regole del Battle Frontier ("on/off", "be able"), stati curati in lotta (sleep, poison… → sonno, avvelenamento…),
  parole inserite nei dialoghi (stagioni, soprannomi, titoli del Battle Frontier), ingredienti delle ricette.
- Nomi che restavano in inglese per mancanza di spazio, ora spostati: Gran Mo, Ciprian, Yarrow, "Ragazza",
  Grandi Magazzini di Dehara, Provocazione, Inibitore.

**Riquadri e impaginazione**
- **Testi degli Allenatori sovrapposti** all'inizio della lotta: il messaggio scorre da solo e le righe finivano una
  sopra l'altra. Ora ogni riquadro ha al massimo due righe (566 testi).
- Circa 680 testi senza a capo che uscivano dal riquadro, reimpaginati.
- Cartelli stradali con una direzione per riga, elenchi dei piani e delle bacche di nuovo in colonna.

**Correzioni**
- Messaggi delle statistiche: "sale di molto! sale!" → "sale di molto!" (correzione nel codice del gioco).
- Pokédex in unità metriche: altezza in metri e peso in kg.
- Grafica: icone di stato (VLN, PAR, DRM, GEL, BRU, KO), ESP, PS, "B Esci", PRESENTA.
- Revisione con più controlli automatici e rilettura: circa 450 correzioni tra cui frasi rivolte al protagonista rese
  neutre (vale per ragazzo e ragazza: "Ti do il benvenuto" invece di "Benvenuto"), messaggi di lotta con i nomi
  invertiti, nomi ufficiali di mosse e Pokémon (Fiordifesa, Fletchindr…), errori di senso e di grammatica.

## Cosa cambiava già nelle versioni precedenti

- Terminologia dei giochi ufficiali (Palestra, Capopalestra, Medaglia, Superquattro, MT/MN…) e 875 testi sostituiti
  con il testo ufficiale di Rosso Fuoco.
- Nomi di personaggi e luoghi di Unbound coerenti ovunque (Zefiro, Avorio, Ciprian, Gran Mo…).
- Messaggi di lotta con codici o nomi ripetuti, testi fuori dai riquadri, ~1.340 testi inglesi tradotti.
- Pronomi del protagonista ("Prendi lui!" → "Prendilo!/Prendila!") e parole inserite con il genere sbagliato.
- ~4.000 dialoghi riscritti in italiano naturale (slang resta slang, nessuna volgarità aggiunta).

## Limiti noti

- Restano in inglese: i nomi delle mosse Z, parole della Chiacchierata facile e decorazioni della base segreta
  (funzioni di Rosso Fuoco non usate da Unbound), il logo grafico della Torre Lotta.
- Alcune frasi usano articoli davanti a nomi inseriti dal gioco (es. "un [strumento]"): l'accordo non è sempre giusto.
- Non tutta la storia è stata giocata con questa versione: segnalazioni benvenute.

## Contenuto della repository

| Percorso | Cosa è |
|---|---|
| `patch/` | patch BPS da applicare alla ROM inglese |
| `translation/it.json` | traduzione completa (formato di `unbound-translator`, dopo tutte le correzioni testuali) |
| `tools/` | script della revisione, da mettere in `out/` di `unbound-translator`: `build_v7.sh` (build completa), `pronoun_fix.py`, `v7_apply.py` + `v7_batches/` (testi aggiunti e corretti), `v7_gfx.py` (grafica), `v7_code.py` (Pokédex metrico, messaggi statistiche), controlli `megacheck*.py`, `romscan2.py`, `trainer_scan.py`, `check_fixes.py` |

Ricostruire la ROM dalla repository originale (con i file di `tools/` in `out/`):

```bash
python 005_hybrid_injector.py rom/unbound.gba translation/it.json -o out/x-it.gba --target-lang it --reclaim-script-slots --fail-on-no-space
python out/v7_gfx.py out/x-it.gba out/x-gfx.gba
python out/v7_code.py out/x-gfx.gba out/unbound-ita.gba
```

## Crediti

- [Simopich/unbound-translator](https://github.com/Simopich/unbound-translator) — strumenti di estrazione,
  traduzione e iniezione, e traduzione italiana di partenza (licenza MIT).
- Team di Pokémon Unbound (Skeli e collaboratori) per il gioco.
- Testi ufficiali italiani di Pokémon Rosso Fuoco usati come riferimento per la terminologia.

Pokémon, Pokémon Unbound, Rosso Fuoco, Nintendo, Game Freak e i nomi correlati appartengono ai rispettivi proprietari.
Progetto amatoriale non ufficiale, non affiliato né approvato da loro.

---

## English

Revised and corrected **Italian** patch for Pokémon Unbound, built on top of the Italian translation of
[Simopich/unbound-translator](https://github.com/Simopich/unbound-translator). Apply
`patch/pokemon-unbound-ita-v7.bps` to the clean English ROM (MD5 `9cad8e771940e7f7094d13911552cef0`).

**Saves are compatible** with the English game, the original Simopich patch and every earlier version of this patch:
only text and graphics change. Save in-game, keep the same ROM file name, and load from the in-game menu; emulator
save states from an older ROM may show old text, so don't use them across versions.

v7 fixes ~70 trainer lines that were still shown in English, 80+ never-extracted English strings, overlapping trainer
intro text, ~680 text box overflows, the "rose sharply! rose!" stat message, metric Pokédex units, status icons and
~450 proofreading fixes (gender-neutral player lines, official move/Pokémon names). Revision made with AI assistance
(Claude) and automated checks over the whole ROM; beta quality. No ROM is distributed. MIT License, original
copyright kept.
