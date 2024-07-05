#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <wiringPi.h>

#define GPIO_PIN 17 // Replace with your desired GPIO pin number

int main() {
    // Initialize WiringPi using the Broadcom pin number scheme
    if (wiringPiSetupGpio() == -1) {
        perror("wiringPiSetupGpio");
        return EXIT_FAILURE;
    }

    // Set the GPIO pin to input mode with an internal pull-up resistor
    pinMode(GPIO_PIN, INPUT);
    pullUpDnControl(GPIO_PIN, PUD_UP);

    // Read the GPIO pin value in a loop to see changes
    while (1) {
        int value = digitalRead(GPIO_PIN);
        printf("GPIO %d value: %d\n", GPIO_PIN, value);

        // Sleep for a short period to avoid flooding the console
        usleep(500000); // 500 milliseconds
    }

    return EXIT_SUCCESS;
}
