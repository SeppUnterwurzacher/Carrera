from carreralib import ControlUnit
from colorama import Fore, Back, Style
import os
cu = ControlUnit('/dev/serial0')

print("gestartet")



class Driver:
    def __init__(self, address):
        self.address = address
        self.name = address
        self.timestamp_new = 0
        self.lap_time = 0
        self.total_time = 0
        self.lap = 0
        self.bestlap = 0
        self.position_info = 0
        self.position = 0
        
    def zeit(self, data):
        self.timestamp_old = float(self.timestamp_new)
        self.timestamp_new = float(data.timestamp)

        if self.timestamp_old > 0:
            self.lap_time = (self.timestamp_new - self.timestamp_old) / 1000

            if self.bestlap > 0 and self.lap_time < self.bestlap:
                self.bestlap = self.lap_time

            self.lap += 1
            
            if self.lap > rms.max_lap:
                rms.first = self.address

            self.total_time = self.total_time + self.lap_time
            self.position_info = (self.address, self.lap, self.total_time)
        
            """ print("Driver: " + str(self.address) + " - " + self.name)
            print("Rundenzeit: " + str(self.lap_time))
            print("Runde: " + str(self.lap))
            print("Total: " + str(self.total_time)) """

            print("Fahrer: " + str(self.position_info[0]) + ", Runden: " + str(self.position_info[1]) + " Zeit: " + str(self.position_info[2]))

class RMS:
    def __init__(self):
        self.max_lap = 0
        self.laps = [0, 0, 0]
        self.times = [0, 0, 0]
        self.zeiten = [0, 0, 0]
        self.zeiten_sortiert = []
        self.ergebnis = []
        self.not_first_round = False
        self.first = -1


drivers = [Driver(i) for i in range(0, 3)]

# Festlegen der Namen der Fahrer
drivers[0].name = "Rot"
drivers[1].name = "Gelb"
drivers[2].name = "Blau"

rms = RMS()

def position():
    if rms.not_first_round:
        # Die Positions Infos je Fahrer werden zusammengefasst und sortiert
        rms.zeiten_sortiert = []
        for i in range(0, 3):
            rms.zeiten[i] = drivers[i].position_info
        
        for x in rms.zeiten:
            if isinstance(x, tuple)==True:
                rms.zeiten_sortiert.append(x)
        rms.zeiten_sortiert = sorted(rms.zeiten_sortiert, key = lambda item: (item[1]*-1, item[2]))
        
        reihung = 1
        for x in rms.zeiten_sortiert:
            drivers[x[0]].position = reihung
            rms.ergebnis[x] = drivers[x[0]].name
            reihung += 1

    rms.not_first_round = True

while True:
    data = cu.request()

    if isinstance(data, ControlUnit.Timer):
        os.system('clear')
        
        address = data.address
        drivers[address].zeit(data)

        position()
        print("zeiten:" + str(rms.zeiten))
        print("sortiert:" + str(rms.zeiten_sortiert))
        print("sortiert:" + str(rms.ergebnis))
        
        for i in range(0, 3):
            print("Position " + str(i) + ": " + str(drivers[i].position))
        #print("Runden:" + str(rms.laps))
        #print("Runden:" + str(rms.times))
        #print("Fuehrender:" + str(rms.first))