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
- [X] Rimuovere commenti per efficentare memoria
- [X] Rendere più intutitvo lo stato della missione (numeri display,X quando non annullabile,direzione ecc..)
- [ ] far funzionare il bottone home
- [ ] risolvere "smallMotorD.run_for_degrees()" e "mv.motoriMovimento()"
- [ ] funzione sleep() per time.sleep() per migliore gestione
- [ ] aggiungere gestione async/threading del bottone
- [ ] pulire README.md

## Idee:
- multi file
- Microaggiustamenti in base alla batteria (8300-8000 mV)
- Aggiungere sistema di accelerazione/decelerazione
- Migliorare l'efficacia e la precisione delle curve
- Migliorare il PID per permettere al robot di andare più veloce
- Finire la funzione del machine learning

## Note di sviluppo/ info-source:
- Per threads codice di esempio:
import threading
import time
import RPi.GPIO as GPIO  # Libreria per i GPIO di Raspberry Pi

BUTTON_PIN = 17  # Sostituisci con il numero del pin a cui è collegato il pulsante
stop_robot = False  # Variabile di controllo

 #Configurazione GPIO
GPIO.setmode(GPIO.BCM)  
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PULLUP)  # Pull-up interno

def azione_secondaria():
    print("Azione secondaria in esecuzione...")
    time.sleep(2)
    print("Azione secondaria completata.")

def muovi_robot():
    global stop_robot
    print("Il robot inizia a muoversi...")
    azione_secondaria()

    while not stop_robot:
        print("Il robot sta ancora camminando...")
        time.sleep(1)

    print("Robot fermato.")

# Avvia il movimento del robot in un thread separato
thread_robot = threading.Thread(target=muovi_robot)
thread_robot.start()

# Funzione che attende la pressione del pulsante
print("Premi il pulsante per fermare il robot...")
while GPIO.input(BUTTON_PIN):  # Finché il pulsante NON è premuto (pull-up)
    time.sleep(0.1)  # Controlla ogni 100 ms

stop_robot = True  # Ferma il robot
thread_robot.join()

print("Fine programma.")
GPIO.cleanup()  # Libera i pin GPIO
- https://tuftsceeo.github.io/SPIKEPythonDocs/SPIKE2.html#top
- https://libdoc.fh-zwickau.de/opus4/frontdoor/deliver/index/docId/15400/file/lego_spike_linux.pdf
- https://github.com/smr99/lego-hub-tk
