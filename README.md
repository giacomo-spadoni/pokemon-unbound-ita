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

1. Scarica [`patch/pokemon-unbound-ita-v6.bps`](patch/pokemon-unbound-ita-v6.bps).
2. Applicala alla ROM inglese di Unbound con un programma per patch BPS, per esempio
   [Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/) (dal browser) o Flips.
3. Risultato atteso: MD5 `27798867a171ded20ea0d022feacd4f5`, CRC32 `39379493`.

I salvataggi in gioco (`.sav`) restano compatibili con la versione inglese e con le versioni precedenti della patch.
I salvataggi rapidi dell'emulatore (save state) invece possono dare problemi tra versioni diverse: prima di cambiare
patch, salva dal menu del gioco.

## Cosa cambia rispetto alla patch originale

**Terminologia ufficiale**
- Termini come nei giochi italiani: Palestra, Capopalestra, Allenatore, Medaglia, Superquattro, Campione, Bacche, MT/MN…
- 875 testi (mosse, strumenti, messaggi di lotta) sostituiti con il **testo ufficiale di Rosso Fuoco**.
- Nomi dei personaggi e dei luoghi di Unbound coerenti ovunque, anche nelle lotte (prima comparivano ancora
  Zeph, Ivory, Marlon, Big Mo… mentre nei dialoghi erano Zefiro, Avorio, Ciprian, Gran Mo…).

**Errori corretti**
- Nome del Pokémon ripetuto in testa ai messaggi di lotta ("PikachuLa Dif. di Pikachu…"), possessivo inglese "’s".
- Messaggi di lotta con codici al posto dei nomi ("0F è tornato da 23!").
- Testi che uscivano dai riquadri: descrizioni di mosse, strumenti, Pokédex, 57 abilità.
- ~1.340 testi rimasti in inglese tradotti dentro lo spazio originale.
- **Pronomi del protagonista**: il gioco inserisce "him/her" da una tabella a parte, e l'italiano diventava
  "Prendi lui!", "portare lui qui", "la mamma di suo". Ora escono "Prendilo!/Prendila!" ecc., corretti per
  protagonista maschio e femmina (oltre 30 frasi, tra cui la scena iniziale nel laboratorio).
- Altre parole inserite a runtime con il genere sbagliato ("la mia figlio", "al signora che mi ha aiutato").

**Dialoghi rivisti**
- ~4.000 dialoghi riscritti in italiano naturale, trama compresa: niente frasi tradotte alla lettera, personaggi con la
  loro personalità (slang resta slang, le parolacce hanno la stessa intensità dell'inglese, nessuna aggiunta).
- Forme neutre per il protagonista dove possibile.

## Limiti noti

- Restano in inglese: parole della Chiacchierata facile, decorazioni della base segreta, nomi delle mosse Z, alcune
  liste di Rosso Fuoco non usate da Unbound, e 3 nomi in spazi troppo piccoli.
- Alcune frasi usano articoli davanti a nomi inseriti dal gioco (es. "un [strumento]"): l'accordo non è sempre giusto.
- Non tutta la storia è stata giocata con questa versione: segnalazioni benvenute.

## Contenuto della repository

| Percorso | Cosa è |
|---|---|
| `patch/` | patch BPS da applicare alla ROM inglese |
| `translation/it.json` | traduzione completa nel formato di `unbound-translator` (si può iniettare con i suoi strumenti) |
| `tools/` | script usati per la revisione (da mettere in `out/` di `unbound-translator`): `dlg_tools.py` (revisione dialoghi), `pronoun_fix.py` (pronomi e correzioni finali), `megacheck.py` (controllo automatico sulla ROM), `build.sh`, `verify2.py` |

Ricostruire la ROM dalla repository originale:

```bash
python tools/pronoun_fix.py translation/it.json out/it-final.json   # (già applicato in it.json)
python 005_hybrid_injector.py rom/unbound.gba out/it-final.json -o out/unbound-ita.gba --target-lang it --reclaim-script-slots --fail-on-no-space
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
[Simopich/unbound-translator](https://github.com/Simopich/unbound-translator). It applies to the English ROM
(MD5 `9cad8e771940e7f7094d13911552cef0`) and fixes terminology (official FireRed Italian text), battle message bugs,
text box overflows, gendered pronoun substitutions, untranslated trainer names, and rewrites ~4,000 dialogues in
natural Italian. Revision made with AI assistance (Claude) and automated checks over the whole ROM; beta quality.
No ROM is distributed. MIT License, original copyright kept.
