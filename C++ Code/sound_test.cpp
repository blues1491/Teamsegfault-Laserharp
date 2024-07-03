#include <SFML/Audio.hpp>
#include <iostream>
#include <vector>
#include <string>
#include <thread>
#include <chrono>
#include <unordered_map>

//First do: sudo apt-get install libsfml-dev git build-essential

int main()
{
    std::string folder = "Sound Samples/"; 
    std::vector<std::string> soundFiles = {"C3.wav", "D3.wav", "E3.wav", "F3.wav", "G3.wav", "A3.wav", "B3.wav", "C4.wav"}; 
    
    std::vector<sf::SoundBuffer> buffers(soundFiles.size());
    std::vector<sf::Sound> sounds(soundFiles.size());
    
    for (size_t i = 0; i < soundFiles.size(); ++i) 
    {
        std::string fullPath = folder + soundFiles[i];
        if (!buffers[i].loadFromFile(fullPath)) 
        {
            std::cerr << "Error loading " << fullPath << std::endl;
            return -1;
        }
        sounds[i].setBuffer(buffers[i]);
    }

    // Map laser inputs to sound indices
    std::unordered_map<int, int> laserToSoundMap = 
    {
        {0, 0}, // Laser 0 -> C3
        {1, 1}, // Laser 1 -> D3
        {2, 2}, // Laser 2 -> E3
        {3, 3}, // Laser 3 -> F3
        {4, 4}, // Laser 4 -> G3
        {5, 5}, // Laser 5 -> A3
        {6, 6}, // Laser 6 -> B3
        {7, 7}  // Laser 7 -> C4
    };
    
    for(const auto& pair : laserToSoundMap)
    {
        sounds[pair.second].play();
        std::this_thread::sleep_for(std::chrono::milliseconds(500)); // Add delay between playing sounds
    }

    // Keep the program running to allow all sounds to finish playing
    std::this_thread::sleep_for(std::chrono::seconds(5));
}
