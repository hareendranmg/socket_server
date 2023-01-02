import serial
import asyncio
import websockets
import time
import codecs
import binascii


config_ser = serial.Serial('/dev/ttyUSB0', 115200)
awr_data_ser = serial.Serial('/dev/ttyUSB1', 921600)
gps_ser = serial.Serial('/dev/ttyUSB2', 9600, timeout=0.5)



async def handler(websocket, path):
    async for req in websocket:                   
        if req == 'gps_on':
            while req != 'gps_off':
                data = gps_ser.readline()
                # time.sleep(0.5)
                print("Sending: " + data.decode('utf-8'))
                await websocket.send(data)   
                # req = await websocket.recv()
        if req == 'gps_off':
            gps_ser.close()
            print('Disconnected...')
            await websocket.send("Disconnected") 
        if req == 'radar_on':
            print('firat')
            with open('config.txt', 'r') as file:
                print('second')
                index = 0
                for line in file:
                    index = index + 1 
                    data_bytes = line.encode('utf-8')
                    config_ser.write(data_bytes)
                    time.sleep(0.05)
                    data  = config_ser.read_until("\r".encode('utf-8'))
                    data = data.strip(b'\n\r').decode()
                    print('third in loop '+str(index))


                data_bytes = 'configDataPort 921600 1'.encode('utf-8')
                config_ser.write(data_bytes)
                print('fourth')
            while req != 'radar_off':
                bytecount = awr_data_ser.inWaiting()
                data = awr_data_ser.read(bytecount);
                print(data);
                await websocket.send(data)   
                time.sleep(0.5)        
        if req == 'radar_off':
            awr_data_ser.close()
            config_ser.close()
            print('Disconnected...')
            await websocket.send("Disconnected") 
                           


start_server = websockets.serve(handler, "192.168.2.115", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
