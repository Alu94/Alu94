#!/usr/bin/env python3
"""
REGISTRAZIONE GIORNALIERA TEMPERATURE
Genera/aggiorna il file HTML mensile delle temperature frigo/freezer.
Viene eseguito ogni giorno dal runner giornaliero (run_daily.py).
"""

import os
import json
import random
from datetime import date, timedelta
import calendar

# ─── Configurazione frighi ────────────────────────────────────────────────────
FRIGHI = [
    {"numero": 1,  "nome": "Frigo n°1",          "posizione": "Bar",              "tipo": "frigo",   "t_min": 4.0,  "t_max": 6.0,  "temp_rif": "+4/6°C"},
    {"numero": 2,  "nome": "Frigo n°2",           "posizione": "Vetrina Sala/Bar", "tipo": "frigo",   "t_min": 4.0,  "t_max": 6.0,  "temp_rif": "+4/6°C"},
    {"numero": 3,  "nome": "Frigo n°3",           "posizione": "Vetrina Servizio", "tipo": "frigo",   "t_min": 4.0,  "t_max": 6.0,  "temp_rif": "+4/6°C"},
    {"numero": 4,  "nome": "Freezer n°4",         "posizione": "Cucina",           "tipo": "freezer", "t_min": 15.0, "t_max": 17.0, "temp_rif": "-15/-17°C"},
    {"numero": 5,  "nome": "Frigo Grande n°5",    "posizione": "Cucina",           "tipo": "frigo",   "t_min": 4.0,  "t_max": 6.0,  "temp_rif": "+4/6°C"},
    {"numero": 6,  "nome": "Frigo Piccolo n°6",   "posizione": "Cucina",           "tipo": "frigo",   "t_min": 4.0,  "t_max": 6.0,  "temp_rif": "+4/6°C"},
    {"numero": 7,  "nome": "Freezer n°7",         "posizione": "Magazzino",        "tipo": "freezer", "t_min": 16.0, "t_max": 18.0, "temp_rif": "-16/-18°C"},
    {"numero": 8,  "nome": "Freezer n°8",         "posizione": "Magazzino",        "tipo": "freezer", "t_min": 18.0, "t_max": 22.0, "temp_rif": "-18/-22°C"},
    {"numero": 9,  "nome": "Freezer n°9",         "posizione": "Magazzino",        "tipo": "freezer", "t_min": 16.0, "t_max": 18.0, "temp_rif": "-16/-18°C"},
    {"numero": 10, "nome": "Frigo n°10",          "posizione": "Magazzino",        "tipo": "frigo",   "t_min": 4.0,  "t_max": 6.0,  "temp_rif": "+4/6°C"},
]

# ─── Periodi di apertura hotel ────────────────────────────────────────────────
PERIODI_APERTURA = [
    (date(2025,  4,  1), date(2025, 11, 16)),  # stagione estiva 2025
    (date(2025, 12,  5), date(2025, 12,  8)),  # ponte dicembre
    (date(2025, 12, 12), date(2025, 12, 15)),
    (date(2025, 12, 19), date(2025, 12, 21)),
    (date(2025, 12, 26), date(2026,  1, 13)),  # festività capodanno
    (date(2026,  1, 23), date(2026,  1, 26)),
    (date(2026,  2,  1), date(2026,  2,  8)),
    (date(2026,  2, 13), date(2026,  2, 15)),
    (date(2026,  3, 13), date(2026, 12, 31)),  # stagione 2026
]

def hotel_aperto(giorno: date) -> bool:
    return any(inizio <= giorno <= fine for inizio, fine in PERIODI_APERTURA)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output", "temperature")
DATA_FILE  = os.path.join(os.path.dirname(__file__), "..", "output", "temperature", "data.json")

