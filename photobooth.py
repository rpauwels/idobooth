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
    renderImage(path)
    camera.stop_preview()
    time.sleep(5)

def renderImage(file):
    #screen.fill((0,0,0))
    if not file in image_cache:
        image_cache[file] = pygame.image.load(file)
    image = image_cache[file]
    screen.blit(image, (0, 0))

def renderText(text, x, y, right):
    font = pygame.font.SysFont("monospace", 72)
    rendered_text = font.render(text, True, (255, 255, 255))
    text_rect = rendered_text.get_rect()
    if right:
        text_rect.right = screen.right - x
    else:
        text_rect.left = x
    text_rect.top = y
    screen.blit(rendered_text, text_rect)

def slideshow():
    global slideshow_running
    for dir in sorted(os.listdir(IMG_FOLDER)):
        for i in range(0,3):
            for file in sorted(os.listdir(os.path.join(IMG_FOLDER, dir))):
                renderImage(os.path.join(IMG_FOLDER, dir, file))
                renderText("1. kies je props", 700, 0, False)
                renderText("2. druk op de zwarte knop voor foto's", 700, 30, False)
                #renderText("   druk op de rode knop voor een filmpje", 700, 30, False)
                renderText("3. smile!", 700, 60, False)
                pygame.display.flip()
                time.sleep(0.5)
                if not slideshow_running:
                    logging.info("Slideshow stopped")
                    screen.fill((0,0,0))
                    pygame.display.flip()
                    return
            time.sleep(0.5)
                    
def leftButton(channel):
    logging.info("Left button pressed")

def rightButton(channel):
    global slideshow_running
    slideshow_running = False
    logging.info("Right button pressed")
    dir = time.strftime('%y%m%d-%H%M%S')
    os.mkdir(dir)
    with picamera.PiCamera() as camera:
        camera.annotate_text_size = 160
        camera.vflip = True
        takePicture(camera, 8, dir, os.path.join(dir, "1.jpg"))
        takePicture(camera, 5, dir, os.path.join(dir, "2.jpg"))
        takePicture(camera, 5, dir, os.path.join(dir, "3.jpg"))
    slideshow_running = True

GPIO.add_event_detect(R_BUTTON_PIN, GPIO.FALLING, callback=rightButton, bouncetime=500)
GPIO.add_event_detect(L_BUTTON_PIN, GPIO.FALLING, callback=leftButton, bouncetime=500)

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
        slideshow()

