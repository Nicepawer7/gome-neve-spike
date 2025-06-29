# LEGO type:advanced slot:0 autostart
from sys import exit
import hub # type: ignore
from time import sleep
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
                if self.programma_selezionato == 9:
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
        """
            Il metodo __init__ in una classe Python è un metodo speciale chiamato costruttore.
            Viene automaticamente invocato ogni volta che una nuova istanza (oggetto) della classe viene creata.
            Il suo scopo principale è inizializzare gli attributi dell'oggetto con valori specificati al momento della creazione dell'oggetto.
        """
        self.spike = spike
        self.manager = manager
        self.motoreSinistro = Motor('A')
        self.motoreDestro = Motor('B')
        self.movement_motors = MotorPair('A', 'B')
        self.pid = self.PID(spike,manager,self)
        self.ciroscopio = self.Ciroscopio(spike,self.movement_motors,manager)

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

            def vaiDrittoPID(self,distanza,velocitàMax = 80,multithreading = None):
                '''
                distanza:
                velocità:
                multithreading:
                    multithreading = avviaMotore(5, 100, 'C')'''
                self.distanza = distanza
                self.velocitàMax = velocitàMax
                distanzaCompiuta = 0
                dt = 0.001
                if not Manager.stop:
                    print("Avvio vai dritto pid")
                    if multithreading == None:
                        self.run_multithreading = False

                    target = self.spike.motion_sensor.get_yaw_angle()
                    errore = 0
                    erroreVecchio = 0
                    integrale = 0
                    derivata = 0

                    if distanza < 0:
                        print('ERR: distanza < 0')
                        distanza = abs(distanza)

                    self.left_Startvalue = self.movimenti.motoreSinistro.get_degrees_counted()
                    self.right_Startvalue = self.movimenti.motoreDestro.get_degrees_counted()
                    self.spike.light_matrix.show_image("ARROW_N")

                    while self.distanza >= distanzaCompiuta:
                        if self.spike.left_button.is_pressed():
                            self.manager.skip()
                            self.spike.movement_motors.stop()
                            return
                        if self.run_multithreading:
                            next(multithreading)
                        angolo = self.spike.motion_sensor.get_yaw_angle()
                        distanzaCompiuta = self.ottieniDistanzaCompiuta()
                        errore = angolo - target
                        integrale += errore * dt
                        derivata = errore - erroreVecchio
                        correzione = round(errore * self.kp + integrale * self.ki + derivata * self.kd)
                        correzione = max(-100, min(correzione, 100))
                        erroreVecchio = errore
                        #velocità = 50
                        velocità = self.calcoloVelocità(distanzaCompiuta,distanza)
                        #print("Correzione:" + str(correzione) + " Velocità: " + str(velocità))
                        self.calcoloPID(velocità)
                        self.movimenti.movement_motors.start_at_power(velocità, -correzione) # in base a gesù ci va un meno
                        if distanzaCompiuta == None:
                            distanzaCompiuta = 0.1


                    self.movimenti.movement_motors.stop()
                    self.run_multithreading = True
                    self.runSmall = True
                    multithreading = 0
                    self.manager.wait(0.2)
                    print("Finito pid")
                    return

            def calcoloVelocità(self,distanzaCompiuta,distanza):
                kCurva = distanza/5
                velocità = 0
                if distanzaCompiuta < kCurva:
                    velocità = radice(((((distanzaCompiuta-kCurva)**2)/kCurva**2)-1)*(-(self.velocitàMax-40)**2))+40
                elif kCurva <= distanzaCompiuta <= distanza-kCurva:
                    velocità = self.velocitàMax
                elif distanza-kCurva<= distanzaCompiuta < distanza:
                    velocità = (radice(((((distanzaCompiuta-distanza+kCurva)**2)/kCurva**2)-1)*(-(self.velocitàMax-30)**2))+30)
                return int(velocità)

            def calcoloPID(self,velocità):
                if self.spike.left_button.is_pressed():
                    self.manager.skip()
                    return

                if velocità == 100:
                    self.kp = 6
                    self.ki = 0.25
                    self.kd = 0
                elif 100 > velocità >= 90:
                    self.kp = 6
                    self.ki = 0.3
                    self.kd = 0
                elif 90 > velocità >= 80:
                    self.kp = 7
                    self.ki = 0.30
                    self.kd = 1
                elif 80 > velocità >= 70:
                    self.kp = 7
                    self.ki = 0.35
                    self.kd = 1
                elif 70 > velocità >= 60:
                    self.kp = 8
                    self.ki = 0.30
                    self.kd = 1
                elif 60 > velocità >= 50:
                    self.kp = 8
                    self.ki = 0.3
                    self.kd = 1
                elif 50 > velocità >= 40:
                    self.kp = 17
                    self.ki = 0.4
                    self.kd = 1
                elif 40 > velocità :
                    self.kp = 25
                    self.ki = 0.5
                    self.kd = 1

            def ottieniDistanzaCompiuta(self):
                if self.spike.left_button.is_pressed():
                    self.manager.skip()
                    return
                distanzaCompiuta = (abs(self.movimenti.motoreSinistro.get_degrees_counted() - self.left_Startvalue) + abs(self.movimenti.motoreDestro.get_degrees_counted() - self.right_Startvalue)) / 2
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

        def ciroscopio(self, angolo, verso=1):
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
                    while gyroValue <= angolo:
                        gyroValue = self.spike.motion_sensor.get_yaw_angle()
                        if prec > gyroValue:
                            gyroValue = 360 + gyroValue
                        else:
                            prec = gyroValue
                        speed = self.decelerate(gyroValue,angolo)
                        self.movement_motors.start_tank_at_power(speed,speed * -1 )
                        if self.spike.left_button.is_pressed():
                            self.manager.skip()
                            return
                elif verso == -1:
                    print("Inizio curva avanti verso sinistra")
                    self.spike.light_matrix.show_image("ARROW_NW")
                    prec = 1 #valore iniziale per il controllo del valore precedente
                    while abs(gyroValue) <= angolo:
                        gyroValue = self.spike.motion_sensor.get_yaw_angle()
                    if prec < gyroValue:
                        gyroValue = 360 - gyroValue
                    else:
                        prec = gyroValue
                    speed = self.decelerate(gyroValue,angolo)
                    self.movement_motors.start_tank_at_power(speed * -1, speed)
                    if self.spike.left_button.is_pressed():
                        self.manager.skip()
                        return
            self.movement_motors.stop()
            print("Fine curva avanti")
            self.manager.wait(0.2)
            return

        def oipocsoric(self, angolo, verso=1):
            if not Manager.stop:
                if verso not in [1, -1]:
                    raise ValueError("Il verso deve essere 1 (destra) o -1 (sinistra)")
                self.spike.motion_sensor.reset_yaw_angle()
                gyroValue = self.spike.motion_sensor.get_yaw_angle()
                angolo -= 2
                if verso == 1:
                    print("Inizio curva indietro verso destra")
                    prec = -1
                    self.spike.light_matrix.show_image("ARROW_SE")
                    while gyroValue <= angolo:
                        gyroValue = self.spike.motion_sensor.get_yaw_angle()
                        if prec > gyroValue:
                            gyroValue = 360 + gyroValue
                        else:
                            prec = gyroValue
                        speed = self.decelerate(gyroValue,angolo)
                        self.movement_motors.start_tank_at_power(speed, speed * -1)
                        if self.spike.left_button.is_pressed():
                            self.manager.skip()
                            self.movement_motors.stop()
                            return
                elif verso == -1:
                    print("Inizio curva indietro verso sinistra")
                    self.spike.light_matrix.show_image("ARROW_SW")
                    prec = 1
                    while abs(gyroValue) <= angolo + 1:
                        gyroValue = self.spike.motion_sensor.get_yaw_angle()
                        if prec < gyroValue:
                            gyroValue = 360 - gyroValue
                        else:
                            prec = gyroValue
                        speed = self.decelerate(gyroValue,angolo)
                        self.movement_motors.start_tank_at_power(speed * -1, speed)
                        if self.spike.left_button.is_pressed():
                            self.manager.skip()
                            self.movement_motors.stop()
                            return
                self.movement_motors.stop()
                print("Fine curva dietro")
                self.manager.wait(0.2)
                return

        def decelerate(self,degrees,setdegrees,maxSpeed=100):
            vIncrease = (maxSpeed-30)/2
            vMove = 30 + vIncrease # la posizione della cosinusoide risulta in funzione della velocità massima (opzionale ma figo) cos(x*b)*w +t
            if not Manager.stop:
                if self.spike.left_button.is_pressed():
                    self.manager.skip()
                    return
                elif degrees <= setdegrees-setdegrees/3 and setdegrees > 30 and setdegrees < 260:
                    speed = cos(degrees*(pi/(setdegrees-(setdegrees/3))))*vIncrease+vMove
                elif setdegrees > 260:
                    speed = cos(degrees*(pi/(setdegrees)))*vIncrease+vMove
                else:
                    speed = 30
            return int(speed)

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

    def muoviMotore(self,porta,gradi,velocità = 100):
        """
        porta = (C,D)
        gradi = distanza
        velocità"""

        if self.spike.left_button.is_pressed():
            porta.stop()
            self.manager.skip()
            return
        if not Manager.stopand (porta == C or porta == D):
            self.spike.light_matrix.show_image("TARGET")
        elif not Manager.stop and (porta == self.motoreDestro or porta == self.motoreSinistro):
            self.spike.light_matrix.show_image("PACMAN")
        else:
            return
        porta.run_for_degrees(gradi,velocità)

