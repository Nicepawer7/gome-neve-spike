import matplotlib.pyplot as plt
from math import sqrt as radice
velocitàMax = 100
distanza = 1000
kCurva = 3
percorsa = []
i = 0

velocità = []
while i < distanza/kCurva/2:
    velocità.append(radice(abs(((i-(distanza/kCurva/2))**2)/((distanza/kCurva/2)**2)-1)*(velocitàMax-30)**2)+30) 
    print(radice(abs(((i-(distanza/kCurva/2))**2)/((distanza/kCurva/2)**2)-1)*(velocitàMax-30)**2)+30) #prima ellisse sezionata
    percorsa.append(i)
    i += 1

fig, ax = plt.subplots()
ax.plot(percorsa,velocità)
ax.plot([0,0],[30,100],color="green",linestyle="dashed")
ax.plot([0,distanza],[30,30],color="green",linestyle="dashed")
ax.set(xlabel='Gradi obbiettivo', ylabel='Velocità',
       title='Funzione della velocità in relazione alla rotazione mancante')
ax.grid()
plt.show()