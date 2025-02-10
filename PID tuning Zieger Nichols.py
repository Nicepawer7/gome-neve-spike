# LEGO type:standard slot:0

# correzzione i base alla batteria

from spike import PrimeHub, Motor, MotorPair, ColorSensor
from hub import battery
import sys, time, hub

# definire l'oggetto che rappresenta l'hub (il robot in sè)
spike = PrimeHub()


# configurazione del robot
movement_motors = MotorPair('A', 'B')
motoreSinistro = Motor('A')
motoreDestro = Motor('B')
# costanti PID (da modificare in base al comportamento del robot)
Kp = 0.01
Ki = 0
Kd = 0

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
        global run_multithreading, runSmall, inMain



        loop = True

        #variabili per il PID
        target = spike.motion_sensor.get_yaw_angle()#Impostare come angolo target, l'angolo corrente del robot (se il robot è orientato a 86 gradi, mentre va avanti dritto deve rimanere sempre a 86 gradi)
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

            angolo = spike.motion_sensor.get_yaw_angle()    #In un loop, calcola l'angolo misurato dal giroscopio
            distanzaCompiuta = ottieniDistanzaCompiuta(self) # e calcola la distanza percorsa grazie alla funzione definita sotto

            calcoloPID(velocità)#calcola i valori delle costanti che regolano il PID Kp, Ki e Kd in base alla velocità

            errore = angolo - target#imposta l'errore come la differenza tra l'angolo attuale e l'angolo target
            integrale += errore#imposta l'integrale come la somma di sè stesso e l'errore (l'integrale tiene conto di tutti gli errori nel tempo, andando a sommarli ogni volta che il loop ricomincia)
            derivata = errore - erroreVecchio#imposta la derivata come la differenza tra l'errore attuale e l'errore precedente (la derivata tiene conto di come cambia l'errore nel tempo)

            correzione = (errore * Kp + integrale * Ki + derivata * Kd) #calcola la correzione
            correzione = max(-100, min(corgit config --global sequence.editor "nano -w"rezione, 100))#limita la correzione entro i valori di -100 e 100
            print(Kp)
            time.sleep(1)
            Kp += Kp/3
            erroreVecchio = errore

            self.movement_motors.start_at_power(int(velocità), int(correzione) * -1) # muove in avanti il robot alla velocità definita dal parametro e sterzando a destra o a sinistra in base alla correzione
            if distanzaCompiuta >= distanza: #se la distanza compiuta è maggiore o uguale alla distanza impostata, esci dal loop
                loop = False

        self.movement_motors.stop()# Assicuriamoci di fermare i motori alla fine
        runSmall = True
        multithreading = 0
        time.sleep(0.2)
        return

        global gyroValue, inMain

        if inMain:
            return

        if verso not in [1, -1]:
            raise ValueError("Il verso deve essere 1 (destra) o -1 (sinistra)")# Verifica che il verso sia valido, altrimenti solleva un errore
        resetGyroValue()
        target = (normalize_angle(angolo)) * verso
        gyroValue = spike.motion_sensor.get_yaw_angle()
        if verso == 1:
            movement_motors.start_tank_at_power(25, -30)
            while gyroValue < target - 1:
                gyroValue = spike.motion_sensor.get_yaw_angle()
                if inMain:
                    break

                if self.spike.left_button.is_pressed():
                    inMain = True
                    break
                #print(gyroValue)
            movement_motors.stop()
        elif verso == -1:
            movement_motors.start_tank_at_power(-30, 25)
            while gyroValue > target + 1:
                gyroValue = spike.motion_sensor.get_yaw_angle()
                if inMain:
                    break

                if self.spike.left_button.is_pressed():
                    inMain = True
                    break
                #print(gyroValue)
            movement_motors.stop()
        time.sleep(0.2)

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

        self.left_Startvalue = self.motoreSinistro.get_degrees_counted()
        self.right_Startvalue = self.motoreDestro.get_degrees_counted()
        x = ottieniDistanzaCompiuta(self)

        while True:# Inizia un ciclo infinito
            if run_multithreading:#eseguire una funzione simultaneamente se definita nel parametro
                next(multithreading)

            x = ottieniDistanzaCompiuta(self)# Ottiene la distanza percorsa dal robot
            target = equazione# Calcola il valore target usando l'equazione fornita
            angolo_attuale = spike.motion_sensor.get_yaw_angle()# Ottiene l'angolo attuale del robot
            errore = angolo_attuale - target# Calcola l'errore tra l'angolo attuale e il target
            correzione = (errore * Kp)# Calcola la correzione usando il controllo proporzionale
            self.movement_motors.start_at_power(int(velocità), int(correzione) * -1)# Avvia i motori con la velocità e la correzione calcolate
            if x >= distanza_max:# Se la distanza percorsa supera o eguaglia la distanza massima
                break# Esce dal ciclo
        self.movement_motors.stop()# Ferma i motori alla fine del movimento
        run_multithreading = True
        runSmall = True
        multithreading = 0
        return


# Altre funzioni ausiliarie
def resetGyroValue(): #Resetta il valore dell'angolo misurato dal giroscopio a 0
    global gyroValue
    spike.motion_sensor.reset_yaw_angle()
    gyroValue = 0

def calcoloPID(velocità): #Calcola le costanti che regolano il PID in base alla velocità del robot
    '''
    velocità: velocità alla quale si sta spostando il robot
    '''
    global Kp
    global Ki
    global Kd


def avviaMotore(gradi, velocità, porta, spike): #Permette di muovere un motore secondario mentre il robot si sposta
    '''
    rotazioni: quante rotazioni vuoi che compia il motore piccolo (1 rotazione = 360 gradi ovviamente)
    velocità: a quale velocità desideri che il motore vada
    porta: a quale porta è connesso il motore piccolo che vuoi muovere
    '''
    global runSmall, run_multithreading, inMain

    if inMain:
        return

    while runSmall:
        if inMain:
                break

        if spike.left_button.is_pressed():
            inMain = True
            break
        motor = Motor(porta)
        motor.set_degrees_counted(0)

        loop_small = True
        while loop_small:
            distanzaPercorsa = motor.get_degrees_counted()#In un loop, prima calcola la distanza in gradi compiuta dal motore
            motor.start_at_power(velocità)# Poi lo avvia alla velocità data dal parametro
            if (abs(distanzaPercorsa) > abs(gradi)):#E se la distanza compiuta dal motore, calcolata precedentemente, diventa maggiore delle rotazioni convertite in gradi date dal paramentro
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


class bcolors:
    BATTERY = '\033[32m'
    BATTERY_LOW = '\033[31m'

    ENDC = '\033[0m'

mv = Movimenti(spike, 'A', 'B', movement_motors)

if battery.voltage() < 8000:
    print(bcolors.BATTERY_LOW + "batteria scarica: " + str(battery.voltage()) + " \n ----------------------------- \n >>>> carica la batteria o cambiala <<<< \n ----------------------------- \n"+ bcolors.ENDC)
else:
    print(bcolors.BATTERY + "livello batteria: " + str(battery.voltage()) + bcolors.ENDC)


#missione
mv.vaiDrittoPID(100000,25)




sys.exit()