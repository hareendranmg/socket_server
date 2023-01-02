import serial
import asyncio
import websockets

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.5)


async def handler(websocket, path):
    pre_req = ''
    while True:
        async for req in websocket:
            if req == None or req == '' or req == 0:
                req = pre_req

            print(req)
            if req == 'connect':
                print("Connected...")
                await websocket.send("Connected")                    
            if req == 'gps':
                data = ser.readline()
                # time.sleep(0.5)
                print("Sending: " + data.decode('utf-8'))
                await websocket.send(data)                    
            if req == 'disconnect':
                s.close()
                break
                print('Disconnected...')
                await websocket.send("Disconnected")   

            pre_req = req                 


start_server = websockets.serve(handler, "192.168.2.115", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
