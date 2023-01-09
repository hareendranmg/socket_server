import serial
import asyncio
import websockets
import time
import codecs
import binascii
import os
from pypylon import genicam
from pypylon import pylon
import sys
from io import StringIO, BytesIO
import socket
import base64
# import cv2
import numpy as np
import pickle
from PIL import Image



# config_ser = serial.Serial('/dev/ttyUSB0', 115200)
# awr_data_ser = serial.Serial('/dev/ttyUSB1', 921600)
# gps_ser = serial.Serial('/dev/ttyUSB2', 9600, timeout=0.5)

def get_host_ip():
    try:
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
        return host_ip
    except:
        return None


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
        if req == 'camera_on':
            try:
                buff = BytesIO()
                countOfImagesToGrab = 10
                maxCamerasToUse = 1
                exitCode = 0
                img0 = []
                img1 = []
                
                tlFactory = pylon.TlFactory.GetInstance()
                devices = tlFactory.EnumerateDevices()
                print(len(devices))
                if len(devices) == 0:
                    raise pylon.RUNTIME_EXCEPTION("No camera present.")

                cameras = pylon.InstantCameraArray(min(len(devices), maxCamerasToUse))    
                l = cameras.GetSize()

                for i, cam in enumerate(cameras):
                    cam.Attach(tlFactory.CreateDevice(devices[i]))
                    cam.Open()
                    cam.Width=2448
                    cam.Height=2048
                    cam.ExposureTime.SetValue(100000)
                    # cam.ExposureTime.SetValue(20000)
                    print("Using device ", cam.GetDeviceInfo().GetModelName())

                cameras.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

                converter = pylon.ImageFormatConverter()
                converter.OutputPixelFormat = pylon.PixelType_BGR8packed
                converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

                while req != 'camera_off':
                    if not cameras.IsGrabbing():
                        break

                    grabResult = cameras.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
                    cameraContextValue = grabResult.GetCameraContext()
                    # print(grabResult)

                    if grabResult.GrabSucceeded():
                        image = converter.Convert(grabResult) # Access the openCV image data
                        # print(image)
                        if cameraContextValue == 0: #If camera 0, save array into img0[]
                            img0 = image.GetArray()
                        else: #if camera 1, save array into img1[]
                            img1 = image.GetArray()

                        if len(img1) == 0:
                            img1 = img0
                        # print(img0)

                    else:
                        print("Error: ", grabResult.ErrorCode)
                    grabResult.Release()
                    # f = StringIO()
                    # np.savez_compressed(f,frame=img0)
                    # f.seek(0)
                    # out = f.read()
                    # image_b64 = base64.b64encode(img0).decode("utf-8")
                    # print(image_b64)
                    # print(image_b64)
                    # await websocket.send(str(image_b64))
                    # await websocket.send(img0)
                    # print(img0.shape)
                    # data = pickle.dumps(img0)

                    pil_img = Image.fromarray(img0)
                    pil_img.save(buff, format="JPEG")
                    new_image_string = base64.b64encode(buff.getvalue()).decode("utf-8")
                    # print("-------------------------------------------------------------")
                    # print(new_image_string)
                    # print("-------------------------------------------------------------")
                    # await websocket.send(image_b64)
                    await websocket.send(new_image_string)
                    # pil_img.
                    # await websocket.send(str(img0))
                    time.sleep(0.1)


            except genicam.GenericException as e:
                print("An exception occurred.", e.GetDescription())
                exitCode = 1

        print("############################################")
        print("############ CAMERA OFF ###################")
        print("############################################")
                


start_server = websockets.serve(handler, get_host_ip(), 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
