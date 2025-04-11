# LEGO type:standard slot:0 autostart

import sys, time, hub
from spike import PrimeHub, Motor, MotorPair
from hub import battery

spike = PrimeHub()
movement_motors = MotorPair('A', 'B')
motoreSinistro = Motor('A')
motoreDestro = Motor('B')
C = Motor('C')
D = Motor('D')
Kp = 0
Ki = 0
Kd = 0

integrale = 0
previousError = 0
velocità = 100
spike.motion_sensor.reset_yaw_angle()
angolo = 0
target = 0
class Movimenti:
    def __init__(self,Kp,Ki,Kd):
        self.integrale = 0
        self.previousError = 0
        self.kp = Kp
        self.ki = Ki
        self.kd = Kd
        
    def calcoloPID(self,velocità):

        if velocità == 100:
            self.kp = 13
            self.ki = 0.3
            self.kd = 0
        elif 40 <= velocità < 75:
            self.kp = 18.4
            self.ki = 0
            self.kd = 5
        elif velocità < 40:
            self.kp = 28
            self.ki = 0.25
            self.kd = 1.5

    def pid(self,target, angolo):
        dt = 0.001
        error = target - angolo
        self.integrale += error * dt
        derivata = (error - self.previousError) / dt
        correzione = (error * self.kp + self.integrale * self.ki + derivata * self.kd)
        self.previousError = error
        print(error)
        return correzione
    
mv = Movimenti(Kp,Ki,Kd)
pressed = False
while True:
    mv.calcoloPID(velocità) 
    yaw = spike.motion_sensor.get_yaw_angle()
    #print("Yaw:" + str(yaw) + "Target: " + str(target))
    steer = mv.pid(target, yaw)
    #print("Velocita: " + str(velocità) + "Steering: " + str(steer))
    movement_motors.start_at_power(int(velocità), int(steer))
