#include "sysfs_gpio.h"
#include <SFML/Audio.hpp>
#include <iostream>
#include <thread>
#include <vector>
#include <string>
#include <unordered_map>
#include <unistd.h>

using namespace std;

void monitorGPIO(int gpio_pin, const std::string& sound_file, const std::string& folder)
{
    // Export the GPIO pin and set direction to input
    gpioInput(gpio_pin);

    // Load the sound file
    sf::SoundBuffer buffer;
    if (!buffer.loadFromFile(folder + sound_file))
    {
        std::cerr << "Error loading " << folder + sound_file << std::endl;
        return;
    }

    sf::Sound sound;
    sound.setBuffer(buffer);

    while (true)
    {
        int value = gpioRead(gpio_pin);
        if (value == -1)
        {
            cerr << "Failed to read GPIO value for pin " << gpio_pin << endl;
            return;
        }

        if (value == 0)
        {
            sound.play();
            while (sound.getStatus() == sf::Sound::Playing)
            {
                // Keep the program running to allow the sound to finish playing
                usleep(100000); // Sleep for 100 ms
            }
        }

        usleep(10000); // Sleep for 500 ms before reading again
    }
}

int main()
{
    std::string folder = "../Sound Samples/";
    std::unordered_map<int, std::string> gpio_to_sound = {
        {17, "C3.wav"},
        {27, "E3.wav"}
    };

    std::vector<std::thread> threads;

    for (const auto& entry : gpio_to_sound)
    {
        threads.emplace_back(monitorGPIO, entry.first, entry.second, folder);
    }

    for (auto& t : threads)
    {
        t.join();
    }

    return 0;
}
