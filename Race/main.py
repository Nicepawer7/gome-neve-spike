# LEGO type:advanced slot:0 autostart
import sys, hub # type: ignore
from time import sleep
from spike import PrimeHub, Motor, MotorPair, ColorSensor # type: ignore
from hub import battery # type: ignore
from math import cos

spike = PrimeHub()
colors = ('green','red','blue','yellow','orange','pink','violet','azure')
movement_motors = MotorPair('A', 'B')
motoreSinistro = Motor('A')
motoreDestro = Motor('B')
C = Motor('C')
D = Motor('D')
colorSensor = ColorSensor('E')
pi = 3.141
Kp = 0
Ki = 0
Kd = 0
programma_selezionato = 1
stop = False
run_multithreading = True
gyroValue = 0
runSmall = True
def skip():
    global stop
    global programma_selezionato
    programma_selezionato -= 1
    stop = True
    spike.light_matrix.show_image("NO")
    movement_motors.stop()
    sleep(0.30)

class bcolors:
        BATTERY = '\033[32m'
        BATTERY_LOW = '\033[31m'
        ENDC = '\033[0m'

if battery.voltage() < 8000:
    print(bcolors.BATTERY_LOW + "batteria scarica: " + str(battery.voltage()) + " \n ----------------------------- \n >>>> carica la batteria o cambiala <<<< \n ----------------------------- \n"+ bcolors.ENDC)
else:
    print(bcolors.BATTERY + "livello batteria: " + str(battery.voltage()) + bcolors.ENDC)

