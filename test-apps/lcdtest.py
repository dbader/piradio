import ctypes
import time

raspi_lcd = ctypes.cdll.LoadLibrary("./lcd.so")

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

def bitblt(pixels):
    raspi_lcd.LCD_ClearScreen()
    for y in range(64):
        for x in range(128):
            if pixels[y*128+x]:
                raspi_lcd.LCD_PutPixel(x, y)
    raspi_lcd.LCD_WriteFramebuffer()

bitblt([1] * (128*64))
