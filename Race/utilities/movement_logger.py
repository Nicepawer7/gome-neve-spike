# LEGO type:advanced slot:1 autostart
import hub,time # type: ignore
from spike import PrimeHub, Motor, MotorPair # type: ignore
spike = PrimeHub() #type: ignore
motoreSinistro = Motor('A')
motoreDestro = Motor('B')
C = Motor('C')
D = Motor('D')
programmaSelezionato = ["ARROW_N","GHOST","GO_LEFT","GO_RIGHT"]
def move_log(): # aggiungere calcolo per indietro con bottone destro
    lStart = motoreSinistro.get_degrees_counted() #posizione iniziale sinistra
    rStart = motoreDestro.get_degrees_counted()
    while spike.left_button.is_pressed() == False: # attende di essere premuto e nel mentre conta i gradi
        lPercorsi = motoreSinistro.get_degrees_counted() #spazio percorso
        rPercorsi = motoreDestro.get_degrees_counted()
    l = abs(lPercorsi) - lStart # potrebbe non funzionare andando indietro
    r = abs(rPercorsi) - rStart
    avg = str((l + r)/2) # media dello spazio percorso
    print("Gradi percorsi dritto: " + avg + " gradi")
    return

def turn_log():
    startGyro = spike.motion_sensor.get_yaw_angle()
    while spike.left_button.is_pressed() == False: # attende di essere premuto e nel mentre conta i gradi di rotazione
        gyro = spike.motion_sensor.get_yaw_angle()
    print("Gradi girati: " + str(startGyro-gyro) + " verso un lato") # potrebbe essere necessario normalizzare i gradi in qualche modo

def left_log():
    lStart = C.get_degrees_counted() # gradi iniziali motore sinistro
    while spike.left_button.is_pressed() == False:
        l = C.get_degrees_counted() # gradi finchè I/O sinistro non viene premuto
    print("Motore sinistro ruotato di: " + str(l-lStart) + " gradi")

def right_log():
    rStart = D.get_degrees_counted()
    while spike.left_button.is_pressed() == False:
        r = D.get_degrees_counted()
    print("Motore destro ruotato di: " + str(r-rStart) + " gradi")

def start(i):
    if i == 0:
        spike.light_matrix.show_image(programmaSelezionato[i])
        move_log()
    if i == 1:
        spike.light_matrix.show_image(programmaSelezionato[i])
        turn_log()
    if i == 2:
        spike.light_matrix.show_image(programmaSelezionato[i])
        left_log()
    if i == 3:
        spike.light_matrix.show_image(programmaSelezionato[i])
        right_log()
    time.sleep(0.50)
    return 0

def manager():
    i = 0
    spike.light_matrix.show_image("ANGRY")
    while True:
        if spike.left_button.is_pressed():
            time.sleep(0.50)
            i = start(i)
            spike.light_matrix.show_image("ANGRY")
        if spike.right_button.is_pressed():
            time.sleep(0.50)
            i += 1
            if i == 0:
                spike.light_matrix.show_image(programmaSelezionato[i])
            if i == 1:
                spike.light_matrix.show_image(programmaSelezionato[i])
            if i == 2:
                spike.light_matrix.show_image(programmaSelezionato[i])
            if i == 3:
                spike.light_matrix.show_image(programmaSelezionato[i])
            

manager()
