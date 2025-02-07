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
smallMotorC = Motor('C')
smallMotorD = Motor('D')
colorSensor = ColorSensor('E')
#grandezza_ruote = float('x') #inserire il numero corretto (circonferenza), al momento (20 agosto) non ne ho la più pallida idea

# costanti PID (da modificare in base al comportamento del robot)
Kp = 0
Ki = 0
Kd = 0

inMain = True

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
        global run_multithreading, runSmall, inMain

        if inMain:
            return

        if multithreading == None:
            run_multithreading = False

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

            if inMain:
                break

            if self.spike.left_button.is_pressed():
                inMain = True
                break

            if run_multithreading:#eseguire una funzione simultaneamente se definita nel parametro
                next(multithreading)

            angolo = spike.motion_sensor.get_yaw_angle()    #In un loop, calcola l'angolo misurato dal giroscopio
            distanzaCompiuta = ottieniDistanzaCompiuta(self) # e calcola la distanza percorsa grazie alla funzione definita sotto

            calcoloPID(velocità)#calcola i valori delle costanti che regolano il PID Kp, Ki e Kd in base alla velocità

            errore = angolo - target#imposta l'errore come la differenza tra l'angolo attuale e l'angolo target
            integrale += errore#imposta l'integrale come la somma di sè stesso e l'errore (l'integrale tiene conto di tutti gli errori nel tempo, andando a sommarli ogni volta che il loop ricomincia)
            derivata = errore - erroreVecchio#imposta la derivata come la differenza tra l'errore attuale e l'errore precedente (la derivata tiene conto di come cambia l'errore nel tempo)

            correzione = (errore * Kp + integrale * Ki + derivata * Kd) #calcola la correzione
            correzione = max(-100, min(correzione, 100))#limita la correzione entro i valori di -100 e 100

            erroreVecchio = errore

            self.movement_motors.start_at_power(int(velocità), int(correzione) * -1) # muove in avanti il robot alla velocità definita dal parametro e sterzando a destra o a sinistra in base alla correzione

            if distanzaCompiuta >= distanza: #se la distanza compiuta è maggiore o uguale alla distanza impostata, esci dal loop
                loop = False

        self.movement_motors.stop()# Assicuriamoci di fermare i motori alla fine
        run_multithreading = True
        runSmall = True
        multithreading = 0
        time.sleep(0.2)
        return

    def ciroscopio(self, angolo, verso):
        """
        Ruota il robot di un certo angolo in una direzione specifica.

        Parametri:
        angolo: Angolo di rotazione del robot (in gradi)
        verso: Direzione di rotazione (1 per destra, -1 per sinistra)
        """

        global gyroValue, inMain

        if inMain:
            return

        if verso not in [1, -1]:
            raise ValueError("Il verso deve essere 1 (destra) o -1 (sinistra)")# Verifica che il verso sia valido, altrimenti solleva un errore
        resetGyroValue()
        target = (normalize_angle(angolo)) * verso
        gyroValue = spike.motion_sensor.get_yaw_angle()
        if verso == 1:
            movement_motors.start_tank_at_power(30, -25)
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
            movement_motors.start_tank_at_power(-25, 30)
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

    def oipocsoric(self, angolo, verso):
        """
        Ruota il robot di un certo angolo in una direzione specifica.

        Parametri:
        angolo: Angolo di rotazione del robot (in gradi)
        verso: Direzione di rotazione (1 per destra, -1 per sinistra)
        """

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

        if multithreading == None:
            run_multithreading = False

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

    def seguiLinea(self, distanza, velocità, lato, multithreading = None):
        '''
        distanza: quanto si deve spostare il robot (in gradi)
        velocità: a che velocità si deve muovere
        lato: su quale lato della linea il robot deve seguire ('sinistra' o 'destra')
        multithreading: definire la funzione che si vuole eseguire mentre il robot si sposta Es:

            multithreading = avviaMotore(5, 100, 'C')
            vaiDrittoPID(1000, 80, multithreading=multithreading )
        '''
        global Kp, Ki, Kd, run_multithreading, runSmall, colorSensor# Dichiarazione delle variabili globali

        if multithreading == None:
            run_multithreading = False# Se non c'è multithreading, imposta la variabile a False

        errore = 0# Inizializza l'errore corrente
        erroreVecchio = 0# Inizializza l'errore precedente
        integrale = 0# Inizializza l'integrale dell'errore
        derivata = 0# Inizializza la derivata dell'errore

        loop = True# Imposta il flag del loop principale

        if distanza < 0:
            print('ERR: distance < 0')
            distanza = abs(distanza)# Assicura che la distanza sia positiva

        invert = 1# Inizializza il fattore di inversione
        if lato == 'sinistra':
            invert = 1# Se il lato è 'sinistra', mantieni invert a 1
        elif lato == 'destra':
            invert = -1# Se il lato è 'destra', imposta invert a -1

        self.left_Startvalue = self.leftMotor.get_degrees_counted()# Memorizza la posizione iniziale del motore sinistro
        self.right_Startvalue = self.rightMotor.get_degrees_counted()# Memorizza la posizione iniziale del motore destro
        distanzaCompiuta = ottieniDistanzaCompiuta(self)# Calcola la distanza iniziale percorsa

        while loop:
            if run_multithreading:
                next(multithreading)# Esegue il prossimo passo della funzione di multithreading se attiva

            distanzaCompiuta = ottieniDistanzaCompiuta(self)# Aggiorna la distanza percorsa

            calcoloPID(velocità)# Calcola i parametri PID in base alla velocità

            erroreVecchio = errore# Memorizza l'errore precedente
            errore = colorSensor.get_reflected_light() - 50# Calcola l'errore basato sulla lettura del sensore di colore
            integrale += errore# Aggiorna l'integrale dell'errore
            derivata = errore - erroreVecchio# Calcola la derivata dell'errore
            correzione = (errore * Kp + integrale * Ki + derivata * Kd) * invert# Calcola la correzione PID
            correzione = max(-100, min(correzione, 100))# Limita la correzione tra -100 e 100

            self.movement_motors.start_at_power(int(velocità), int(correzione))# Avvia i motori con la velocità e la correzione calcolate

            if distanzaCompiuta >= distanza:
                loop = False# Termina il loop se la distanza percorsa è maggiore o uguale a quella richiesta

        self.movement_motors.stop()# Ferma i motori
        run_multithreading = True# Ripristina il flag del multithreading
        runSmall = True# Ripristina il flag runSmall
        multithreading = 0# Resetta la variabile multithreading
        return# Termina la funzione

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

    if velocità >= 75:
        Kp = 14
        Ki = 0
        Kd = 3
    elif 40 <= velocità < 75:
        Kp = 18.4
        Ki = 0
        Kd = 5
    elif velocità < 40:
        Kp = 28
        Ki = 0.25
        Kd = 1.5

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


