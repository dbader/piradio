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
// Filename:    
// Description: 
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
// History:     05.11.2012 Initial version V0.9.0
//--------------------------------------------------------------------------------------------------

//=== Includes =====================================================================================

#include "std_c.h"
#include "lcd.h"
#include <stdio.h>
#include <stdlib.h>
#include "raspilcd.h"

//=== Preprocessing directives (#define) ===========================================================

//=== Type definitions (typedef) ===================================================================

//=== Global constants =============================================================================

//=== Global variables =============================================================================

//=== Local constants  =============================================================================

#include "font_terminal_6x8.inc"
#include "font_terminal_12x16.inc"
#include "font_fixedsys_8x15.inc"
#include "font_lucida_10x16.inc"

//=== Local variables ==============================================================================

uint8	framebuffer[LCD_WIDTH][LCD_HEIGHT/8];
uint8	PenColor;
uint8	FillColor;
uint8	FontNumber;

//=== Local function prototypes ====================================================================

void lcd_write_cmd(uint8 d);
void lcd_write_data(uint8 d);
void lcd_set_xy(uint8 x,uint8 ypage);

//--------------------------------------------------------------------------------------------------
// Name:      LCD_SSetPenColor
// Function:  Set pen color
//            
// Parameter: 0=White 1=Black
// Return:    -
//--------------------------------------------------------------------------------------------------
void LCD_SetPenColor(uint8 c)
{
	PenColor = c;
}

//--------------------------------------------------------------------------------------------------
// Name:      LCD_SSetFillColor
// Function:  Set fill color
//            
// Parameter: -1=transparent, 0=white, 1=black
// Return:    
//--------------------------------------------------------------------------------------------------
void LCD_SetFillColor(int8 c)
{
	FillColor = c;
}

//--------------------------------------------------------------------------------------------------
// Name:      LCD_SSetFont 
// Function:  Set font 
//            
// Parameter: 0..3 for Fonts
// Return:    -
//--------------------------------------------------------------------------------------------------
void LCD_SetFont(uint8 f)
{
	FontNumber = f;
}

//--------------------------------------------------------------------------------------------------
// Name:      LCD_ClearScreen
// Function:  Clear Screen
//            
// Parameter: -
// Return:    -
//--------------------------------------------------------------------------------------------------
void LCD_ClearScreen(void)
{
	uint16	x,y;
	
	for(y=0;y<(LCD_HEIGHT/8);y++) 
	{
		for(x=0;x<LCD_WIDTH;x++)  framebuffer[x][y] = 0;
	}
}

//--------------------------------------------------------------------------------------------------
// Name:      LCD_PutPixel
// Function:  Set single pixel at x,x
//            
// Parameter: x,y position, color
// Return:    -
//--------------------------------------------------------------------------------------------------
void LCD_PutPixel(uint8 x,uint8 y,uint8 color)
{
	if((x < LCD_WIDTH) && (y < LCD_HEIGHT))
	{
		if(color)	framebuffer[x][y>>3] |=   (1<<(y & 7));
			else	framebuffer[x][y>>3] &=  ~(1<<(y & 7));
	}
}

//--------------------------------------------------------------------------------------------------
// Name:      LCD_DrawLine
// Function:  Draw line from xy to xy 
//            
// Parameter: Start and endpoint
// Return:    -
//--------------------------------------------------------------------------------------------------
void LCD_DrawLine(uint8 x0,uint8 y0,uint8 x1,uint8 y1)
{
	int16  dx,sx,dy,sy,err,e2;  // for Bresenham
	int8	i;
	
	if(y0 == y1)			// horizontale Linie
	{
		if(x0 > x1) { i=x0; x0=x1; x1=i; } 	// swap direction
		while (x0 <= x1)	LCD_PutPixel(x0++,y0,PenColor);
	}
	else if(x0 == x1)		// vertikale Linie
	{
		if(y0 > y1) { i=y0; y0=x1; y1=i; } 	// swap direction
		while (y0 <= y1)	LCD_PutPixel(x0,y0++,PenColor);
	}
	else		// Bresenham Algorithmus
	{
		dx = abs(x1-x0);
		sx = x0<x1 ? 1 : -1;
		dy = -abs(y1-y0);
		sy = y0<y1 ? 1 : -1; 
		err = dx+dy; 
 		for(;;)
		{
			LCD_PutPixel(x0,y0,PenColor);
			if (x0==x1 && y0==y1) break;
			e2 = 2*err;
			if (e2 > dy) { err += dy; x0 += sx; } /* e_xy+e_x > 0 */
			if (e2 < dx) { err += dx; y0 += sy; } /* e_xy+e_y < 0 */
		}
	}
}

