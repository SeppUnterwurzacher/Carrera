from carreralib import ControlUnit
import os
import curses
from curses import wrapper
from reset import test
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
    
    def reset(self):
        self.timestamp_new = 0
        self.lap_time = 0
        self.total_time = 0
        self.lap = 0
        self.bestlap = 0
        self.position_info = 0
        self.position = 0


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
drivers[0].name = "rot "
drivers[1].name = "gelb"
drivers[2].name = "blau"

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

def menu_footer(stdscr, zeiten_win, statistik_win, warten=False):
    try:
        key = stdscr.getch()
    except:
        key = None
    
    if key == ord(" "):
        cu.start()
    elif key == ord("r"):
        cu.reset()
        for zeiten in rms.zeiten_sortiert:
            drivers[zeiten[0]].reset()
        
        zeiten_win.clear()
        statistik_win.clear()
        zeiten_win.refresh()
        statistik_win.refresh()
        cu.start()
    elif key == ord("q"):
        quit()


def rennen_standard(stdscr, zeiten_win, statistik_win, text_farben):
    
    warten_auf_bestaetigung = True
    rennen_offen = True
    frage = "Wie viele Runden?"
    max_runden = ""

    while warten_auf_bestaetigung: 
        zeiten_win.clear()
        zeiten_win.addstr(f"{frage}")
        zeiten_win.addstr(3, 0, "Eingabe mit (o) bestätigen", curses.A_ITALIC)
        zeiten_win.addstr(2, 0, f"Anzahl: {max_runden}")
        
        zeiten_win.refresh()
        
        key = zeiten_win.getkey()

        if key == "o":
            try:
                max_runden = int(max_runden)
                warten_auf_bestaetigung = False
                zeiten_win.clear()
                zeiten_win.addstr(4, 1, "Rennen mit Leertaste starten")
                cu.start()
                zeiten_win.refresh()
            except:
                max_runden = ""
                frage = "Ungültige Eingabe"
                zeiten_win.clear()
                zeiten_win.addstr(f"{frage}")
                zeiten_win.addstr(2, 0, f"Anzahl: {max_runden}")
                zeiten_win.refresh()

            
        else:
            max_runden = max_runden + key
        
    
    stdscr.nodelay(True)

    while rennen_offen:

        daten = daten_auslesen()
        
        if len(rms.zeiten_sortiert) > 0 and daten:
            zeiten_win.clear()
            position = 1

            zeiten_win.addstr(1, 2, "Pos.")
            zeiten_win.addstr(1, 8, "Driver")
            zeiten_win.addstr(1, 18, "Lap")
            zeiten_win.addstr(1, 26, "Time")

            zeiten_win.hline(2, 2, "=", 30)

            for zeiten in rms.zeiten_sortiert:
                fahrer = drivers[zeiten[0]].name
                fahrer_id = zeiten[0]
                runden = zeiten[1]
                gesamtzeit = round(zeiten[2], 2)
                zeiten_win.addstr(position + 2, 3, f"{position}", text_farben[fahrer_id])
                zeiten_win.addstr(position + 2, 8, f"{fahrer}", text_farben[fahrer_id])
                zeiten_win.addstr(position + 2, 19, f"{runden}", text_farben[fahrer_id])
                zeiten_win.addstr(position + 2, 26, f"{gesamtzeit}", text_farben[fahrer_id])
                position += 1
            zeiten_win.refresh()
            
            #statistik_win.clear()
            statistik_win.addstr(1, 1, "Driver")
            statistik_win.addstr(1, 10, "Last")
            statistik_win.addstr(1, 18, "Fastest")
            statistik_win.hline(2, 1, "=", 25)

            position = 1
            for zeiten in rms.zeiten_sortiert:
                fahrer = drivers[zeiten[0]].name
                fahrer_id = zeiten[0]
                
                zeit_last_lap = round(drivers[zeiten[0]].lap_time, 2)
                zeit_fastest_lap = round(drivers[zeiten[0]].bestlap, 2)
                statistik_win.addstr(position + 2, 1, f"{fahrer}", text_farben[fahrer_id])
                statistik_win.addstr(position + 2, 10, f"{zeit_last_lap}", text_farben[fahrer_id])
                statistik_win.addstr(position + 2, 20, f"{zeit_fastest_lap}", text_farben[fahrer_id])
                position += 1

            statistik_win.refresh()

            for zeiten in rms.zeiten_sortiert:
                rennen_offen = False
                runden = zeiten[1]
                if runden < max_runden:
                    rennen_offen = True

        menu_footer(stdscr=stdscr, zeiten_win=zeiten_win, statistik_win=statistik_win)
        

    stdscr.nodelay(False)
    stdscr.addstr(3, 1, "Rennen beendet")
    menu_footer(stdscr=stdscr, zeiten_win=zeiten_win, statistik_win=statistik_win)

def daten_auslesen ():
    data = cu.poll()

    if isinstance(data, ControlUnit.Timer):
        os.system('clear')
        
        address = data.address
        drivers[address].zeit(data)

        position()
        return True
    else:
        return False

def main(stdscr):
    cu.reset()
    stdscr.clear()
    stdscr.refresh()

    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
    text_farben = [
        curses.color_pair(1), 
        curses.color_pair(2),
        curses.color_pair(3)
    ]

    header_win = curses.newwin(1, 100, 1, 3)
    zeiten_win = curses.newwin(10, 32, 3, 3)
    statistik_win = curses.newwin(10, 32, 3, 50)
    footer_win = curses.newwin(1, 100, 15, 3)

    stdscr.refresh()
    
    header_win.clear()
    header_win.addstr("Goglsche Race-Management-System", curses.A_REVERSE)
    header_win.refresh()

    footer_win.clear()
    footer_win.addstr("Drücke (q) zum Beenden, (Leertaste) für Start, (r) für Reset")
    footer_win.refresh()

    zeiten_win.clear()
    zeiten_win.addstr("Hauptmenü:")
    zeiten_win.addstr(3, 1, "1 - Standard Rennen")
    zeiten_win.refresh()

    key = stdscr.getch()

    if key == ord("1"):
        rennen_standard(stdscr=stdscr, zeiten_win=zeiten_win, statistik_win=statistik_win, text_farben=text_farben)
    elif key == ord("q"):
        quit() 



wrapper(main)