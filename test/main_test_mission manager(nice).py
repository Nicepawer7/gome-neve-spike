# LEGO type:standard slot:0

from spike import PrimeHub, Motor, MotorPair, ColorSensor
from hub import battery
import sys, time, hub

spike = PrimeHub()

colors = ('green','red','blue','yellow','orange','pink','violet','azure')

movement_motors = MotorPair('A', 'B')
motoreSinistro = Motor('A')
motoreDestro = Motor('B')
smallMotorC = Motor('C')
smallMotorD = Motor('D')
colorSensor = ColorSensor('E')
Kp = 0
Ki = 0
Kd = 0
stop = False
run_multithreading = True
gyroValue = 0
runSmall = True

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
            print("Not stop")
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
            while loop:
                if self.spike.left_button.is_pressed():
                    stop = True
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

                if distanzaCompiuta >= distanza:
                    loop = False

            self.movement_motors.stop()
            run_multithreading = True
            runSmall = True
            multithreading = 0
            time.sleep(0.2)
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
                movement_motors.start_tank_at_power(30, -25)
                while gyroValue < target - 1:
                    gyroValue = spike.motion_sensor.get_yaw_angle()
                    if self.spike.left_button.is_pressed():
                        stop = True
                        return
                movement_motors.stop()
            elif verso == -1:
                movement_motors.start_tank_at_power(-25, 30)
                while gyroValue > target + 1:
                    gyroValue = spike.motion_sensor.get_yaw_angle()
                    if self.spike.left_button.is_pressed():
                        stop = True
                        return
                movement_motors.stop()
            time.sleep(0.2)

    def oipocsoric(self, angolo, verso):
        global gyroValue, stop
        if not stop:
            if verso not in [1, -1]:
                raise ValueError("Il verso deve essere 1 (destra) o -1 (sinistra)")
            resetGyroValue()
            target = (normalize_angle(angolo)) * verso
            gyroValue = spike.motion_sensor.get_yaw_angle()
            if verso == 1:
                movement_motors.start_tank_at_power(25, -30)
                while gyroValue < target - 1:
                    gyroValue = spike.motion_sensor.get_yaw_angle()
                    if self.spike.left_button.is_pressed():
                        stop = True
                        return
                movement_motors.stop()
            elif verso == -1:
                movement_motors.start_tank_at_power(-30, 25)
                while gyroValue > target + 1:
                    gyroValue = spike.motion_sensor.get_yaw_angle()
                    if self.spike.left_button.is_pressed():
                        stop = True
                        return
                movement_motors.stop()
            time.sleep(0.2)

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
                stop = True
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
                stop = True
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
            stop = True
            return
        if not stop:
            movement_motors.move(distanza, unit="degrees", steering=sterzo, speed=velocità)
            return

    def resetGyroValue(self):
        global gyroValue, stop, spike
        if spike.left_button.is_pressed():
            stop = True
            return
        spike.motion_sensor.reset_yaw_angle()
        gyroValue = 0

    def calcoloPID(velocità):
        global Kp
        global Ki
        global Kd
        global gyroValue, stop, spike
        if spike.left_button.is_pressed():
            stop = True
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
                stop = True
                return
            motor = Motor(porta)
            motor.set_degrees_counted(0)

            loop_small = True
            while loop_small:
                if spike.left_button.is_pressed():
                    stop = True
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
            stop = True
            return

        distanzaCompiuta = (
                                   abs(data.motoreSinistro.get_degrees_counted() - data.left_Startvalue) +
                                   abs(data.motoreDestro.get_degrees_counted() - data.right_Startvalue)) / 2

        return distanzaCompiuta

    def normalize_angle(angle):
        global stop, spike

        if spike.left_button.is_pressed():
            stop = True
            return

        while angle > 180:
            angle -= 360
        while angle < -180:
            angle += 360
        return angle

    class bcolors:
        BATTERY = '\033[32m'
        BATTERY_LOW = '\033[31m'
        ENDC = '\033[0m'

    if battery.voltage() < 8000:
        print(bcolors.BATTERY_LOW + "batteria scarica: " + str(
            battery.voltage()) + " \n ----------------------------- \n >>>> carica la batteria o cambiala <<<< \n ----------------------------- \n" + bcolors.ENDC)
    else:
        print(bcolors.BATTERY + "livello batteria: " + str(battery.voltage()) + bcolors.ENDC)

    print(sys.version)
