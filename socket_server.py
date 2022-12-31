import socket
import serial
import time

def Main():
   
    host = '192.168.2.110' #Server ip
    port = 7564

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))

    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.5)
    
    print("Server Started")
    req, addr = s.recvfrom(1024)
    req = req.decode('utf-8')
    
    while req != 'disconnect':
        if req == 'connect':
            print("Connected...")
            s.sendto('success'.decode('utf-8'), addr)
            
        if req == 'gps':
            data = ser.readline()
            # time.sleep(0.5)
            print("Sending: " + data.decode('utf-8'))
            s.sendto(data, addr)

        req, addr = s.recvfrom(1024)
        req = req.decode('utf-8')
        
    s.close()

if __name__=='__main__':
    Main()