def program_1():
    #prima missione per raccogliere pezzi
    #

    mv.vaiDrittoPID(1300, 65)
    movement_motors.move(1600, unit="degrees", steering=0, speed=-90)
    return

def program_3():
    #alzare la vela della barca + squalo
    #4° fine da destra

    multithreading = avviaMotore(120, -50, 'D', spike) 
    mv.vaiDrittoPID(1520, 50, multithreading=multithreading) #intermerda, parti
    mv.ciroscopio(90, 1) #gira sub
    mv.vaiDrittoPID(615 , 50)
    movement_motors.move(200, unit="degrees", steering=0, speed=-50)
    motoreSinistro.run_for_degrees(630, 50)
    mv.ciroscopio(12, -1)
    mv.vaiDrittoPID(340, 50)
    smallMotorD.run_for_degrees(150, 80)
    movement_motors.move(300, unit="degrees", steering=-70, speed=-50)
    smallMotorD.run_for_degrees(90, -100)
    movement_motors.move(1300, unit="degrees", steering=0, speed=-100)
    return

def program_2():
    #prendere il sub e portarlo a destinazione, cambiare base
    #2° fine da destra

    multi = avviaMotore(80,20,"D", spike) 
    mv.vaiDrittoPID(1450,50,multi)
    mv.ciroscopio(90,-1)
    mv.vaiDrittoPID(120,30)
    smallMotorD.run_for_degrees(45,-20)
    movement_motors.move(300, unit="degrees", steering=0, speed=-50)
    mv.oipocsoric(88,1)
    multi = avviaMotore(45,20,"D", spike) 
    mv.vaiDrittoPID(100,50,multi)
    movement_motors.move(200, unit="degrees", steering=0, speed=-50)
    time.sleep(0.1)
    smallMotorD.run_for_degrees(45,-20)
    mv.ciroscopio(5,-1)
    mv.vaiDrittoPID(150, 50)
    mv.ciroscopio(5,1)
    smallMotorD.run_for_degrees(50,100)
    movement_motors.move(2500, unit="degrees", steering=-10, speed=-100)

    return

