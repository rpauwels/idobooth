#!/usr/bin/python

import os
import sys
import logging
import subprocess
import time
import random
import RPi.GPIO as GPIO
import picamera
import pygame

L_BUTTON_PIN = 23
R_BUTTON_PIN = 27
IMG_FOLDER = "foto"

os.putenv('SDL_FBDEV', '/dev/fb0')
os.putenv('SDL_VIDEODRIVER', 'fbcon') # fbcon, directfb, svgalib, x11
os.putenv('SDL_NOMOUSE', '1')

GPIO.setmode(GPIO.BCM)
GPIO.setup(L_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(R_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
image_cache = {}
slideshow_running = True

def takePicture(camera, countdown, dir, index):
    camera.annotate_text_size = 160
    for count in range(countdown, 0, -1):
        camera.annotate_text = str(count)
        time.sleep(1)
    screen.fill((255,255,255))
    pygame.display.flip()
    camera.annotate_text = ''
    for i in range(55,95,5):
        camera.brightness = i
        time.sleep(0.2/8)
    logging.info("Capturing photo {}".format(index))
    path = os.path.join(IMG_FOLDER, dir, "{}.jpg".format(index))
    camera.stop_preview()
    camera.brightness = 50
    camera.capture(path)
    renderImage(path)
    renderText("Foto {} van 3".format(index), screen.get_rect().centerx, 0, False)
    pygame.display.flip()
    time.sleep(5)

def renderImage(file):
    if not file in image_cache:
        image_cache[file] = pygame.image.load(file)
    screen.blit(image_cache[file], (0, 0))

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
    dirs = os.listdir(IMG_FOLDER)
    random.shuffle(dirs)
    for dir in dirs:
        for i in range(0,2):
            for file in sorted(os.listdir(os.path.join(IMG_FOLDER, dir))):
                checkEvents()
                if not slideshow_running:
                    logging.info("Slideshow stopped")
                    return
                renderImage(os.path.join(IMG_FOLDER, dir, file))
                renderText("1. kies je props", 700, 0, False)
                renderText("2. druk op de zwarte knop voor foto's", 700, 50, False)
                #renderText("   druk op de rode knop voor een filmpje", 700, 30, False)
                renderText("3. smile!", 700, 100, False)
                pygame.display.flip()
                time.sleep(0.5)
            time.sleep(0.5)
                    
def leftButton(channel):
    logging.info("Left button pressed")
    with picamera.PiCamera() as camera:
        camera.vflip = True
        camera.start_preview()
        camera.annotate_text_size = 100
        camera.annotate_text = 'filmpje'
        camera.start_preview()
        time.sleep(2)
        camera.annotate_text_size = 160
        for count in range(5, 0, -1):
            camera.annotate_text = str(count)
            time.sleep(1)
        camera.annotate_text = ''
        camera.start_recording(time.strftime('%y%m%d-%H%M%S') + '.h264')
        camera.wait_recording(10)
        camera.stop_recording();

def rightButton(channel):
    global slideshow_running
    if GPIO.input(channel) or not slideshow_running:
        logging.debug("Right button cancelled")
        return;
    logging.info("Right button pressed")
    slideshow_running = False
    dir = time.strftime('%y%m%d-%H%M%S')
    os.mkdir(os.path.join(IMG_FOLDER, dir))
    with picamera.PiCamera() as camera:
        camera.vflip = True
        camera.annotate_text_size = 100
        camera.annotate_text = 'foto\'s'
        camera.start_preview()
        time.sleep(2)
        camera.shutter_speed = camera.exposure_speed
        camera.exposure_mode = 'off'
        gains = camera.awb_gains
        camera.awb_mode = 'off'
        camera.awb_gains = gains
        takePicture(camera, 5, dir, 1)
        camera.start_preview()
        takePicture(camera, 5, dir, 2)
        camera.start_preview()
        takePicture(camera, 5, dir, 3)
    for i in range(0,5):
        for file in sorted(os.listdir(os.path.join(IMG_FOLDER, dir))):
            renderImage(os.path.join(IMG_FOLDER, dir, file))
            pygame.display.flip()
            time.sleep(0.5)
    slideshow_running = True

def checkEvents():
    for event in pygame.event.get():
        if event.type in (pygame.QUIT, pygame.KEYDOWN):
            sys.exit()

GPIO.add_event_detect(R_BUTTON_PIN, GPIO.FALLING, callback=rightButton, bouncetime=2000)
GPIO.add_event_detect(L_BUTTON_PIN, GPIO.FALLING, callback=leftButton, bouncetime=2000)

logging.basicConfig(level=logging.DEBUG,filename='photobooth.log',format='%(asctime)s %(message)s')
if not os.path.exists(IMG_FOLDER):
    os.mkdir(IMG_FOLDER)

logging.debug("Initializing Pygame")
pygame.init()
pygame.mouse.set_visible(0)
size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
logging.debug("Initializing screen size {} x {}".format(size[0], size[1]))
screen = pygame.display.set_mode(size)

logging.debug("Starting slideshow")
try:
    while True:
        checkEvents()
        time.sleep(0.1)
        if slideshow_running:
            slideshow()
finally:
    pygame.quit()
    GPIO.cleanup()
