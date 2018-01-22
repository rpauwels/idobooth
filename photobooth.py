#!/usr/bin/python

import os
import logging
import subprocess
import time
import RPi.GPIO as GPIO
import picamera
import pygame

L_BUTTON_PIN = 23
R_BUTTON_PIN = 27
IMG_FOLDER = "foto"

GPIO.setmode(GPIO.BCM)
GPIO.setup(L_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(R_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
image_cache = {}
slideshow_running = True

def takePicture(camera, countdown, filename):
    camera.start_preview()
    while countdown > 0:
        camera.annotate_text = str(countdown)
        countdown -= 1
        time.sleep(1)
    camera.annotate_text = ''
    for i in xrange(50,100,5):
        camera.brightness = i
        time.sleep(0.05)
    logging.info("Capturing " + filename)
    path = os.path.join(IMG_FOLDER, filename)
    camera.brightness = 50
    camera.capture(path)
    displayImage(path)
    camera.stop_preview()
    time.sleep(5)

def displayImage(file):
    screen.fill((0,0,0))
    if not file in image_cache:
        logging.info("Loading " + file)
        image_cache[file] = pygame.image.load(file)
    image = image_cache[file]
    logging.info("Loaded " + file + " from cache")
    screen.blit(image, (0, 0))

def renderText(text, x, y, right):
    font = pygame.font.SysFont("monospace", 72)
    rendered_text = font.render(text, True, (255, 255, 255))
    text_rect = rendered_text.get_rect()
    if right:
        text_rect.right = x
    else:
        text_rect.left = x
    text_rect.top = y
    screen.blit(rendered_text, text_rect)
                    
def leftButton(channel):
    logging.info("Left button pressed")

def rightButton(channel):
    logging.info("Right button pressed " + slideshow_running)
    slideshow_running = False
    with picamera.PiCamera() as camera:
        camera.annotate_text_size = 160
        camera.vflip = True
        prefix = time.strftime('%y%m%d%H%M%S')
        takePicture(camera, 8, prefix + "-1.jpg")
        takePicture(camera, 5, prefix + "-2.jpg")
        takePicture(camera, 5, prefix + "-3.jpg")
    slideshow_running = True

GPIO.add_event_detect(R_BUTTON_PIN, GPIO.FALLING, callback=rightButton, bouncetime=1000)
GPIO.add_event_detect(L_BUTTON_PIN, GPIO.FALLING, callback=leftButton, bouncetime=1000)

logging.basicConfig(level=logging.DEBUG)
if not os.path.exists(IMG_FOLDER):
    os.mkdir(IMG_FOLDER)

pygame.init()
pygame.mouse.set_visible(0)
size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)

while True:
    time.sleep(0.1)
    if slideshow_running:
        logging.info("Restarting slideshow")
        for f in sorted(os.listdir(IMG_FOLDER)):
            displayImage(os.path.join(IMG_FOLDER, f))
            renderText("druk op de rechtse knop", 0, 0, True)
            pygame.display.flip()
            time.sleep(1)
            if not slideshow_running:
                logging.info("Slideshow stopped")
                break