//--------------------------------------------------------------------------------------------------
// Name:      LCD_DrawCircle
// Function:  Draw circle with centerpont an radius
//			  linewidth=1 pixel, no fill
//            
// Parameter: xy centerpoint and radius
// Return:    -
//--------------------------------------------------------------------------------------------------
void LCD_DrawCircle(uint8 x0,uint8 y0,uint8 radius)
  {
    int f = 1 - radius;
    int ddF_x = 0;
    int ddF_y = -2 * radius;
    int x = 0;
    int y = radius;
 
    LCD_PutPixel(x0, y0 + radius,PenColor);
    LCD_PutPixel(x0, y0 - radius,PenColor);
    LCD_PutPixel(x0 + radius, y0,PenColor);
    LCD_PutPixel(x0 - radius, y0,PenColor);
 
    while(x < y) 
    {
      if(f >= 0) 
      {
        y--;
        ddF_y += 2;
        f += ddF_y;
      }
      x++;
      ddF_x += 2;
      f += ddF_x + 1;
 
      LCD_PutPixel(x0 + x, y0 + y,PenColor);
      LCD_PutPixel(x0 - x, y0 + y,PenColor);
      LCD_PutPixel(x0 + x, y0 - y,PenColor);
      LCD_PutPixel(x0 - x, y0 - y,PenColor);
      LCD_PutPixel(x0 + y, y0 + x,PenColor);
      LCD_PutPixel(x0 - y, y0 + x,PenColor);
      LCD_PutPixel(x0 + y, y0 - x,PenColor);
      LCD_PutPixel(x0 - y, y0 - x,PenColor);
    }
}

//--------------------------------------------------------------------------------------------------
// Name:      LCD_DrawEllipse
// Function:  Draw ellipse with centerpont an "radius"
//			  linewidth=1 pixel, no fill
//            
// Parameter: xy centerpoint and "x,y radius"
// Return:    -
//--------------------------------------------------------------------------------------------------
void LCD_DrawEllipse(int xm, int ym, int a, int b)
{
   int dx = 0, dy = b; /* im I. Quadranten von links oben nach rechts unten */
   long a2 = a*a, b2 = b*b;
   long err = b2-(2*b-1)*a2, e2; /* Fehler im 1. Schritt */
 
	do 
	{
		LCD_PutPixel(xm+dx, ym+dy,PenColor); /* I. Quadrant */
		LCD_PutPixel(xm-dx, ym+dy,PenColor); /* II. Quadrant */
		LCD_PutPixel(xm-dx, ym-dy,PenColor); /* III. Quadrant */
		LCD_PutPixel(xm+dx, ym-dy,PenColor); /* IV. Quadrant */
 
		e2 = 2*err;
		if (e2 <  (2*dx+1)*b2) { dx++; err += (2*dx+1)*b2; }
		if (e2 > -(2*dy-1)*a2) { dy--; err -= (2*dy-1)*a2; }
	} 
	while (dy >= 0);
 
	while (dx++ < a) 
	{ /* fehlerhafter Abbruch bei flachen Ellipsen (b=1) */
       LCD_PutPixel(xm+dx, ym,PenColor); /* -> Spitze der Ellipse vollenden */
       LCD_PutPixel(xm-dx, ym,PenColor); 
	}
}

//--------------------------------------------------------------------------------------------------
// Name:      LCD_DrawRect
// Function:  Draw rectangle, with pencolor and fillcolor 
//            
// Parameter: two diagonal points and  linewidth
// Return:    -
//--------------------------------------------------------------------------------------------------
void LCD_DrawRect(uint8 x0,uint8 y0,uint8 x1,uint8 y1,uint8 line)
{
	uint8 x,y;

	y = y0;
	while(y<=y1)		// zeilenweise durcharbeiten
	{
		x = x0;
		while(x<=x1)
		{
			if((y < y0 + line) || (y > y1 - line) || (x < x0 + line) || (x > x1 - line))
			{
				LCD_PutPixel(x,y,PenColor);
			}
			else
			{
				if(      FillColor == 0) LCD_PutPixel(x,y,0);
				else if(FillColor == 1) LCD_PutPixel(x,y,1);
			}
			x++;
		}
		y++;
	}
}

