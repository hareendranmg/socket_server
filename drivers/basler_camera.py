from pypylon import pylon
from PIL import Image
from io import BytesIO
import base64


class BaslerCamera:
    def __init__(self):
        try:
            self.img0 = []
            self.img1 = []
            
            tlFactory = pylon.TlFactory.GetInstance()
            devices = tlFactory.EnumerateDevices()

            if len(devices) == 0:
                raise pylon.RUNTIME_EXCEPTION("No camera present.")

            self.cameras = pylon.InstantCameraArray(2)    

            for i, cam in enumerate(self.cameras):
                cam.Attach(tlFactory.CreateDevice(devices[i]))
                cam.Open()
                cam.Width=2448
                cam.Height=2048
                cam.ExposureTime.SetValue(100000)

            self.cameras.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

            self.converter = pylon.ImageFormatConverter()
            self.converter.OutputPixelFormat = pylon.PixelType_RGB8packed
            self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

        except Exception as e:
            print("Exception occurred in setting up cameras.", e)

    def grab_images(self):
        try:
            if not self.cameras.IsGrabbing():
                raise pylon.RUNTIME_EXCEPTION("Cameras are not grabbing")

            grabResult = self.cameras.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
            cameraContextValue = grabResult.GetCameraContext()

            if grabResult.GrabSucceeded():
                image = self.converter.Convert(grabResult)
                if cameraContextValue == 0:
                    self.img0 = image.GetArray()
                else:
                    self.img1 = image.GetArray()

                if len(self.img1) == 0:
                    self.img1 = self.img0

            else:
                print("Error: ", grabResult.ErrorCode)

            grabResult.Release()            
            pil_img0 = Image.fromarray(self.img0)
            resized_image0 = pil_img0.resize((400, 400))
            pil_img1 = Image.fromarray(self.img1)
            resized_image1 = pil_img1.resize((400, 400))

            with BytesIO() as buff:
                resized_image1.save(buff, format="JPEG")
                new_image_string1 = base64.b64encode(buff.getvalue()).decode("utf-8")
                buff.seek(0)
                buff.truncate(0)
                resized_image0.save(buff, format="JPEG")
                new_image_string0 = base64.b64encode(buff.getvalue()).decode("utf-8")
                buff.close()
    
                return new_image_string0 + "::" + new_image_string1

        except Exception as e:
            print("Exception occurred in grabing images.", e)
