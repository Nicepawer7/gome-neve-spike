# importare le librerie di spike
from spike import PrimeHub, Motor, MotorPair, ColorSensor, Timer, wait_for_seconds, wait_until, hub


# definire l'oggetto che rappresenta l'hub (il robot in sè)
spike = PrimeHub()

# configurazione del robot
movement_motors = MotorPair('A', 'B')
smallMotorC = Motor('C')
smallMotorD = Motor('D')
colorSensor = ColorSensor('E')
#grandezza_ruote = float('x') #inserire il numero corretto (circonferenza), al momento (20 agosto) non ne ho la più pallida idea

# costanti PID (da modificare in base al comportamento del robot)
Kp = 0
Ki = 0
Kd = 0

run_multithreading = True #variabile per l'esecuzione di più comandi contemporaneamente (es: muovere un braccio mentre il robot è in movimento)
gyroValue = 0 #valore dell'angolo misurato dal giroscopio
runSmall = True


#classe contenente tutte le funzioni per i movimenti del robot
class Movimenti:
    def __init__(self, spike, motoreSinistro, motoreDestro, movement_motors):
        """
            Il metodo __init__ in una classe Python è un metodo speciale chiamato costruttore. 
            Viene automaticamente invocato ogni volta che una nuova istanza (oggetto) della classe viene creata. 
            Il suo scopo principale è inizializzare gli attributi dell'oggetto con valori specificati al momento della creazione dell'oggetto.
        """
        self.spike = spike
        self.motoreSinistro = Motor(motoreSinistro)
        self.motoreDestro = Motor(motoreDestro)
        self.movement_motors = movement_motors

    def vaiDrittoPID(self, distanza, velocità, multithreading = None):
        '''
        distanza: quanto si deve spostare il robot (in gradi)
        velocità: a che velocità si deve muovere
        multithreading: definire la funzione che si vuole eseguire mentre il robot si sposta Es: 
            
            multithreading = avviaMotore(5, 100, 'C')
            vaiDrittoPID(1000, 80, multithreading=multithreading )
        '''
        global Kp, Ki, Kd
        global run_multithreading, runSmall
        
        if multithreading == None:
            run_multithreading = False
        
        loop = True
        
        #variabili per il PID
        target = spike.motion_sensor.get_yaw_angle()  #Impostare come angolo target, l'angolo corrente del robot (se il robot è orientato a 86 gradi, mentre va avanti dritto deve rimanere sempre a 86 gradi)
        errore = 0
        erroreVecchio = 0
        integrale = 0
        derivata = 0
        
        #controlla che non ci siano errori con la distanza inserita
        if distanza < 0:
            print('ERR: distanza < 0')
            distanza = abs(distanza)
        
        self.left_Startvalue = self.motoreSinistro.get_degrees_counted()
        self.right_Startvalue = self.motoreDestro.get_degrees_counted()
        distanzaCompiuta = ottieniDistanzaCompiuta(self)
        
        while loop:
            if run_multithreading:  #eseguire una funzione simultaneamente se definita nel parametro
                next(multithreading)

            angolo = spike.motion_sensor.get_yaw_angle()     #In un loop, calcola l'angolo misurato dal giroscopio
            distanzaCompiuta = ottieniDistanzaCompiuta(self) # e calcola la distanza percorsa grazie alla funzione definita sotto
            
            calcoloPID(velocità)  #calcola i valori delle costanti che regolano il PID Kp, Ki e Kd in base alla velocità
            
            errore = angolo - target  #imposta l'errore come la differenza tra l'angolo attuale e l'angolo target
            integrale += errore   #imposta l'integrale come la somma di sè stesso e l'errore (l'integrale tiene conto di tutti gli errori nel tempo, andando a sommarli ogni volta che il loop ricomincia)
            derivata = errore - erroreVecchio  #imposta la derivata come la differenza tra l'errore attuale e l'errore precedente (la derivata tiene conto di come cambia l'errore nel tempo)
            
            correzione = (errore * Kp + integrale * Ki + derivata * Kd) #calcola la correzione
            correzione = max(-100, min(correzione, 100))  #limita la correzione entro i valori di -100 e 100
            
            erroreVecchio = errore
            
            self.movement_motors.start_at_power(int(velocità), int(correzione) * -1) # muove in avanti il robot alla velocità definita dal parametro e sterzando a destra o a sinistra in base alla correzione
            
            if distanzaCompiuta >= distanza: #se la distanza compiuta è maggiore o uguale alla distanza impostata, esci dal loop
                loop = False
            
        self.movement_motors.stop()  # Assicuriamoci di fermare i motori alla fine
        run_multithreading = True
        runSmall = True
        multithreading = 0
        return
    
    def ciroscopio(self, angolo, verso, velocita=30):
        """
        Ruota il robot di un certo angolo in una direzione specifica.
        
        Parametri:
        angolo: Angolo di rotazione del robot (in gradi)
        verso: Direzione di rotazione (1 per destra, -1 per sinistra)
        velocita: Velocità di rotazione (predefinita a 30)
        """
        
        if verso not in [1, -1]:
            raise ValueError("Il verso deve essere 1 (destra) o -1 (sinistra)")  # Verifica che il verso sia valido, altrimenti solleva un errore
        
        angolo_attuale = normalize_angle(spike.motion_sensor.get_yaw_angle())  # Ottiene l'angolo attuale del robot e lo normalizza
        angolo_target = normalize_angle(angolo_attuale + (angolo * verso))  # Calcola l'angolo target aggiungendo l'angolo di rotazione desiderato
        
        while abs(normalize_angle(spike.motion_sensor.get_yaw_angle()) - angolo_target) > 2:  # Continua a ruotare finché non si è vicini all'angolo target
            differenza = abs(normalize_angle(spike.motion_sensor.get_yaw_angle()) - angolo_target)  # Calcola la differenza tra l'angolo attuale e quello target
            velocita_attuale = min(velocita, max(10, differenza / 2))  # Calcola la velocità di rotazione in base alla differenza, con un minimo di 10
            
            if verso == 1:  # Se il verso è 1, ruota a destra
                self.movement_motors.start_tank_at_power(velocita_attuale, velocita_attuale * 3)  # Avvia i motori per ruotare a destra
            else:  # Altrimenti, ruota a sinistra
                self.movement_motors.start_tank_at_power(velocita_attuale * 3, -velocita_attuale)  # Avvia i motori per ruotare a sinistra
        
        self.movement_motors.stop()  # Ferma i motori una volta raggiunto l'angolo target
        return

    def equazione(self, equazione, distanza_max, velocità, multithreading = None):
        """
        Esegui un movimento basato sull'equazione PID.
        
        Parametri:
        equazione: equazione che descrive la traiettoria del robot.
        distanza_max: Distanza massima che il robot deve percorrere.
        velocità: Velocità di movimento del robot.
        """
        
        global Kp
        global run_multithreading
        
        if multithreading == None:
            run_multithreading = False
        
        self.left_Startvalue = self.motoreSinistro.get_degrees_counted()
        self.right_Startvalue = self.motoreDestro.get_degrees_counted()
        x = ottieniDistanzaCompiuta(self)
        
        while True:  # Inizia un ciclo infinito
            if run_multithreading:  #eseguire una funzione simultaneamente se definita nel parametro
                next(multithreading)

            x = ottieniDistanzaCompiuta(self)  # Ottiene la distanza percorsa dal robot
            target = equazione  # Calcola il valore target usando l'equazione fornita
            angolo_attuale = spike.motion_sensor.get_yaw_angle()  # Ottiene l'angolo attuale del robot
            errore = angolo_attuale - target  # Calcola l'errore tra l'angolo attuale e il target
            correzione = (errore * Kp)  # Calcola la correzione usando il controllo proporzionale
            self.movement_motors.start_at_power(int(velocità), int(correzione) * -1)  # Avvia i motori con la velocità e la correzione calcolate
            if x >= distanza_max:  # Se la distanza percorsa supera o eguaglia la distanza massima
                break  # Esce dal ciclo
        self.movement_motors.stop()  # Ferma i motori alla fine del movimento
        run_multithreading = True
        runSmall = True
        multithreading = 0
        return

    def seguiLinea(self, distanza, velocità, lato, multithreading = None):
        '''
        distanza: quanto si deve spostare il robot (in gradi)
        velocità: a che velocità si deve muovere
        lato: su quale lato della linea il robot deve seguire ('sinistra' o 'destra')
        multithreading: definire la funzione che si vuole eseguire mentre il robot si sposta Es: 
            
            multithreading = avviaMotore(5, 100, 'C')
            vaiDrittoPID(1000, 80, multithreading=multithreading )
        '''
        global Kp, Ki, Kd, run_multithreading, runSmall, colorSensor  # Dichiarazione delle variabili globali

        if multithreading == None:
            run_multithreading = False  # Se non c'è multithreading, imposta la variabile a False
        
        errore = 0  # Inizializza l'errore corrente
        erroreVecchio = 0  # Inizializza l'errore precedente
        integrale = 0  # Inizializza l'integrale dell'errore
        derivata = 0  # Inizializza la derivata dell'errore
        
        loop = True  # Imposta il flag del loop principale
        
        if distanza < 0:
            print('ERR: distance < 0')
            distanza = abs(distanza)  # Assicura che la distanza sia positiva
        
        invert = 1  # Inizializza il fattore di inversione
        if lato == 'sinistra':
            invert = 1  # Se il lato è 'sinistra', mantieni invert a 1
        elif lato == 'destra':
            invert = -1  # Se il lato è 'destra', imposta invert a -1
        
        self.left_Startvalue = self.leftMotor.get_degrees_counted()  # Memorizza la posizione iniziale del motore sinistro
        self.right_Startvalue = self.rightMotor.get_degrees_counted()  # Memorizza la posizione iniziale del motore destro
        distanzaCompiuta = ottieniDistanzaCompiuta(self)  # Calcola la distanza iniziale percorsa

        while loop:
            if run_multithreading:
                next(multithreading)  # Esegue il prossimo passo della funzione di multithreading se attiva
                
            distanzaCompiuta = ottieniDistanzaCompiuta(self)  # Aggiorna la distanza percorsa
            
            calcoloPID(velocità)  # Calcola i parametri PID in base alla velocità
            
            erroreVecchio = errore  # Memorizza l'errore precedente
            errore = colorSensor.get_reflected_light() - 50  # Calcola l'errore basato sulla lettura del sensore di colore
            integrale += errore  # Aggiorna l'integrale dell'errore
            derivata = errore - erroreVecchio  # Calcola la derivata dell'errore
            correzione = (errore * Kp + integrale * Ki + derivata * Kd) * invert  # Calcola la correzione PID
            correzione = max(-100, min(correzione, 100))  # Limita la correzione tra -100 e 100
            
            self.movement_motors.start_at_power(int(velocità), int(correzione))  # Avvia i motori con la velocità e la correzione calcolate
            
            if distanzaCompiuta >= distanza:
                loop = False  # Termina il loop se la distanza percorsa è maggiore o uguale a quella richiesta
        
        self.movement_motors.stop()  # Ferma i motori
        run_multithreading = True  # Ripristina il flag del multithreading
        runSmall = True  # Ripristina il flag runSmall
        multithreading = 0  # Resetta la variabile multithreading
        return  # Termina la funzione
   
