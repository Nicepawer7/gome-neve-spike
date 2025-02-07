x = 5.5 # float
y = 2 # int
testo = "Hello World" # string
boolean = True # boolean

lista = [1, 2, 3, 4, 5]

def somma(a, b):
    return a + b

# +, -, *, /, **, >, <, >=, <=, ==, !=, and, or, not

if x > y:
    print("x è maggiore di y")
elif x == y:
    print("x è uguale a y")
else:
    print("y è maggiore di x")

x = x -1
print(x)

while x > y:
    print(x)
    x -= 1 # x = x - 1

for numero in lista:
    print(numero)

class Cane:
    def __init__(self, nome, eta, razza):
        self.nome = nome
        self.eta = eta
        self.razza = razza

    def abbaia(self):
        print(f"{self.nome} dice: Woof!")
    
    def cammina(self):
        print(f"{self.nome} cammina")


fuffi = Cane("Fuffi", 5, "Beagle")

dema = Cane("Dema", 3, "Pastore Tedesco")

fuffi.abbaia()
dema.cammina()

