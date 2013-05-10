 #! /usr/bin/env python
 # Plot random pixels on the screen.

import pygame
import os
import logging

logger = logging.getLogger('fakelcd')

LCD_WIDTH, LCD_HEIGHT = 128, 64
LCD_COLOR_BG = (148, 175, 204)
LCD_COLOR_FG = (32, 32, 32)
BACKGROUND_IMAGE = os.path.join(os.getcwd(), 'test-apps/simulator-frontplate.png')

KEY_CENTER = pygame.K_RETURN
KEY_LEFT = pygame.K_LEFT
KEY_RIGHT = pygame.K_RIGHT
KEY_UP = pygame.K_UP
KEY_DOWN = pygame.K_DOWN

should_quit = False

lcd = None
screen = None
pressed_keys = None

def update(pixels):
    for y in range(LCD_HEIGHT):
        for x in range(LCD_WIDTH):
            lcd.set_at((x, y), LCD_COLOR_FG if pixels[y*LCD_WIDTH+x] else LCD_COLOR_BG)
    screen.blit(lcd, (42, 76))
    pygame.display.flip()

def init():
    global lcd
    global screen
    background = pygame.image.load(BACKGROUND_IMAGE)
    width, height = background.get_rect()[2:]
    screen = pygame.display.set_mode((width, height))
    background = background.convert()
    lcd = pygame.Surface((LCD_WIDTH, LCD_HEIGHT)).convert()
    lcd.fill(LCD_COLOR_BG)
    pygame.display.set_caption('piradio simulator')
    screen.blit(background, background.get_rect())
    screen.blit(lcd, (42, 76))
    pygame.display.flip()

def pollkeys():
    global should_quit
    global pressed_keys

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            logger.info('Shutdown requested')
            should_quit = True

    pressed_keys = pygame.key.get_pressed()

    if pressed_keys[pygame.K_ESCAPE]:
        logger.info('Shutdown requested')
        should_quit = True

def keydown(key):
    return pressed_keys[key]

if __name__ == '__main__':
    import time
    init()
    update([0] * LCD_WIDTH * LCD_HEIGHT)
    while not should_quit:
        pollkeys()
        time.sleep(0.01)
