# LEGO type:advanced slot:0 autostart

import time

startm = time.ticks_ms()
startu = time.ticks_us()
i = 0
while i < 5000:
    print("Milli " + str((time.ticks_ms() - startm) /1000) + "Nano " + str((time.ticks_us() - startu) / 1000000))
    i += 1