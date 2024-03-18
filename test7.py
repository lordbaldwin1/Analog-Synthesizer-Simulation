import numpy as np
import sounddevice as sd
from scipy.signal import butter, lfilter
import tkinter as tk
from tkinter import Scale, Button, Label, HORIZONTAL, Radiobutton, IntVar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

fs = 44100

def generate_wave(form, freq, duration):
    t = np.linspace(0, duration, int(fs * duration), False)
    if form == 'sine':
        return np.sin(freq * t * 2 * np.pi)
    elif form == 'square':
        return np.sign(np.sin(freq * t * 2 * np.pi))
    elif form == 'sawtooth':
        return 2 * (t * freq - np.floor(1/2 + t * freq))
    elif form == 'triangle':
        return 2 * np.abs(2 * (t * freq - np.floor(1/2 + t * freq))) - 1

def envelope(adsr, wave):
    attack, decay, sustain, release = adsr
    total_length = len(wave)
    attack_length = int(total_length * attack / (attack + decay + sustain + release))
    decay_length = int(total_length * decay / (attack + decay + sustain + release))
    sustain_length = int(total_length * sustain / (attack + decay + sustain + release))
    release_length = total_length - (attack_length + decay_length + sustain_length)
    attack_curve = np.linspace(0, 1, attack_length)
    decay_curve = np.linspace(1, sustain, decay_length)
    sustain_curve = np.full(sustain_length, sustain)
    release_curve = np.linspace(sustain, 0, release_length)
    adsr_curve = np.concatenate([attack_curve, decay_curve, sustain_curve, release_curve])
    return wave * adsr_curve

def lowpass(cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normalized_cutoff = cutoff / nyquist
    b, a = butter(order, normalized_cutoff, btype='low', analog=False)
    return b, a

def low_pass_filter(data, cutoff_freq, fs, order=5):
    b, a = lowpass(cutoff_freq, fs, order=order)
    return lfilter(b, a, data)

def apply_saturation(wave, level):
    return np.tanh(level * wave)

def play_sound():
    freq = frequency_scale.get()
    duration = duration_scale.get()
    attack = attack_scale.get() / 100
    decay = decay_scale.get() / 100
    sustain = sustain_scale.get() / 100
    release = release_scale.get() / 100
    cutoff_freq = cutoff_scale.get()
    saturation_level = saturation_scale.get()

    adsr = (attack, decay, sustain, release)

    if waveform_var.get() == 4:
        wave = sum([generate_wave(form, freq, duration) for form in ['sine', 'square', 'sawtooth', 'triangle']]) / 4
    else:
        forms = ['sine', 'square', 'triangle', 'sawtooth']
        wave = generate_wave(forms[waveform_var.get()], freq, duration)

    enveloped_wave = envelope(adsr, wave)
    filtered_wave = low_pass_filter(enveloped_wave, cutoff_freq, fs)
    saturated_wave = apply_saturation(filtered_wave, saturation_level)

    sd.play(saturated_wave, fs)

    plt.figure(figsize=(8, 4))
    plt.plot(np.linspace(0, duration, int(fs * duration), False), saturated_wave)
    plt.title('Generated Waveform')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.show()

root = tk.Tk()
root.title("Sound Synthesizer")

waveform_var = IntVar()
waveform_var.set(0)
waveforms = ['Sine Wave', 'Square Wave', 'Triangle Wave', 'Sawtooth Wave', 'Combined Wave']
for i, waveform in enumerate(waveforms):
    Radiobutton(root, text=waveform, variable=waveform_var, value=i).pack(anchor=tk.W)

frequency_scale = Scale(root, from_=100, to=2000, orient=HORIZONTAL, label="Frequency (Hz)")
frequency_scale.set(440)
frequency_scale.pack()

duration_scale = Scale(root, from_=1, to=5, orient=HORIZONTAL, label="Duration (seconds)")
duration_scale.set(2)
duration_scale.pack()

attack_scale = Scale(root, from_=0, to=100, orient=HORIZONTAL, label="Attack (%)")
attack_scale.set(10)
attack_scale.pack()

decay_scale = Scale(root, from_=0, to=100, orient=HORIZONTAL, label="Decay (%)")
decay_scale.set(20)
decay_scale.pack()

sustain_scale = Scale(root, from_=0, to=100, orient=HORIZONTAL, label="Sustain (level)")
sustain_scale.set(60)
sustain_scale.pack()

release_scale = Scale(root, from_=0, to=100, orient=HORIZONTAL, label="Release (%)")
release_scale.set(10)
release_scale.pack()

cutoff_scale = Scale(root, from_=100, to=5000, orient=HORIZONTAL, label="Cutoff Frequency (Hz)")
cutoff_scale.set(2500)
cutoff_scale.pack()

saturation_scale = Scale(root, from_=0, to=3, resolution=0.1, orient=HORIZONTAL, label="Saturation Level")
saturation_scale.set(1.5)
saturation_scale.pack()

play_button = Button(root, text="Play", command=play_sound)
play_button.pack()

root.mainloop()