def race(program):
    Manager.stop = False
    print("Avvio missione " + str(program))
    if program == 1:
        pid.vaiDrittoPID(3450)
        exit()
    if program == 2:
        #prendere il sub e portarlo a destinazione, cambiare base 2° fine da destra
        """multi = avviaMotore(80,20,"D",self.spike)
        mv.vaiDrittoPID(1450,50,multi)
        mv.ciroscopio(90,-1)
        mv.vaiDrittoPID(120,30)
        mv.muoviMotore(D,45,-20)
        mv.motoriMovimento(-300,0,50)
        mv.oipocsoric(88,1)
        multi = avviaMotore(45,20,"D",self.spike)
        mv.vaiDrittoPID(100,50,multi)
        mv.motoriMovimento(200,0,-50)
        wait(0.1)
        mv.muoviMotore(D,45,-20)
        mv.ciroscopio(5,-1)
        mv.vaiDrittoPID(150, 50)
        mv.ciroscopio(5,1)
        mv.muoviMotore(D,40,100)
        mv.motoriMovimento(2500,-10,-100)
        return"""
    if program == 3:
        #alzare la vela della barca + squalo 4° fine da destra
        """multithreading = avviaMotore(120, -50, 'D', self.spike)
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
        return"""
    if program == 4:
        #2° fine da 2° grande da sinistra?
        """mv.vaiDrittoPID(400, 50)
        wait(0.2)
        mv.motoriMovimento(450,0,-100)
        return"""
    if program == 5:
        #5° da sinistra
    #2° linea fine
        """mv.muoviMotore(D,40 , -80)
        mv.vaiDrittoPID(320, 40)
        mv.ciroscopio(90, 1)
        mv.vaiDrittoPID(330, 50)
        multithreading = avviaMotore(40 , 40 , "D",self.spike)
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
        return"""
    if program == 6:
        """mv.vaiDrittoPID(150, 50)
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
        return"""
    if program == 7:
        """#10° da destra
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
        return"""
    if program == 8:
        """#2°dalla 2 linea grande
        schivabarca = avviaMotore(5, -50, "D", self.spike)
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
        return"""
    return


manager = Manager(spike)
mv = Movimenti(spike,manager)
pid = mv.pid
cr = mv.ciroscopio
manager.manager()

print("FINE")
