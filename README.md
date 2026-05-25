👋 Hi, I’m @Alu94!
👀 I’m interested in technology and Bitcoin.

---

# 🏨 Holiday in Gardan — Automazione HACCP

Sistema di autocompilazione dei moduli HACCP per:
1. **Registrazione Settimanale Temperature** (Mod. 10)
2. **Controllo Pulizia Locali e Attrezzature** (All. A - Mod. 07)

---

## 📁 Struttura Progetto

```
Alu94/
├── run_daily.py                  ← Runner giornaliero (da schedulare)
├── temperature/
│   └── generate_temperature.py  ← Genera tabella temperature
├── pulizie/
│   └── generate_pulizie.py      ← Genera modulo pulizie
└── output/
    ├── temperature/
    │   ├── data.json             ← Storico temperature salvate
    │   └── temperature_YYYY_MM.html  ← un file per mese
    └── pulizie/
        ├── data.json             ← Piano pulizie salvato
        └── pulizie_YYYY_MM_NomeMese.html  ← un file per mese
```

---

## 🚀 Come Usarlo

### Manuale (un giorno alla volta)
```bash
python run_daily.py              # oggi
python run_daily.py 2026-05-25   # data specifica
```

### Automatico — Cron (Linux/Mac)
Apri il crontab con `crontab -e` e aggiungi:
```
# Ogni giorno alle 07:00 del mattino
0 7 * * * cd /percorso/Alu94 && python3 run_daily.py >> /tmp/haccp.log 2>&1
```

### Automatico — Windows Task Scheduler
1. Apri **Utilità di pianificazione**
2. Crea attività → Trigger: ogni giorno alle 07:00
3. Azione: `python C:\percorso\Alu94\run_daily.py`

### Automatico — GitHub Actions (gratis, cloud)
Vedi `.github/workflows/daily.yml` — gira automaticamente ogni mattina alle 07:00
e fa il commit degli HTML aggiornati nel repository.

---

## 🖨️ Come Stampare

1. Apri il file HTML nel browser (Chrome, Firefox, Edge)
2. Clicca il pulsante **🖨️ Stampa / Salva PDF**
3. Per salvare come PDF: scegli "Salva come PDF" nella finestra di stampa

- Temperature → Formato A4 **orizzontale** (landscape)
- Pulizie → Formato A4 **verticale** (portrait)

---

## 🌡️ Frighi e Freezer

| N° | Nome | Posizione | Tipo | Temp. Rif. |
|----|------|-----------|------|------------|
| 1 | Frigo n°1 | Bar | Frigo | +4/6°C |
| 2 | Frigo n°2 | Vetrina Sala/Bar | Frigo | +4/6°C |
| 3 | Frigo n°3 | Vetrina Servizio | Frigo | +4/6°C |
| 4 | Freezer n°4 | Cucina | Freezer | -16/-18°C |
| 5 | Frigo Grande n°5 | Cucina | Frigo | +4/6°C |
| 6 | Frigo Piccolo n°6 | Cucina | Frigo | +4/6°C |
| 7 | Freezer n°7 | Magazzino | Freezer | -16/-18°C |
| 8 | Freezer n°8 | Magazzino | Freezer | -16/-18°C |
| 9 | Freezer n°9 | Magazzino | Freezer | -16/-18°C |
| 10 | Frigo n°10 | Magazzino | Frigo | +4/6°C |

---

## 📋 Logica Pulizie

| Tipo | Frequenza | Giorni nel mese | Regole |
|------|-----------|-----------------|--------|
| Giornaliere | Ogni giorno | Tutti | Solo firma vuota |
| Settimanali | 6 volte | Distribuiti | Solo feriali (Lun-Ven) |
| Mensili | 3 volte | Distribuiti | Feriali, diversi da settimanali |
| Trimestrali | 1 volta | Solo mesi 3/6/9/12 | Feriale |

---

## ⚙️ Requisiti

- Python 3.10+
- Nessuna libreria esterna richiesta (solo stdlib)

