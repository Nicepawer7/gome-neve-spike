# LEGO type:advanced slot:0 autostart

import hub
from spike import PrimeHub
spike = PrimeHub()
spike.motion_sensor.reset_yaw_angle()
while True:
    print(spike.motion_sensor.get_yaw_angle())
