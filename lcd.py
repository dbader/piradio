import ctypes
import time

LCD_WIDTH, LCD_HEIGHT = 128, 64
raspi_lcd = ctypes.cdll.LoadLibrary("./lcd.so")

should_quit = False
KEY_CENTER = 4
KEY_LEFT = 0
KEY_RIGHT = 1
KEY_UP = 2
KEY_DOWN = 3


def pollkeys():
    pass

def keydown(key):
    return False

def init():
    raspi_lcd.RaspiLcdHwInit()
    raspi_lcd.LCD_Init()
    raspi_lcd.LCD_ClearScreen()
    raspi_lcd.LCD_WriteFramebuffer()

#raspi_lcd.SetBacklight(32)
#raspi_lcd.LCD_SetContrast(18)

# raspi_lcd.UpdateButtons()
# buttons = ctypes.c_uint8.in_dll(raspi_lcd, "Button")
# pressed_buttons = ctypes.c_uint8.in_dll(raspi_lcd, "ButtonPressed")

    raspi_lcd.LCD_SetPenColor(1)
    raspi_lcd.LCD_DrawLine(0, 0, 100, 60)
    raspi_lcd.LCD_WriteFramebuffer()

def update(pixels):
    raspi_lcd.LCD_ClearScreen()
    for y in range(64):
        for x in range(128):
            if pixels[y*128+x]:
                raspi_lcd.LCD_PutPixel(x, y)
    raspi_lcd.LCD_WriteFramebuffer()

# bitblt([1] * (128*64))
