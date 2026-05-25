#!/usr/bin/env python3
"""
RUN DAILY — Runner giornaliero
Esegui questo script ogni giorno (es. con cron o GitHub Actions).
Aggiorna automaticamente:
  1. La tabella temperature del mese corrente
  2. Il modulo pulizie del mese corrente

Utilizzo:
  python run_daily.py                # usa la data di oggi
  python run_daily.py 2026-05-25     # usa una data specifica (per test)
"""

import sys
import os
from datetime import date

# Aggiunge le cartelle dei moduli al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "temperature"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pulizie"))

import generate_temperature
import generate_pulizie

def main():
    if len(sys.argv) > 1:
        try:
            data_target = date.fromisoformat(sys.argv[1])
        except ValueError:
            print(f"❌ Data non valida: {sys.argv[1]}. Formato atteso: YYYY-MM-DD")
            sys.exit(1)
    else:
        data_target = date.today()

    print(f"\n{'='*60}")
    print(f"  🏨  Holiday in Gardan — Autocompilazione HACCP")
    print(f"  📅  Data: {data_target.strftime('%d/%m/%Y')}")
    print(f"{'='*60}\n")

    # 1. Temperature
    try:
        percorso_temp = generate_temperature.main(data_target)
        print(f"  ✅ Temperature: {percorso_temp}")
    except Exception as e:
        print(f"  ❌ Errore temperature: {e}")

    # 2. Pulizie
    try:
        percorso_pul = generate_pulizie.main(data_target)
        print(f"  ✅ Pulizie: {percorso_pul}")
    except Exception as e:
        print(f"  ❌ Errore pulizie: {e}")

    print(f"\n{'='*60}")
    print("  💡 Apri i file HTML in un browser e clicca 'Stampa'")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