# Altre funzioni ausiliarie 
def resetGyroValue(): #Resetta il valore dell'angolo misurato dal giroscopio a 0
    global gyroValue
    hub.motion.yaw_pitch_roll(0)
    spike.motion_sensor.reset_yaw()

    gyroValue = 0

def calcoloPID(velocità): #Calcola le costanti che regolano il PID in base alla velocità del robot
    '''
    velocità: velocità alla quale si sta spostando il robot
    '''
    global Kp
    global Ki
    global Kd
    
    # NB: I valori sono da regolare in base a come si comporta il robot
    if velocità > 0:
        Kp = -0.17 * velocità + 12.83
        Ki = 12
        Kd = 1.94 * velocità - 51.9
        if Kp < 3.2:
            Kp = 3.2
    else:
        Kp = (11.1 * abs(velocità))/(0.5 * abs(velocità) -7) - 20
        Ki = 10
        #Ki = 0.02
        Kd = 1.15**(- abs(velocità)+49) + 88

def avviaMotore(rotazioni, velocità, porta): #Permette di muovere un motore secondario mentre il robot si sposta
    '''
    rotazioni: quante rotazioni vuoi che compia il motore piccolo (1 rotazione = 360 gradi ovviamente)
    velocità: a quale velocità desideri che il motore vada
    porta: a quale porta è connesso il motore piccolo che vuoi muovere
    '''
    global runSmall
    global run_multithreading

    while runSmall:
        motor = Motor(porta)
        motor.set_degrees_counted(0)

        loop_small = True
        while loop_small:
            distanzaPercorsa = motor.get_degrees_counted()   #In un loop, prima calcola la distanza in gradi compiuta dal motore
            motor.start_at_power(velocità)  # Poi lo avvia alla velocità data dal parametro
            if (abs(distanzaPercorsa) > abs(rotazioni) * 360):   #E se la distanza compiuta dal motore, calcolata precedentemente, diventa maggiore delle rotazioni convertite in gradi date dal paramentro
                loop_small = False    #ferma il loop
            yield

        motor.stop()
        runSmall = False
        run_multithreading = False
    yield

def ottieniDistanzaCompiuta(data):

    distanzaCompiuta = (
                    abs(data.motoreSinistro.get_degrees_counted() - data.left_Startvalue) + 
                    abs(data.motoreDestro.get_degrees_counted() - data.right_Startvalue)) / 2

    return distanzaCompiuta

def normalize_angle(angle):
    """Normalizza l'angolo per farlo rientrare nell'intervallo da -180 a 180 gradi."""
    while angle > 180:
        angle -= 360
    while angle < -180:
        angle += 360
    return angle



mv = Movimenti(spike, 'A', 'B', movement_motors)
resetGyroValue()
