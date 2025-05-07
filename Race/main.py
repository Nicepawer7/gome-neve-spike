# LEGO type:advanced slot:0 autostart
from sys import exit
import hub # type: ignore
from time import sleep
from time import ticks_us
from spike import PrimeHub, Motor, MotorPair # type: ignore
from hub import battery # type: ignore
from math import cos
from math import sqrt as radice
from math import pi

C = Motor('C')
D = Motor('D')
spike = PrimeHub()



class Manager:
    stop = False
    def __init__(self,spike):
        self.spike = spike
        self.colors = ('green','red','blue','yellow','orange','pink','violet','azure')
        self.programma_selezionato = 1
        self.battery_manager()
    def manager(self,):
        self.spike.light_matrix.write(1)
        self.spike.status_light.on(self.colors[0])
        print("Waiting for start")
        while True:
            #selezione programma
            if self.spike.right_button.is_pressed() and self.spike.left_button.is_pressed():
                break
            elif self.spike.right_button.is_pressed():
                sleep(0.50)
                self.programma_selezionato += 1
                if self.programma_selezionato >= 9:
                    print("programma a 9,reset")
                    self.programma_selezionato = 1
                print("Missione selezionata:" + str(self.programma_selezionato))
                self.spike.light_matrix.write(self.programma_selezionato)
                self.spike.status_light.on(self.colors[self.programma_selezionato-1])
            #esecuzione programma
            elif self.spike.left_button.is_pressed():
                sleep(0.50)
                print("AVVIO il programma: " + str(self.programma_selezionato))
                race(self.programma_selezionato)
                self.programma_selezionato += 1
                print("Concluso il programma: " + str(self.programma_selezionato))
                if self.programma_selezionato == 9:
                    print("programma a 9,reset")
                    self.programma_selezionato = 1
                self.spike.light_matrix.write(self.programma_selezionato)
                self.spike.status_light.on(self.colors[self.programma_selezionato-1])

    def skip(self):
        self.programma_selezionato -= 1
        Manager.stop = True
        self.spike.light_matrix.show_image("NO")
        Movimenti.movement_motors.stop()
        sleep(0.30)
    def wait(self,timer):
        if self.spike.left_button.is_pressed():
            print("Chiamo skip")
            self.skip()
            return
        if not Manager.stop:
            self.spike.light_matrix.show_image("TORTOISE")
            sleep(timer)
        return
    def battery_manager(self):
        BATTERY = '\033[32m'
        BATTERY_LOW = '\033[31m'
        ENDC = '\033[0m'
        voltage = battery.voltage()
        if voltage < 8000:
            print(BATTERY_LOW + "batteria scarica: " + str(voltage) + " \n ----------------------------- \n >>>> carica la batteria o cambiala <<<< \n ----------------------------- \n"+ ENDC)
        else:
            print(BATTERY + "livello batteria: " + str(voltage) + ENDC)

