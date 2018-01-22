#!/usr/bin/python

import os
import logging
import subprocess
import time
import signal
import RPi.GPIO as GPIO
import picamera

L_BUTTON_PIN = 23
R_BUTTON_PIN = 27
IMG_FOLDER = "foto"

GPIO.setmode(GPIO.BCM)
GPIO.setup(L_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(R_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def takePicture(camera, countdown, filename):
    while countdown > 0:
        countdown -= 1
        camera.annotate_text = str(countdown)
        time.sleep(1)
    camera.annotate_text = ''
    for i in xrange(50,100,10):
        camera.brightness = i
    logging.info("Capturing")
    camera.capture(os.path.join(IMG_FOLDER, filename))
    logging.info("Restoring framerate")
    camera.brightness = 50

if not os.path.exists(IMG_FOLDER):
    os.mkdir(IMG_FOLDER)
logging.basicConfig(level=logging.DEBUG)
with picamera.PiCamera() as camera:
    camera.annotate_text_size = 160
    #camera.vflip = True
    logging.info("Running fbi")
    slideshow = subprocess.Popen(['fbi'] +
        [os.path.join(IMG_FOLDER, f) for f in os.listdir(IMG_FOLDER)])
    while True:
        if (GPIO.input(L_BUTTON_PIN) == False):
            logging.info("Left button pressed")
        elif (GPIO.input(R_BUTTON_PIN) == False):
            logging.info("Right button pressed")
            #slideshow.terminate()
            camera.start_preview()
            prefix = time.strftime('%y%m%d%H%M%S')
            takePicture(camera, 8, prefix + "-1.jpg")
            takePicture(camera, 5, prefix + "-2.jpg")
            takePicture(camera, 5, prefix + "-3.jpg")
            #slideshow = subprocess.Popen(['fbi', os.path.join(IMG_FOLDER, "*.jpg")])
            camera.stop_preview()
