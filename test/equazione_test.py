# PROGRAMMA PER TESTARE LA FUNZIONE equazione

from spike import PrimeHub, Motor, MotorPair, ColorSensor, Timer, wait_for_seconds, wait_until, hub

spike = PrimeHub()
motoreSinistro = Motor('A')
motoreDestro = Motor('B')
movement_motors = MotorPair('A', 'B')

class Movimenti:
    def __init__(self, spike, motoreSinistro, motoreDestro):
        self.spike = spike
        self.motoreSinistro = motoreSinistro
        self.motoreDestro = motoreDestro
        self.movement_motors = movement_motors

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
        
        while True:  # Inizia un ciclo infinito
            if run_multithreading:  #eseguire una funzione simultaneamente se definita nel parametro
                next(multithreading)

            x = ottieniDistanzaCompiuta(self)  # Ottiene la distanza percorsa dal robot
            target = equazione  # Calcola il valore target usando l'equazione fornita
            angolo_attuale = hub.motion_sensor.get_yaw_angle()  # Ottiene l'angolo attuale del robot
            errore = angolo_attuale - target  # Calcola l'errore tra l'angolo attuale e il target
            correzione = (errore * Kp)  # Calcola la correzione usando il controllo proporzionale
            self.movement_motors.start_at_power(int(velocità), int(correzione) * -1)  # Avvia i motori con la velocità e la correzione calcolate
            if x >= distanza_max:  # Se la distanza percorsa supera o eguaglia la distanza massima
                break  # Esce dal ciclo
        self.movement_motors.stop()  # Ferma i motori alla fine del movimento


def ottieniDistanzaCompiuta(data):

    distanzaCompiuta = (
                    abs(data.motoreSinistro.get_degrees_counted() - data.left_Startvalue) + 
                    abs(data.motoreDestro.get_degrees_counted() - data.right_Startvalue)) / 2

    return distanzaCompiuta


hub.motion.yaw_pitch_roll(0)
mv = Movimenti(spike, motoreSinistro, motoreDestro)
mv.equazione("inserire equazione", 100, 80)  # Esegue il movimento fino a 100 unità