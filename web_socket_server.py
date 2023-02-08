import asyncio
import websockets
import time
from datetime import datetime

from drivers.adis16470 import ADIS16470
from drivers.gps import GPS
from drivers.awr6843aopevm import AWR6843AOPEVM
from drivers.basler_camera import BaslerCamera


class WebSocketServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    async def handler(self, websocket):
        try:
            client_ip, client_port = websocket.remote_address
            print(f"{datetime.now()}: Client connected: {client_ip}:{client_port}")
            
            async for req in websocket:      
                self.previous_command = req 

                if req == 'start':
                    imu = ADIS16470()
                    gps = GPS()
                    radar = AWR6843AOPEVM()
                    camera = BaslerCamera()

                    print(f'{datetime.now()}: Sending sensor data...')
                    while True:
                        await websocket.send(imu.read_data() + "#####" + gps.read_data().decode() + "#####" + radar.read_data())            
                        # await websocket.send(imu.read_data() + "#####" + gps.read_data()  + "#####" + radar.read_data() + "#####" + camera.grab_images())            
                        time.sleep(0.5)

                if req == 'imu_on':
                    imu = ADIS16470()
                    print(f'{datetime.now()}: Sending IMU data...')
                    while True:
                        await websocket.send(imu.read_data())            
                        time.sleep(0.5)

                if req == 'gps_on':
                    gps = GPS()
                    print(f'{datetime.now()}: Sending GPS data...')
                    while True:
                        await websocket.send(gps.read_data())

                if req == 'radar_on':
                    radar = AWR6843AOPEVM()
                    print(f'{datetime.now()}: Sending Radar data...')
                    while True:
                        await websocket.send(radar.read_data())            
                        time.sleep(0.1)

                if req == 'camera_on':
                    camera = BaslerCamera()
                    print(f'{datetime.now()}: Sending Camera data...')
                    while True:
                        await websocket.send(camera.grab_images())

        except websockets.exceptions.ConnectionClosed:
            if self.previous_command == 'stop':
                print(f"{datetime.now()}: Stopped sending sensor data")
            if self.previous_command == 'imu_on':
                print(f"{datetime.now()}: Stopped sending IMU data")
            if self.previous_command == 'gps_on':
                print(f"{datetime.now()}: Stopped sending GPS data")
            if self.previous_command == 'radar_on':
                print(f"{datetime.now()}: Stopped sending Radar data")
            if self.previous_command == 'camera_on':
                print(f"{datetime.now()}: Stopped sending Camera data")
                
            print(f"{datetime.now()}: Client disconnected: {client_ip}:{client_port}")

    def start(self):
        self.server = websockets.serve(self.handler, self.host, self.port)
        asyncio.get_event_loop().run_until_complete(self.server)
        print(f'{datetime.now()}: Websocket server started at {self.host}:{self.port} address')
        asyncio.get_event_loop().run_forever()

    def stop(self):
        asyncio.get_event_loop().stop()