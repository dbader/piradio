import ctypes
import time

LCD_WIDTH, LCD_HEIGHT = 128, 64
raspilcd = ctypes.cdll.LoadLibrary("./libraspilcd.so")
buttons = ctypes.c_uint8.in_dll(raspilcd, "Button")

KEY_CENTER = 0x04
KEY_LEFT = 0x02
KEY_RIGHT = 0x08
KEY_UP = 0x01
KEY_DOWN = 0x10
_KEYS = [KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN, KEY_CENTER]

def init():
    raspilcd.RaspiLcdHwInit()
    raspilcd.LCD_Init()
    raspilcd.LCD_ClearScreen()
    raspilcd.LCD_WriteFramebuffer()
    raspilcd.LCD_SetPenColor(1)
    raspilcd.LCD_DrawLine(0, 0, LCD_WIDTH-1, LCD_HEIGHT-1)
    raspilcd.LCD_WriteFramebuffer()

def readkeys():
    raspilcd.UpdateButtons()
    return [_keydown(k) for k in _KEYS]

def _keydown(key):
    return bool(buttons.value & key)

def update(pixels):
    raspilcd.LCD_ClearScreen()
    for y in range(LCD_HEIGHT):
        for x in range(LCD_WIDTH):
            if pixels[y * LCD_WIDTH + x]:
                raspilcd.LCD_PutPixel(x, y)
    raspilcd.LCD_WriteFramebuffer()

#raspilcd.SetBacklight(32)
#raspilcd.LCD_SetContrast(18)

if __name__ == '__main__':
    init()
    t = 1.0 / 8.0
    while not True in readkeys():
        update([0] * (LCD_WIDTH * LCD_HEIGHT))
        time.sleep(t)
        update([1] * (LCD_WIDTH * LCD_HEIGHT))
	time.sleep(t)
