# LEGO type:standard slot:0 autostart

import sys, time, hub
from spike import PrimeHub, Motor, MotorPair, ColorSensor
from hub import battery

spike = PrimeHub()
movement_motors = MotorPair('A', 'B')
motoreSinistro = Motor('A')
motoreDestro = Motor('B')
C = Motor('C')
D = Motor('D')
colorSensor = ColorSensor('E')
Kp = 0
Ki = 0
Kd = 0

integrale = 0
previousError = 0
previousTime = 0
velocità = 50

angolo = spike.motion_sensor.get_yaw_angle()
target = angolo

def calcoloPID(velocità):
    global Kp
    global Ki
    global Kd
    global spike

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


def pid(target, angolo):
    global Kp, Ki, Kd, previousTime, previousError, velocità, integrale
    
    currentTime = time.time()
    dt = currentTime - previousTime
    if dt == 0:
        dt = 0.001
    previousTime = currentTime
    error = target - angolo
    integrale += error * dt
    derivata = (error - previousError) / dt
    correzione = (error * Kp + integrale * Ki + derivata * Kd)
    previousError = error
    return correzione
    

while True:
    calcoloPID(velocità) 
    angolo = spike.motion_sensor.get_yaw_angle()
    correzione = pid(target, angolo)
    movement_motors.start_at_power(int(velocità), int(correzione))
      