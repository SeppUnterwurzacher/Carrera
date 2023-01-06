from carreralib import ControlUnit
from colorama import Fore, Back, Style
import os
import keyboard
import curses
from curses import wrapper

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

            if self.bestlap == 0 or self.lap_time < self.bestlap:
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

            #print("Fahrer: " + str(self.position_info[0]) + ", Runden: " + str(self.position_info[1]) + " Zeit: " + str(self.position_info[2]))

class RMS:
    def __init__(self):
        self.max_lap = 0
        self.laps = [0, 0, 0]
        self.times = [0, 0, 0]
        self.zeiten = [0, 0, 0]
        self.zeiten_sortiert = []
        self.ergebnis = [0, 0, 0]
        self.not_first_round = False
        self.first = -1
    


drivers = [Driver(i) for i in range(0, 3)]

# Festlegen der Namen der Fahrer
drivers[0].name = "Rot "
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
        for fahrer_stand in rms.zeiten_sortiert:
            fahrer_index = fahrer_stand[0]
            drivers[fahrer_index].position = reihung
            rms.ergebnis[reihung -1] = drivers[fahrer_index].name
            reihung += 1

    rms.not_first_round = True

while False:
    data = cu.poll()

    if isinstance(data, ControlUnit.Timer):
        os.system('clear')
        
        address = data.address
        drivers[address].zeit(data)

        position()
        #print("zeiten:" + str(rms.zeiten))
        # print("sortiert:" + str(rms.zeiten_sortiert))
        # print("ergebnis: " + str(rms.ergebnis))
        #print("sortiert:" + str(rms.ergebnis))
        
        #for i in range(0, 3):
            #print("Position " + str(i) + ": " + str(drivers[i].position))
        #print("Runden:" + str(rms.laps))
        #print("Runden:" + str(rms.times))
        #print("Fuehrender:" + str(rms.first))

        auto_symbol = "o=o/"
        vorhandene_zeiten = len(rms.zeiten_sortiert)
        
        if vorhandene_zeiten > 0:
            print (Back.WHITE +      "         Runde: " + str(rms.zeiten_sortiert[0][1]) + "                            ")
            print (Style.RESET_ALL + "_____________________________________________")
            for i in range(vorhandene_zeiten):
                platz = str(i + 1) + ": "
                farbe = (Fore.RED, Fore.YELLOW, Fore.BLUE)
                farbe = farbe[rms.zeiten_sortiert[i][0]]
                
                if i == 0:
                    zeit_block = str(rms.zeiten_sortiert[i][2])
                else:
                    if rms.zeiten_sortiert[i][1] == rms.zeiten_sortiert[0][1]:
                        diff_zeit = rms.zeiten_sortiert[0][2] - rms.zeiten_sortiert[i][2]
                        zeit_block = "+ " + str(round(diff_zeit, 2)) + "sec"
                    else:
                        diff_lap = rms.zeiten_sortiert[0][1] - rms.zeiten_sortiert[i][1]
                        zeit_block = "+ " + str(diff_lap) + " lap"
                print (farbe + platz + auto_symbol + "               " + zeit_block)

            print ("")
            print (Fore.WHITE + "_____________________________________________")
            print ("Runden:     " + str(str(round(rms.zeiten_sortiert[0][1], 2))))
            print ("Gesamtzeit: " + str(str(round(rms.zeiten_sortiert[0][2], 2))))
            print ("_____________________________________________")

            print ("Fahrer        Fastest Lap       Rounds")
            for driver in drivers:
                if driver.lap > 0:
                    print(driver.name + "              " + f'{round(driver.bestlap, 2):.2f}' + "             " + str(driver.lap))
        else:
            print (Back.WHITE +      "         Runde: 0 - Rennen gestartet!        ")
            print (Style.RESET_ALL + "_____________________________________________")


def daten_auslesen ():
    data = cu.poll()

    if isinstance(data, ControlUnit.Timer):
        os.system('clear')
        
        address = data.address
        drivers[address].zeit(data)

        position()

def main(stdscr):
    stdscr.clear()
    stdscr.nodelay(True)
    stdscr.addstr("hallo")

    while True:
        daten_auslesen()
        
        if len(rms.zeiten_sortiert) > 0:
            stdscr.clear()
            position = 1

            row_zeiten = 2

            stdscr.addstr(row_zeiten, 3, "Pos.")
            stdscr.addstr(row_zeiten, 8, "Driver")
            stdscr.addstr(row_zeiten, 14, "Lap")
            stdscr.addstr(row_zeiten, 20, "Time")
            
            for zeiten in rms.zeiten_sortiert:
                fahrer = drivers[zeiten[0]].name
                runden = zeiten[1]
                gesamtzeit = round(zeiten[2], 2)
                stdscr.addstr(row_zeiten + position, 4, f"{position}")
                stdscr.addstr(row_zeiten + position, 8, f"{fahrer}")
                stdscr.addstr(row_zeiten + position, 15, f"{runden}")
                stdscr.addstr(row_zeiten + position, 20, f"{gesamtzeit}")
                position += 1
            stdscr.refresh()
            

        try:
            key = stdscr.getkey()
        except:
            key = None
        
        if key == "s":
            cu.start()
        elif key == "q":
            quit()


wrapper(main)