#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>

#define GPIO_PIN 17  // Replace with your GPIO pin number

void export_gpio(int pin) {
    int fd = open("/sys/class/gpio/export", O_WRONLY);
    if (fd == -1) {
        perror("Unable to open /sys/class/gpio/export");
        exit(1);
    }
    
    char buffer[3];
    int len = snprintf(buffer, sizeof(buffer), "%d", pin);
    if (write(fd, buffer, len) != len) {
        perror("Error writing to /sys/class/gpio/export");
        exit(1);
    }
    
    close(fd);
}

void set_gpio_direction(int pin, const char* direction) {
    char path[35];
    snprintf(path, sizeof(path), "/sys/class/gpio/gpio%d/direction", pin);
    
    int fd = open(path, O_WRONLY);
    if (fd == -1) {
        perror("Unable to open GPIO direction file");
        exit(1);
    }
    
    if (write(fd, direction, strlen(direction)) != strlen(direction)) {
        perror("Error writing to GPIO direction file");
        exit(1);
    }
    
    close(fd);
}

int read_gpio_value(int pin) {
    char path[30];
    snprintf(path, sizeof(path), "/sys/class/gpio/gpio%d/value", pin);
    
    int fd = open(path, O_RDONLY);
    if (fd == -1) {
        perror("Unable to open GPIO value file");
        exit(1);
    }
    
    char value;
    if (read(fd, &value, 1) != 1) {
        perror("Error reading GPIO value");
        exit(1);
    }
    
    close(fd);
    
    return value - '0';
}

int main() {
    export_gpio(GPIO_PIN);
    set_gpio_direction(GPIO_PIN, "in");

    while (1) {
        int value = read_gpio_value(GPIO_PIN);
        printf("GPIO %d value: %d\n", GPIO_PIN, value);
        sleep(1);  // Read every 1 second
    }

    return 0;
}
