# PROGRAMMA PER TESTARE LA FUNZIONE ciroscopio

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

    def ciroscopio(self, angolo, verso, velocita=30):
        """
        Ruota il robot di un certo angolo in una direzione specifica.
        
        Parametri:
        angolo: Angolo di rotazione del robot (in gradi)
        verso: Direzione di rotazione (1 per destra, -1 per sinistra)
        velocita: Velocità di rotazione (predefinita a 30)
        """
        
        if verso not in [1, -1]:
            raise ValueError("Il verso deve essere 1 (destra) o -1 (sinistra)")  # Verifica che il verso sia valido, altrimenti solleva un errore
        
        angolo_attuale = normalize_angle(spike.motion_sensor.get_yaw_angle())  # Ottiene l'angolo attuale del robot e lo normalizza
        angolo_target = normalize_angle(angolo_attuale + (angolo * verso))  # Calcola l'angolo target aggiungendo l'angolo di rotazione desiderato
        
        while abs(normalize_angle(spike.motion_sensor.get_yaw_angle()) - angolo_target) > 2:  # Continua a ruotare finché non si è vicini all'angolo target
            differenza = abs(normalize_angle(spike.motion_sensor.get_yaw_angle()) - angolo_target)  # Calcola la differenza tra l'angolo attuale e quello target
            velocita_attuale = min(velocita, max(10, differenza / 2))  # Calcola la velocità di rotazione in base alla differenza, con un minimo di 10
            
            if verso == 1:  # Se il verso è 1, ruota a destra
                self.movement_motors.start_tank_at_power(velocita_attuale, velocita_attuale * 3)  # Avvia i motori per ruotare a destra
            else:  # Altrimenti, ruota a sinistra
                self.movement_motors.start_tank_at_power(velocita_attuale * 3, -velocita_attuale)  # Avvia i motori per ruotare a sinistra
        
        self.movement_motors.stop()  # Ferma i motori una volta raggiunto l'angolo target


def normalize_angle(angle):
    """Normalizza l'angolo per farlo rientrare nell'intervallo da -180 a 180 gradi."""
    while angle > 180:
        angle -= 360
    while angle < -180:
        angle += 360
    return angle


hub.motion.yaw_pitch_roll(0)
mv = Movimenti(spike, motoreSinistro, motoreDestro)
mv.ciroscopio(90, 1)  # Ruota a destra di 90 gradi