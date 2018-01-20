#!/usr/bin/python

import os
import logging
import RPi.GPIO as GPIO
import picamera

L_BUTTON_PIN = 23
R_BUTTON_PIN = 27
IMG_FOLDER = "foto"

GPIO.setmode(GPIO.BCM)
GPIO.setup(L_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # start taken pics
GPIO.setup(R_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # exit program

def takePicture(camera, countdown):
    while countdown > 0:
        countdown -= 1
        camera.annotate_text = str(countdown)
        time.sleep(1)
    camera.annotate_text = 'smile'
    timestamp = time.time()
    timestampAsString = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d_%H-%M-%S')
    camera.capture(IMG_FOLDER + os.pathsep + str(timestampAsString) + '.jpg')

log = logging.getLogger()
if not os.path.exists(IMG_FOLDER):
    os.mkdir(IMG_FOLDER)
with picamera.PiCamera() as camera:
    camera.annotate_text_size = 160
    camera.vflip = True;
    logging.info("Initialized and waiting for button press")
    while True:
        
        if (GPIO.input(L_BUTTON_PIN) == False):
            logging.info("Left button pressed")
        elif (GPIO.input(R_BUTTON_PIN) == False):
            logging.info("Right button pressed")
            camera.start_preview()
            takePicture(camera, 8, "1.jpg")
            takePicture(camera, 5, "2.jpg")
            takePicture(camera, 5, "3.jpg")
