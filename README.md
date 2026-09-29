# auditus

*auditus, -us*: l'udito, l'atto dell'ascoltare.

Un corso pratico di acustica e audio per musicisti, costruito su un impianto
domestico reale: una scheda Steinberg UR22mkII, un microfono a condensatore,
due casse da scrivania e una chitarra. Ogni lezione unisce un po' di teoria e
una prova d'ascolto fatta con suoni generati al computer o registrati.

Prima si impara ad **ascoltare**, poi a **registrare**.

## Lezioni

| # | Titolo | Stato |
| --- | --- | --- |
| 1 | Il suono e l'orecchio | in corso |
| 2 | Ottimizzare l'ascolto | da fare |
| 3 | I numeri del suono: dB, dBFS, frequenza di campionamento, bit | da fare |
| 4 | Ascoltare in modo critico | da fare |

Seguirà una seconda parte sulla registrazione: microfoni, ripresa della
chitarra acustica, voce e chitarra, ritocchi, esportazione.

Ogni lezione ha una cartella in `lezioni/` con lo script che genera i suoni di
prova:

```
cd lezioni/01_suono_e_orecchio
python3 genera_suoni.py
aplay suoni/01_la_110.wav
```

## Ascoltare

Siamo su Linux: i file si ascoltano con `aplay` (pacchetto `alsa-utils`),
da terminale, senza aprire lettori pesanti.

```
aplay suoni/01_la_110.wav                  # attraverso PulseAudio: il modo normale
aplay -l                                   # elenca le schede e i loro numeri
```

Tutti i suoni di una lezione, uno dopo l'altro:

```
for f in suoni/*.wav; do echo "$f"; aplay -q "$f"; done
```

Senza `-D` il suono passa da PulseAudio, che lo manda all'uscita predefinita e
lo mescola con quello che sta già suonando (il browser, Spotify). Ctrl+C
interrompe l'ascolto.

`aplay -D plughw:1,0 file.wav` scavalca PulseAudio e parla direttamente con la
scheda 1: funziona solo se nient'altro la sta usando, altrimenti risponde
`Device or resource busy`.

## Strumenti

In `strumenti/`, per analizzare le proprie registrazioni:

| Script | A cosa serve |
| --- | --- |
| `livelli.py` | durata, picco e RMS in dBFS, campioni saturati |
| `accenti.py` | tempo, shuffle e accenti per movimento di una ritmica |
| `accordi.py` | accordi per mezza battuta, scelti tra quelli indicati |
| `midinfo.py` | tracce, strumenti, tempo e metrica di un file MIDI |

```
cd strumenti
python3 livelli.py registrazione.wav
python3 accenti.py strofa.wav --canale 2
python3 accordi.py brano.wav --accordi A,D7,E7,F#m,F
```

## Manualetto

`manualetto/` contiene la guida alla Steinberg UR22mkII su Linux (Debian,
PulseAudio, ALSA): pannello, collegamenti, guadagno, ascolto, comandi
`arecord`/`aplay`, problemi comuni, ordine sicuro per il +48V. Il PDF si
rigenera con:

```
python3 manualetto/manualetto_ur22.py
```

## Requisiti

Python 3, numpy e reportlab (pacchetti Debian `python3-numpy` e
`python3-reportlab`). Per l'ascolto basta `aplay` (alsa-utils).

## Licenza

MIT, vedi `LICENSE`.
