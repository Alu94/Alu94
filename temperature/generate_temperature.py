#!/usr/bin/env python3
"""
REGISTRAZIONE GIORNALIERA TEMPERATURE
Genera/aggiorna il file HTML mensile delle temperature frigo/freezer.
Viene eseguito ogni giorno dal runner giornaliero (run_daily.py).
"""

import os
import json
import random
from datetime import date
import calendar

# ─── Configurazione frighi ────────────────────────────────────────────────────
FRIGHI = [
    {"numero": 1,  "nome": "Frigo n°1",          "posizione": "Bar",              "tipo": "frigo",   "temp_rif": "+4/6°C"},
    {"numero": 2,  "nome": "Frigo n°2",           "posizione": "Vetrina Sala/Bar", "tipo": "frigo",   "temp_rif": "+4/6°C"},
    {"numero": 3,  "nome": "Frigo n°3",           "posizione": "Vetrina Servizio", "tipo": "frigo",   "temp_rif": "+4/6°C"},
    {"numero": 4,  "nome": "Freezer n°4",         "posizione": "Cucina",           "tipo": "freezer", "temp_rif": "-16/-18°C"},
    {"numero": 5,  "nome": "Frigo Grande n°5",    "posizione": "Cucina",           "tipo": "frigo",   "temp_rif": "+4/6°C"},
    {"numero": 6,  "nome": "Frigo Piccolo n°6",   "posizione": "Cucina",           "tipo": "frigo",   "temp_rif": "+4/6°C"},
    {"numero": 7,  "nome": "Freezer n°7",         "posizione": "Magazzino",        "tipo": "freezer", "temp_rif": "-16/-18°C"},
    {"numero": 8,  "nome": "Freezer n°8",         "posizione": "Magazzino",        "tipo": "freezer", "temp_rif": "-16/-18°C"},
    {"numero": 9,  "nome": "Freezer n°9",         "posizione": "Magazzino",        "tipo": "freezer", "temp_rif": "-16/-18°C"},
    {"numero": 10, "nome": "Frigo n°10",          "posizione": "Magazzino",        "tipo": "frigo",   "temp_rif": "+4/6°C"},
]

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output", "temperature")
DATA_FILE  = os.path.join(os.path.dirname(__file__), "..", "output", "temperature", "data.json")

