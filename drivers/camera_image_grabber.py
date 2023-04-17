import os
import shutil
import cv2
from pypylon import pylon

class CameraImageGrabber:
    def __init__(self):
        self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
        self.camera.Open()
        self.camera.Width=800
        self.camera.Height=800
        self.camera.ExposureTime.SetValue(60000)
        self.camera.Gain.SetValue(0)
        self.camera.PixelFormat.SetValue('BGR8')
        self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        self.output_dir = 'output'
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)  # Delete the folder and its contents recursively
        os.makedirs(self.output_dir)
        self.image_counter = 1

    def __del__(self):
        self.stop()

    def stop(self):
        try:
            self.camera.StopGrabbing()
            self.camera.Close()
        except:
            pass

    def grab_images(self, num_images=1000):
        while self.image_counter <= num_images:
            grab_result = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
            image_data = grab_result.GetArray()
            image_file = os.path.join(self.output_dir, f'{self.image_counter:06d}.jpg')
            cv2.imwrite(image_file, image_data)
            # print(f'Saved image: {image_file}')
            grab_result.Release()
            self.image_counter += 1
