import matplotlib.pyplot as plt
import numpy as np
from math import cos
pi = 3.141
setpoint = 180
gradiAttuale = []
v = []
i = 0
while i <= setpoint:
    v.append(cos(i*(pi/setpoint))*35+65)
    gradiAttuale.append(i)
    i += 1

fig, ax = plt.subplots()
ax.plot(gradiAttuale,v)
ax.set(xlabel='Gradi di rotazione', ylabel='Velocità',
       title='Funzione della velocità in relazione alla rotazione mancante')
ax.grid()
plt.show()