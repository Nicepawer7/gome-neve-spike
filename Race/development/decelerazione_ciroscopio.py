import matplotlib.pyplot as plt
import numpy as np
from math import cos
pi = 3.141
setdegrees = 180
maxSpeed = 100
degrees = 0
gradiAttuale = []
speed = []

while degrees <= setdegrees:
    vIncrease = (maxSpeed-30)/2
    vMove = 30 + vIncrease # la posizione della funzione risulta in funzione della velocità massima (opzionale ma figo) cos(x*b)*w + t
    speed.append(cos(degrees*(pi/setdegrees))*vIncrease+vMove)
    gradiAttuale.append(degrees)
    degrees += 1

fig, ax = plt.subplots()
ax.axhline(y=30, color="black")
ax.axhline(y=maxSpeed, color="black")
ax.axvline(color="black")
ax.axvline(x = setdegrees, color="black")
ax.plot(gradiAttuale,speed)
ax.set(xlabel='Gradi di rotazione', ylabel='Velocità',
       title='Funzione della velocità in relazione alla rotazione mancante')
ax.grid()
plt.show()