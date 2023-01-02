import asyncio
import websockets
import serial

gps_ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.5)

async def send_message(websocket, path):
    # pre_req = await websocket.recv()

    while True:
        req = await websocket.recv()
        print(req)
        # if req == '' or req == None or req == 0:
            # req = pre_req

        if req == 'gps':
            data = gps_ser.readline()
            print(data.decode('utf-8'))
            await websocket.send(data)

        if req == "disconnect":
            break

        pre_req = req
        print('asd')

start_server = websockets.serve(send_message, "192.168.2.115", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
