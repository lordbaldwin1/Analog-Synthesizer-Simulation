import numpy as np
import sounddevice as sd
from scipy.io import wavfile
from scipy.signal import butter, lfilter
import argparse
import keyboard

fs = 44100

keyboard_mapping = {
    'a': 261.63,  # C4
    'w': 277.18,  # C#4/Db4
    's': 293.66,  # D4
    'e': 311.13,  # D#4/Eb4
    'd': 329.63,  # E4
    'f': 349.23,  # F4
    't': 369.99,  # F#4/Gb4
    'g': 392.00,  # G4
    'y': 415.30,  # G#4/Ab4
    'h': 440.00,  # A4
    'u': 466.16,  # A#4/Bb4
    'j': 493.88,  # B4
}

def play(tone, duration):
    sd.play(tone, fs)
    sd.wait()

def sine_wave(freq, duration):
    t = np.linspace(0, duration, int(fs * duration), False)
    note = np.sin(freq * t * 2 * np.pi)
    return note

def square_wave(freq, duration):
    t = np.linspace(0, duration, int(fs * duration), False)
    note = np.sign(np.sin(freq * t * 2 * np.pi))
    return note

def sawtooth_wave(freq, duration):
    t = np.linspace(0, duration, int(fs * duration), False)
    note = 2 * (t * freq - np.floor(1/2 + t * freq))
    return note

def triangle_wave(freq, duration):
    t = np.linspace(0, duration, int(fs * duration), False)
    note = 2 * np.abs(2 * (t * freq - np.floor(1/2 + t * freq))) - 1
    return note

def envelope(envelope, wave):
    attack, decay, sustain, release = envelope
    total_length = len(wave)
    attack_length = int(total_length * attack / (attack + decay + sustain + release))
    decay_length = int(total_length * decay / (attack + decay + sustain + release))
    sustain_length = int(total_length * sustain / (attack + decay + sustain + release))
    release_length = total_length - (attack_length + decay_length + sustain_length)

    attack_curve = np.linspace(0, 1, attack_length)
    decay_curve = np.linspace(1, 0.5, decay_length)
    sustain_curve = np.full(sustain_length, 0.5)
    release_curve = np.linspace(0.5, 0, release_length)

    adsr_curve = np.concatenate([attack_curve, decay_curve, sustain_curve, release_curve])
    return wave * adsr_curve

def save_wave(filename, data, samplerate):
    data = np.int16((data / data.max()) * 32767)
    wavfile.write(filename, samplerate, data)

def lowpass(cutoff, fs, order=4):
    x = 0.5 * fs
    cutoff2 = cutoff / x
    b, a = butter(order, cutoff2, btype='low', analog=False)
    return b, a

def low_pass_filter(data, cutoff_freq, fs, order=5):
    b, a = lowpass(cutoff_freq, fs, order=order)
    y = lfilter(b, a, data)
    return y

def apply_saturation(wave, level):
    return np.tanh(level * wave)

parser = argparse.ArgumentParser(description="synthesizer")
parser.add_argument('-freq', type=float, default=261.63, help="frequency of the note")
parser.add_argument('-duration', type=float, default=2.0, help="duration of the note")
parser.add_argument('-interactive', action='store_true', help="Enable interactive mode to play notes using the keyboard")
args = parser.parse_args()

adsr_envelope = (0.1, 0.2, 0.6, 0.1)

if args.interactive:
    print("Interactive mode: Press keys to play notes. Press ESC to exit.")
    while True:
        for key, freq in keyboard_mapping.items():
            if keyboard.is_pressed(key):
                note = envelope(adsr_envelope, sine_wave(freq, args.duration))
                play(note, args.duration)
                while keyboard.is_pressed(key):
                    pass
        if keyboard.is_pressed('esc'):
            print("Exiting interactive mode...")
            break
else:
    frequency = args.freq 
    duration = args.duration

    sine_wave_note = envelope(adsr_envelope, sine_wave(frequency, duration))
    square_wave_note = envelope(adsr_envelope, square_wave(frequency, duration))
    sawtooth_wave_note = envelope(adsr_envelope, sawtooth_wave(frequency, duration))
    triangle_wave_note = envelope(adsr_envelope, triangle_wave(frequency, duration))

    combined_wave = (sine_wave_note + square_wave_note + sawtooth_wave_note + triangle_wave_note) / 4

    cutoff_frequency = 2500
    filtered_wave = low_pass_filter(combined_wave, cutoff_frequency, fs)

    saturation_level = 1.5
    saturated_wave = apply_saturation(filtered_wave, saturation_level)

    save_wave('saturated_filtered_combined_wave.wav', saturated_wave, fs)
    play(saturated_wave, duration)