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
- [X] IMPLEMENTARE LE COSE DI CIRO FATTE A META DIO CA + -Finire Accelerazione-Decelerazione PID
- [X] rimuovere color sensor e metterlo in un altro file
- [ ] Testare il PID e ricalibrato
- [ ] Se i test in laboratorio risultano positivi fare il merge con main
- [ ] Sistemare la documentazione

- [ ] 
- [ ] Capire dov'è il Massachussets

## Idee:
- strutturare tutto a moduli e pacchetti, migliore modularita e leggibilità (innit,ecc)
-  Alleggerire i moduli importati (es: from hub import motion_sensor)
- grafici per osservare andamento pid
- aggiungere gestione async del bottone
- aggiungere exit con bottone centrale
- controllo anti-blocco vaidrittoPID()
- Microaggiustamenti in base alla batteria (8300-8000 mV)
- Finire la funzione del machine learning
- ~~Calibrare il pid con il metodo Zieger-Nichols~~ scartato
- ~~gestione bottone con threading~~ non supportato
-  ~~approfondire il simulatore dell' hardware Spike~~ outdated e non funzionante
- ~~Pid con dt~~ (time non funziona con i decimi di secondo)
- ~~Sistemare wait con time.time()~~ (-/)

## Note di sviluppo/ info-source:
- https://tuftsceeo.github.io/SPIKEPythonDocs/SPIKE2.html#top
- https://libdoc.fh-zwickau.de/opus4/frontdoor/deliver/index/docId/15400/file/lego_spike_linux.pdf
- https://github.com/smr99/lego-hub-tk
- https://github.com/gpdaniels/spike-prime simulatore hardware spike e firmware
- https://matplotlib.org/stable/ libreria per i grafici
