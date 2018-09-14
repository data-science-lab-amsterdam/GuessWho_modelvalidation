# Big Data Expo 2018 - Guess Who game

### How to run the game:

#### Voorbereiding
* clone de repository in een offline beschikbare plek (dus geen cloudmap oid!)
* `git clone http://git.datasciencelab.nl/intern/Expo2018.git`
* `cd Expo2018`
* maak een nieuwe python 3.6 omgeving aan
* `conda create -n expo2018 python=3.6`
* `source activate expo2018`
* installeer de requirements
* `pip install -r requirements.txt`

#### Opstarten
* Verbind 2 laptops dmv een netwerk en zorg dat je de map `./data` (binnen de projectmap) geshared hebt. Laptop 2 moet bestanden van Laptop 1 in deze gedeelde folder kunnen lezen.
* Laptop 1
    * Verbind met scherm 1
    * Start PhotoBooth app (op een Mac)
    * Start het rsync-script (verwijzingen zouden bij standaard mac instellingen moeten kloppen: folder A: photo booth map en folder B: de shared folder. Code 23 error komt voor. Check dus even of nieuwe fotos inderdaad van A naar B gaan.)
    * `bash src/stream_fotos.sh`
    * Start de controlepagina
    * `python src/controlpage/app.py`
    * Open http://127.0.0.1:8050/ in je browser
* Laptop 2
    * Verbind met scherm 2
    * Start het andere synchronisatiescript:
    * python src/sync_checked_faces.py
    * Start het spel
    * `python src/game/dash-app.py`
    * Open http://127.0.0.1:8123/ in je browser

#### Spelen
* Bij laptop 1:
    * Persoon komt in de Photo booth
    * Maak een foto met de PhotoBooth app (foto komt op scherm)
    * Switch naar het browserwindow met de controlepagina
    * Klik op de 'Update'-knop linksbovenin
    * Selecteer de foto (laatste 10 staan in de pulldown)
    * Klik op de 'Start analyse'-knop
    * Voer een naam in (dring aan op niet meer dan 10 karakters svp !)
    * Pas de classificaties aan waar ze niet kloppen
    * Klik op 'Opslaan'
* Bij laptop 2:
    * Persoon komt bij het spel
    * Refresh het spel
    * Klik op de 'Update'-knop linkbovenin (refreshed de onlangs genomen fotos) en kies een foto/karakter voor de speler
    * Start de game, doorloop even de uitleg en spelen maar!

