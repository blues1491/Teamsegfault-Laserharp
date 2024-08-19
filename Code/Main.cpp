#include <SFML/Audio.hpp>
#include <iostream>
#include <thread>
#include <vector>
#include <string>
#include <unordered_map>
#include <unistd.h>
#include <pigpio.h>


// Installs: sudo apt-get install libsfml-dev git build-essential pigpio alsa-utils
// Enable GPOI code: sudo systemctl enable pigpiod
// Start Gpio reading: sudo systemctl start pigpiod

// Compile with: g++ -Wall -g -o Main.cpp -lpigpio -lrt -pthread -lsfml-audio -lsfml-system Main
// Run with: sudo ./Main


void monitorGPIO(int gpio_pin, const std::string& sound_file, const std::string& folder)
{
    gpioSetMode(gpio_pin, PI_INPUT);

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
            std::cerr << "Failed to read GPIO value for pin " << gpio_pin << std::endl;
            return;
        }

        if (value == 0) // 0 = reading input from laser
        {
            sound.play();
            while (sound.getStatus() == sf::Sound::Playing) {}
        }
    }
}

int main()
{
    std::string folder = "Sound Samples/";
    std::unordered_map<int, std::string> gpio_to_sound = 
    {
        {21, "C3.wav"},
        {20, "D3.wav"},
        {16, "E3.wav"},
        {12, "F3.wav"},
        {25, "G3.wav"},
        {24, "A3.wav"},
        {23, "B3.wav"}
    };
    
    if (gpioInitialise() < 0) 
    {
        std::cerr << "GPIO initialization failed." << std::endl;
        return 1;
    }


    std::vector<std::thread> threads;

    for (const auto& entry : gpio_to_sound)
        threads.emplace_back(monitorGPIO, entry.first, entry.second, folder);

    for (auto& t : threads)
        t.join();
    
    gpioTerminate();

    return 0;
}
