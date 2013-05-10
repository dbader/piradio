 #! /usr/bin/env python
 # Plot random pixels on the screen.

import pygame
import os

LCD_WIDTH, LCD_HEIGHT = 128, 64
LCD_COLOR_BG = (148, 175, 204)
LCD_COLOR_FG = (10, 10, 10)
BACKGROUND_IMAGE = os.path.join(os.getcwd(), 'test-apps/simulator-frontplate.png')

background = pygame.image.load(BACKGROUND_IMAGE)
width, height = background.get_rect()[2:]
lcd = pygame.Surface((LCD_WIDTH, LCD_HEIGHT))
lcd.fill(LCD_COLOR_BG)

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('piradio simulator')

clock = pygame.time.Clock()
running = True

screen.blit(background, background.get_rect())

def lcd_setpixel(x, y, enabled):
    lcd.set_at((x, y), LCD_COLOR_FG if enabled else LCD_COLOR_BG)
    
def lcd_vline(x, enabled):
    for y in range(LCD_HEIGHT):
        lcd_setpixel(x, y, enabled)

def lcd_hline(y, enabled):
    for x in range(LCD_WIDTH):
        lcd_setpixel(x, y, enabled)
 
while running:
    pressed_keys = pygame.key.get_pressed()
    if pressed_keys[pygame.K_RETURN] or pressed_keys[pygame.K_SPACE]:
        print 'center'
    if pressed_keys[pygame.K_UP]:
        print 'up'
        lcd_vline(16, True)        
    if pressed_keys[pygame.K_DOWN]:
        print 'down'
    if pressed_keys[pygame.K_LEFT]:
        print 'left'
        lcd_hline(16, True)        
    if pressed_keys[pygame.K_RIGHT]:
        print 'right'    
    if pressed_keys[pygame.K_ESCAPE]:
        running = False                
    
    screen.blit(lcd, (42, 76))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    pygame.display.flip()
    clock.tick(240)