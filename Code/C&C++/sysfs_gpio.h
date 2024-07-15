// Sysfs RPi 3b/3b+ GPIO Library
// UTA Computer Engineering
// Jason Losh

//-----------------------------------------------------------------------------
// Hardware Target
//-----------------------------------------------------------------------------

// Target Platform: RPi 3b/3b+
// Target uC:       BCM2837
// System Clock:    -

//-----------------------------------------------------------------------------
// Device includes, defines, and assembler directives
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// Subroutines
//-----------------------------------------------------------------------------

#ifndef SYSFS_GPIO_H_
#define SYSFS_GPIO_H_

// Called to configure the pin as an input or output
void gpioOutput(int pin);
void gpioInput(int pin);

// Called to set and output pin to a given value (1 or 0)
void gpioWrite(int pin, int value);

// Called to get the status (1 or 0) of a pin
int gpioRead(int pin);

#endif