class Movimenti:
    movement_motors = MotorPair('A', 'B')
    def __init__(self,spike,manager):
        self.spike = spike
        self.manager = manager
        self.motoreSinistro = Motor('A')
        self.motoreDestro = Motor('B')
        self.movement_motors = MotorPair('A', 'B')
        self.pid = self.PID(spike,manager,self)
        self.cr = self.Ciroscopio(spike,self.movement_motors,manager)

    def avanti(self,distanza,verso = 1,velocitàMax = 90,multithreading = None):
            '''
            distanza:
            velocità:
            multithreading:
                multithreading = avviaMotore(5, 100, 'C')'''
            distanzaCompiuta = 0
            dt_start = 0
            self.spike.motion_sensor.reset_yaw_angle()
            if not Manager.stop:
                print("Avvio vai dritto pid")
                if multithreading == None:
                    self.run_multithreading = False
                if verso == -1:
                    self.movement_motors = MotorPair('B','A')

                errore = 0
                erroreVecchio = 0
                integrale = 0
                derivata = 0

                if distanza < 0:
                    print('ERR: distanza < 0')
                    distanza = abs(distanza)

                self.left_startValue = self.motoreSinistro.get_degrees_counted()
                self.right_startValue = self.motoreDestro.get_degrees_counted()
                self.spike.light_matrix.show_image("ARROW_N")

                while distanza >= distanzaCompiuta:
                    if self.spike.left_button.is_pressed():
                        self.manager.skip()
                        self.movement_motors.stop()
                        return
                    if self.run_multithreading:
                        next(multithreading)
                    errore = -self.spike.motion_sensor.get_yaw_angle()
                    distanzaCompiuta = self.pid.ottieniDistanzaCompiuta()
                    dt = (ticks_us() - dt_start)/1000000
                    dt_start = ticks_us()
                    integrale += errore * dt
                    derivata = (errore - erroreVecchio)/dt
                    erroreVecchio = errore
                    velocità = self.pid.calcoloVelocità(distanzaCompiuta,distanza,velocitàMax)
                    self.pid.calcoloPID(velocità)
                    correzione = round(errore * self.pid.kp + integrale * self.pid.ki + derivata * self.pid.kd)
                    correzione = max(-100, min(correzione, 100))
                    #print("Correzione: " + str(correzione) + " Proporzionale" + str(errore*self.pid.kp) + " Integrale: "+ str(integrale*self.pid.ki) + " Derivata " + str(derivata*self.pid.kd) + " Angolo: " + str(errore))
                    self.movement_motors.start_at_power(velocità, correzione)
                    if distanzaCompiuta == None:
                        distanzaCompiuta = 0.1

                print(distanzaCompiuta)
                self.movement_motors.stop()
                self.run_multithreading = True
                self.runSmall = True
                multithreading = 0
                self.manager.wait(0.2)
                if verso == -1:
                    self.movement_motors = MotorPair('A','B')
                print("Finito pid")
                return

    def ciroscopio(self, angolo, verso=1,maxSpeed = 90,bias = 0):
        if not Manager.stop:
            if verso not in [1, -1]:
                raise ValueError("Il verso deve essere 1 (destra) o -1 (sinistra)")
            self.spike.motion_sensor.reset_yaw_angle()
            gyroValue = self.spike.motion_sensor.get_yaw_angle()
            angolo -= 2
            if verso == 1:
                print("Inizio curva avanti verso destra")
                prec = -1 #valore iniziale per il controllo del valore precedente
                self.spike.light_matrix.show_image("ARROW_NE")
                while gyroValue <= angolo: #finchè angolo attuale minore di obbiettivo
                    gyroValue = self.spike.motion_sensor.get_yaw_angle()
                    if prec > gyroValue: #fondamnetalmente normalizzo l'angolo, se il valore precedente è più grande sono passato da 180 a -180
                        gyroValue = 360 + gyroValue
                    else:
                        prec = gyroValue
                    speed = self.cr.decelerate(gyroValue,angolo,maxSpeed)
                    self.movement_motors.start_tank_at_power(speed,(speed-bias) * -1 )
                    if self.spike.left_button.is_pressed():
                        self.manager.skip()
                        return
            elif verso == -1:
                print("Inizio curva avanti verso sinistra")
                self.spike.light_matrix.show_image("ARROW_NW")
                prec = 1 #valore iniziale per il controllo del valore giroscopio precedente
                while abs(gyroValue) <= angolo-1: #finchè angolo attuale minore di obbiettivo
                    gyroValue = self.spike.motion_sensor.get_yaw_angle()#fondamnetalmente normalizzo l'angolo, se il valore precedente è più piccolo sono passato da -180 a 180
                    if prec < gyroValue:
                        gyroValue = 360 - gyroValue
                    else:
                        prec = gyroValue
                    speed = self.cr.decelerate(gyroValue,angolo,maxSpeed)
                    self.movement_motors.start_tank_at_power((speed - bias)* -1, speed)
                    if self.spike.left_button.is_pressed():
                        self.manager.skip()
                        return
        print("Gyro" + str(gyroValue))
        self.movement_motors.stop()
        print("Fine curva avanti")
        self.manager.wait(0.2)
        return

    def motoriMovimento(self, distanza, sterzo = 0, velocità = 100):
        if self.spike.left_button.is_pressed():
            self.manager.skip()
            return
        if not Manager.stop and velocità > 0:
            self.spike.light_matrix.show_image("GO_UP")
        elif not Manager.stop and velocità < 0:
            self.spike.light_matrix.show_image("GO_DOWN")
        else:
            return
        self.movement_motors.move(distanza, unit="degrees", steering=sterzo, speed=velocità)
        return

    def muoviMotore(self,porta,gradi,direzione = 1,velocità = 100):
        """
        porta = (C,D)
        gradi = distanza
        velocità"""

        if self.spike.left_button.is_pressed():
            porta.stop()
            self.manager.skip()
            return
        if not Manager.stop and (porta == C or porta == D):
            self.spike.light_matrix.show_image("TARGET")
        elif not Manager.stop and (porta == self.motoreDestro or porta == self.motoreSinistro):
            self.spike.light_matrix.show_image("PACMAN")
        else:
            return
        print(gradi)
        gradi *= direzione
        print(gradi)
        porta.run_for_degrees(gradi,velocità)

    class PID:
            def __init__(self,spike,manager,istanza):
                self.spike = spike
                self.manager = manager
                self.movimenti = istanza
                self.run_multithreading = True
                self.runSmall = True
                self.kp = 0
                self.ki = 0
                self.kd = 0

            def calcoloVelocità(self,distanzaCompiuta,distanza,velocitàMax):
                #kCurva = distanza/5
                velocitàMin = 20 # minimo di 5-8 con fattore di sicurezza 150%
                velocità = 0
                """if distanzaCompiuta < kCurva:
                    velocità = radice(((((distanzaCompiuta-kCurva)**2)/kCurva**2)-1)*(-(velocitàMax-40)**2))+40
                elif kCurva <= distanzaCompiuta <= distanza-kCurva:
                    velocità = velocitàMax
                elif distanza-kCurva<= distanzaCompiuta < distanza:
                    velocità = (radice(((((distanzaCompiuta-distanza+kCurva)**2)/kCurva**2)-1)*(-(velocitàMax-30)**2))+30)"""
                d = distanza
                """d = distanza - (distanza/((distanza*8)/3004))
                if distanzaCompiuta < d:
                    velocità = cos((distanzaCompiuta+d/2)*(2*pi)/d)*((velocitàMax-velocitàMin)/2)+((velocitàMax+velocitàMin)/2)
                elif d < distanzaCompiuta < distanza:
                    velocità = velocitàMin"""
                if distanzaCompiuta < distanza/2:
                    velocitàMin = 40
                if distanza > 1500:
                    velocitàMax = 200
                velocità = cos((distanzaCompiuta+d/2)*(2*pi)/d)*((velocitàMax-velocitàMin)/2)+((velocitàMax+velocitàMin)/2)
                if velocità > 100:
                    velocità = 100
                #potrei frenare con velocità più bassa di quella necessaria a muoversi
                return int(velocità)

            def calcoloPID(self,velocità):
                if self.spike.left_button.is_pressed():
                    self.manager.skip()
                    return
                if velocità == 100:
                    self.kp = 2.3
                    self.ki = 4
                    self.kd = 0.42
                elif 100 > velocità >= 90:
                    self.kp = 2.7
                    self.ki = 4
                    self.kd = 0.4
                elif 90 > velocità >= 80:
                    self.kp = 2.8
                    self.ki = 3.8
                    self.kd = 0.4
                elif 80 > velocità >= 70:
                    self.kp = 2.5
                    self.ki = 3.6
                    self.kd = 0.42
                elif 70 > velocità >= 60:
                    self.kp = 2.5
                    self.ki = 3.6
                    self.kd = 0.42
                elif 60 > velocità >= 50:
                    self.kp = 2.7
                    self.ki = 3.4
                    self.kd = 0.44
                elif 50 > velocità >= 40:
                    self.kp = 2.8
                    self.ki = 3.3
                    self.kd = 0.48
                elif 40 > velocità :
                    self.kp = 2.9
                    self.ki = 3.3
                    self.kd = 0.48

            def ottieniDistanzaCompiuta(self):
                if self.spike.left_button.is_pressed():
                    self.manager.skip()
                    return
                distanzaCompiuta = (abs(self.movimenti.motoreSinistro.get_degrees_counted() - self.movimenti.left_startValue) + abs(self.movimenti.motoreDestro.get_degrees_counted() - self.movimenti.right_startValue)) / 2
                return distanzaCompiuta

            def avviaMotore(self,porta,gradi,velocità = 100):
                while self.runSmall:
                    if self.spike.left_button.is_pressed():
                        self.manager.skip()
                        return
                    porta.set_degrees_counted(0)

                    loop_small = True
                    while loop_small:
                        if spike.left_button.is_pressed():
                            self.manager.skip()
                            return
                        distanzaPercorsa = porta.get_degrees_counted()
                        porta.start_at_power(velocità)
                        if (abs(distanzaPercorsa) > abs(gradi)):
                            loop_small = False
                        yield

                    porta.stop()
                    self.runSmall = False
                    self.run_multithreading = False
                yield

    class Ciroscopio:
        def __init__(self,spike,movement_motors,manager):
            self.spike = spike
            self.movement_motors = movement_motors
            self.manager = manager

        def decelerate(self,degrees,setdegrees,maxSpeed):
            vIncrease = (maxSpeed-30)/2
            vMove = 30 + vIncrease # la posizione della cosinusoide risulta in funzione della velocità massima (opzionale ma figo) cos(x*b)*w +t
            if not Manager.stop:
                if self.spike.left_button.is_pressed():
                    self.manager.skip()
                    return
                if degrees <= setdegrees-setdegrees/3 and setdegrees >= 30 and setdegrees < 260:
                    speed = cos(degrees*(pi/(setdegrees-(setdegrees/3))))*vIncrease+vMove
                elif setdegrees < 30 or 5 >= setdegrees - degrees:
                    speed = 25
                elif setdegrees > 260:
                    speed = cos(degrees*(pi/(setdegrees)))*vIncrease+vMove

                print("velocità" + str(speed))
            return int(speed)

