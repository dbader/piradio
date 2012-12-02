//------------------------------------------------------------------------------
//                                  _            _
//                                 | |          | |
//      ___ _ __ ___  ___ _   _ ___| |_ ___  ___| |__
//     / _ \ '_ ` _ \/ __| | | / __| __/ _ \/ __| '_ \.
//    |  __/ | | | | \__ \ |_| \__ \ ||  __/ (__| | | |
//     \___|_| |_| |_|___/\__, |___/\__\___|\___|_| |_|
//                         __/ |
//                        |___/    Engineering
//
// File:        std_c.h
// Description: Basic typedefinitions for portable C-Code
//
// Author:      Martin Steppuhn
// History:     01.01.2006 Initial version
//------------------------------------------------------------------------------

#ifndef STD_C_H
#define STD_C_H

/**** Includes ****************************************************************/

/**** Preprocessing directives (#define) **************************************/

// Boolean values

#define TRUE                1
#define FALSE               0

#define true                1
#define false               0

/**** Type definitions (typedef) **********************************************/

// Standard types

typedef unsigned char     uint8;
typedef unsigned short    uint16;
typedef unsigned long     uint32;

typedef unsigned long     ulong;

typedef unsigned char     bool;

typedef signed char       int8;
typedef signed short      int16;
typedef signed long       int32;

/**** Global constants (extern) ***********************************************/

/**** Global variables (extern) ***********************************************/

/**** Global function prototypes **********************************************/

#endif