MESI_IT = ["", "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
           "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]

# ─── Generazione temperatura casuale ─────────────────────────────────────────

def genera_temperatura(tipo: str) -> str:
    if tipo == "frigo":
        temp = round(random.uniform(4.0, 6.0), 1)
        return f"+{temp}"
    else:  # freezer
        temp = round(random.uniform(16.0, 18.0), 1)
        return f"-{temp}"

def genera_orario() -> str:
    """Orario casuale tra 08:00 e 10:30"""
    minuti_totali = random.randint(8 * 60, 10 * 60 + 30)
    ore = minuti_totali // 60
    minuti = minuti_totali % 60
    return f"{ore:02d}:{minuti:02d}"

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

# ─── Aggiunta riga del giorno ─────────────────────────────────────────────────

def aggiungi_giorno(dati: dict, giorno: date) -> dict:
    chiave = giorno.isoformat()
    if chiave in dati:
        return dati  # già compilato oggi

    riga = {
        "data":    giorno.strftime("%d/%m/%Y"),
        "orario":  genera_orario(),
        "temperature": {
            str(f["numero"]): genera_temperatura(f["tipo"]) for f in FRIGHI
        }
    }
    dati[chiave] = riga
    return dati

# ─── Generazione HTML ─────────────────────────────────────────────────────────

def genera_html(anno: int, mese: int, dati: dict) -> str:
    nome_mese = MESI_IT[mese]
    num_giorni = calendar.monthrange(anno, mese)[1]

    # Costruisce le righe della tabella
    righe_html = ""
    for giorno_n in range(1, num_giorni + 1):
        giorno = date(anno, mese, giorno_n)
        chiave = giorno.isoformat()
        riga   = dati.get(chiave)

        if riga:
            data_str   = riga["data"]
            orario_str = riga["orario"]
            celle_temp = "".join(
                f'<td class="temp">{riga["temperature"].get(str(f["numero"]), "")}</td>'
                for f in FRIGHI
            )
        else:
            data_str   = giorno.strftime("%d/%m/%Y")
            orario_str = ""
            celle_temp = "".join('<td class="temp vuoto"></td>' for _ in FRIGHI)

        righe_html += f"""<tr>
            <td class="data">{data_str}</td>
            <td class="orario">{orario_str}</td>
            {celle_temp}
            <td class="firma"></td>
            <td class="note"></td>
          </tr>"""

    # Intestazioni frighi (compatte)
    intestazioni = ""
    for f in FRIGHI:
        intestazioni += f"""<th class="frigo-header">
            <span class="fn">{f['nome']}</span><br>
            <span class="fp">{f['posizione']}</span><br>
            <span class="fr">{f['temp_rif']}</span>
          </th>"""

    html = f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<title>Temperature - {nome_mese} {anno}</title>
<style>
  @page {{
    size: A4 landscape;
    margin: 6mm 5mm;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: Arial, sans-serif;
    font-size: 6pt;
    color: #000;
    background: #fff;
  }}

  /* Intestazione azienda */
  .hdr {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1mm;
  }}
  .hdr-centro {{ text-align: center; flex: 1; }}
  .hdr-nome {{
    font-size: 9pt;
    font-weight: bold;
    text-transform: uppercase;
    line-height: 1.2;
  }}
  .hdr-sub {{ font-size: 6pt; font-style: italic; color: #333; }}
  .hdr-mod  {{ font-size: 6pt; color: #666; white-space: nowrap; }}

  /* Titolo */
  .titolo {{
    font-size: 9pt;
    font-weight: bold;
    text-align: center;
    text-transform: uppercase;
    border: 1.5px solid #000;
    padding: 1.5mm 2mm;
    margin: 1mm 0;
    letter-spacing: 0.5px;
  }}
  .mese-anno {{
    text-align: center;
    font-size: 7.5pt;
    font-weight: bold;
    margin-bottom: 1.5mm;
  }}

  /* Tabella */
  table {{
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
  }}
  th, td {{
    border: 0.4pt solid #444;
    padding: 0.4mm 0.3mm;
    text-align: center;
    vertical-align: middle;
    line-height: 1.1;
  }}
  thead th {{
    background: #cfe2f3;
    font-size: 5.5pt;
  }}
  .frigo-header {{ width: 7.6%; }}
  .fn {{ font-size: 5.5pt; font-weight: bold; display: block; }}
  .fp {{ font-size: 4.5pt; color: #333; display: block; }}
  .fr {{ font-size: 4.5pt; color: #900; font-weight: bold; display: block; }}

  .col-data   {{ width: 6%; }}
  .col-ora    {{ width: 4.5%; }}
  .col-firma  {{ width: 6%; }}
  .col-note   {{ width: 7%; }}

  tbody tr {{ height: 4.8mm; }}
  tbody tr:nth-child(even) {{ background: #f7fbff; }}

  td.data   {{ font-size: 6pt; font-weight: bold; }}
  td.orario {{ font-size: 6pt; }}
  td.temp   {{ font-size: 6.5pt; font-weight: bold; color: #154360; }}
  td.vuoto  {{ background: #fafafa; }}
  td.firma  {{ background: #fffde7; }}
  td.note   {{ background: #fff8f8; font-size: 5pt; }}

  /* Footer note */
  .footer {{
    margin-top: 1mm;
    font-size: 5pt;
    color: #444;
    border-top: 0.4pt solid #999;
    padding-top: 0.8mm;
    line-height: 1.4;
  }}

  /* Bottone stampa (solo schermo) */
  @media screen {{
    .btn-wrap {{ text-align: center; padding: 6px; }}
    .btn-stampa {{
      padding: 7px 20px;
      background: #154360;
      color: #fff;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 10pt;
    }}
  }}
  @media print {{
    .btn-wrap {{ display: none; }}
    body {{ font-size: 6pt; }}
  }}
</style>
</head>
<body>

<div class="btn-wrap">
  <button class="btn-stampa" onclick="window.print()">🖨️ Stampa / Salva PDF</button>
</div>

<div class="hdr">
  <span class="hdr-mod">Mod. 10</span>
  <div class="hdr-centro">
    <div class="hdr-nome">Villaggio Hotel &amp; Appartamenti "Holiday in Gardan"</div>
    <div class="hdr-sub">Piano Autocontrollo Igienico Sanitario</div>
  </div>
  <span class="hdr-mod">&nbsp;</span>
</div>

<div class="titolo">Registrazione Giornaliera Temperature</div>
<div class="mese-anno">{nome_mese} {anno}</div>

<table>
  <thead>
    <tr>
      <th class="col-data">DATA</th>
      <th class="col-ora">ORA</th>
      {intestazioni}
      <th class="col-firma">FIRMA</th>
      <th class="col-note">Note superamento<br>valori limite (*)</th>
    </tr>
  </thead>
  <tbody>
    {righe_html}
  </tbody>
</table>

<div class="footer">
  (*) Istruzione al personale / riparazione / sostituzione apparecchio / regolazione del refrigeratore / eventuale smaltimento dei cibi &nbsp;|&nbsp;
  NB. Sono possibili limitati e brevi rialzi termici incidentali (max +3°C). &nbsp;|&nbsp;
  Servizio e controllo HACCP: <strong>TS SICUREZZA S.r.l. - Trento</strong>
</div>

</body>
</html>"""
    return html

# ─── Entry point ─────────────────────────────────────────────────────────────

def main(data_target: date = None):
    if data_target is None:
        data_target = date.today()

    anno = data_target.year
    mese = data_target.month

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    dati = carica_dati()
    dati = aggiungi_giorno(dati, data_target)
    salva_dati(dati)

    html = genera_html(anno, mese, dati)

    nome_file = f"temperature_{anno}_{mese:02d}.html"
    percorso  = os.path.join(OUTPUT_DIR, nome_file)
    with open(percorso, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[Temperature] ✅ Aggiornato: {percorso}")
    return percorso

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        d = date.fromisoformat(sys.argv[1])
        main(d)
    else:
        main()
