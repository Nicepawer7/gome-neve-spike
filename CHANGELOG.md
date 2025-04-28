# Changelog
## Versione 0.9.2.69 17:41 Sabato 26/04/25
* **MODIFICHE**
    * a quanto pare dopo aver scavato un po' nello spike si può misurare il tempo in millisecondi e anche in nanosecondi con il comando time.ticks_ms() e time.ticks_us()
    * Ho implementato la misura del periodo dt per derivata e integrale e sembra funzionare molto bene, le costanti sono calibrate e l'accelerazione non sputtana troppo.
* **COSE DA FARE**
    * Rendere più preciso il pid e iniziare a programmare tutte le missioni
    * piangere
## Versione 0.9.2 17:41 Sabato 26/04/25
* **MODIFICHE**
    * Calibrato il pid a intervalli di velocità di 10
    * Sistemato la funzione velocità
    * Corretto file con classi ordinate,ufficialmente main.py
    * Non ho potuto implementare in modo classico la derivata poichè spike 2 non permette le misure in millisecondi ma solo in secondi, sembra che spike 3 lo permetta ma dovrei testare,potrebbe essere utile viste le altre funzionalità disponibili e l'ide che sembra essere funzionante
* **COSE DA FARE**
    * Migliorare l'acccelerazione che sia più precisa
## Versione 0.9.1 22:13 Domenica 13/04/25
* **MODIFICHE**
    * Testato le funzioni che sembrano funzionare al momento
    * Reso il file con riscrittura delle funzioni il main
    * creato un file main con una modifica alla struttura delel classi, non testato ha una funzione che fa andare indietro il robot con il pid (costanti probabilmente sbagliate), inoltre rende possibile usare tutte le funzioni di movimento direttamente dall'oggetto __mv__
* **COSE DA FARE**
    * Finire calibrazione Pid (ora calibrato solo a 100)
## Versione 0.9 (molto arbitrariamente) 01:40 AM Domenica 13/04/25
* **MODIFICHE**
    * Ristrutturato tutto il file main in un nuovo file temporaneo "riscrittura main con classi", questo nuovo sistema dovrebbe rendere più gestibile l'intero codice e mantenibile in futuro
    * Spostato in un altro file il line follower
    * aggiunto al main (senza ccelerazione) dt non in base al tempo
* **COSE DA FARE**
    * Testare ogni parte del nuovo codice"
    * Suddividerlo in file,in modo da formare una libreria
    * Aggiungere dei commenti
    * Dormire
