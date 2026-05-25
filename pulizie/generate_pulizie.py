#!/usr/bin/env python3
"""
CONTROLLO PULIZIA LOCALI E ATTREZZATURE  (All. A - Mod. 07)
Genera/aggiorna il file HTML mensile del modulo pulizie.
- Pulizie giornaliere  : compilate con la data, FIRMA lasciata vuota
- Pulizie settimanali  : 6 giorni feriali distribuiti nel mese
- Pulizie mensili      : 3 giorni feriali diversi da quelli settimanali
- Pulizie trimestrali  : 1 giorno ogni trimestre (mesi 3-6-9-12)
- A inizio mese viene creato automaticamente un nuovo file
"""

import os
import json
import calendar
from datetime import date, datetime, timedelta

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output", "pulizie")
DATA_FILE  = os.path.join(os.path.dirname(__file__), "..", "output", "pulizie", "data.json")

MESI_IT = ["", "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
           "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]

# ─── Calcolo giorni feriali ───────────────────────────────────────────────────

def giorni_feriali_mese(anno: int, mese: int) -> list[int]:
    """Restituisce lista di numeri-giorno (1..31) che sono Lun-Ven"""
    num_giorni = calendar.monthrange(anno, mese)[1]
    feriali = []
    for g in range(1, num_giorni + 1):
        d = date(anno, mese, g)
        if d.weekday() < 5:  # 0=Lun .. 4=Ven
            feriali.append(g)
    return feriali

def distribuisci_giorni(feriali: list[int], quanti: int, escludi: list[int] = None) -> list[int]:
    """
    Seleziona 'quanti' giorni feriali distribuiti uniformemente nel mese,
    escludendo quelli già scelti (escludi).
    """
    if escludi is None:
        escludi = []
    candidati = [g for g in feriali if g not in escludi]
    if quanti >= len(candidati):
        return sorted(candidati)

    # Distribuzione uniforme: divide i candidati in 'quanti' fasce
    step = len(candidati) / quanti
    scelti = []
    for i in range(quanti):
        idx = int(i * step + step / 2)
        idx = min(idx, len(candidati) - 1)
        scelti.append(candidati[idx])
    return sorted(scelti)

def giorno_trimestrale(anno: int, mese: int, feriali: list[int]) -> int | None:
    """Restituisce 1 giorno solo nei mesi di fine trimestre (3,6,9,12)"""
    if mese not in (3, 6, 9, 12):
        return None
    # Terza settimana: cerca un feriale intorno al giorno 15-18
    preferiti = [g for g in feriali if 14 <= g <= 20]
    return preferiti[0] if preferiti else (feriali[len(feriali)//2] if feriali else None)

# ─── Carica / salva dati ──────────────────────────────────────────────────────

def carica_dati() -> dict:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salva_dati(dati: dict):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(dati, f, indent=2, ensure_ascii=False)

def chiave_mese(anno: int, mese: int) -> str:
    return f"{anno}-{mese:02d}"

def calcola_piano_mese(anno: int, mese: int) -> dict:
    """
    Calcola il piano pulizie per un intero mese e lo restituisce come dict.
    Il piano NON cambia una volta calcolato (viene salvato in data.json).
    """
    feriali = giorni_feriali_mese(anno, mese)

    settimanali = distribuisci_giorni(feriali, 6)
    mensili     = distribuisci_giorni(feriali, 3, escludi=settimanali)
    trimestrale = giorno_trimestrale(anno, mese, feriali)

    num_giorni = calendar.monthrange(anno, mese)[1]
    tutti_giorni = list(range(1, num_giorni + 1))

    return {
        "anno": anno,
        "mese": mese,
        "tutti_giorni":  tutti_giorni,
        "settimanali":   settimanali,
        "mensili":       mensili,
        "trimestrale":   trimestrale,
    }

# ─── Generazione HTML ─────────────────────────────────────────────────────────

def _celle_giorni_giornalieri(tutti_giorni: list[int], anno: int, mese: int) -> str:
    """
    Per le pulizie giornaliere: genera la tabella 2-colonne con tutti i giorni del mese.
    Firma lasciata vuota.
    """
    righe = ""
    meta = (len(tutti_giorni) + 1) // 2
    sinistra = tutti_giorni[:meta]
    destra   = tutti_giorni[meta:]

    for i, g in enumerate(sinistra):
        d_sx = date(anno, mese, g)
        str_sx = f"{g:02d}/{mese:02d}"
        if i < len(destra):
            g_dx  = destra[i]
            d_dx  = date(anno, mese, g_dx)
            str_dx = f"{g_dx:02d}/{mese:02d}"
        else:
            str_dx = ""

        righe += f"""
        <tr>
          <td class="g-data">{str_sx}</td>
          <td class="g-firma"></td>
          <td class="g-note"></td>
          <td class="g-sep"></td>
          <td class="g-data">{str_dx}</td>
          <td class="g-firma"></td>
          <td class="g-note"></td>
        </tr>"""
    return righe

def _celle_pulizie_speciali(giorni: list[int], anno: int, mese: int, max_righe: int) -> str:
    """
    Per settimanali/mensili/trimestrali: mostra solo i giorni scelti,
    in formato 2-colonne, le firme vuote.
    """
    meta = (len(giorni) + 1) // 2
    sinistra = giorni[:meta]
    destra   = giorni[meta:]

    # Padding fino a max_righe
    while len(sinistra) < max_righe:
        sinistra.append(None)
    while len(destra) < max_righe:
        destra.append(None)

    righe = ""
    for i in range(max_righe):
        g_sx = sinistra[i]
        g_dx = destra[i]

        str_sx = f"{g_sx:02d}/{mese:02d}" if g_sx else ""
        str_dx = f"{g_dx:02d}/{mese:02d}" if g_dx else ""

        righe += f"""
        <tr>
          <td class="g-data">{str_sx}</td>
          <td class="g-firma"></td>
          <td class="g-note"></td>
          <td class="g-sep"></td>
          <td class="g-data">{str_dx}</td>
          <td class="g-firma"></td>
          <td class="g-note"></td>
        </tr>"""
    return righe

def genera_html(piano: dict) -> str:
    anno  = piano["anno"]
    mese  = piano["mese"]
    nome_mese = MESI_IT[mese]

    tutti_giorni = piano["tutti_giorni"]
    settimanali  = piano["settimanali"]
    mensili      = piano["mensili"]
    trimestrale  = piano["trimestrale"]

    # Celle giornaliere
    gg_rows = _celle_giorni_giornalieri(tutti_giorni, anno, mese)

    # Celle settimanali (6 giorni → 3 per colonna)
    sw_rows = _celle_pulizie_speciali(settimanali, anno, mese, max_righe=3)

    # Celle mensili (3 giorni → 2+1)
    sm_rows = _celle_pulizie_speciali(mensili, anno, mese, max_righe=2)

    # Celle trimestrali (1 giorno)
    tr_giorni = [trimestrale] if trimestrale else []
    st_rows   = _celle_pulizie_speciali(tr_giorni, anno, mese, max_righe=1)

    html = f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<title>Controllo Pulizia Locali - {nome_mese} {anno}</title>
<style>
  @page {{
    size: A4 portrait;
    margin: 10mm 8mm;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: Arial, sans-serif;
    font-size: 7.5pt;
    color: #000;
    background: #fff;
  }}
  .header-azienda {{
    text-align: center;
    margin-bottom: 4px;
  }}
  .header-azienda .nome {{
    font-size: 10pt;
    font-weight: bold;
    text-transform: uppercase;
  }}
  .header-azienda .sottotitolo {{ font-size: 7.5pt; font-style: italic; }}
  .doc-info {{
    display: flex;
    justify-content: space-between;
    font-size: 7pt;
    color: #555;
    margin-bottom: 3px;
  }}
  .titolo-tabella {{
    font-size: 11pt;
    font-weight: bold;
    text-align: center;
    text-transform: uppercase;
    border: 2px solid #000;
    padding: 3px;
    margin-bottom: 3px;
    letter-spacing: 0.5px;
  }}
  .mese-info {{
    text-align: center;
    font-size: 9pt;
    font-weight: bold;
    margin-bottom: 6px;
  }}

  /* Sezioni */
  .sezione {{
    margin-bottom: 8px;
    page-break-inside: avoid;
  }}
  .sezione-titolo {{
    font-size: 8pt;
    font-weight: bold;
    background: #1a5276;
    color: white;
    padding: 3px 5px;
    margin-bottom: 0;
  }}
  .sezione-descr {{
    font-size: 6pt;
    background: #eaf2ff;
    border: 1px solid #aac;
    border-top: none;
    padding: 3px 5px;
    line-height: 1.4;
    margin-bottom: 0;
  }}

  /* Tabelle */
  table {{
    width: 100%;
    border-collapse: collapse;
  }}
  th, td {{
    border: 1px solid #555;
    padding: 2px 3px;
    text-align: center;
    vertical-align: middle;
  }}
  th {{
    background: #d0e4f7;
    font-size: 6.5pt;
    font-weight: bold;
  }}
  .g-data  {{ width: 11%; font-weight: bold; font-size: 7pt; }}
  .g-firma {{ width: 22%; background: #fffde7; }}
  .g-note  {{ width: 16%; background: #fff8f8; }}
  .g-sep   {{ width: 2%; border: none; background: #fff; }}

  .footer-haccp {{
    margin-top: 8px;
    font-size: 6pt;
    color: #555;
    border-top: 1px solid #999;
    padding-top: 3px;
    text-align: center;
  }}

  .no-print {{ }}
  .btn-stampa {{
    display: inline-block;
    margin: 8px 0;
    padding: 6px 18px;
    background: #1a5276;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 10pt;
  }}
  @media print {{
    .no-print {{ display: none; }}
    .sezione {{ page-break-inside: avoid; }}
  }}
</style>
</head>
<body>

<div class="no-print" style="text-align:center; padding:6px;">
  <button class="btn-stampa" onclick="window.print()">🖨️ Stampa / Salva PDF</button>
</div>

<div class="header-azienda">
  <div class="nome">Villaggio Hotel &amp; Appartamenti "Holiday in Gardan"</div>
  <div class="sottotitolo">Piano Autocontrollo Igienico Sanitario</div>
</div>

<div class="doc-info">
  <span>All. A - Mod. 07</span>
  <span>Mese: <strong>{nome_mese}</strong> &nbsp; Anno: <strong>{anno}</strong></span>
</div>

<div class="titolo-tabella">Controllo Pulizia Locali e Attrezzature</div>

<!-- ════════════════════════════════════════════════
     PULIZIE GIORNALIERE
════════════════════════════════════════════════ -->
<div class="sezione">
  <div class="sezione-titolo">📅 PULIZIE GIORNALIERE</div>
  <div class="sezione-descr">
    <strong>CUCINA:</strong> pavimenti, lavelli e vasche, coltelli e utensili, superfici di lavoro, affettatrici, taglieri (lavare con detergente neutro e disinfettare con igienizzante). Piastre di cottura (lavare con detergente neutro fortemente tensioattivo e a basso potere schiumogeno).
    <strong>MAGAZZINO:</strong> pavimenti (lavare con detergente neutro e disinfettare con igienizzante).
    <strong>BAR:</strong> Vetrinette (lavare con detergente a base alcolica). Erogatori di bevande (lavare i beccucci con detergente neutro e disinfettare con igienizzante).
    <strong>SALA:</strong> Vetrinette (lavare con detergente a base alcolica). Erogatori delle bevande (lavare i beccucci con detergente neutro e disinfettare con igienizzante).
    <strong>SERVIZI IGIENICI:</strong> pavimenti, cestini, specchi, rubinetti, mensole, sanitari (lavare e disinfettare con igienizzante).
  </div>
  <table>
    <thead>
      <tr>
        <th>Giorno</th><th>Firma Addetto</th><th>Note</th>
        <th class="g-sep"></th>
        <th>Giorno</th><th>Firma Addetto</th><th>Note</th>
      </tr>
    </thead>
    <tbody>
      {gg_rows}
    </tbody>
  </table>
</div>

<!-- ════════════════════════════════════════════════
     PULIZIE SETTIMANALI
════════════════════════════════════════════════ -->
<div class="sezione">
  <div class="sezione-titolo">📆 PULIZIE SETTIMANALI</div>
  <div class="sezione-descr">
    <strong>CUCINA:</strong> cappe aspiranti e frigoriferi (lavare e disinfettare con igienizzante). Pareti lavabili, armadi, ripiani, sottotavoli, scaffali, maniglie, porte (lavare e disinfettare con igienizzante). Friggitrice (lavare con detergente ad alto potere sgrassante). Cassetti (riordinare e detergere).
    <strong>BAR - SALA:</strong> frigoriferi (lavare e disinfettare con igienizzante). Vani portaposate e scaldapiatti.
    <strong>MAGAZZINO:</strong> scaffali, maniglie, porte, pareti (lavare e disinfettare con igienizzante).
    <strong>SERVIZI IGIENICI:</strong> rubinetterie e sanitari (disincrostare con disincrostante acido). Pareti piastrellate (lavare e disinfettare con igienizzante).
  </div>
  <table>
    <thead>
      <tr>
        <th>Giorno</th><th>Firma Addetto</th><th>Note</th>
        <th class="g-sep"></th>
        <th>Giorno</th><th>Firma Addetto</th><th>Note</th>
      </tr>
    </thead>
    <tbody>
      {sw_rows}
    </tbody>
  </table>
</div>

<!-- ════════════════════════════════════════════════
     PULIZIE MENSILI
════════════════════════════════════════════════ -->
<div class="sezione">
  <div class="sezione-titolo">🗓️ PULIZIE MENSILI</div>
  <div class="sezione-descr">
    <strong>CUCINA:</strong> compressori, radiatori, soffitto e pareti (detergente a base alcolica).
    <strong>MAGAZZINO:</strong> ripiani del magazzino (detergente a base alcolica), soffitto e pareti.
    <strong>SERVIZI IGIENICI:</strong> Vetri (detergente a base alcolica). Plafoniere (lavare e disinfettare con igienizzante).
  </div>
  <table>
    <thead>
      <tr>
        <th>Giorno</th><th>Firma Addetto</th><th>Note</th>
        <th class="g-sep"></th>
        <th>Giorno</th><th>Firma Addetto</th><th>Note</th>
      </tr>
    </thead>
    <tbody>
      {sm_rows}
    </tbody>
  </table>
</div>

<!-- ════════════════════════════════════════════════
     PULIZIE TRIMESTRALI
════════════════════════════════════════════════ -->
<div class="sezione">
  <div class="sezione-titolo">📋 PULIZIE TRIMESTRALI</div>
  <div class="sezione-descr">
    <strong>TUTTE LE AREE:</strong> derattizzazione e deblattizzazione (ev. effettuata da ditte specializzate). Monitoraggio derattizzazione.
    {f"<em>(Prevista per questo mese: {trimestrale:02d}/{mese:02d}/{anno})</em>" if trimestrale else "<em>(Non prevista questo mese)</em>"}
  </div>
  <table>
    <thead>
      <tr>
        <th>Giorno</th><th>Firma Addetto</th><th>Note</th>
        <th class="g-sep"></th>
        <th>Giorno</th><th>Firma Addetto</th><th>Note</th>
      </tr>
    </thead>
    <tbody>
      {st_rows}
    </tbody>
  </table>
</div>

<!-- ════════════════════════════════════════════════
     VERIFICA BIMENSILE RESPONSABILE HACCP
════════════════════════════════════════════════ -->
<div class="sezione">
  <div class="sezione-titolo">✅ VERIFICA BIMENSILE STATO DI PULIZIA — Responsabile HACCP</div>
  <table>
    <thead>
      <tr>
        <th style="width:20%">Giorno</th>
        <th style="width:35%">Firma Resp. HACCP</th>
        <th>Intervento correttivo</th>
        <th style="width:35%">Firma Resp. HACCP</th>
        <th>Intervento correttivo</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td></td><td style="background:#fffde7;height:18px;"></td><td></td>
        <td style="background:#fffde7;"></td><td></td>
      </tr>
    </tbody>
  </table>
</div>

<div class="footer-haccp">
  Servizio e controllo HACCP realizzato in collaborazione con: <strong>TS SICUREZZA S.r.l. - Trento</strong>
</div>

</body>
</html>"""
    return html

# ─── Entry point ─────────────────────────────────────────────────────────────

def main(data_target: date = None):
    if data_target is None:
        data_target = date.today()

    anno  = data_target.year
    mese  = data_target.month
    k     = chiave_mese(anno, mese)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    dati = carica_dati()

    # Se il piano del mese non è ancora stato calcolato, lo calcola e salva
    if k not in dati:
        piano = calcola_piano_mese(anno, mese)
        dati[k] = piano
        salva_dati(dati)
        print(f"[Pulizie] 📅 Nuovo piano mese creato per {MESI_IT[mese]} {anno}")
    else:
        piano = dati[k]

    html = genera_html(piano)

    nome_file = f"pulizie_{anno}_{mese:02d}_{MESI_IT[mese]}.html"
    percorso  = os.path.join(OUTPUT_DIR, nome_file)
    with open(percorso, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[Pulizie] ✅ Aggiornato: {percorso}")
    return percorso

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        d = date.fromisoformat(sys.argv[1])
        main(d)
    else:
        main()
