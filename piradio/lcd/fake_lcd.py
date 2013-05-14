#! /usr/bin/env python
"""A fake LCD driver based on PyGame / SDL for testing piradio without
a real LCD board."""

import pygame
import os
import logging

logger = logging.getLogger('fakelcd')

LCD_WIDTH, LCD_HEIGHT = 128, 64
K_LEFT = 0
K_RIGHT = 1
K_UP = 2
K_DOWN = 3
K_CENTER = 4
LCD_COLOR_BG = (148, 175, 204)
LCD_COLOR_FG = (32, 32, 32)
BACKGROUND_IMAGE = os.path.join(os.getcwd(), 'assets',
                                'simulator-frontplate.png')

keymap = [
    pygame.K_LEFT,
    pygame.K_RIGHT,
    pygame.K_UP,
    pygame.K_DOWN,
    pygame.K_RETURN,
]

lcd = None
screen = None
framebuffer = [0] * (LCD_WIDTH * LCD_HEIGHT)


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
            pixel_color = (LCD_COLOR_FG if pixels[y*LCD_WIDTH+x]
                           else LCD_COLOR_BG)
            lcd.set_at((x, y), pixel_color)
    screen.fill(LCD_COLOR_BG,
                pygame.Rect(40, 74, LCD_WIDTH + 4, LCD_HEIGHT + 4))
    screen.blit(lcd, (42, 76))
    pygame.display.flip()
    global framebuffer
    framebuffer = pixels


def readkeys():
    def draw_key(key, pos):
        """Visualize key presses with black circles."""
        if keys[key]:
            pygame.draw.circle(screen, (0, 0, 0), pos, 12)
        else:
            pygame.draw.circle(screen, (255, 255, 255), pos, 12)

    for _ in pygame.event.get():
        # Eat up any events in the queue.
        pass
    pressed_keys = pygame.key.get_pressed()
    keys = [0] * len(keymap)
    for i, k in enumerate(keymap):
        if pressed_keys[k]:
            keys[i] = True

    # Visualize key presses
    draw_key(K_LEFT, (214, 107))
    draw_key(K_RIGHT, (307, 107))
    draw_key(K_UP, (260, 66))
    draw_key(K_DOWN, (260, 151))
    draw_key(K_CENTER, (260, 109))
    update(framebuffer)

    return keys


def set_contrast(c):
    logging.debug('Setting contrast to %.2f', c)
    LCD_COLOR_FG[0] = 127 - 158 * c
    LCD_COLOR_FG[1] = 127 - 158 * c
    LCD_COLOR_FG[2] = 127 - 158 * c


def set_backlight_enabled(enabled):
    logging.debug('Setting backlight to %s', 'on' if enabled else 'off')
    global LCD_COLOR_BG
    if enabled:
        LCD_COLOR_BG = (148, 175, 204)
    else:
        LCD_COLOR_BG = (80, 120, 80)
    update(framebuffer)


if __name__ == '__main__':
    import time
    init()
    update([0] * LCD_WIDTH * LCD_HEIGHT)
    while not True in readkeys():
        time.sleep(0.01)
