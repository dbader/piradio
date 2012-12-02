//--------------------------------------------------------------------------------------------------
//                                  _            _     
//                                 | |          | |    
//      ___ _ __ ___  ___ _   _ ___| |_ ___  ___| |__  
//     / _ \ '_ ` _ \/ __| | | / __| __/ _ \/ __| '_ \. 
//    |  __/ | | | | \__ \ |_| \__ \ ||  __/ (__| | | |
//     \___|_| |_| |_|___/\__, |___/\__\___|\___|_| |_|
//                         __/ |                       
//                        |___/    Engineering (www.emsystech.de)
//
// Filename:    raspilcd.h
// Description: Hardware abstraction layer for Raspi-LCD
//    
// Open Source Licensing 
//
// This program is free software: you can redistribute it and/or modify it under the terms of 
// the GNU General Public License as published by the Free Software Foundation, either version 3 
// of the License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,but WITHOUT ANY WARRANTY; without
// even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License along with this program.  
// If not, see <http://www.gnu.org/licenses/>.
//
// Dieses Programm ist Freie Software: Sie können es unter den Bedingungen der GNU General Public
// License, wie von der Free Software Foundation, Version 3 der Lizenz oder (nach Ihrer Option) 
// jeder späteren veröffentlichten Version, weiterverbreiten und/oder modifizieren.
//
// Dieses Programm wird in der Hoffnung, dass es nützlich sein wird, aber OHNE JEDE GEWÄHRLEISTUNG,
// bereitgestellt; sogar ohne die implizite Gewährleistung der MARKTFÄHIGKEIT oder EIGNUNG FÜR 
// EINEN BESTIMMTEN ZWECK. Siehe die GNU General Public License für weitere Details.
//
// Sie sollten eine Kopie der GNU General Public License zusammen mit diesem Programm erhalten 
// haben. Wenn nicht, siehe <http://www.gnu.org/licenses/>.
//                       
// Author:      Martin Steppuhn
// History:     18.10.2012 Initial version
//				04.11.2012 V0.9
//--------------------------------------------------------------------------------------------------

#ifndef RASPILCD_H
#define RASPILCD_H

//=== Includes =====================================================================================	

#include "std_c.h"
#include "bcm2835.h"

//=== Preprocessing directives (#define) ===========================================================

// Pin Setup for RaspiLCD

#define		PIN_LCD_RST			25
#define		PIN_LCD_CS			8
#define		PIN_LCD_RS			7
#define		PIN_LCD_MOSI		10
#define		PIN_LCD_SCLK		11
#define		PIN_LCD_BACKLIGHT	18

#define	LCD_RST_CLR 		bcm2835_gpio_clr(PIN_LCD_RST) 
#define	LCD_RST_SET			bcm2835_gpio_set(PIN_LCD_RST) 

#define	LCD_CS_CLR 			bcm2835_gpio_clr(PIN_LCD_CS)
#define	LCD_CS_SET			bcm2835_gpio_set(PIN_LCD_CS)

#define	LCD_RS_CLR 			bcm2835_gpio_clr(PIN_LCD_RS)
#define	LCD_RS_SET			bcm2835_gpio_set(PIN_LCD_RS)

#define	LCD_SPI_PUTC(__d)	SpiPutc(__d)
#define	LCD_SPI_WAIT_BUSY

#define		BUTTON_UP				(Button & 0x01)
#define		BUTTON_LEFT				(Button & 0x02)
#define		BUTTON_CENTER			(Button & 0x04)
#define		BUTTON_RIGHT			(Button & 0x08)
#define		BUTTON_DOWN				(Button & 0x10)

#define		BUTTON_PRESSED_UP		(ButtonPressed & 0x01)
#define		BUTTON_PRESSED_LEFT		(ButtonPressed & 0x02)
#define		BUTTON_PRESSED_CENTER	(ButtonPressed & 0x04)
#define		BUTTON_PRESSED_RIGHT	(ButtonPressed & 0x08)
#define		BUTTON_PRESSED_DOWN		(ButtonPressed & 0x10)

//=== Type definitions (typedef) ===================================================================

//=== Global constants (extern) ====================================================================

//=== Global variables (extern) ====================================================================

extern uint8	Button;
extern uint8	ButtonPressed;

//=== Global function prototypes ===================================================================

int RaspiLcdHwInit(void);
void UpdateButtons(void);
int GetRaspberryHwRevision(void);
void SpiPutc(unsigned char d);
void SetBacklight(uint8 light);
void SleepMs(uint32 ms);

#endif
