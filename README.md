# Programmi e codici in python per spike prime
## Gome Neve FLL Team - Scuola Ladina di Fassa
## Uso:
- Installare git, Visual Studio Code (o qualsiasi editor di codice che supporti le medesemime estensioni) e le estensioni necessarie (lego spike prime, python)
- Clonare questa repo col comando 'git clone __https://github.com/Nicepawer7/gome-neve-spike__'
- Modificare i file e aggiornare la repo coi comandi'git commit -a -m "__descrizione della modifica effettuata__" ' e 'git push origin main' e accedere con l'account di un contributor su github
- Per motivi di memoria sono stati rimmossi i comenti dalla branch __main__, per leggerli è necessario aprire la branch __con_commenti__ e aprire il file necessario.
## Missioni da Fare:

### Da Fare/concludere:

### Possibilmente da sistemare: 

## To-do list:
- [x] Controllare i parametri e i valori nella funzione 'calcoloPID()' 
- [x] Testare il funzionamento della funzione 'ottieniDistanzaCompiuta()'
- [x] Creare il programma di raccoglimento dei dati
- [x] Testare il funzionamento di tutti i metodi della classe 'Movimenti' tramite gli appositi file di test
- [X] Rimuovere commenti per efficentare memoria
- [X] Rendere più intutitvo lo stato della missione (numeri display,X quando non annullabile,direzione ecc..)
- [X] Aggiungere la possibilità di fermare l'esecuzione della singola missione e ripartire

## Idee:
- ~~Calibrare il pid con il metodo Zieger-Nichols~~ (scartato)
- ~~gestione bottone con threading~~ non supportato
- aggiungere gestione async del bottone
- controllo anti-blocco vaidrittoPID()
- multi file per migliore modularità
- Microaggiustamenti in base alla batteria (8300-8000 mV)
- Aggiungere sistema di accelerazione/decelerazione
- Migliorare l'efficacia e la precisione delle curve
- Migliorare il PID per permettere al robot di andare più veloce
- Finire la funzione del machine learning

## Note di sviluppo/ info-source:
- https://tuftsceeo.github.io/SPIKEPythonDocs/SPIKE2.html#top
- https://libdoc.fh-zwickau.de/opus4/frontdoor/deliver/index/docId/15400/file/lego_spike_linux.pdf
- https://github.com/smr99/lego-hub-tk
