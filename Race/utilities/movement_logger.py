# LEGO type:advanced slot:0 autostart
import hub # type: ignore
from spike import PrimeHub, Motor, MotorPair # type: ignore
spike = Primehub() #type: ignore
motoreSinistro = Motor('A')
motoreDestro = Motor('B')
C = Motor('C')
D = Motor('D')
programmaSelezionato = ["ARROW_N","GHOST","GO_LEFT","GO_RIGHT"]
def move_log(): # aggiungere calcolo per indietro con bottone destro
    lStart = motoreSinistro.get_degrees_counted() #posizione iniziale sinistra
    rStart = motoreDestro.get_degrees_counted()
    while spike.left_button.is_pressed() != False: # attende di essere premuto e nel mentre conta i gradi
        lPercorsi = motoreSinistro.get_degrees_counted() #spazio percorso
        rPercorsi = motoreDestro.get_degrees_counted()
    l = abs(lPercorsi) - lStart # potrebbe non funzionare andando indietro
    r = abs(rPercorsi) - rStart
    avg = str((l + r)/2) # media dello spazio percorso
    print("Gradi percorsi dritto: " + avg + " gradi")
    return

def turn_log():
    startGyro = spike.motion_sensor.get_yaw_angle()
    while spike.left_button.is_pressed() != False: # attende di essere premuto e nel mentre conta i gradi di rotazione
        gyro = spike.motion_sensor.get_yaw_module()
    print("Gradi girati: " + str(startGyro-gyro) + " verso un lato") # potrebbe essere necessario normalizzare i gradi in qualche modo

def left_log():
    lStart = C.get_degrees_counted() # gradi iniziali motore sinistro
    while spike.left_button.is_pressed():
        l = C.get_degrees_counted() # gradi finchè I/O sinistro non viene premuto
    print("Motore sinistro ruotato di: " + str(l-lStart) + " gradi")

def right_log():
    rStart = D.get_degrees_counted()
    while spike.left_button.is_pressed():
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
    return 0

def manager():
    i = 0
    while True:
        if i == 4:
            i = 0
        if spike.left_button.is_pressed():
            i = start(i)
        if spike.right_button.is_pressed():
            i += 1
        print(i)

manager()
