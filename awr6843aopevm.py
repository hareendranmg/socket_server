import serial
import time

class AWR6843AOPEVM:
    def __init__(self):
        index = 1
        config_ser = serial.Serial('/dev/ttyUSB0', 115200)
        self.data_ser = serial.Serial('/dev/ttyUSB1', 921600)

        with open('config.txt', 'r') as file:
            for line in file:
                data_bytes = line.encode('utf-8')
                config_ser.write(data_bytes)
                time.sleep(0.02)
                index = index + 1
                print(index)

            data_bytes = 'configDataPort 921600 1'.encode('utf-8')
            config_ser.write(data_bytes)


    def read_data(self):        
        bytecount = self.data_ser.inWaiting()
        print("*****************************")
        print(bytecount)

        return self.data_ser.read(bytecount);
