import matplotlib.pyplot as plt
from math import sqrt as radice
from math import cos,pi
velocitàMax = 100
velocitàMin = 25
distanza = 3000
percorsa = []
velocità = []
i = 0

fig, ax = plt.subplots()
ax.set(xlabel='Gradi obbiettivo', ylabel='Velocità',
       title='Funzione della velocità in relazione alla rotazione mancante')
ax.grid()
ax.plot([0,0],[velocitàMin,velocitàMax],color="black",linestyle="dashed")
ax.plot([distanza,distanza],[velocitàMin,velocitàMax],color="black",linestyle="dashed")
ax.plot([0,distanza],[velocitàMin,velocitàMin],color="black",linestyle="dashed")
ax.plot([0,distanza],[velocitàMax,velocitàMax],color="black",linestyle="dashed")

"""while i < kCurva:
    #velocità.append(radice(abs(((i-(distanza/kCurva/2))**2)/((distanza/kCurva/2)**2)-1)*(velocitàMax-30)**2)+30) 
    velocità.append(radice(((((i-kCurva)**2)/kCurva**2)-1)*(-(velocitàMax-30)**2))+30)
    percorsa.append(i)
    i += 1
while kCurva <= i <= distanza-kCurva:
    velocità.append(velocitàMax)
    percorsa.append(i)
    i += 1"""
#while distanza-kCurva<= i <= distanza:
while i < distanza:
    #velocità.append(radice(((((i-distanza+kCurva)**2)/kCurva**2)-1)*(-(velocitàMax-30)**2))+30) #sistema vecchio
    velocità.append(cos((i+distanza/2)*(2*pi)/distanza)*((velocitàMax-velocitàMin)/2)+((velocitàMax+velocitàMin)/2)) # sinusoide
    percorsa.append(i)
    i += 1

ax.plot(percorsa,velocità,color="red",linewidth=2)
plt.show()