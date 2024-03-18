# Analog-Synthesizer-Simulation - Zachary Springer


# Program Overview
Hello! This project was intended to simulate an analog synthesizer. In reality, I created a small program in Python which allows you either generate different types of wave and adjust the synthesizer settings, or you can load a wave file and adjust the synthesizer settings and play these modified waves. I also added a feature which plays a few notes which you can modify. For the loaded and generated waves, there is a visual representation of the waves produced on the GUI. As should have been said, this program, when run, opens a little GUI that lets you use all of its features.

# How to Build and Run
This program is coded in Python, so you will need an up-to-date Python interpreter to run the script. Personally, I am using Python version 3.12 and the libraries used may not work on older versions of Python. This program uses numpy, sounddevice, scipy, and matplotlib which will need to be installed to run this script. Apart from that, the script should be pretty straight forward in an environment which can run Python scripts, simply type, "python synthesizer.py". 
# Testing
It was difficult for me to test my code as the only intended output I had was from other synthesizers that people had created in Python. The only issue is that I couldn't find any that were similar to mine because most people were using a synthesizer with MIDI and I couldn't seem to get that working. My only testing was with the visualization of the waves that were produced. I also tested my output by saving some waveforms to wave files and looking at them in Audacity.

# View of Program
![Alt text](https://media.discordapp.net/attachments/578719648988528660/1219237433670111262/8c03c609aa2f505055a22456d949de44.png?ex=660a9258&is=65f81d58&hm=d6e2010ce02f91573b1a63b2b20dea8b6660af763701613d2a0e16de182e3b7a&=&format=webp&quality=lossless&width=628&height=676 "Optional title")

# What Worked?
There was a lot that did not work with this program. Initially, I wanted to create a piano that would take keyboard inputs and synthesize them based on settings either hard coded or adjusted through command line arguments. I tried for many hours to get this to work, but it was never responsive enough for my liking. I also tried setting up a virtual MIDI piano, but I couldn't get it to connect properly to my script. Eventually I ended up going back to the basic generation of waves and built some things from there which I thought were interesting. This was my first time building a program with a GUI so I'm somewhat satisfied with that. Apart from that I'm fairly disappointed with how everything sounds and I'm not entirely sure that the synthesizing is working as it should. In the future, I would like to try making a playable piano again.