def equazione(self, equazione, distanza_max, velocità, multithreading = None):
    global Kp
    global run_multithreading, stop
    if multithreading == None:
        run_multithreading = False
    self.left_Startvalue = self.motoreSinistro.get_degrees_counted()
    self.right_Startvalue = self.motoreDestro.get_degrees_counted()
    x = ottieniDistanzaCompiuta(self)
    while True:
        if self.spike.left_button.is_pressed():
            stop = True
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

def motoriMovimento(self, distanza, sterzo, velocità):
    global stop

    if self.spike.left_button.is_pressed():
        stop = True
        return
    if not stop:
        movement_motors.move(distanza, unit="degrees", steering=sterzo, speed=velocità)
        return

def resetGyroValue():
    global gyroValue, stop, spike
    if spike.left_button.is_pressed():
        stop = True
        return
    spike.motion_sensor.reset_yaw_angle()
    gyroValue = 0

def calcoloPID(velocità):
    global Kp
    global Ki
    global Kd
    global gyroValue, stop, spike
    if spike.left_button.is_pressed():
        stop = True
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
            stop = True
            return
        motor = Motor(porta)
        motor.set_degrees_counted(0)

        loop_small = True
        while loop_small:
            if spike.left_button.is_pressed():
                stop = True
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
        stop = True
        return

    distanzaCompiuta = (
                    abs(data.motoreSinistro.get_degrees_counted() - data.left_Startvalue) +
                    abs(data.motoreDestro.get_degrees_counted() - data.right_Startvalue)) / 2

    return distanzaCompiuta

def normalize_angle(angle):
    global stop, spike

    if spike.left_button.is_pressed():
        stop = True
        return

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

print(sys.version)