def race(program):
    Manager.stop = False
    print("Avvio missione " + str(program))
    if program == 1:
        # primo quadrato piccolo rosso da sinistra
        mv.avanti(900)
        mv.muoviMotore(D,300,85,direzione=1)
    if program == 2:
        # 2° piccolo da destra base blu |TMG :)
        mv.avanti(300)
        mv.ciroscopio(30,-1)
        mv.avanti(1330)
        mv.ciroscopio(30,-1,maxSpeed=30)
        mv.avanti(500)
        mv.ciroscopio(27,-1)
        mv.avanti(800,-1,70)
        mv.muoviMotore(C,200)
        mv.ciroscopio(5,1)
        mv.avanti(1600)
        mv.muoviMotore(D,600,-1)
        mv.avanti(500)
        mv.muoviMotore(D,600)
        mv.ciroscopio(20,-1)
        mv.motoriMovimento(2500,-30)
        exit()
    if program == 3:
        pass
    if program == 4:
        pass
    if program == 5:
        mv.avanti(2500)
    if program == 6:
        mv.avanti(3000)
    if program == 7:
        mv.avanti(3500)
    if program == 8:
        mv.avanti(4000)
    return


manager = Manager(spike)
mv = Movimenti(spike,manager)
manager.manager()

print("FINE")
