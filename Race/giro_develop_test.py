# LEGO type:advanced slot:0 autostart

import sys, time, hub
from spike import PrimeHub, Motor, MotorPair, ColorSensor
from hub import battery
spike = PrimeHub()
gyroValue = spike.motion_sensor.get_yaw_angle()
setdegree = 90
turnSpeed = 100
while True:
    gyroValue = spike.motion_sensor.get_yaw_angle()
    missingTurn = setdegrees - gyroValue
    str(speed = (missingTurn - 1)**0.2)
    print("Rotazione " + str(gyroValue) " Velocità ruote " + speed)