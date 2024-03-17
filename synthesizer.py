import numpy as np
import sounddevice as sd
from scipy.io import wavfile
fs = 44100

def play_tone(tone, duration):
    sd.play(tone, fs)
    sd.wait()

def generate_sine_wave(freq, duration):
    t = np.linspace(0, duration, int(fs * duration), False)
    note = np.sin(freq * t * 2 * np.pi)
    return note

def generate_square_wave(freq, duration):
    t = np.linspace(0, duration, int(fs * duration), False)
    note = np.sign(np.sin(freq * t * 2 * np.pi))
    return note

def generate_sawtooth_wave(freq, duration):
    t = np.linspace(0, duration, int(fs * duration), False)
    note = 2 * (t * freq - np.floor(1/2 + t * freq))
    return note

def save_wave(filename, data, samplerate):
    wavfile.write(filename, samplerate, data)

frequency = 261.63 
duration = 2.0  

sine_wave = generate_sine_wave(frequency, duration)
save_wave('sine_wave.wav', sine_wave, fs)

square_wave = generate_square_wave(frequency, duration)
save_wave('square_wave.wav', square_wave, fs)

sawtooth_wave = generate_sawtooth_wave(frequency, duration)
save_wave('sawtooth_wave.wav', sawtooth_wave, fs)