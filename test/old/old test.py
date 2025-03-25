# LEGO type:advanced slot:0 autostart

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
            while loop:
                if self.spike.left_button.is_pressed():
                    stop()
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

                if distanzaCompiuta >= distanza:
                    loop = False

            self.movement_motors.stop()
            run_multithreading = True
            runSmall = True
            multithreading = 0
            time.sleep(0.2)
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
                movement_motors.start_tank_at_power(30, -25)
                while gyroValue < target - 1:
                    gyroValue = spike.motion_sensor.get_yaw_angle()
                    if self.spike.left_button.is_pressed():
                        stop()
                        movement_motors.stop()
                        return
                movement_motors.stop()
            elif verso == -1:
                movement_motors.start_tank_at_power(-25, 30)
                while gyroValue > target + 1:
                    gyroValue = spike.motion_sensor.get_yaw_angle()
                    if self.spike.left_button.is_pressed():
                        stop()
                        movement_motors.stop()
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
                        stop()
                        movement_motors.stop()
                        return
                movement_motors.stop()
            elif verso == -1:
                movement_motors.start_tank_at_power(-30, 25)
                while gyroValue > target + 1:
                    gyroValue = spike.motion_sensor.get_yaw_angle()
                    if self.spike.left_button.is_pressed():
                        stop()
                        movement_motors.stop()
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
                stop()
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
            stop()
            return
        if not stop:
            movement_motors.move(distanza, unit="degrees", steering=sterzo, speed=velocità)
            return

    def resetGyroValue(self):
        global gyroValue, stop, spike
        if spike.left_button.is_pressed():
            stop()
            return
        spike.motion_sensor.reset_yaw_angle()
        gyroValue = 0

    def calcoloPID(self, velocità):
        global Kp
        global Ki
        global Kd
        global gyroValue, stop, spike
        if spike.left_button.is_pressed():
            stop()
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

    def avviaMotore(self, gradi, velocità, porta, spike):
        global runSmall, run_multithreading, stop

        while runSmall:
            if spike.left_button.is_pressed():
                stop()
                return
            motor = Motor(porta)
            motor.set_degrees_counted(0)

            loop_small = True
            while loop_small:
                if spike.left_button.is_pressed():
                    stop()
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

    """def ottieniDistanzaCompiuta(data):
        global stop, spike

        if spike.left_button.is_pressed():
            stop()
            return

        distanzaCompiuta = (
                                   abs(data.motoreSinistro.get_degrees_counted() - data.left_Startvalue) +
                                   abs(data.motoreDestro.get_degrees_counted() - data.right_Startvalue)) / 2

        return distanzaCompiuta

    def normalize_angle(angle):
        global stop, spike

        if spike.left_button.is_pressed():
            stop()
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
        print(bcolors.BATTERY + "livello batteria: " + str(battery.voltage()) + bcolors.ENDC)"""

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

mv = Movimenti(spike, 'A', 'B', movement_motors)

#inzio ---------------------------------------------------------------------------------------------------------------------------------


#fine-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

print("Normalmente questo messaggio non verrà mai visto")
sys.exit()

