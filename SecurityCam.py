from picamera import PiCamera
from picamera.array import PiRGBArray
import time
import glob
import os
import cv2
from skimage.metrics import structural_similarity as ssim
import imutils
import numpy as np
import json
import datetime as dt
from send_message import SendMessage
from google_drive import G_Drive
import threading


class SecurityCam(object):

    def __init__(self, conf="/home/pi/Documents/python_scripts/SecurityCam_config.json"):
        
        # load attributes
        self.conf = json.load(open(conf))
                   
        # initiate directory[
        self.directory = self.conf["dir"]
        if not os.path.isdir(self.directory):
            os.mkdir(self.directory)
            print("created directory: " + self.directory)
            
    def start_cam(self, show=False, save=None):
        print("start cam")
        # if the attributes are not specified, extract the values from the config.json
        if show == None:
            show = self.conf["save"]
        
        if save == None:
            save = self.conf["save"]
            
        avg = None
        motionCounter = 0
        lastUploaded = dt.datetime(2020, 1, 1)
        
        # capture frames from the camera
        self.camera = PiCamera()
        self.camera.start_preview()
        self.camera.resolution = (640, 480)
        self.rawCapture = PiRGBArray(self.camera, size=(640, 480))
        time.sleep(self.conf["camera_warmup_time"])

        for f in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True):

            frame = f.array
            now = dt.datetime.now()
            self.text = "No movement"
            
            # prep the frame
            #frame = imutils.resize(frame, width=250)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            
            # initialize average if is None
            if avg is None:
                avg = gray.copy().astype("float")
                self.rawCapture.truncate(0)
                # restart the loop when being initiated
                continue
        
            cv2.accumulateWeighted(gray, avg, 0.5)
            frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
            
            # threshold the delta image, dilate the thresholded image to fill
            # in holes, then find contours on thresholded image
            thresh = cv2.threshold(frameDelta, self.conf["delta_thresh"], 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            
            # define whether there is change
            # loop over the contours
            for c in cnts:
                
                # if the contour is too small, ignore it
                if cv2.contourArea(c) > self.conf["min_area"]:
                    # change the indicator
                    # compute the bounding box for the contour, draw it on the frame,
                    # and update the text
                    (x, y, w, h) = cv2.boundingRect(c)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    self.text = "Movement detected"
                
            # draw the text and timestamp on the frame
            ts = now.strftime("%A %d %B %Y %H:%M:%S%p")
            cv2.putText(frame, "Room Status: {}".format(self.text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
            
            if show:
                # display the security feed
                cv2.imshow("Security Feed", frame)
                key = cv2.waitKey(1) & 0xFF
                
            if save:
                if self.text == "Movement detected":
                    if (now - lastUploaded).seconds >= self.conf["min_upload_seconds"]:
                        motionCounter += 1
                        if motionCounter >= self.conf["min_motion_frames"]:
                            name = "{}-{:02d}-{:02d}_{:02d}h{:02d}m{:02d}s".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
                            cv2.imwrite(self.directory + name + ".jpg", frame)
                            lastUploaded = now
                            motionCounter = 0
                            
            self.rawCapture.truncate(0)
            
    def upload(self, interval=60):
        print("start uploading")
        g_drive = G_Drive()
        
        while True:
            try:
                files = [os.path.join(self.directory, f) for f in os.listdir(self.directory) if os.path.isfile(os.path.join(self.directory, f))]
                for file in files:
                    upload = os.path.basename(file)
                    g_drive.upload(upload)
                    print("uploaded file {}".format(file))
                    os.remove(file)
                time.sleep(interval)
  
            except:
                print("failed to upload, try again after intervel sleep")
                time.sleep(interval)
        
    
    def notify_by_email(receiver="willem.boone@outlook.com"):

        text = ""
        subject = "PiCamera movement detected"
        messenger = SendMessage()
        while True:
            if self.text == "Movement detected":
                messenger.send_email(text, subject, receiver, files=None)
                
                
def printing():
    print("thread is working")
        
        
if __name__ == "__main__":
    SC = SecurityCam()
    
    #SC.start_cam(show=True, save=True)
    thr_2 = threading.Thread(target=SC.upload)
    thr_2.setDaemon(True)
    thr_1 = threading.Thread(target=SC.start_cam)
    thr_1.setDaemon(True)

    thr_2.start()
    thr_1.start()
    

