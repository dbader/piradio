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
// Filename:    hal.c
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
//--------------------------------------------------------------------------------------------------

//=== Includes =====================================================================================

#include "std_c.h"
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "raspilcd.h"

//=== Preprocessing directives (#define) ===========================================================

//=== Type definitions (typedef) ===================================================================

//=== Global constants =============================================================================

//=== Global variables =============================================================================

uint8	Button,ButtonPressed;

//=== Local constants  =============================================================================

//=== Local variables ==============================================================================

uint8	PinButton[5];
uint8	ButtonMem;

//=== Local function prototypes ====================================================================


//--------------------------------------------------------------------------------------------------
// Name:      HalInit
// Function:  Setup GPIO for Raspi_LCD
//            
// Parameter: -
// Return:    -
//--------------------------------------------------------------------------------------------------
int RaspiLcdHwInit(void)
{
	int HwRev;
	
	HwRev = GetRaspberryHwRevision();
	
	if (!bcm2835_init()) return 0;
	
	// Buttons 	
	PinButton[0] = 	17;
	PinButton[1] = (HwRev < 2) ? 21 : 27;
	PinButton[2] = 22;
	PinButton[3] = 23;
	PinButton[4] = 24;
	
	bcm2835_gpio_fsel(PinButton[0],BCM2835_GPIO_FSEL_INPT)	;	// Set GPIO Pin to Input 
	bcm2835_gpio_fsel(PinButton[1],BCM2835_GPIO_FSEL_INPT)	;	// Set GPIO Pin to Input 
	bcm2835_gpio_fsel(PinButton[2],BCM2835_GPIO_FSEL_INPT)	;	// Set GPIO Pin to Input 
	bcm2835_gpio_fsel(PinButton[3],BCM2835_GPIO_FSEL_INPT)	;	// Set GPIO Pin to Input 
	bcm2835_gpio_fsel(PinButton[4],BCM2835_GPIO_FSEL_INPT)	;	// Set GPIO Pin to Input 

	bcm2835_gpio_set_pud(PinButton[0],BCM2835_GPIO_PUD_UP); 	// Enable Pullup
	bcm2835_gpio_set_pud(PinButton[1],BCM2835_GPIO_PUD_UP); 	// Enable Pullup
	bcm2835_gpio_set_pud(PinButton[2],BCM2835_GPIO_PUD_UP); 	// Enable Pullup
	bcm2835_gpio_set_pud(PinButton[3],BCM2835_GPIO_PUD_UP); 	// Enable Pullup
	bcm2835_gpio_set_pud(PinButton[4],BCM2835_GPIO_PUD_UP); 	// Enable Pullup	
	
	// LCD Display
	bcm2835_gpio_fsel(PIN_LCD_MOSI,     BCM2835_GPIO_FSEL_OUTP);	// GPIO10 Output: MOSI
	bcm2835_gpio_fsel(PIN_LCD_SCLK,     BCM2835_GPIO_FSEL_OUTP);	// GPIO11 Output: SCLK
	bcm2835_gpio_fsel(PIN_LCD_RST,      BCM2835_GPIO_FSEL_OUTP);	// GPIO25 Output: RST
	bcm2835_gpio_fsel(PIN_LCD_CS ,      BCM2835_GPIO_FSEL_OUTP);	// GPIO8  Output: CS
	bcm2835_gpio_fsel(PIN_LCD_RS,       BCM2835_GPIO_FSEL_OUTP);	// GPIO7  Output: RS
	bcm2835_gpio_fsel(PIN_LCD_BACKLIGHT,BCM2835_GPIO_FSEL_OUTP);	// GPIO18 Output: Backlight
	
	Button = ButtonMem = ButtonPressed = 0;
	
	return 1;
}

//--------------------------------------------------------------------------------------------------
// Name:      UpdateButtons
// Function:  Read button states and save them to the variable "Button" and "ButtonPressed"
//            
// Parameter: 
// Return:    
//--------------------------------------------------------------------------------------------------
void UpdateButtons(void)
{
	ButtonMem = Button;		// Save last State
	
	Button = 0;
	if(!bcm2835_gpio_lev(PinButton[0])) Button |= (1<<0);
	if(!bcm2835_gpio_lev(PinButton[1])) Button |= (1<<1);
	if(!bcm2835_gpio_lev(PinButton[2])) Button |= (1<<2);
	if(!bcm2835_gpio_lev(PinButton[3])) Button |= (1<<3);
	if(!bcm2835_gpio_lev(PinButton[4])) Button |= (1<<4);
	
	ButtonPressed = (Button ^ ButtonMem) & Button;			// Set by Pressing a Button
}

//--------------------------------------------------------------------------------------------------
// Name:        GetRaspberryHwRevision
// Function:  	Check wich Hardware is used:
//				http://www.raspberrypi.org/archives/1929
//	
//				Model B Revision 1.0 									2
//				Model B Revision 1.0 + ECN0001 (no fuses, D14 removed) 	3
//				Model B Revision 2.0 									4, 5, 6
//            
// Parameter: 	-
// Return:      0=no info , 1=HW Rev.1, 2=HW Rev.2
//--------------------------------------------------------------------------------------------------
int GetRaspberryHwRevision(void)
{	
	FILE *fp;
	char line[32];
	char s[32];
	int i;
	
	fp = fopen("/proc/cpuinfo", "r");		// open as file
	if(fp != NULL)
	{	
		while(fgets(line,32,fp))			// get line
		{
			sscanf(line,"%s : %x",(char*)&s,&i);		// parse for key and value
			if(strcmp(s,"Revision") == 0)				// check for "Revision"
			{			
				//printf("Found: %s=%i\r\n",s,i);
				if(i < 4)  return 1;
				else		return 2;
			}
		}
	}
	else
	{
		//printf("cpuinfo not available.\r\n"); 
		return 0;
	}
	//printf("no revision info available.\r\n"); 
	return 0;
}


//--------------------------------------------------------------------------------------------------
// Name:    	SpiPutc
// Function:  	Emulate SPI on GPIO (Bitbanging)
//            
// Parameter: 	Databyte to send
// Return:      -
//--------------------------------------------------------------------------------------------------
void SpiPutc(unsigned char d)
{
	int i,n;
	
	for(i=0;i<8;i++)
	{
		if(d & 0x80)	bcm2835_gpio_set(PIN_LCD_MOSI);		// MOSI = 1
			else		bcm2835_gpio_clr(PIN_LCD_MOSI);		// MOSI = 0
		d <<= 1;
		
		for(n=0;n<4;n++) bcm2835_gpio_clr(PIN_LCD_SCLK); 	// CLK = 0
		for(n=0;n<4;n++) bcm2835_gpio_set(PIN_LCD_SCLK);	// CLK = 1
	}
}

//--------------------------------------------------------------------------------------------------
// Name:    	SetBacklight
// Function:  	Hintergrundbeleuchtung
//            
// Parameter: 	0=Off 1=On
// Return:      -
//--------------------------------------------------------------------------------------------------
void SetBacklight(uint8 light)
{
	if(light)	bcm2835_gpio_set(PIN_LCD_BACKLIGHT);
		else	bcm2835_gpio_clr(PIN_LCD_BACKLIGHT)	;
}

//--------------------------------------------------------------------------------------------------
// Name:    	SleepMs
// Function:  	Sleep /Delay in Milliseconds
//            
// Parameter: 	Milliseconds
// Return:      -
//--------------------------------------------------------------------------------------------------
void SleepMs(uint32 ms)
{
	bcm2835_delay(ms);
}


