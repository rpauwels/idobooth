#!/usr/bin/python

import os
import logging
import subprocess
import time
import psutil
import RPi.GPIO as GPIO
import picamera

import pygame

L_BUTTON_PIN = 23
R_BUTTON_PIN = 27
IMG_FOLDER = "foto"

GPIO.setmode(GPIO.BCM)
GPIO.setup(L_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(R_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def takePicture(camera, countdown, filename):
    camera.start_preview()
    while countdown > 0:
        countdown -= 1
        camera.annotate_text = str(countdown)
        time.sleep(1)
    camera.annotate_text = ''
    for i in xrange(50,100,5):
        camera.brightness = i
        time.sleep(0.05)
    logging.info("Capturing")
    path = os.path.join(IMG_FOLDER, filename)
    camera.capture(path)
    camera.stop_preview()
    displayImage(path)
    camera.brightness = 50

def kill(pname):
    for proc in psutil.process_iter():
        if proc.name() == pname:
            proc.terminate()

def displayImage(screen, image):
    image = pygame.image.load(image)
    screen.blit(image, image.get_rect())
    pygame.display.flip()

def slideshow(screen):
    while (slideshowRunning):
        for f in os.listdir(IMG_FOLDER):
            displayImage(screen, f)
            timer.sleep(1)

logging.basicConfig(level=logging.DEBUG)
if not os.path.exists(IMG_FOLDER):
    os.mkdir(IMG_FOLDER)

pygame.init()
disp_info = pygame.display.Info
screen = pygame.display.set_mode((disp_info.current_w, disp_info.current_h))
slideshowRunning = True
t = Thread(target=slideshow)
t.start()

with picamera.PiCamera() as camera:
    camera.annotate_text_size = 160
    camera.vflip = True
    logging.info("Running fbi")
    #slideshow = subprocess.Popen(['fbi'] +
    #    [os.path.join(IMG_FOLDER, f) for f in os.listdir(IMG_FOLDER)])
    while True:
        if (GPIO.input(L_BUTTON_PIN) == False):
            logging.info("Left button pressed")
        elif (GPIO.input(R_BUTTON_PIN) == False):
            logging.info("Right button pressed")
            #kill('fbi')
            #camera.start_preview()
            prefix = time.strftime('%y%m%d%H%M%S')
            slideshowRunning = False
            takePicture(camera, 8, prefix + "-1.jpg")
            takePicture(camera, 5, prefix + "-2.jpg")
            takePicture(camera, 5, prefix + "-3.jpg")
            #slideshow = subprocess.Popen(['fbi', os.path.join(IMG_FOLDER, "*.jpg")])
            #camera.stop_preview()
            slideshowRunning = True