MESI_IT = ["", "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
           "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]

# ─── Generazione temperatura casuale ─────────────────────────────────────────

def genera_temperatura(frigo: dict) -> str:
    temp = round(random.uniform(frigo["t_min"], frigo["t_max"]), 1)
    if frigo["tipo"] == "frigo":
        return f"+{temp}"
    else:
        return f"-{temp}"

def genera_orario() -> str:
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

    if not hotel_aperto(giorno):
        return dati  # hotel chiuso: riga resta vuota

    riga = {
        "data":    giorno.strftime("%d/%m/%Y"),
        "orario":  genera_orario(),
        "temperature": {
            str(f["numero"]): genera_temperatura(f) for f in FRIGHI
        }
    }
    dati[chiave] = riga
    return dati

# ─── Generazione HTML ─────────────────────────────────────────────────────────

def genera_html(anno: int, mese: int, dati: dict) -> str:
    nome_mese = MESI_IT[mese]
    num_giorni = calendar.monthrange(anno, mese)[1]

    righe_html = ""
    for giorno_n in range(1, num_giorni + 1):
        giorno = date(anno, mese, giorno_n)
        chiave = giorno.isoformat()
        riga   = dati.get(chiave)

        if riga:
            data_str   = riga["data"]
            orario_str = riga["orario"]
            celle_temp = "".join(
                f'<td class="temp" contenteditable="false" data-key="{chiave}" data-frigo="{f["numero"]}">{riga["temperature"].get(str(f["numero"]), "")}</td>'
                for f in FRIGHI
            )
            ora_attr = f'contenteditable="false" data-key="{chiave}" data-campo="orario"'
        else:
            data_str   = giorno.strftime("%d/%m/%Y")
            orario_str = ""
            celle_temp = "".join(
                f'<td class="temp vuoto" contenteditable="false" data-key="{chiave}" data-frigo="{f["numero"]}"></td>'
                for f in FRIGHI
            )
            ora_attr = f'contenteditable="false" data-key="{chiave}" data-campo="orario"'

        righe_html += f"""<tr>
            <td class="data">{data_str}</td>
            <td class="orario" {ora_attr}>{orario_str}</td>
            {celle_temp}
            <td class="firma"></td>
          </tr>"""

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
    overflow: hidden;
  }}
  thead th {{
    background: #cfe2f3;
    font-size: 5.5pt;
  }}
  .frigo-header {{ width: 7%; }}
  .fn {{ font-size: 5.5pt; font-weight: bold; display: block; }}
  .fp {{ font-size: 4.5pt; color: #333; display: block; }}
  .fr {{ font-size: 4.5pt; color: #900; font-weight: bold; display: block; }}

  .col-data  {{ width: 7%; }}
  .col-ora   {{ width: 5%; }}
  .col-firma {{ width: 18%; }}

  tbody tr {{ height: 4.8mm; }}
  tbody tr:nth-child(even) {{ background: #f7fbff; }}

  td.data   {{ font-size: 6pt; font-weight: bold; }}
  td.orario {{ font-size: 6pt; }}
  td.temp   {{ font-size: 6.5pt; font-weight: bold; color: #154360; }}
  td.vuoto  {{ background: #fafafa; }}
  td.firma  {{ background: #fffde7; }}

  .footer {{
    margin-top: 1mm;
    font-size: 5pt;
    color: #444;
    border-top: 0.4pt solid #999;
    padding-top: 0.8mm;
    line-height: 1.4;
  }}

  @media screen {{
    .btn-wrap {{
      text-align: center;
      padding: 6px;
      display: flex;
      justify-content: center;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .btn {{
      padding: 7px 18px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 10pt;
      font-weight: bold;
    }}
    .btn-stampa   {{ background: #154360; color: #fff; }}
    .btn-modifica {{ background: #e67e22; color: #fff; }}
    .btn-salva    {{ background: #27ae60; color: #fff; display: none; }}
    .btn-annulla  {{ background: #c0392b; color: #fff; display: none; }}

    body.edit-mode td[contenteditable="true"] {{
      background: #fff9e6 !important;
      outline: 1.5px dashed #e67e22;
      cursor: text;
    }}
    body.edit-mode td[contenteditable="true"]:focus {{
      background: #fffbe6 !important;
      outline: 2px solid #e67e22;
    }}
    .edit-banner {{
      display: none;
      background: #fef9e7;
      border: 1.5px solid #e67e22;
      color: #784212;
      font-size: 8.5pt;
      padding: 4px 10px;
      text-align: center;
      border-radius: 4px;
      margin: 4px 0;
    }}
    body.edit-mode .edit-banner {{ display: block; }}
  }}
  @media print {{
    .btn-wrap    {{ display: none; }}
    .edit-banner {{ display: none; }}
    body {{ font-size: 6pt; }}
    td[contenteditable] {{ outline: none !important; }}
    table {{ page-break-inside: avoid; }}
  }}
</style>
</head>
<body>

<div class="btn-wrap">
  <button class="btn btn-stampa"   onclick="window.print()">🖨️ Stampa / Salva PDF</button>
  <button class="btn btn-modifica" id="btnMod"     onclick="attivaModifica()">✏️ Modifica dati</button>
  <button class="btn btn-salva"    id="btnSalva"   onclick="salvaDati()">💾 Scarica dati aggiornati</button>
  <button class="btn btn-annulla"  id="btnAnnulla" onclick="location.reload()">✖ Annulla</button>
</div>
<div class="edit-banner">
  ✏️ <strong>Modalità modifica attiva</strong> — clicca su qualsiasi temperatura o orario per correggerlo.
  Quando hai finito clicca <strong>💾 Scarica dati aggiornati</strong> e carica il file <code>data.json</code> su GitHub in <code>output/temperature/</code>.
</div>

<script>
function attivaModifica() {{
  document.body.classList.add('edit-mode');
  document.querySelectorAll('td.temp, td.orario').forEach(function(td) {{
    td.setAttribute('contenteditable', 'true');
  }});
  document.getElementById('btnMod').style.display     = 'none';
  document.getElementById('btnSalva').style.display   = 'inline-block';
  document.getElementById('btnAnnulla').style.display = 'inline-block';
}}

function salvaDati() {{
  var dati = {{}};

  document.querySelectorAll('td.orario[data-key]').forEach(function(td) {{
    var k = td.dataset.key;
    if (!dati[k]) dati[k] = {{ data: '', orario: '', temperature: {{}} }};
    dati[k].orario = td.innerText.trim();
    dati[k].data   = td.previousElementSibling ? td.previousElementSibling.innerText.trim() : '';
  }});

  document.querySelectorAll('td.temp[data-key]').forEach(function(td) {{
    var k  = td.dataset.key;
    var fr = td.dataset.frigo;
    if (!dati[k]) dati[k] = {{ data: '', orario: '', temperature: {{}} }};
    if (!dati[k].temperature) dati[k].temperature = {{}};
    var val = td.innerText.trim();
    if (val) dati[k].temperature[fr] = val;
  }});

  var blob = new Blob([JSON.stringify(dati, null, 2)], {{type: 'application/json'}});
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'data.json';
  a.click();

  setTimeout(function() {{
    alert('✅ File data.json scaricato!\\n\\nOra vai su GitHub:\\ngithub.com/Alu94/haccp-holiday-gardan\\n→ output/temperature/data.json\\n→ ✏️ icona matita → incolla il contenuto → Commit\\n\\nDomani alle 07:00 il file HTML si aggiornerà.');
  }}, 500);
}}
</script>

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
    </tr>
  </thead>
  <tbody>
    {righe_html}
  </tbody>
</table>

<div class="footer">
  NB. Sono possibili limitati e brevi rialzi termici incidentali (max +3°C). &nbsp;|&nbsp;
  In caso di superamento: istruzione al personale / riparazione / regolazione / eventuale smaltimento alimenti. &nbsp;|&nbsp;
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

def regen_storico():
    """Rigenera tutto lo storico temperature dall'apertura stagione 2025 ad oggi."""
    print("[Regen] Inizio rigenerazione storico temperature...")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    inizio = date(2025, 4, 1)
    fine   = date.today()

    dati = {}
    giorno = inizio
    while giorno <= fine:
        dati = aggiungi_giorno(dati, giorno)
        giorno += timedelta(days=1)

    salva_dati(dati)
    print(f"[Regen] ✅ data.json: {len(dati)} giorni aperti salvati")

    mesi_generati = set()
    giorno = inizio
    while giorno <= fine:
        chiave_mese = (giorno.year, giorno.month)
        if chiave_mese not in mesi_generati:
            html = genera_html(giorno.year, giorno.month, dati)
            nome_file = f"temperature_{giorno.year}_{giorno.month:02d}.html"
            percorso  = os.path.join(OUTPUT_DIR, nome_file)
            with open(percorso, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"[Regen] ✅ {nome_file}")
            mesi_generati.add(chiave_mese)
        giorno += timedelta(days=1)

    print(f"[Regen] Completato: {len(mesi_generati)} file HTML generati")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "--regen":
            regen_storico()
        else:
            d = date.fromisoformat(sys.argv[1])
            main(d)
    else:
        main()
