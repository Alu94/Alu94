#!/usr/bin/env python3
"""
REGISTRAZIONE SETTIMANALE TEMPERATURE
Genera/aggiorna il file HTML mensile delle temperature frigo/freezer.
Viene eseguito ogni giorno dal runner giornaliero (run_daily.py).
"""

import os
import json
import random
from datetime import date, datetime, timedelta
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
        return dati  # già compilato

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
        riga = dati.get(chiave)

        if riga:
            data_str   = riga["data"]
            orario_str = riga["orario"]
            celle_temp = "".join(
                f'<td class="temp">{riga["temperature"].get(str(f["numero"]), "")}</td>'
                for f in FRIGHI
            )
            firma_cell = '<td class="firma"></td>'
            note_cell  = '<td class="note"></td>'
        else:
            data_str   = giorno.strftime("%d/%m/%Y")
            orario_str = ""
            celle_temp = "".join('<td class="temp future"></td>' for _ in FRIGHI)
            firma_cell = '<td class="firma"></td>'
            note_cell  = '<td class="note"></td>'

        righe_html += f"""
        <tr>
            <td class="data">{data_str}</td>
            <td class="orario">{orario_str}</td>
            {celle_temp}
            {firma_cell}
            {note_cell}
        </tr>"""

    # Intestazioni frighi
    intestazioni = ""
    for f in FRIGHI:
        intestazioni += f"""
            <th class="frigo-header">
                <div class="frigo-nome">{f['nome']}</div>
                <div class="frigo-pos">{f['posizione']}</div>
                <div class="frigo-rif">Temp rif. {f['temp_rif']}</div>
            </th>"""

    html = f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Registrazione Temperature - {nome_mese} {anno}</title>
<style>
  @page {{
    size: A4 landscape;
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
    margin-bottom: 6px;
  }}
  .header-azienda .nome {{
    font-size: 11pt;
    font-weight: bold;
    text-transform: uppercase;
  }}
  .header-azienda .sottotitolo {{
    font-size: 8pt;
    font-style: italic;
  }}
  .doc-info {{
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: 4px;
  }}
  .doc-info .mod {{ font-size: 7pt; color: #555; }}
  .titolo-tabella {{
    font-size: 12pt;
    font-weight: bold;
    text-align: center;
    text-transform: uppercase;
    border: 2px solid #000;
    padding: 4px;
    margin-bottom: 6px;
    letter-spacing: 1px;
  }}
  .mese-anno {{
    text-align: center;
    font-size: 9pt;
    font-weight: bold;
    margin-bottom: 8px;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
  }}
  th, td {{
    border: 1px solid #333;
    padding: 2px 1px;
    text-align: center;
    vertical-align: middle;
  }}
  th {{
    background-color: #d0e4f7;
    font-weight: bold;
  }}
  .frigo-header {{
    width: 8%;
  }}
  .frigo-nome {{ font-size: 6.5pt; font-weight: bold; }}
  .frigo-pos  {{ font-size: 5.5pt; color: #333; }}
  .frigo-rif  {{ font-size: 5.5pt; color: #c00; font-weight: bold; }}
  .col-data   {{ width: 7%; }}
  .col-orario {{ width: 5%; }}
  .col-firma  {{ width: 7%; }}
  .col-note   {{ width: 9%; }}
  td.data     {{ font-size: 7pt; font-weight: bold; }}
  td.orario   {{ font-size: 7pt; }}
  td.temp     {{ font-size: 7.5pt; font-weight: bold; color: #1a5276; }}
  td.future   {{ background: #f9f9f9; }}
  td.firma    {{ background: #fffde7; }}
  td.note     {{ background: #fff8f8; font-size: 6pt; text-align: left; padding: 1px 2px; }}
  .note-footer {{
    margin-top: 8px;
    font-size: 6.5pt;
    color: #333;
    border-top: 1px solid #999;
    padding-top: 4px;
  }}
  @media print {{
    body {{ font-size: 7pt; }}
    .no-print {{ display: none; }}
    table {{ page-break-inside: avoid; }}
    tr {{ page-break-inside: avoid; }}
  }}
  .btn-stampa {{
    display: inline-block;
    margin: 10px 0;
    padding: 8px 20px;
    background: #1a5276;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 10pt;
  }}
</style>
</head>
<body>

<div class="no-print" style="text-align:center; padding: 8px;">
  <button class="btn-stampa" onclick="window.print()">🖨️ Stampa / Salva PDF</button>
</div>

<div class="header-azienda">
  <div class="nome">Villaggio Hotel &amp; Appartamenti "Holiday in Gardan"</div>
  <div class="sottotitolo">Piano Autocontrollo Igienico Sanitario</div>
</div>

<div class="doc-info">
  <span class="mod">Mod. 10</span>
  <span></span>
</div>

<div class="titolo-tabella">Registrazione Settimanale Temperature</div>
<div class="mese-anno">{nome_mese} {anno}</div>

<table>
  <colgroup>
    <col class="col-data">
    <col class="col-orario">
    {"".join('<col class="col-frigo">' for _ in FRIGHI)}
    <col class="col-firma">
    <col class="col-note">
  </colgroup>
  <thead>
    <tr>
      <th rowspan="2" class="col-data">DATA</th>
      <th rowspan="2" class="col-orario">ORA</th>
      {intestazioni}
      <th rowspan="2" class="col-firma">FIRMA</th>
      <th rowspan="2" class="col-note">Note in caso di<br>superamento valori limite (*)</th>
    </tr>
    <tr><!-- seconda riga header già occupata da rowspan --></tr>
  </thead>
  <tbody>
    {righe_html}
  </tbody>
</table>

<div class="note-footer">
  (*) Istruzione al personale / riparazione / sostituzione apparecchio / regolazione del refrigeratore / eventuale smaltimento dei cibi<br>
  NB. Sono possibili limitati e brevi rialzi termici incidentali (max +3°C). In tal caso si verificherà la qualità delle materie prime e si procederà ad apposita taratura.<br>
  <br>
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

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Carica dati esistenti e aggiunge il giorno odierno
    dati = carica_dati()
    dati = aggiungi_giorno(dati, data_target)
    salva_dati(dati)

    # Filtra solo i dati del mese corrente (per chiarezza nell'HTML)
    # ma passa tutti i dati: la funzione HTML accede solo al mese/anno richiesto
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
        # es: python generate_temperature.py 2026-05-25
        d = date.fromisoformat(sys.argv[1])
        main(d)
    else:
        main()
