// Sysfs RPi 3b/3b+ GPIO Library
// UTA Computer Engineering
// Jason Losh

//-----------------------------------------------------------------------------
// Hardware Target
//-----------------------------------------------------------------------------

// Target Platform: RPi 3b/3b+
// Target uC:       BCM2837
// System Clock:    -

// Notes:
// It is more efficient to not open and close files for each call 
// to read and write, but this approach makes the code simple to understand

// Usage:
// Call gpioOutput or gpioINput to set the pin direction to out or in
// Call gpioWrite to update the value of an output pin
// Call gpioRead to get the status of a pin

//-----------------------------------------------------------------------------
// Device includes, defines, and assembler directives
//-----------------------------------------------------------------------------

#include <stdio.h>

//-----------------------------------------------------------------------------
// Subroutines
//-----------------------------------------------------------------------------

void gpioOutput(int pin)
{
    FILE* file;
    char str[35];
    file = fopen("/sys/class/gpio/export", "w");
    fprintf(file, "%d", pin);
    fclose(file);
    sprintf(str, "/sys/class/gpio/gpio%d/direction", pin);
    file = fopen(str, "w");
    fprintf(file, "out");
    fclose(file);
}

void gpioInput(int pin)
{
    FILE* file;
    char str[35];
    file = fopen("/sys/class/gpio/export", "w");
    fprintf(file, "%d", pin);
    fclose(file);
    sprintf(str, "/sys/class/gpio/gpio%d/direction", pin);
    file = fopen(str, "w");
    fprintf(file, "in");
    fclose(file);
}

void gpioWrite(int pin, int value)
{
    FILE* file;
    char str[35];
    sprintf(str, "/sys/class/gpio/gpio%d/value", pin);
    file = fopen(str, "w");
    fprintf(file, "%d", value);
    fclose(file);
}
  
int gpioRead(int pin)
{
    FILE* file;
    int result;
    char str[30];
    sprintf(str, "/sys/class/gpio/gpio%d/value", pin);
    file = fopen(str, "rw");
    fscanf(file, "%d", &result);
    fclose(file);
    return result;
}
