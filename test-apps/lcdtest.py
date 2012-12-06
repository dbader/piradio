import ctypes
import time

raspilcd = ctypes.cdll.LoadLibrary("lcd.so")

raspi_lcd.RaspiLcdHwInit()
raspi_lcd.LCD_Init()
raspi_lcd.LCD_ClearScreen()
raspi_lcd.LCD_WriteFramebuffer()
#raspi_lcd.SetBacklight(32)
#raspi_lcd.LCD_SetContrast(18)

# raspi_lcd.UpdateButtons()
# buttons = ctypes.c_uint8.in_dll(raspi_lcd, "Button")
# pressed_buttons = ctypes.c_uint8.in_dll(raspi_lcd, "ButtonPressed")

raspi_lcd.LCD_DrawLine(0, 0, 100, 60)
raspi_lcd.LCD_WriteFramebuffer()
