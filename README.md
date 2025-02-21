# Programmi e codici in python per spike prime
## Gome Neve FLL Team - Scuola Ladina di Fassa
## Uso:
- Installare git, cursor e le estensioni necessarie (lego spike prime, python, codeStackr theme)
- Clonare questa repo col comando 'git clone'
- Modificare i file e aggiornare la repo coi comandi 'git add .' 'git commit -m "specificare modifica effettuata" ' 'git push origin main' e accedere con l'account di Ciro su github
## To-do list:
- [X] Calibrare il pid con il metodo Zieger-Nichols (scartato)
- [x] Controllare i parametri e i valori nella funzione 'calcoloPID()' 
- [x] Testare il funzionamento della funzione 'ottieniDistanzaCompiuta()'
- [x] Creare il programma di raccoglimento dei dati
- [x] Testare il funzionamento di tutti i metodi della classe 'Movimenti' tramite gli appositi file di test
- [ ] Rimuovere commenti per efficentare memoria
- [ ] resettare spike
- [ ] Testare la versione migliorata del mission manager (rewrite inMain, senza commenti)
- [ ] risolvere "smallMotorD.run_for_degrees()" e "mv.motoriMovimento()"
- [ ] aggiungere gestione async del bottone

## Idee:
- Custom immage render
- Microaggiustamenti in base alla batteria (8300-8000 mV)
- Aggiungere sistema di accelerazione/decelerazione
- Migliorare l'efficacia e la precisione delle curve
- Migliorare il PID per permettere al robot di andare più veloce
- Finire la funzione del machine learning
