import serial


class GPS:
    def __init__(self):
        self.gps_ser = serial.Serial('/dev/ttyS4', 9600, timeout=0.5)
        
    def __del__(self):
        self.gps_ser.close()

    def read_data(self):
        return self.gps_ser.readline()
