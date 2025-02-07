# LEGO type:advanced slot:5 autostart

# PROGRAMMA PER TESTARE LA FUNZIONE seguiLinea

from spike import PrimeHub, Motor, MotorPair, ColorSensor, Timer, wait_for_seconds, wait_until, hub

spike = PrimeHub()
motoreSinistro = Motor('A')
motoreDestro = Motor('B')
movement_motors = MotorPair('A', 'B')
smallMotorC = Motor('C')
smallMotorD = Motor('D')
run_multithreading = True
runSmall = True
colorSensor = ColorSensor('E')

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

hub.motion.yaw_pitch_roll(0)
mv = Movimenti(spike, motoreSinistro, motoreDestro, movement_motors)
mv.seguiLinea(1000, 80, 'sinistra', multithreading=avviaMotore(5, 100, 'C'))

