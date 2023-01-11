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

global previous_command

def get_host_ip():
    try:
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
        return host_ip
    except:
        return None


async def handler(websocket, path):
    try:
        async for req in websocket:      
            previous_command = req             
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
                    countOfImagesToGrab = 10
                    maxCamerasToUse = 2
                    exitCode = 0
                    img0 = []
                    img1 = []
                    
                    tlFactory = pylon.TlFactory.GetInstance()
                    devices = tlFactory.EnumerateDevices()
                    print(len(devices))
                    if len(devices) == 0:
                        raise pylon.RUNTIME_EXCEPTION("No camera present.")

                    cameras = pylon.InstantCameraArray(2)    

                    # l = cameras.GetSize()
                    for i, cam in enumerate(cameras):
                        cam.Attach(tlFactory.CreateDevice(devices[i]))
                        cam.Open()
                        cam.Width=2448
                        cam.Height=2048
                        cam.ExposureTime.SetValue(100000)
                        print("Using device ", cam.GetDeviceInfo().GetModelName())

                    cameras.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

                    converter = pylon.ImageFormatConverter()
                    converter.OutputPixelFormat = pylon.PixelType_RGB8packed
                    converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned


                    while req != 'camera_off':
                    # while cameras.IsGrabbing():

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
                        
                                        
                        pil_img0 = Image.fromarray(img0)
                        resized_image0 = pil_img0.resize((300, 300))
                        pil_img1 = Image.fromarray(img1)
                        resized_image1 = pil_img1.resize((300, 300))
                        with BytesIO() as buff:
                            resized_image1.save(buff, format="JPEG")
                            new_image_string1 = base64.b64encode(buff.getvalue()).decode("utf-8")
                            buff.seek(0)
                            buff.truncate(0)
                            resized_image0.save(buff, format="JPEG")
                            new_image_string0 = base64.b64encode(buff.getvalue()).decode("utf-8")
                            final_string = new_image_string0+"::"+new_image_string1
                            await websocket.send(final_string)
                            buff.close()


                    print("outside")
                except Exception as e:
                    # cameras.
                    # grabResult.Release()
                    print("An exception occurred.", e)
                    # buff.close()
                    # buff.seek(0)
                    # exitCode = 1

    except websockets.exceptions.ConnectionClosed:
        # Handle the client disconnect
        if previous_command == 'camera_on':
            print("Camera closed")
            # grabResult.Release()
            # buff.close()
            # buff.seek(0)


        print('The client disconnected')


start_server = websockets.serve(handler, get_host_ip(), 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
