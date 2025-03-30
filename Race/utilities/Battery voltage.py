# LEGO type:advanced slot:10

import sys, time, hub
from spike import PrimeHub, Motor, MotorPair, ColorSensor
from hub import battery

spike = PrimeHub()

class bcolors:
        BATTERY = '\033[32m'
        BATTERY_LOW = '\033[31m'
        ENDC = '\033[0m'

if battery.voltage() < 8000:
    spike.light_matrix.write(str(battery.voltage()))
    print(bcolors.BATTERY_LOW + "batteria scarica: " + str(battery.voltage()) + " \n ----------------------------- \n >>>> carica la batteria o cambiala <<<< \n ----------------------------- \n"+ bcolors.ENDC)
else:
    spike.light_matrix.write(str(battery.voltage()))
    print(bcolors.BATTERY + "livello batteria: " + str(battery.voltage()) + bcolors.ENDC)