//--------------------------------------------------------------------------------------------------
// Name:      LCD_PrintXY
// Function:  Print String
//            
// Parameter: x,y startpoint, string
// Return:    -
//--------------------------------------------------------------------------------------------------
void LCD_PrintXY(uint8 x0,uint8 y0,char *s)
{
	uint8	ix,iy,y;
	const uint8 *font;
	const uint8 *pt;
	uint8 	d;
	char c;
	uint8 char_width,char_height,char_size;
	uint8 i_char_height;
	
	if(     FontNumber == 1)   font = font_fixedsys_8x15;
	else if(FontNumber == 2)  font= font_lucida_10x16;
	else if(FontNumber == 3)  font = font_terminal_12x16;
	else					   font = font_terminal_6x8;
	
	char_size =  *font++;
	char_width  = *font++;
	char_height = *font++;
	
	while(*s)
	{
		c = 0;
		if(*s > 31) c = (*s) - 32;
		pt = &font[(uint16)c * char_size];		
		i_char_height = char_height;
		
		y = y0;
				
		while(i_char_height)
		{
			for(ix=0;ix<char_width;ix++)   
			{
				d = *pt++;
				for(iy=0;iy<8;iy++)	// je ein Byte vertikal ausgeben
				{
					if(d & (1<<iy))	LCD_PutPixel(x0+ix,y+iy,1);	
						else			LCD_PutPixel(x0+ix,y+iy,0);	
				}
			}
			i_char_height = (i_char_height >= 8) ? i_char_height - 8 : 0; 
			y+=8;		// nächste "Page"
		}	

		x0+=char_width;	
		s++;		// nächstes Zeichen
	}
}

//--------------------------------------------------------------------------------------------------
// Name:      LCD_DrawBitmap
// Function:  Draw bitmap at startingpoint
//            
// Parameter: Startpoint xy, pointer to bitmaparray
// Return:    -
//--------------------------------------------------------------------------------------------------
void LCD_DrawBitmap(uint8 x0,uint8 y0,const uint8 *bmp)
{
	uint8	width,height;
	uint16	ix,iy;
	
	width     = *bmp++;
	height    = *bmp++;
			
	for(iy=0;iy<height;iy++)
	{
		for(ix=0;ix<width;ix++)
		{
			if(bmp[ix+((iy/8)*width)] & (1<<(iy & 7))) 	LCD_PutPixel(x0+ix,y0+iy,1);
				else								LCD_PutPixel(x0+ix,y0+iy,0);
		}
	}
}

/*
//--------------------------------------------------------------------------------------------------
// Name:      LCD_DrawBitmapFromFile
// Function:  Draw bitmap from file        UNDER CONSTRUCTION !!!
//            
// Parameter: 
// Return:    
//--------------------------------------------------------------------------------------------------
void LCD_DrawBitmapFromFile(uint8 x0,uint8 y0,const char *filename)
{
	uint8	width,height;
	uint16	ix,iy;
	FILE *fp;
	uint8	buf[10000];
	uint8 i;
		
	
	fp = fopen(filename, "rb");		// open as file
	if(fp != NULL)
	{	
		fread(buf, 1, 58,fp);
		
		fread(buf,1,1024,fp);
		
		width = 128;
		height = 64;
		
		i = 0;
		for(iy=0;iy<height;iy++)
		{
			for(ix=0;ix<width;ix++)
			{
				if(buf[(ix/8)+(iy*(width/8))] & (0x80>>(ix & 7))) 	LCD_PutPixel(x0+ix,y0+(height-iy),0);
					else												LCD_PutPixel(x0+ix,y0+(height-iy),1);
			}
		}
	}
}
*/

