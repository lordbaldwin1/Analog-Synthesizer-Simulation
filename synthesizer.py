# Zachary Springer
# 3/18/2024
# CS410P Music, Sound, & Computers
# This program is a basic synthesizer which allows you to do a couple of things
# First, you can generate and play sine, square, sawtooth, and triangle waves.
# You can also combine these waves and play them. You have several options to
# adjust the sound of these waves through sliders on the GUI. You can also
# load a wave file to play it through the synthesizer. You can also play
# a short sequence of notes (which I wish I had implemented my Aleatoric code).
# For all of these things except the short measure of notes, the waveform produced
# is displayed on the GUI.

# Imported Libraries
import numpy as np
import sounddevice as sd
from scipy.io import wavfile
import tkinter as tk
from tkinter import Scale, Button, Label, HORIZONTAL, Radiobutton, IntVar, filedialog, Frame
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import style
import threading
import time

# Global Variables
sample_rate = 44100
loaded_wave = None
loaded_wave_sample_rate = None
measure_flag = False
measure_thread = None
measure_notes = [440, 494, 523, 587, 659, 698, 784]
measure_durations = [0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4]
note_interval = 0.5

# This function plays notes from measure_notes
def measure():
    global measure_flag

    while measure_flag:
        for note, duration in zip(measure_notes, measure_durations):
            if not measure_flag:
                break
            synth_tone(note, duration)
            time.sleep(note_interval)

# This function grabs settings from the sliders in the GUI
# if combined wave is chose, it generates and sums the waves
# else, it selects the chosen wave and generates it.
# Then, it is passed through the ADSR envelope, lowpass filter,
# and saturation and played.
def synth_tone(freq, duration):
    if not measure_flag:
        return
    
    global loaded_wave, loaded_wave_sample_rate

    lfo_rate = lfor_scale.get()
    lfo_depth = lfod_scale.get() / 100

    attack = att_scale.get() / 100
    decay = dur_scale.get() / 100
    sustain = sus_scale.get() / 100
    release = rel_scale.get() / 100

    cutoff_freq = cut_scale.get()

    saturation_level = sat_scale.get()

    adsr = (attack, decay, sustain, release)

    if waveform_var.get() == 4:
        wave = sum([gen_wave(form, freq, duration, lfo_rate, lfo_depth) for form in ['sine', 'square', 'sawtooth', 'triangle']]) / 4
    else:
        forms = ['sine', 'square', 'triangle', 'sawtooth']
        selected_form = forms[waveform_var.get()]
        wave = gen_wave(selected_form, freq, duration, lfo_rate, lfo_depth)

    enveloped_wave = envelope(adsr, wave)

    filtered_wave = lp_filter(enveloped_wave, cutoff_freq, sample_rate)

    saturated_wave = apply_saturation(filtered_wave, saturation_level)

    sd.play(saturated_wave, sample_rate)
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

def save_wave(filename, data, samplerate):
    data = np.int16((data / data.max()) * 32767)
    wavfile.write(filename, samplerate, data)

frequency = 261.63 
duration = 2.0  

sine_wave = sine_wave(frequency, duration)
save_wave('sine_wave.wav', sine_wave, fs)
play(sine_wave, duration)

square_wave = square_wave(frequency, duration)
save_wave('square_wave.wav', square_wave, fs)

sawtooth_wave = sawtooth_wave(frequency, duration)
save_wave('sawtooth_wave.wav', sawtooth_wave, fs)
