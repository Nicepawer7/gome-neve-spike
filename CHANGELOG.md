# Changelog
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
