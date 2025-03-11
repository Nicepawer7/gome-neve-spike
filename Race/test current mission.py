# LEGO type:advanced slot:0 autostart

import sys, time, hub
from spike import PrimeHub, Motor, MotorPair, ColorSensor
from hub import battery

spike = PrimeHub()
colors = ('green','red','blue','yellow','orange','pink','violet','azure')
movement_motors = MotorPair('A', 'B')
motoreSinistro = Motor('A')
motoreDestro = Motor('B')
C = Motor('C')
D = Motor('D')
colorSensor = ColorSensor('E')
Kp = 0
Ki = 0
Kd = 0
stop = False
run_multithreading = True
gyroValue = 0
runSmall = True
def skip():
    global stop
    stop = True
    spike.light_matrix.show_image("NO")
    time.sleep(0.30)

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
                movement_motors.start_tank_at_power(30, -25)
                while gyroValue < target - 1:
                    gyroValue = spike.motion_sensor.get_yaw_angle()
                    if self.spike.left_button.is_pressed():
                        skip()
                        movement_motors.stop()
                        return
                movement_motors.stop()
            elif verso == -1:                
                spike.light_matrix.show_image("ARROW_NW")
                movement_motors.start_tank_at_power(-25, 30)
                while gyroValue > target + 1:
                    gyroValue = spike.motion_sensor.get_yaw_angle()
                    if self.spike.left_button.is_pressed():
                        skip()
                        movement_motors.stop()
                        return
                movement_motors.stop()
            wait(0.2)

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
                movement_motors.start_tank_at_power(25, -30)
                while gyroValue < target - 1:
                    gyroValue = spike.motion_sensor.get_yaw_angle()
                    if self.spike.left_button.is_pressed():
                        skip()
                        movement_motors.stop()
                        return
                movement_motors.stop()
            elif verso == -1:
                spike.light_matrix.show_image("ARROW_SW")
                movement_motors.start_tank_at_power(-30, 25)
                while gyroValue > target + 1:
                    gyroValue = spike.motion_sensor.get_yaw_angle()
                    if self.spike.left_button.is_pressed():
                        skip()
                        movement_motors.stop()
                        return
                movement_motors.stop()
            wait(0.2)

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
        time.sleep(timer)
    return
mv = Movimenti(spike, 'A', 'B', movement_motors)
#inizio -------------------------------------------------------------------------------------------------------------------------------------
def main():
    mv.vaiDrittoPID(1470, 50) # partenza
    mv.muoviMotore(motoreDestro,-150,30)
    mv.muoviMotore(motoreSinistro,80,30)
    mv.muoviMotore(motoreDestro,-100,30)
    mv.muoviMotore(motoreSinistro,120,-30)
    mv.vaiDrittoPID(200, 50)
    mv.vaiDrittoPID(100, 20) # scopa la balena
    wait(0.5)
    mv.motoriMovimento(600,0,-75) #torna indietro
    mv.motoriMovimento(200,90,-50) #curva in retro
    mv.motoriMovimento(1500,0,-100) #base 
    wait(2.5)
    mv.motoriMovimento(1100,0,-100) #polipo
    mv.vaiDrittoPID(850,100)
    return

main()
while True:
    if spike.right_button.is_pressed():
        stop = False
        wait(1)
        main()
    if spike.right_button.is_pressed() and spike.left_button.is_pressed():
        crash()