def race(program):
    global stop
    stop = False
    print("Avvio missione " + str(program))
    if program == 1:
        mv.vaiDrittoPID(1300, 65)
        mv.motoriMovimento(1600,0,-90)
        return
    if program == 2:
        #prendere il sub e portarlo a destinazione, cambiare base 2° fine da destra
        multi = avviaMotore(80,20,"D", spike)
        mv.vaiDrittoPID(1450,50,multi)
        mv.ciroscopio(90,-1)
        mv.vaiDrittoPID(120,30)
        smallMotorD.run_for_degrees(45,-20) #queste funzioni della libreria spike non si fermano automaticamente se la variabile stop = True, quindi ci vuole un controllo prima di eseguirle
        mv.motoriMovimento(300,0,50) #la variabile stop non può mai diventare true perché la funzione è standard di spike, quindi è inutile fare il controllo
        mv.oipocsoric(88,1)
        multi = avviaMotore(45,20,"D", spike)
        mv.vaiDrittoPID(100,50,multi)
        mv.motoriMovimento(200,0,-50) #queste funzioni della libreria spike non si fermano automaticamente se la variabile stop = True, quindi ci vuole un controllo prima di eseguirle
        time.sleep(0.1)
        smallMotorD.run_for_degrees(45,-20) #la variabile stop non può mai diventare true perché la funzione è standard di spike, quindi è inutile fare il controllo
        mv.ciroscopio(5,-1)
        mv.vaiDrittoPID(150, 50)
        mv.ciroscopio(5,1)
        smallMotorD.run_for_degrees(50,100) #queste funzioni della libreria spike non si fermano automaticamente se la variabile stop = True, quindi ci vuole un controllo prima di eseguirle
        mv.motoriMovimento(2500,-10,-100) #la variabile stop non può mai diventare true perché la funzione è standard di spike, quindi è inutile fare il controllo
        return
    if program == 3:
        #alzare la vela della barca + squalo 4° fine da destra
        multithreading = avviaMotore(120, -50, 'D', spike)
        mv.vaiDrittoPID(1520, 50, multithreading=multithreading)
        mv.ciroscopio(90, 1)
        mv.vaiDrittoPID(615 , 50)
        mv.motoriMovimento(200,0,-50)
        motoreSinistro.run_for_degrees(630, 50)
        mv.ciroscopio(12, -1)
        mv.vaiDrittoPID(340, 50)
        #da questo momento in poi la variabile stop non può mai diventare true perché sono tutte funzioni standard di spike, quindi è inutile fare il controllo
        smallMotorD.run_for_degrees(150, 80)
        mv.motoriMovimento(300,-70,-50)
        smallMotorD.run_for_degrees(90, -100)
        mv.motoriMovimento(1300,0,-100)
        return
    if program == 4:
        #2° fine da 2° grande da sinistra?
        mv.vaiDrittoPID(400, 50)
        time.sleep(0.2)
        mv.motoriMovimento(450,0,-100)
        return
    if program == 5:
        #5° da sinistra
    #2° linea fine
        mv.vaiDrittoPID(269, 50)
        mv.ciroscopio(88, 1)
        time.sleep(0.1)
        mv.vaiDrittoPID(400, 50)
        multithreading = avviaMotore(40 , 40 , "D",spike)
        mv.vaiDrittoPID(900, 50, multithreading=multithreading)
        time.sleep(0.2)
        smallMotorD.run_for_degrees(65, -80)
        mv.ciroscopio(45, -1)
        time.sleep(0.1)
        mv.vaiDrittoPID(100 , 75)
        mv.motoriMovimento(375,-45,-50)
        mv.motoriMovimento(50,0,-50)
        smallMotorD.run_for_degrees(65, 60)
        time.sleep(0.5)
        mv.vaiDrittoPID(700, 50)
        smallMotorC.run_for_degrees(90, -70)
        mv.motoriMovimento(500,0,-15)
        time.sleep(0.2)
        smallMotorD.run_for_degrees(85, -80)
        mv.motoriMovimento(300,0,-100)
        mv.ciroscopio(30,-1)
        #mv.vaiDrittoPID(600,70)
        time.sleep(0.5)
        mv.motoriMovimento(2500,10,100)
        return
    if program == 6:
        mv.vaiDrittoPID(50, 50)
        mv.ciroscopio(48, -1)
        mv.vaiDrittoPID(1700, 50)
        mv.ciroscopio(9,-1)
        mv.ciroscopio(57,1)
        mv.vaiDrittoPID(200,50)
        mv.ciroscopio(85.0, 1)
        mv.vaiDrittoPID(1200, 50)
        mv.ciroscopio(13, 1)
        mv.vaiDrittoPID(200, 50)
        mv.motoriMovimento(330,0,-30)
        mv.ciroscopio(86, 1)
        mv.motoriMovimento(1300,-15,100)
        return
    if program == 7:
        #10° da destra
        mv.vaiDrittoPID(1500, 50)
        mv.ciroscopio(40, 1)
        mv.vaiDrittoPID(250, 50)
        smallMotorC.run_for_degrees(850, 100)
        time.sleep(0.5)
        smallMotorC.run_for_degrees(720, -100)
        mv.motoriMovimento(600,0,-75)
        mv.motoriMovimento(200,100,-50)
        mv.motoriMovimento(1500,0,-100)
        time.sleep(2)
        mv.motoriMovimento(1000,0,-100)
        mv.vaiDrittoPID(850,100)
        return
    if program == 8:
        #2°  dalla 2 linea grande
        multi = avviaMotore(5, -50, "D", spike)
        mv.vaiDrittoPID(1200,50,multithreading=multi)
        mv.ciroscopio(60,-1)
        mv.vaiDrittoPID(1030,75)
        smallMotorD.run_for_degrees(-60,30)
        time.sleep(1)
        mv.ciroscopio(52,-1)
        mv.vaiDrittoPID(520,50)
        mv.ciroscopio(38,1)
        mv.vaiDrittoPID(550,60)
        mv.motoriMovimento(700,-40,90)
        mv.vaiDrittoPID(900,90)
        return
programma_selezionato = 1
spike.status_light.on('green')
spike.light_matrix.write(programma_selezionato)
while True:
    stop = False
    time.sleep(0.5)
    #selezione programma
    print("Waiting for start")
    if spike.right_button.is_pressed():
        time.sleep(0.50)
        programma_selezionato += 1
        print("Missione selezionata:" + str(programma_selezionato))
        spike.light_matrix.write(programma_selezionato)
        if  programma_selezionato <= 8 and programma_selezionato >= 1:
            spike.status_light.on(colors[programma_selezionato-1])
        elif programma_selezionato == 9:
            programma_selezionato = 1
            spike.light_matrix.write(programma_selezionato)
            spike.status_light.on(colors[programma_selezionato-1])
    #esecuzione programma
    if spike.left_button.is_pressed():
        time.sleep(0.50) #se la variabile stop diventa True allora interrompi il ciclo di esecuzione
        spike.status_light.on(colors[programma_selezionato-1])
        print("AVVIO il programma: " + str(programma_selezionato))
        race(programma_selezionato)
        programma_selezionato = 2
        spike.light_matrix.write(programma_selezionato)
print("Sto per esplodere")
time.sleep(10)
sys.exit()