//--------------------------------------------------------------------------------------------------
// Name:      LCD_WriteFramebuffer
// Function:  Transfer Framebuffer (RAM) to display via SPI
//            
// Parameter: -
// Return:    -
//--------------------------------------------------------------------------------------------------
void LCD_WriteFramebuffer(void)
{
	uint8	 x;
	lcd_set_xy(0,0);	for(x=0;x<LCD_WIDTH;x++)  lcd_write_data(framebuffer[x][0]);
	lcd_set_xy(0,1);	for(x=0;x<LCD_WIDTH;x++)  lcd_write_data(framebuffer[x][1]);
	lcd_set_xy(0,2);	for(x=0;x<LCD_WIDTH;x++)  lcd_write_data(framebuffer[x][2]);
	lcd_set_xy(0,3);	for(x=0;x<LCD_WIDTH;x++)  lcd_write_data(framebuffer[x][3]);
	lcd_set_xy(0,4);	for(x=0;x<LCD_WIDTH;x++)  lcd_write_data(framebuffer[x][4]);
	lcd_set_xy(0,5);	for(x=0;x<LCD_WIDTH;x++)  lcd_write_data(framebuffer[x][5]);
	lcd_set_xy(0,6);	for(x=0;x<LCD_WIDTH;x++)  lcd_write_data(framebuffer[x][6]);
	lcd_set_xy(0,7);	for(x=0;x<LCD_WIDTH;x++)  lcd_write_data(framebuffer[x][7]);
}

//--------------------------------------------------------------------------------------------------
// Name:      LCD_SetContrast
// Function:  Kontrasteinstellung
//            
// Parameter: Kontrast (0..63)     
// Return:    -
//--------------------------------------------------------------------------------------------------
void LCD_SetContrast(uint8 contrast)
{
	lcd_write_cmd(0x81);
	lcd_write_cmd(contrast);
}

//--------------------------------------------------------------------------------------------------
// Name:      LCD_Init
// Function:  Init displaycontroller
//            
// Parameter: -
// Return:    -
//--------------------------------------------------------------------------------------------------
void LCD_Init(void)
{
	LCD_RST_CLR;		// Reset LCD-Display
	SleepMs(50);		// Wait ~ 200ms	
	LCD_RST_SET;
	SleepMs(200);		// Wait ~ 200ms	

	lcd_write_cmd(0xE2);
	lcd_write_cmd(0x40);
	lcd_write_cmd(0xA1);
	lcd_write_cmd(0xC0);
	lcd_write_cmd(0xA4);
	lcd_write_cmd(0xA6);
	lcd_write_cmd(0xA2);
	lcd_write_cmd(0x2F);
	lcd_write_cmd(0x27);
	
	lcd_write_cmd(0x81);
	lcd_write_cmd(8);

	lcd_write_cmd(0xFA);
	lcd_write_cmd(0x90);
	lcd_write_cmd(0xAF);

	LCD_ClearScreen();
	LCD_WriteFramebuffer();
}

//--------------------------------------------------------------------------------------------------
//--------------------------------------------------------------------------------------------------
//--------------------------------------------------------------------------------------------------
//--------------------------------------------------------------------------------------------------


//--------------------------------------------------------------------------------------------------
// Name:      LcdWriteCmd
// Function:  Kommandobyte an Display senden
//            
// Parameter: Byte
// Return:    -
//--------------------------------------------------------------------------------------------------
void lcd_write_cmd(uint8 d)
{
	LCD_CS_CLR;
	LCD_RS_CLR;			// Command Mode
	LCD_SPI_PUTC(d);
	LCD_SPI_WAIT_BUSY;
	LCD_CS_SET;
}

//--------------------------------------------------------------------------------------------------
// Name:      lcd_write_data
// Function:  Datenbyte an Display senden
//            
// Parameter: Byte
// Return:    -
//--------------------------------------------------------------------------------------------------
void lcd_write_data(uint8 d)
{
	LCD_CS_CLR;
	LCD_RS_SET;			// Data Mode
	LCD_SPI_PUTC(d);
	LCD_SPI_WAIT_BUSY;
	LCD_CS_SET;
}

//--------------------------------------------------------------------------------------------------
// Name:      LcdSetXY
// Function:  Position für Ausgabe festlegen (Koordinaten)
//            
// Parameter: X Position (Pixel), Y Position (Page / 8 Pixel Blocks)
// Return:    -
//--------------------------------------------------------------------------------------------------
void lcd_set_xy(uint8 x,uint8 ypage)
{
	x += LCD_X_OFFSET;
	lcd_write_cmd(0x00 + (x & 0x0F));
	lcd_write_cmd(0x10 + ((x>>4) & 0x0F));
	lcd_write_cmd(0xB0 + (ypage & 0x07));
}
