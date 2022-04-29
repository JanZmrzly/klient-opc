# OPC UA klient v jazyku python Python

OPC UA klient byl vytvořen v rámci bakalářské práce VUT v Brně.

## Popis projektu

Cílem projektu bylo vytvoření OPC UA klineta v programovacím jazyku Python. Projekt je postavený na základech na knihovny [FreeOpcUa](https://github.com/FreeOpcUa).
Práce je zaměřena na možnosti využití jazyku Python pro datovou komunikaci prostřednictvím protokolu OPC UA. Je uvažována komunikace mezi PC a PLC, kdy na straně PLC je aktivován (vestavěný) OPC UA server, na straně PC je vytvořen OPC UA klient. Student v rámci práce nastuduje základní informace o protokolu OPC UA, dále naprogramuje jednoduchou testovací aplikaci na straně PLC a provede konfiguraci OPC UA serveru. Jádrem práce bude vytvoření jednoduchého OPC UA klienta pro PC v jazyku Python. Klient by měl být schopen připojit se PLC a číst hodnoty zpřístupněných proměnných.

## Obsah

* Instalace potřebných knihoven etc.
* Spuštění aplikace
* Jak projekt používat
* Užitečné odkazy
## Instalace potřebných knihoven etc.

#TODO: Doplnit, vytvorit base.txt

## Spuštění aplikace

Aplikace se spouští pomocí následujícího příkazu:

Pro Windows OS:

```bash
python3 start_application.py
```

Pro Mac OS:

```bash
python start_application.py
```
## Jak projekt používat

![Náhled]()

## Užitečné odkazy

* [text_baklářské_práce](https://www.vutbr.cz/studenti/zav-prace/detail/139739)
* [FreeOpcUa](https://github.com/FreeOpcUa)
* [VUT_BRNO](https://www.vut.cz/)