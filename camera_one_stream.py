from pypylon import pylon
from PIL import Image
from io import BytesIO
from flask import Flask, Response

from utils import helpers


app = Flask(__name__)

def initialize_camera():    
    try:
        tlFactory = pylon.TlFactory.GetInstance()
        devices = tlFactory.EnumerateDevices()

        global camera
        camera = pylon.InstantCamera(tlFactory.CreateDevice(devices[0]))
        camera.Open()
        camera.Width=2448
        camera.Height=2048
        camera.ExposureTime.SetValue(100000)

        global converter
        converter = pylon.ImageFormatConverter()
        converter.OutputPixelFormat = pylon.PixelType_RGB8packed
        converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

        camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

    except Exception as e:
        print(f"Exception occurred in setting up camera. {e}")

def start_grabing():
    while True:
        grabResult = camera.RetrieveResult(4000, pylon.TimeoutHandling_ThrowException)
        image = converter.Convert(grabResult).GetArray()
        grabResult.Release()            
        image = Image.fromarray(image)
        image = image.resize((400, 400))

        with BytesIO() as buff:
            image.save(buff, format="JPEG")
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buff.getvalue() + b'\r\n\r\n')

@app.route("/")
def stream():
    try:
        return Response(start_grabing(), mimetype="multipart/x-mixed-replace; boundary=frame")
    except Exception as e:
        print(f"Exception occurred in streaming. {e}")


if __name__ == "__main__":
    initialize_camera()
    app.run(host=helpers.get_host_ip(), port=8001)