class Movimenti: #classe movimenti
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
        distanza:
        velocità:
        multithreading:
            multithreading = avviaMotore(5, 100, 'C')'''
        global Kp, Ki, Kd
        global run_multithreading, runSmall, stop
        if not stop:
            print("Avvio vai dritto pid")
            if multithreading == None:
                run_multithreading = False

            loop = True

            target = spike.motion_sensor.get_yaw_angle()
            errore = 0
            erroreVecchio = 0
            integrale = 0
            derivata = 0
            if distanza < 0:
                print('ERR: distanza < 0')
                distanza = abs(distanza)
            self.left_Startvalue = self.motoreSinistro.get_degrees_counted()
            self.right_Startvalue = self.motoreDestro.get_degrees_counted()
            distanzaCompiuta = ottieniDistanzaCompiuta(self)
            spike.light_matrix.show_image("ARROW_N")
            while loop:
                if self.spike.left_button.is_pressed():
                    skip()
                    self.movement_motors.stop()
                    return
                if run_multithreading:
                    next(multithreading)
                angolo = spike.motion_sensor.get_yaw_angle()
                distanzaCompiuta = ottieniDistanzaCompiuta(self)

                calcoloPID(velocità)
                errore = angolo - target
                integrale += errore
                derivata = errore - erroreVecchio

                correzione = (errore * Kp + integrale * Ki + derivata * Kd)
                correzione = max(-100, min(correzione, 100))
                erroreVecchio = errore
                self.movement_motors.start_at_power(int(velocità), int(correzione) * -1)
                if distanzaCompiuta == None:
                    distanzaCompiuta = 0.1
                elif distanzaCompiuta >= distanza:
                    loop = False

            self.movement_motors.stop()
            run_multithreading = True
            runSmall = True
            multithreading = 0
            wait(0.2)
            print("Finito pid")
            return
    
    def ciroscopio(self, angolo, verso):
        global gyroValue, stop
        if not stop:
            if verso not in [1, -1]:
                raise ValueError("Il verso deve essere 1 (destra) o -1 (sinistra)")
            resetGyroValue()
            target = (normalize_angle(angolo)) * verso
            gyroValue = spike.motion_sensor.get_yaw_angle()
            if verso == 1:
                spike.light_matrix.show_image("ARROW_NE")
                while gyroValue < target - 1:
                    gyroValue = spike.motion_sensor.get_yaw_angle()
                    speed = decelerate(gyroValue,angolo)
                    movement_motors.start_tank_at_power(speed,(speed- 5) * -1 )
                    if self.spike.left_button.is_pressed():
                        skip()
                        return
            elif verso == -1:                
                spike.light_matrix.show_image("ARROW_NW")
                while gyroValue > target + 1:
                    gyroValue = spike.motion_sensor.get_yaw_angle()
                    speed = decelerate(gyroValue,angolo)
                    movement_motors.start_tank_at_power((speed-5) * -1, speed)
                    if self.spike.left_button.is_pressed():
                        skip()
                        return
            movement_motors.stop() # !!!!
            wait(0.2)
            return

    def oipocsoric(self, angolo, verso):
        global gyroValue, stop
        if not stop:
            if verso not in [1, -1]:
                raise ValueError("Il verso deve essere 1 (destra) o -1 (sinistra)")
            resetGyroValue()
            target = (normalize_angle(angolo)) * verso
            gyroValue = spike.motion_sensor.get_yaw_angle()
            if verso == 1:
                spike.light_matrix.show_image("ARROW_SE")
                while gyroValue < target - 1:
                    gyroValue = spike.motion_sensor.get_yaw_angle()
                    speed = decelerate(gyroValue,angolo)
                    movement_motors.start_tank_at_power(speed-5, speed * -1)
                    if self.spike.left_button.is_pressed():
                        skip()
                        movement_motors.stop()
                        return
            elif verso == -1:
                spike.light_matrix.show_image("ARROW_SW")
                while gyroValue > target + 1:
                    gyroValue = spike.motion_sensor.get_yaw_angle()
                    speed = decelerate(gyroValue,angolo)
                    movement_motors.start_tank_at_power(speed * -1, speed - 5)
                    if self.spike.left_button.is_pressed():
                        skip()
                        movement_motors.stop()
                        return
            movement_motors.stop() #!!!
            wait(0.2)
            return

    def equazione(self, equazione, distanza_max, velocità, multithreading=None):
        global Kp
        global run_multithreading, stop
        if multithreading == None:
            run_multithreading = False
        self.left_Startvalue = self.motoreSinistro.get_degrees_counted()
        self.right_Startvalue = self.motoreDestro.get_degrees_counted()
        x = ottieniDistanzaCompiuta(self)
        while True:
            if self.spike.left_button.is_pressed():
                skip()
                return
            if run_multithreading:
                next(multithreading)

            x = ottieniDistanzaCompiuta(self)
            target = equazione
            angolo_attuale = spike.motion_sensor.get_yaw_angle()
            errore = angolo_attuale - target
            correzione = (errore * Kp)
            self.movement_motors.start_at_power(int(velocità), int(correzione) * -1)
            if x >= distanza_max:
                break
        self.movement_motors.stop()
        run_multithreading = True
        runSmall = True
        multithreading = 0
        return

    def seguiLinea(self, distanza, velocità, lato, multithreading=None):
        global Kp, Ki, Kd, run_multithreading, runSmall, colorSensor, stop

        if multithreading == None:
            run_multithreading = False

        errore = 0
        erroreVecchio = 0
        integrale = 0
        derivata = 0
        loop = True

        if distanza < 0:
            distanza = abs(distanza)

        invert = 1
        if lato == 'sinistra':
            invert = 1
        elif lato == 'destra':
            invert = -1

        self.left_Startvalue = self.leftMotor.get_degrees_counted()
        self.right_Startvalue = self.rightMotor.get_degrees_counted()
        distanzaCompiuta = ottieniDistanzaCompiuta(self)

        while loop:
            if self.spike.left_button.is_pressed():
                skip()
                return

            if run_multithreading:
                next(multithreading)

            distanzaCompiuta = ottieniDistanzaCompiuta(self)
            calcoloPID(velocità)
            erroreVecchio = errore
            errore = colorSensor.get_reflected_light() - 50
            integrale += errore
            derivata = errore - erroreVecchio
            correzione = (errore * Kp + integrale * Ki + derivata * Kd) * invert
            correzione = max(-100, min(correzione, 100))
            self.movement_motors.start_at_power(int(velocità), int(correzione))

            if distanzaCompiuta >= distanza:
                loop = False

        self.movement_motors.stop()
        run_multithreading = True
        runSmall = True
        multithreading = 0
        return

    def motoriMovimento(self, distanza, sterzo, velocità):
        global stop

        if self.spike.left_button.is_pressed():
            skip()
            return
        if not stop and velocità > 0:
            spike.light_matrix.show_image("GO_UP")
        elif not stop and velocità < 0:
            spike.light_matrix.show_image("GO_DOWN")
        else:
            return
        movement_motors.move(distanza, unit="degrees", steering=sterzo, speed=velocità)
        return

    def muoviMotore(self,porta,gradi,velocità):
        """
        porta = (C,D)
        gradi = distanza
        velocità"""

        if self.spike.left_button.is_pressed():
            skip()
            return
        if not stop  and (porta == C or porta == D):
            spike.light_matrix.show_image("TARGET")
        elif not stop and (porta == motoreDestro or porta == motoreSinistro):
            spike.light_matrix.show_image("PACMAN")
        else:
            return
        porta.run_for_degrees(gradi,velocità)



def decelerate(degrees,setdegrees): 
    # potrebbe essere un idea migliore la radice
    maxSpeed = 100
    vIncrease = (maxSpeed-30)/2
    vMove = 30 + vIncrease # la posizione della cosinusoide risulta in funzione della velocità massima (opzionale ma figo) cos(x*b)*w +t
    speed = cos(degrees*(pi/setdegrees))*vIncrease+vMove
    print("Velocità della ruota dominante: " + str(speed))
    return int(speed)

def accelerate():  
    pass  
"""def map_range(x,in_min,in_max,out_min,out_max):
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min"""
    
def resetGyroValue():
    global gyroValue, stop, spike
    if spike.left_button.is_pressed():
        skip()
        return
    spike.motion_sensor.reset_yaw_angle()
    gyroValue = 0

def calcoloPID(velocità):
    global Kp
    global Ki
    global Kd
    global gyroValue, stop, spike
    if spike.left_button.is_pressed():
        skip()
        return

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

def avviaMotore(gradi, velocità, porta, spike):
    global runSmall, run_multithreading, stop

    while runSmall:
        if spike.left_button.is_pressed():
            skip()
            return
        motor = Motor(porta)
        motor.set_degrees_counted(0)

        loop_small = True
        while loop_small:
            if spike.left_button.is_pressed():
                skip()
                return
            distanzaPercorsa = motor.get_degrees_counted()
            motor.start_at_power(velocità)
            if (abs(distanzaPercorsa) > abs(gradi)):
                loop_small = False
            yield

        motor.stop()
        runSmall = False
        run_multithreading = False
    yield

def ottieniDistanzaCompiuta(data):
    global stop, spike

    if spike.left_button.is_pressed():
        skip()
        return

    distanzaCompiuta = (
                    abs(data.motoreSinistro.get_degrees_counted() - data.left_Startvalue) +
                    abs(data.motoreDestro.get_degrees_counted() - data.right_Startvalue)) / 2

    return distanzaCompiuta

def normalize_angle(angle):
    global stop, spike

    if spike.left_button.is_pressed():
        skip()
        return

    while angle > 180:
        angle -= 360
    while angle < -180:
        angle += 360
    return angle

def wait(timer):
    if spike.left_button.is_pressed():
        print("Chiamo skip")
        skip()
        return
    if not stop:
        spike.light_matrix.show_image("TORTOISE")
        sleep(timer)
    return


def race(program):
    mv = Movimenti(spike, 'A', 'B', movement_motors)
    global stop
    stop = False
    print("Avvio missione " + str(program))
    if program == 1:
        mv.ciroscopio(300,1)
        mv.ciroscopio(180,1)
        """mv.vaiDrittoPID(1300, 65)
        mv.motoriMovimento(1600,0,-90)"""
        return
    if program == 2:
        #prendere il sub e portarlo a destinazione, cambiare base 2° fine da destra
        multi = avviaMotore(80,20,"D", spike)
        mv.vaiDrittoPID(1450,50,multi)
        mv.ciroscopio(90,-1)
        mv.vaiDrittoPID(120,30)
        mv.muoviMotore(D,45,-20) 
        mv.motoriMovimento(-300,0,50)
        mv.oipocsoric(88,1)
        multi = avviaMotore(45,20,"D", spike)
        mv.vaiDrittoPID(100,50,multi)
        mv.motoriMovimento(200,0,-50)
        wait(0.1)
        mv.muoviMotore(D,45,-20)
        mv.ciroscopio(5,-1)
        mv.vaiDrittoPID(150, 50)
        mv.ciroscopio(5,1)
        mv.muoviMotore(D,40,100) 
        mv.motoriMovimento(2500,-10,-100)
        return
    if program == 3:
        #alzare la vela della barca + squalo 4° fine da destra
        multithreading = avviaMotore(120, -50, 'D', spike)
        mv.vaiDrittoPID(1520, 50, multithreading=multithreading)
        mv.ciroscopio(90, 1)
        mv.vaiDrittoPID(615 , 50)
        mv.motoriMovimento(200,0,-50)
        mv.muoviMotore(motoreSinistro,630, 50)
        mv.ciroscopio(12, -1)
        mv.vaiDrittoPID(340, 50)
        #da questo momento in poi la variabile stop non può mai diventare true perché sono tutte funzioni standard di spike, quindi è inutile fare il controllo
        mv.muoviMotore(D,150, 80)
        mv.motoriMovimento(300,-70,-50)
        mv.muoviMotore(D,90, -100)
        mv.motoriMovimento(1300,0,-100)
        return
    if program == 4:
        #2° fine da 2° grande da sinistra?
        mv.vaiDrittoPID(400, 50)
        wait(0.2)
        mv.motoriMovimento(450,0,-100)
        return
    if program == 5:
        #5° da sinistra
    #2° linea fine
        mv.muoviMotore(D,40 , -80)
        mv.vaiDrittoPID(320, 40)
        mv.ciroscopio(90, 1)
        mv.vaiDrittoPID(330, 50)
        multithreading = avviaMotore(40 , 40 , "D",spike)
        mv.vaiDrittoPID(1100, 50, multithreading=multithreading)
        mv.muoviMotore(D,65, -80)
        mv.ciroscopio(58, -1)
        mv.motoriMovimento(170,0,-30)
        mv.ciroscopio(51,1) #post squalo
        mv.motoriMovimento(250,0,-60)
        mv.muoviMotore(D,65, 60)
        mv.vaiDrittoPID(600, 50)
        mv.muoviMotore(C,90, -70)
        mv.motoriMovimento(500,0,-15)
        mv.muoviMotore(D,85, -80)
        mv.motoriMovimento(200,0,-100)
        mv.ciroscopio(20,-1)
        mv.vaiDrittoPID(900,70)
        mv.ciroscopio(35,1)
        mv.vaiDrittoPID(1500,90)
        return
    if program == 6:
        mv.vaiDrittoPID(150, 50)
        mv.ciroscopio(51, -1)
        mv.vaiDrittoPID(1400, 50) 
        mv.ciroscopio(60,1)
        mv.vaiDrittoPID(450,50)
        mv.ciroscopio(72, 1)
        mv.vaiDrittoPID(350, 50) 
        mv.muoviMotore(C,-720,100)
        mv.vaiDrittoPID(390,40)
        mv.muoviMotore(C,160,-50)
        mv.ciroscopio(12,1)
        mv.vaiDrittoPID(230,50)
        mv.motoriMovimento(-400,10,30)
        mv.ciroscopio(80, 1) 
        mv.motoriMovimento(1500,-11, 100)            
        return
    if program == 7:
        #10° da destra
        """
        mv.vaiDrittoPID(1730, 50) # partenza
        mv.motoriMovimento(-250,0,30)
        mv.ciroscopio(45, 1) # guarda balena
        mv.vaiDrittoPID(360, 50)
        mv.vaiDrittoPID(70, 25) # scopa la balena
        wait(0.5)
        mv.motoriMovimento(600,0,-75) #torna indietro
        mv.motoriMovimento(200,90,-50) #curva in retro
        mv.motoriMovimento(1500,10,-100) #base 
        wait(2.5)
        mv.motoriMovimento(1100,0,-80) #polipo
        mv.vaiDrittoPID(850,100)"""
        mv.vaiDrittoPID(1730, 50) # partenza
        mv.motoriMovimento(-250,0,30)
        mv.ciroscopio(45, 1) # guarda balena
        mv.vaiDrittoPID(360, 50)
        mv.motoriMovimento(70,0, 25) # scopa la balena
        wait(0.5)
        mv.motoriMovimento(600,0,-75) #torna indietro
        mv.motoriMovimento(200,90,-50) #curva in retro
        mv.motoriMovimento(1500,0,-100) #base 
        wait(2.5)
        mv.motoriMovimento(1100,0,-100) #polipo
        mv.vaiDrittoPID(850,100)
        return
    if program == 8:
        #2°  dalla 2 linea grande
        schivabarca = avviaMotore(5, -50, "D", spike)
        mv.vaiDrittoPID(1150,50,multithreading=schivabarca)
        mv.ciroscopio(60,-1)
        mv.vaiDrittoPID(1150,60)
        mv.muoviMotore(D,-50,30)
        wait(1)
        mv.ciroscopio(61,-1)
        mv.vaiDrittoPID(400,50)
        mv.ciroscopio(32,1)
        mv.vaiDrittoPID(200,40)
        mv.ciroscopio(34,1)
        mv.motoriMovimento(-350,0,60)
        mv.ciroscopio(110,1)
        return
    
def main():
    global programma_selezionato
    spike.light_matrix.write(1)
    spike.status_light.on(colors[0])
    print("Waiting for start")
    while True:
        #selezione programma
        if spike.right_button.is_pressed() and spike.left_button.is_pressed():
            break
        elif spike.right_button.is_pressed():
            sleep(0.50)
            programma_selezionato += 1
            if programma_selezionato == 9:
                print("programma a 9,reset")
                programma_selezionato = 1
            print("Missione selezionata:" + str(programma_selezionato))
            spike.light_matrix.write(programma_selezionato)
            spike.status_light.on(colors[programma_selezionato-1])
        #esecuzione programma
        elif spike.left_button.is_pressed():
            sleep(0.50)
            print("AVVIO il programma: " + str(programma_selezionato))
            race(programma_selezionato)
            programma_selezionato += 1
            print("Concluso il programma: " + str(programma_selezionato))
            if programma_selezionato == 9:
                print("programma a 9,reset")
                programma_selezionato = 1
            spike.light_matrix.write(programma_selezionato)
            spike.status_light.on(colors[programma_selezionato-1])
main()

sys.exit("Normalmente questo messaggio non verrà mai visto")
