import asyncio
import websockets
import time
from datetime import datetime

from drivers.adis16470 import ADIS16470
from utils import helpers


class IMUWebSocketServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    async def handler(self, websocket):
        try:
            client_ip, client_port = websocket.remote_address
            print(f"{datetime.now()}: Client connected: {client_ip}:{client_port}")
            
            async for req in websocket:      
                if req == 'connect':
                    imu = ADIS16470()
                    print(f'{datetime.now()}: Sending IMU data...')
                    while True:
                        await websocket.send(imu.read_data())
                        time.sleep(0.5)

        except websockets.exceptions.ConnectionClosed:                
            print(f"{datetime.now()}: Stopped sending IMU data. Client disconnected: {client_ip}:{client_port}")

    def start(self):
        self.server = websockets.serve(self.handler, self.host, self.port)
        asyncio.get_event_loop().run_until_complete(self.server)
        print(f'{datetime.now()}: Websocket server started at {self.host}:{self.port} address')
        asyncio.get_event_loop().run_forever()

    def stop(self):
        asyncio.get_event_loop().stop()



def main():
    try:
        ws = IMUWebSocketServer(helpers.get_host_ip(), helpers.imu_port)
        ws.start()
    except KeyboardInterrupt:
        print(f'\n{datetime.now()}: Closing Server...')
        ws.stop()


if __name__ == '__main__':
    main()