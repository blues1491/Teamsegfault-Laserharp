#include <iostream>
#include <fstream>
#include <string>
#include <unistd.h>

class GPIO {
public:
    GPIO(int pin) : pinNumber(pin) {
        exportGPIO();
        setDirection("in");
    }

    ~GPIO() {
        unexportGPIO();
    }

    int readValue() {
        std::string path = "/sys/class/gpio/gpio" + std::to_string(pinNumber) + "/value";
        std::ifstream gpioValueFile(path);

        if (!gpioValueFile.is_open()) {
            std::cerr << "Failed to open GPIO value file: " << path << std::endl;
            return -1;
        }

        std::string value;
        gpioValueFile >> value;
        gpioValueFile.close();

        return std::stoi(value);
    }

private:
    int pinNumber;

    void exportGPIO() {
        std::ofstream exportFile("/sys/class/gpio/export");
        if (!exportFile.is_open()) {
            std::cerr << "Failed to open export file" << std::endl;
            return;
        }
        exportFile << pinNumber;
        exportFile.close();
    }

    void unexportGPIO() {
        std::ofstream unexportFile("/sys/class/gpio/unexport");
        if (!unexportFile.is_open()) {
            std::cerr << "Failed to open unexport file" << std::endl;
            return;
        }
        unexportFile << pinNumber;
        unexportFile.close();
    }

    void setDirection(const std::string &direction) {
        std::string path = "/sys/class/gpio/gpio" + std::to_string(pinNumber) + "/direction";
        std::ofstream directionFile(path);

        if (!directionFile.is_open()) {
            std::cerr << "Failed to open direction file: " << path << std::endl;
            return;
        }

        directionFile << direction;
        directionFile.close();
    }
};

int main() {
    int gpioPin = 17; // Change this to the GPIO pin number you want to read

    GPIO gpio(gpioPin);

    while (true) {
        int value = gpio.readValue();
        std::cout << "GPIO " << gpioPin << " value: " << value << std::endl;
        usleep(500000); // Sleep for 500 ms
    }

    return 0;
}
