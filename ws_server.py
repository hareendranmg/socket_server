import serial
import asyncio
import websockets

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.5)


async def handler(websocket, path):
    async for req in websocket:
        if req == 'connect':
            print("Connected...")
            await websocket.send("Connected")                    
        if req == 'gps':
            while req != 'disconnect':
                data = ser.readline()
                # time.sleep(0.5)
                print("Sending: " + data.decode('utf-8'))
                await websocket.send(data)                    
        if req == 'disconnect':
            s.close()
            print('Disconnected...')
            await websocket.send("Disconnected")                    


start_server = websockets.serve(handler, "192.168.2.115", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
