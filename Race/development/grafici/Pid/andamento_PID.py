import matplotlib.pyplot as plt
from math import sqrt as radice
velocitàMax = 100
distanza = 3000
kCurva = distanza/4
percorsa = []
velocità = []
i = 0

fig, ax = plt.subplots()
ax.set(xlabel='Gradi obbiettivo', ylabel='Velocità',
       title='Funzione della velocità in relazione alla rotazione mancante')
ax.grid()
ax.plot([0,0],[30,100],color="black",linestyle="dashed")
ax.plot([distanza,distanza],[30,velocitàMax],color="black",linestyle="dashed")
ax.plot([0,distanza],[30,30],color="black",linestyle="dashed")
ax.plot([0,distanza],[100,100],color="black",linestyle="dashed")

while i < kCurva:
    #velocità.append(radice(abs(((i-(distanza/kCurva/2))**2)/((distanza/kCurva/2)**2)-1)*(velocitàMax-30)**2)+30) 
    velocità.append(radice(((((i-kCurva)**2)/kCurva**2)-1)*(-(velocitàMax-30)**2))+30)
    percorsa.append(i)
    i += 1
while kCurva <= i <= distanza-kCurva:
    velocità.append(velocitàMax)
    percorsa.append(i)
    i += 1
while distanza-kCurva<= i <= distanza:
    velocità.append(radice(((((i-distanza+kCurva)**2)/kCurva**2)-1)*(-(velocitàMax-30)**2))+30)
    percorsa.append(i)
    i += 1

ax.plot(percorsa,velocità,color="red",linewidth=2)
plt.show()