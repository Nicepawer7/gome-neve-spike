# PROGRAMMA PER TESTARE LA FUNZIONE vaiDrittoPID

from spike import PrimeHub, Motor, MotorPair, ColorSensor, Timer, wait_for_seconds, wait_until, hub

spike = PrimeHub()
motoreSinistro = Motor('A')
motoreDestro = Motor('B')
movement_motors = MotorPair('A', 'B')
smallMotorC = Motor('C')
smallMotorD = Motor('D')
run_multithreading = True
runSmall = True

class Movimenti:
    def __init__(self, spike, motoreSinistro, motoreDestro):
        """
            Il metodo __init__ in una classe Python è un metodo speciale chiamato costruttore. 
            Viene automaticamente invocato ogni volta che una nuova istanza (oggetto) della classe viene creata. 
            Il suo scopo principale è inizializzare gli attributi dell'oggetto con valori specificati al momento della creazione dell'oggetto.
        """
        self.spike = spike
        self.motoreSinistro = Motor('A')
        self.motoreDestro = Motor('B')
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
        global run_multithreading
        
        if multithreading == None:
            run_multithreading = False
        
        loop = True
        
        #variabili per il PID
        target = hub.motion_sensor.get_yaw_angle()  #Impostare come angolo target, l'angolo corrente del robot (se il robot è orientato a 86 gradi, mentre va avanti dritto deve rimanere sempre a 86 gradi)
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

            angolo = hub.motion_sensor.get_yaw_angle()     #In un loop, calcola l'angolo misurato dal giroscopio
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
mv = Movimenti(spike, motoreSinistro, motoreDestro)
mv.vaiDrittoPID(1000, 80, multithreading=avviaMotore(5, 100, 'C'))