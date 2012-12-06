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

keymap = [
    pygame.K_LEFT,
    pygame.K_RIGHT,
    pygame.K_UP,
    pygame.K_DOWN,
    pygame.K_RETURN,
]

lcd = None
screen = None

def init(debug=False):
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

def update(pixels):
    for y in range(LCD_HEIGHT):
        for x in range(LCD_WIDTH):
            lcd.set_at((x, y), LCD_COLOR_FG if pixels[y*LCD_WIDTH+x] else LCD_COLOR_BG)
    screen.blit(lcd, (42, 76))
    pygame.display.flip()

def readkeys():
    for event in pygame.event.get():
        pass
    pressed_keys = pygame.key.get_pressed()
    keys = [0] * len(keymap)
    for i, k in enumerate(keymap):
        if pressed_keys[k]:
            keys[i] = True
    return keys

def set_contrast(c):
    logging.debug('Setting contrast to %.2f', c)
    LCD_COLOR_FG[0] = 127 - 158 * c
    LCD_COLOR_FG[1] = 127 - 158 * c
    LCD_COLOR_FG[2] = 127 - 158 * c

def set_backlight_enabled(enabled):
    logging.debug('Setting backlight to %s', 'on' if enabled else 'off')
    if enabled:
        LCD_COLOR_BG = (148, 175, 204)
    else:
        LCD_COLOR_BG = (20, 40, 20)


if __name__ == '__main__':
    import time
    init()
    update([0] * LCD_WIDTH * LCD_HEIGHT)
    while not True in readkeys():
        time.sleep(0.01)
