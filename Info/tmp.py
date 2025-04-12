class Manager:
    stop = True
    def __init__(self):
        self.stop = Manager.stop
    def qulo(self):
        Manager.stop = False
print(Manager.stop)
mv = Manager()
mv.qulo()
print(Manager.stop)


"""class Gay:
    def __init__(self):
        self.stop = False
        qulo(self)
    def falsifica(self):
        self.stop = False
class qulo:
    def __init__(self,gay):
        self.gay = gay
    def verifica(self):
        self.stop = True
        print(self.gay.stop)
Gay()
mv = qulo()
mv.verificaerifica()"""