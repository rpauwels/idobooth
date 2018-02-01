#!/usr/bin/python
# coding=utf-8

import os, sys, logging, subprocess, time, random
from collections import OrderedDict
import RPi.GPIO as GPIO
import picamera
import pygame

os.putenv('SDL_FBDEV', '/dev/fb0')
os.putenv('SDL_VIDEODRIVER', 'fbcon') # fbcon, directfb, svgalib, x11
os.putenv('SDL_NOMOUSE', '1')

pygame.init()
pygame.mouse.set_visible(0)
size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
screen = pygame.display.set_mode(size)
image_cache = {}
slideshow_running = True

logging.basicConfig(level=logging.DEBUG,filename='photobooth.log',format='%(asctime)s %(message)s')

L_BUTTON_PIN = 23
R_BUTTON_PIN = 27
IMG_FOLDER = "foto"
TITLE_FONT = pygame.font.Font("Economica.otf", 60)
FG_COLOR = (255, 255, 255)
SUBTITLE_COLOR = (221, 221, 221)

GPIO.setmode(GPIO.BCM)
GPIO.setup(L_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(R_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def renderOSD():
    MARGIN = 30
    title = TITLE_FONT.render(u"véronique + raf", True, FG_COLOR)
    title_rect = title.get_rect()
    title_rect.left = MARGIN
    title_rect.top = 0.7 * size[1]
    date_font = pygame.font.Font("Economica.otf", 40)
    date = date_font.render("3 februari 2018", True, FG_COLOR)
    date_rect = date.get_rect()
    date_rect.center = title_rect.center
    date_rect.top = title_rect.bottom
    bg = pygame.Surface((title_rect.width + 2 * MARGIN, title_rect.height + date_rect.height + 2 * MARGIN))
    bg.set_alpha(100)
    screen.blit(bg, (0, title_rect.top - MARGIN))
    screen.blit(title, title_rect)
    screen.blit(date, date_rect)
    
    guestbook_text = date_font.render("gastenboekvideo", True, FG_COLOR)
    guestbook_text_rect = guestbook_text.get_rect()
    up_red = pygame.image.load('arrow-red.png')
    up_red_rect = up_red.get_rect()
    up_red_rect.centerx = guestbook_text_rect.centerx
    video = pygame.image.load('video-camera.png')
    video_rect = video.get_rect()
    video_rect.centerx = guestbook_text_rect.centerx
    video_rect.top = up_red_rect.bottom
    pygame.draw.circle(screen, FG_COLOR, video_rect.center, 48)
    screen.blit(video, video_rect)
    screen.blit(up_red, up_red_rect)
    guestbook_text_rect.top = 98
    screen.blit(guestbook_text, guestbook_text_rect)
    
    photo_text = date_font.render("foto's nemen", True, FG_COLOR)
    photo_text_rect = photo_text.get_rect()
    photo_text_rect.right = size[0]
    up_black = pygame.image.load('arrow-black.png')
    up_black_rect = up_black.get_rect()
    up_black_rect.centerx = photo_text_rect.centerx
    photo = pygame.image.load('photo-camera-64.png')
    photo_rect = photo.get_rect()
    photo_rect.centerx = photo_text_rect.centerx
    photo_rect.top = up_black_rect.bottom
    pygame.draw.circle(screen, FG_COLOR, photo_rect.center, 48)
    screen.blit(photo, photo_rect)
    screen.blit(up_black, up_black_rect)
    photo_text_rect.top = 98
    screen.blit(photo_text, photo_text_rect)

def drawInstructions(icons):
    caption_font = pygame.font.Font("Economica.otf", 60)
    pygame.draw.line(screen, FG_COLOR, (0, size[1] / 2), (size[0], size[1] / 2), 5)
    time.sleep(0.01)
    i = 0
    for key, value in icons.items():
        i += 1
        props = pygame.image.load(key)
        props_rect = props.get_rect()
        props_rect.center = (size[0] / (len(icons) + 1) * i, size[1] / 2)
        pygame.draw.circle(screen, FG_COLOR, props_rect.center, 100)
        caption_top = props_rect.bottom + 60
        for caption in value:
            caption = caption_font.render(caption, True, FG_COLOR)
            caption_rect = caption.get_rect()
            caption_rect.midtop = (props_rect.centerx, caption_top)
            screen.blit(caption, caption_rect)
            caption_top = caption_rect.bottom
        screen.blit(props, props_rect)

def renderVideoInstructions():
    icons = OrderedDict()
    icons['mask.png'] = ['kies je props']
    icons['video-camera.png'] = ['je krijgt 5 seconden!']
    drawInstructions(icons)

def renderPhotoInstructions():
    icons = OrderedDict()
    icons['mask.png'] = ['kies je props']
    icons['pose.png'] = ['sta klaar']
    icons['photo-camera.png'] = ['smile']
    drawInstructions(icons)

def renderPhotoFinished():
    title = TITLE_FONT.render("bedankt!", True, FG_COLOR)
    title_rect = title.get_rect()
    title_rect.center = (size[0] / 2, 50)
    screen.blit(title, title_rect)
    icons = OrderedDict()
    icons['giftbox.png'] = ['je krijgt het', 'resultaat binnenkort']
    icons['repeat.png'] = ['nog eens?', 'neem er zoveel je wil']
    drawInstructions(icons)

def renderVideoFinished():
    title = TITLE_FONT.render("bedankt!", True, FG_COLOR)
    title_rect = title.get_rect()
    title_rect.center = (size[0] / 2, 50)
    screen.blit(title, title_rect)
    icons = OrderedDict()
    icons['giftbox.png'] = ['je krijgt het', 'resultaat binnenkort']
    drawInstructions(icons)

def takePicture(camera, countdown, dir, index):
    camera.annotate_text_size = 160
    camera.start_preview()
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
    pygame.display.flip()
    time.sleep(5)

def renderImage(file):
    if not file in image_cache:
        image_cache[file] = pygame.image.load(file)
    screen.blit(image_cache[file], (0, 0))

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
                renderOSD()
                pygame.display.flip()
                time.sleep(0.5)
            time.sleep(0.5)
                    
def leftButton(channel):
    global slideshow_running
    if GPIO.input(channel) or not slideshow_running:
        logging.debug("Left button cancelled")
        return;
    renderVideoInstructions()
    pygame.display.flip()
    logging.info("Left button pressed")
    slideshow_running = False
    file_name = time.strftime('%y%m%d-%H%M%S')
    h264_name = file_name + '.h264'
    mp4_name = file_name + '.mp4'
    with picamera.PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.framerate = 90
        camera.vflip = True
        time.sleep(5)
        camera.start_preview()
        camera.annotate_text_size = 160
        for count in range(5, 0, -1):
            camera.annotate_text = str(count)
            time.sleep(1)
        camera.annotate_text = ''
        camera.start_recording(h264_name)
        camera.wait_recording(5)
        camera.stop_recording()
        renderVideoFinished()
        pygame.display.flip()
        camera.stop_preview()
    subprocess.call(['MP4Box','-fps','30','-add',h264_name,mp4_name])
    time.sleep(2)
    for i in range(0,3):
        subprocess.call(['omxplayer','-b','--no-osd','--no-keys',mp4_name])
    slideshow_running = True

def rightButton(channel):
    global slideshow_running
    if GPIO.input(channel) or not slideshow_running:
        logging.debug("Right button cancelled")
        return;
    renderPhotoInstructions()
    pygame.display.flip()
    logging.info("Right button pressed")
    slideshow_running = False
    dir = time.strftime('%y%m%d-%H%M%S') + '-f'
    os.mkdir(os.path.join(IMG_FOLDER, dir))
    with picamera.PiCamera() as camera:
        camera.vflip = True
        camera.annotate_text_size = 100
        camera.annotate_text = 'foto\'s'
        time.sleep(2)
        camera.shutter_speed = camera.exposure_speed
        camera.exposure_mode = 'off'
        gains = camera.awb_gains
        camera.awb_mode = 'off'
        camera.awb_gains = gains
        takePicture(camera, 5, dir, 1)
        takePicture(camera, 5, dir, 2)
        takePicture(camera, 5, dir, 3)
    for i in range(0,5):
        for file in sorted(os.listdir(os.path.join(IMG_FOLDER, dir))):
            renderImage(os.path.join(IMG_FOLDER, dir, file))
            if i > 2:
                renderPhotoFinished()
            pygame.display.flip()
            time.sleep(0.5)
    slideshow_running = True

def checkEvents():
    for event in pygame.event.get():
        if event.type in (pygame.QUIT, pygame.KEYDOWN):
            sys.exit()

GPIO.add_event_detect(R_BUTTON_PIN, GPIO.FALLING, callback=rightButton, bouncetime=2000)
GPIO.add_event_detect(L_BUTTON_PIN, GPIO.FALLING, callback=leftButton, bouncetime=2000)
if not os.path.exists(IMG_FOLDER):
    os.mkdir(IMG_FOLDER)

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