def program_4():
    #polipo
    #2° fine da 2° grande da sinistra?
    
    mv.vaiDrittoPID(400, 50)
    time.sleep(0.2)
    movement_motors.move(450, unit="degrees", steering=0, speed=-100)

    """multi = smallMotorC.run_for_degrees(75, 20)
    mv.vaiDrittoPID(1150,50, multithreading=multi)
    mv.ciroscopio(45, 1)
    mv.vaiDrittoPID(900, 50)
    mv.ciroscopio(28, 1)
    mv.vaiDrittoPID(170, 40)
    smallMotorC.run_for_degrees(46, -20)
    mv.vaiDrittoPID(50, 50)
    smallMotorC.run_for_degrees(90, 20)
    mv.ciroscopio(15, 1)
    time.sleep(0.2)
    mv.vaiDrittoPID(100, 50)
    mv.ciroscopio(40, 1)
    mv.vaiDrittoPID(1500, 80)
    mv.ciroscopio(20, -1)
    mv.vaiDrittoPID(800, 80)
    time.sleep(2)
    movement_motors.move(900, unit="degrees", steering=0, speed=-60)
    time.sleep(0.15)
    mv.vaiDrittoPID(1000, 80)
"""
    return

def program_5():
    #5° da sinistra
#2° linea fine
    #allineati con la barca
    mv.vaiDrittoPID(269, 50)
    mv.ciroscopio(88, 1)
    time.sleep(0.1)
    mv.vaiDrittoPID(400, 50)
    #abbassa braccio + mezzo tragitto
    multithreading = avviaMotore(40 , 40 , "D",spike)
    mv.vaiDrittoPID(900, 50, multithreading=multithreading)
    time.sleep(0.2)
    #squalo
    smallMotorD.run_for_degrees(65, -80)
    mv.ciroscopio(45, -1)
    time.sleep(0.1)
    mv.vaiDrittoPID(100 , 75)
    #riposizionamento
    movement_motors.move(375, unit="degrees", steering=-45, speed=-50) #torna indietro
    movement_motors.move(50, unit="degrees", steering=0, speed=-50)
    #abbassa braccio + finisci tragitto
    smallMotorD.run_for_degrees(65, 60)
    time.sleep(0.5)
    mv.vaiDrittoPID(700, 50)
    #gabbie + rientro
    smallMotorC.run_for_degrees(90, -70)
    movement_motors.move(500, unit="degrees", steering=0, speed=-15)
    time.sleep(0.2)
    smallMotorD.run_for_degrees(85, -80)
    movement_motors.move(300, unit="degrees", steering=0, speed=-100)
    mv.ciroscopio(30,-1)
    #mv.vaiDrittoPID(600,70)
    time.sleep(0.5)
    movement_motors.move(2500,unit="degrees",steering=10,speed=100)

    
    return

def program_6():
    mv.vaiDrittoPID(50, 50) # partenza
    mv.ciroscopio(48, -1) # sinistra in area
    mv.vaiDrittoPID(1700, 50) # fino a tridente
    mv.ciroscopio(9,-1)
    mv.ciroscopio(57,1)
    mv.vaiDrittoPID(200,50)
    # movement_motors.move(200,unit="degrees",steering=-80,speed=40)
    mv.ciroscopio(85.0, 1) #  guarda lato destro
    mv.vaiDrittoPID(1200, 50) # fino a pre-pianta
    mv.ciroscopio(13, 1) # guarda pianta
    mv.vaiDrittoPID(200, 50) # fino a pianto
    movement_motors.move(330, unit="degrees", steering=0, speed=-30) # torna indietro
    mv.ciroscopio(86, 1) # raccogli gamberi
    movement_motors.move(1300,unit="degrees",steering=-15,speed=100)
    """"
    mv.vaiDrittoPID(50, 50) # partenza
    mv.ciroscopio(48, -1) # sinistra in area
    mv.vaiDrittoPID(2000, 50) # fino a tridente
    mv.ciroscopio(133.0, 1) #  guarda lato destro
    mv.vaiDrittoPID(1300, 50) # fino a pre-pianta
    mv.ciroscopio(13, 1) # guarda pianta
    mv.vaiDrittoPID(290, 50) # fino a pianta
    movement_motors.move(430, unit="degrees", steering=0, speed=-30) # torna indietro
    mv.ciroscopio(75, 1) # raccogli gamberi
    mv.vaiDrittoPID(1300, 100) # home
    """
    return

