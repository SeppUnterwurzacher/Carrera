from threading import Timer
from carreralib import ControlUnit
cu = ControlUnit('/dev/serial0')

print("gestartet")



class Driver:
    def __init__(self, address):
        self.address = address
    timestamp_new = 0
    lap_time = 0
    lap = 0


drivers = [Driver(i) for i in range(0, )]

while True:
    data = cu.request()

    if isinstance(data, ControlUnit.Timer):
        address = data.address
        drivers[address].timestamp_old = float(drivers[address].timestamp_new)
        drivers[address].timestamp_new = float(data.timestamp)
        

        if drivers[address].timestamp_old > 0:
            drivers[address].lap_time = (drivers[address].timestamp_new - drivers[address].timestamp_old) / 1000
            drivers[address].lap += 1
        
            print("Driver: " + str(address))
            print("Rundenzeit: " + str(drivers[address].lap_time))
            print("Runde: " + str(drivers[address].lap))
        
 