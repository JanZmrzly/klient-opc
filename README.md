# OPC UA klient v jazyku python Python

OPC UA klient byl vytvořen v rámci bakalářské práce VUT v Brně.

## Popis projektu

Cílem projektu bylo vytvoření OPC UA klineta v programovacím jazyku Python. Projekt je postavený na základech na knihovny [FreeOpcUa](https://github.com/FreeOpcUa).
Práce je zaměřena na možnosti využití jazyku Python pro datovou komunikaci prostřednictvím protokolu OPC UA. Je uvažována komunikace mezi PC a PLC, kdy na straně PLC je aktivován (vestavěný) OPC UA server, na straně PC je vytvořen OPC UA klient. V rámci práce byly nastudovány základní informace o protokolu OPC UA, dále naprogramována jednoduchá testovací aplikaci na straně PLC a provedena konfiguraci OPC UA serveru. Jádrem práce bylo vytvoření jednoduchého OPC UA klienta pro PC v jazyku Python. Klient je schopen připojit se k PLC a číst hodnoty zpřístupněných proměnných.

## Obsah

* Instalace potřebných knihoven etc.
* Spuštění aplikace
* Náhled uživatelského rozhraní
* Užitečné odkazy
## Instalace potřebných knihoven etc.

Pro Windows OS:

```bash
python3 -m pip install -r base.txt
```

Pro Mac OS:

```bash
python -m pip install -r base.txt
```

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
## Náhled uživatelského rozhraní


![Náhled](https://github.com/JanZmrzly/klient-opc/blob/main/ua_client_final_preview_r.jpg)

## Licence

[GNU General Public License v3.0](https://github.com/JanZmrzly/klient-opc/blob/main/LICENCE.txt)

## Užitečné odkazy

* [text_bakalářské_práce](https://www.vutbr.cz/studenti/zav-prace/detail/139739)
* [FreeOpcUa](https://github.com/FreeOpcUa)
* [vut_brno](https://www.vut.cz/)