def program_7():
#10° da destra

    mv.vaiDrittoPID(1500, 50) # partenza
    mv.ciroscopio(40, 1) # guarda balena
    mv.vaiDrittoPID(250, 50) # scopa la balena
    smallMotorC.run_for_degrees(850, 100) #abbassa gamberetti
    time.sleep(0.5)
    smallMotorC.run_for_degrees(720, -100) # alza
    movement_motors.move(600, unit="degrees", steering=0, speed=-75) #torna indietro
    movement_motors.move(200, unit="degrees", steering=100, speed=-50) #curva in retro
    movement_motors.move(1500, unit="degrees", steering=0, speed=-100) #base 
    time.sleep(2)
    movement_motors.move(1000, unit="degrees", steering=0, speed=-100) #polipo
    mv.vaiDrittoPID(850,100)


    
    return

def program_8():
   #2°  dalla 2 linea grande
    multi = avviaMotore(5, -50, "D", spike)
    mv.vaiDrittoPID(1200,50,multithreading=multi) #fino a sonar
    mv.ciroscopio(60,-1)
    mv.vaiDrittoPID(1030,75) #fino a sottmarino 
    smallMotorD.run_for_degrees(-60,30)
    time.sleep(1)
    mv.ciroscopio(52,-1)
    mv.vaiDrittoPID(520,50) 
    mv.ciroscopio(38,1)
    mv.vaiDrittoPID(550,60)
    movement_motors.move(700, unit="degrees", steering=-40, speed=90)
    mv.vaiDrittoPID(900,90)
    return

def program_9():
    return



main = True
programma_selezionato = 1
spike.status_light.on('green')
spike.light_matrix.write(programma_selezionato)

while main:
    inMain = True
    #selezione programma
    if spike.right_button.is_pressed():
        time.sleep(0.50)
        programma_selezionato += 1
        spike.light_matrix.write(programma_selezionato)

        if programma_selezionato == 1:
            spike.status_light.on('green')
        elif programma_selezionato == 2:
            spike.status_light.on('red')
        elif programma_selezionato == 3:
            spike.status_light.on('blue')
        elif programma_selezionato == 4:
            spike.status_light.on('yellow')
        elif programma_selezionato == 5:
            spike.status_light.on('orange')
        elif programma_selezionato == 6:
            spike.status_light.on('pink')
        elif programma_selezionato == 7:
            spike.status_light.on('violet')
        elif programma_selezionato == 8:
            spike.status_light.on('azure')
        elif programma_selezionato == 9:
            spike.status_light.on('black')
        
        if programma_selezionato == 10:
            programma_selezionato = 1
            spike.light_matrix.write(programma_selezionato)
            spike.status_light.on('green')

    #esecuzione programma
    if spike.left_button.is_pressed():
        inMain = False
        time.sleep(0.50)

        if programma_selezionato == 1:
            spike.status_light.on("green")
            spike.light_matrix.show_image("DUCK")
            program_1()
            programma_selezionato = 2
            spike.light_matrix.write(programma_selezionato)
        elif programma_selezionato == 2:
            spike.status_light.on("red")
            spike.light_matrix.show_image("DUCK")
            program_2()
            programma_selezionato = 3
            spike.light_matrix.write(programma_selezionato)
        elif programma_selezionato == 3:
            spike.status_light.on("blue")
            spike.light_matrix.show_image("DUCK")
            program_3()
            programma_selezionato = 4
            spike.light_matrix.write(programma_selezionato)
        elif programma_selezionato == 4:
            spike.status_light.on("yellow")
            spike.light_matrix.show_image("DUCK")
            program_4()
            programma_selezionato = 5
            spike.light_matrix.write(programma_selezionato)
        elif programma_selezionato == 5:
            spike.status_light.on("orange")
            spike.light_matrix.show_image("DUCK")
            program_5()
            programma_selezionato = 6
            spike.light_matrix.write(programma_selezionato)
        elif programma_selezionato == 6:
            spike.status_light.on("pink")
            spike.light_matrix.show_image("DUCK")
            program_6()
            programma_selezionato = 7
            spike.light_matrix.write(programma_selezionato)
        elif programma_selezionato == 7:
            spike.status_light.on("violet")
            spike.light_matrix.show_image("DUCK")
            program_7()
            programma_selezionato = 8
            spike.light_matrix.write(programma_selezionato)
        elif programma_selezionato == 8:
            spike.status_light.on("azure")
            spike.light_matrix.show_image("DUCK")
            program_8()
            programma_selezionato = 9
            spike.light_matrix.write(programma_selezionato)
        elif programma_selezionato == 9:
            spike.status_light.on("black")
            spike.light_matrix.show_image("DUCK")
            program_9()
            programma_selezionato = 10
            main = False

sys.exit()