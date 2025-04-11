# LEGO type:advanced slot:0 autostart
import time
p = float(time.time())
qulo = True
i = 0
while i < 10:
    tempo = float(time.time())
    print(tempo-p)
    if tempo-p > 0:
        print("Fatto " + str(tempo-p))
        i += 1

    
