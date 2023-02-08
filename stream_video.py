from pypylon import pylon
from PIL import Image
from io import BytesIO
import base64
from datetime import datetime
from flask import Flask, Response


app = Flask(__name__)

@app.route("/")
def stream():
    try:
        def generate():
            img0 = []
            img1 = []
            
            tlFactory = pylon.TlFactory.GetInstance()
            devices = tlFactory.EnumerateDevices()

            if len(devices) == 0:
                raise pylon.RUNTIME_EXCEPTION("No camera present.")

            cameras = pylon.InstantCameraArray(2)    

            for i, cam in enumerate(cameras):
                cam.Attach(tlFactory.CreateDevice(devices[i]))
                cam.Open()
                cam.Width=2448
                cam.Height=2048
                cam.ExposureTime.SetValue(100000)

            cameras.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

            converter = pylon.ImageFormatConverter()
            converter.OutputPixelFormat = pylon.PixelType_RGB8packed
            converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

            while True:
                if not cameras.IsGrabbing():
                    raise pylon.RUNTIME_EXCEPTION("Cameras are not grabbing")

                grabResult = cameras.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
                cameraContextValue = grabResult.GetCameraContext()

                if grabResult.GrabSucceeded():
                    image = converter.Convert(grabResult)
                    if cameraContextValue == 0:
                        img0 = image.GetArray()
                    else:
                        img1 = image.GetArray()

                    if len(img1) == 0:
                        img1 = img0

                else:
                    print(f"{datetime.now()}: Error: {grabResult.ErrorCode}")

                grabResult.Release()            
                pil_img0 = Image.fromarray(img0)
                resized_image0 = pil_img0.resize((400, 400))
                pil_img1 = Image.fromarray(img1)
                resized_image1 = pil_img1.resize((400, 400))

                with BytesIO() as buff:
                    resized_image1.save(buff, format="JPEG")
                    # new_image_string1 = base64.b64encode(buff.getvalue()).decode("utf-8")
                    # buff.seek(0)
                    # buff.truncate(0)
                    # resized_image0.save(buff, format="JPEG")
                    # new_image_string0 = base64.b64encode(buff.getvalue()).decode("utf-8")
                    # buff.close()
        
                    # return new_image_string0 + "::" + new_image_string1
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buff.getvalue() + b'\r\n\r\n')

        return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


    except Exception as e:
        print(f"{datetime.now()}: Exception occurred in setting up cameras. {e}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, threaded=True)