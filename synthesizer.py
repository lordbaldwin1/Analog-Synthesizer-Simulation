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
<<<<<<< HEAD
from scipy.io import wavfile
fs = 44100

def play(tone, duration):
    sd.play(tone, fs)
    sd.wait()

def sine_wave(freq, duration):
=======
from scipy.signal import butter, lfilter
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
<<<<<<< HEAD

<<<<<<< HEAD
<<<<<<< HEAD
def generate_wave(form, freq, duration):
>>>>>>> c7f5cd4 (done attempting to make keyboard)
    t = np.linspace(0, duration, int(fs * duration), False)
    if form == 'sine':
        return np.sin(freq * t * 2 * np.pi)
    elif form == 'square':
        return np.sign(np.sin(freq * t * 2 * np.pi))
    elif form == 'sawtooth':
        return 2 * (t * freq - np.floor(1/2 + t * freq))
    elif form == 'triangle':
        return 2 * np.abs(2 * (t * freq - np.floor(1/2 + t * freq))) - 1
=======
sequence_notes = [440, 494, 523, 587, 659, 698, 784]
sequence_durations = [0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4]
=======
=======
>>>>>>> 0476048 (finished comments, removed extra files)
measure_notes = [440, 494, 523, 587, 659, 698, 784]
measure_durations = [0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4]
>>>>>>> 44bc7b0 (fixed formatting)
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

# This function turns on the measure flag and creates a thread
# which will execute the measure() function
def start_measure():
    global measure_flag, measure_thread

    if not measure_flag:
        measure_flag = True
        measure_thread = threading.Thread(target=measure)
        measure_thread.start()

# This function turns off the measure flag and
# makes sure the threads finished execution
def stop_measure():
    global measure_flag

    measure_flag = False

    if measure_thread:
        measure_thread.join()

# This function generates the four waves
# and returns them as a numpy array
def gen_wave(form, freq, duration, lfo_rate, lfo_depth, wave=None):
    duration_int = int(sample_rate * duration)

    t = np.linspace(0, duration, duration_int, False)

    pi_2 = 2 * np.pi

    lfo_frequency = pi_2 * lfo_rate
    lfo = np.sin(lfo_frequency * t) * lfo_depth * freq

    modulated_freq = freq + lfo
    
    if wave is not None:
        wave_product = wave * (1 + lfo)
        return wave_product
    else:
        if form == 'sine':
            wave_sine = np.sin(pi_2 * modulated_freq * t)
            return wave_sine
        elif form == 'square':
            wave_square = np.sign(np.sin(pi_2 * modulated_freq * t))
            return wave_square
        elif form == 'sawtooth':
            wave_sawtooth = 2 * (t * modulated_freq - np.floor(1/2 + t * modulated_freq))
            return wave_sawtooth
        elif form == 'triangle':
            wave_triangle = 2 * np.abs(2 * (t * modulated_freq - np.floor(1/2 + t * modulated_freq))) - 1
            return wave_triangle
>>>>>>> 751ebde (added loading wave file, sequencer)

<<<<<<< HEAD
<<<<<<< HEAD
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
=======
=======
# This function takes in the adsr list and a numpy array
# and calculates the asdr length and curve and then
# applies them to the wave, returning the original
# waveform with the adsr envelope applied
>>>>>>> 30bf801 (finished comments)
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

    enveloped_wave = wave * adsr_curve

    return enveloped_wave

# This function is a simple order 5 lowpass filter
def lowpass(cutoff, sample_rate, order=5):
    x = 0.5 * sample_rate

    cutoff2 = cutoff / x

    b, a = butter(order, cutoff2, btype='low', analog=False)

    return b, a

<<<<<<< HEAD
<<<<<<< HEAD
def low_pass_filter(data, cutoff_freq, fs, order=5):
    b, a = lowpass(cutoff_freq, fs, order=order)
<<<<<<< HEAD
    return lfilter(b, a, data)
>>>>>>> c7f5cd4 (done attempting to make keyboard)

square_wave = square_wave(frequency, duration)
save_wave('square_wave.wav', square_wave, fs)
=======
=======
def lp_filter(data, cutoff_freq, sample_rate, order=5):
    b, a = lowpass(cutoff_freq, sample_rate, order=order)

>>>>>>> 44bc7b0 (fixed formatting)
    filtered_data = lfilter(b, a, data)
=======
# This function applies the lowpass filter to the passed in
# wave and returns it
def lp_filter(wave, cutoff_freq, sample_rate, order=5):
    b, a = lowpass(cutoff_freq, sample_rate, order=order)

    filtered_wave = lfilter(b, a, wave)
>>>>>>> 30bf801 (finished comments)

    return filtered_wave

# This function is a basic saturator using the hyperbolic
# tangent to limit amplitude, the level adjusts the steepness
# of the tanh curve.
# This idea was retrieved from here:
# https://www.reddit.com/r/DSP/comments/w7aad3/comment/ihincol/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button
def apply_saturation(wave, level):
    saturated_wave = np.tanh(level * wave)

    return saturated_wave
>>>>>>> 751ebde (added loading wave file, sequencer)

<<<<<<< HEAD
<<<<<<< HEAD
sawtooth_wave = sawtooth_wave(frequency, duration)
save_wave('sawtooth_wave.wav', sawtooth_wave, fs)
=======
=======
# This function takes values from the GUI, generates
# waves, if a wave file is loaded, it takes that, else
# it generates a wave. Then it envelopes, filters, and saturates
# the wave. Lastly, it displays the waveform on the GUI.
>>>>>>> 30bf801 (finished comments)
def play_sound():
    global loaded_wave, loaded_wave_sample_rate

    freq = fre_scale.get()

    if loaded_wave is None:
        duration = dur_scale.get()
    else:
        duration = len(loaded_wave) / loaded_wave_sample_rate

    lfo_rate = lfor_scale.get()
    lfo_depth = lfod_scale.get() / 100

    attack = att_scale.get() / 100
    decay = dec_scale.get() / 100
    sustain = sus_scale.get() / 100
    release = rel_scale.get() / 100

    cutoff_freq = cut_scale.get()

    saturation_level = sat_scale.get()

    adsr = (attack, decay, sustain, release)

    if loaded_wave is not None:
        wave = gen_wave(None, freq, duration, lfo_rate, lfo_depth, loaded_wave)
    elif waveform_var.get() == 4:
        wave_forms = ['sine', 'square', 'sawtooth', 'triangle']
        wave = np.zeros(int(sample_rate * duration))
        for form in wave_forms:
            wave += gen_wave(form, freq, duration, lfo_rate, lfo_depth) / 4
    else:
        forms = ['sine', 'square', 'triangle', 'sawtooth']
        selected_form = forms[waveform_var.get()]
        wave = gen_wave(selected_form, freq, duration, lfo_rate, lfo_depth)

    enveloped_wave = envelope(adsr, wave)

    filtered_wave = lp_filter(enveloped_wave, cutoff_freq, sample_rate)

    saturated_wave = apply_saturation(filtered_wave, saturation_level)

    if loaded_wave is not None:
        sd.play(saturated_wave, loaded_wave_sample_rate)
    else:
        sd.play(saturated_wave, sample_rate)

    ax.clear()

    time_array = np.linspace(0, duration, len(saturated_wave))

    ax.plot(time_array, saturated_wave)
    ax.set_title('Generated Waveform')
    ax.set_xlabel('Time (sec)')
    ax.set_ylabel('Amplitude')

    canvas.draw()

# This function resets the loaded wave file data
def unload_wave():
    global loaded_wave, loaded_wave_sample_rate

    loaded_wave = None
    loaded_wave_sample_rate = None

# This function opens and reads wave file data
# information to be played.
def load_wave():
    global loaded_wave, loaded_wave_sample_rate

    filename = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])

    if filename:
        loaded_wave_sample_rate, data = wavfile.read(filename)
        if len(data.shape) > 1:
            data = np.mean(data, axis=1)

        loaded_wave = np.interp(data, (data.min(), data.max()), (-1, 1))

# Resets all of the settings on the GUI.
# Reset button calls this.
def default_settings():
    fre_scale.set(440)
    dur_scale.set(2)

    lfor_scale.set(0)
    lfod_scale.set(0)

    att_scale.set(10)
    dec_scale.set(20)
    sus_scale.set(60)
    rel_scale.set(10)

    cut_scale.set(2500)

    sat_scale.set(1.5)

    waveform_var.set(0)

# This function ensures that all processes are
# terminated before the window is closed.
# I was randomly getting errors when closing the application.
def on_close():
    global measure_flag

    measure_flag = False

    if measure_thread and measure_thread.is_alive():
        measure_thread.join()

    root.destroy()

# This code initializes the window for the Tkinter GUI
# and sets up some colors and titles.
root = tk.Tk()
root.title("basic synth")
dark_grey = '#2a2a2a'
root.configure(bg=dark_grey)

# These frames are basically containers for GUI buttons.
left_frame = Frame(root, bg=dark_grey)
left_frame.pack(side=tk.LEFT, padx=10, pady=10)

right_frame = Frame(root, bg=dark_grey)
right_frame.pack(side=tk.RIGHT, padx=10, pady=10)

# This waveform variable is used to keep track of
# which waveform radio button is selected.
waveform_var = IntVar()
waveform_var.set(0)
waveforms = ['Sine Wave', 
             'Square Wave', 
             'Triangle Wave', 
             'Sawtooth Wave', 
             'Combined Wave']

# Creates radio button for waveforms
for i, waveform in enumerate(waveforms):
    radiobutton = Radiobutton(left_frame, text=waveform, variable=waveform_var, value=i, bg=dark_grey, fg='white', selectcolor=dark_grey, activebackground=dark_grey, activeforeground='green')
    radiobutton.pack(anchor=tk.W)

# These scales are the sliders for frequency, duration, LFO rate/depth
# ADSR, cutoff, and saturation.

#Frequency/Duration
fre_scale = Scale(left_frame, from_=100, to=2000, orient=HORIZONTAL, label="Frequency (Hz)", bg='#424242', fg='white', troughcolor='gray')
fre_scale.set(440)
fre_scale.pack(fill=tk.X)

dur_scale = Scale(left_frame, from_=1, to=5, orient=HORIZONTAL, label="Duration (seconds)", bg='#424242', fg='white', troughcolor='gray')
dur_scale.set(2)
dur_scale.pack(fill=tk.X)

# LFO Rate/Depth
lfor_scale = Scale(left_frame, from_=0, to=10, resolution=0.1, orient=HORIZONTAL, label="LFO Rate (Hz)", bg='#424242', fg='white', troughcolor='gray')
lfor_scale.set(0)
lfor_scale.pack(fill=tk.X)

lfod_scale = Scale(left_frame, from_=0, to=100, orient=HORIZONTAL, label="LFO Depth (Percentage of Frequency)", bg='#424242', fg='white', troughcolor='gray')
lfod_scale.set(0)
lfod_scale.pack(fill=tk.X)

# ADSR: attack, decay, sustain, release
att_scale = Scale(right_frame, from_=0, to=100, orient=HORIZONTAL, label="Attack (%)", bg='#424242', fg='white', troughcolor='gray')
att_scale.set(10)
att_scale.pack(fill=tk.X)

dec_scale = Scale(right_frame, from_=0, to=100, orient=HORIZONTAL, label="Decay (%)", bg='#424242', fg='white', troughcolor='gray')
dec_scale.set(20)
dec_scale.pack(fill=tk.X)

sus_scale = Scale(right_frame, from_=0, to=100, orient=HORIZONTAL, label="Sustain (level)", bg='#424242', fg='white', troughcolor='gray')
sus_scale.set(60)
sus_scale.pack(fill=tk.X)

rel_scale = Scale(right_frame, from_=0, to=100, orient=HORIZONTAL, label="Release (%)", bg='#424242', fg='white', troughcolor='gray')
rel_scale.set(10)
rel_scale.pack(fill=tk.X)

# Cutoff
cut_scale = Scale(right_frame, from_=100, to=5000, orient=HORIZONTAL, label="Cutoff Frequency (Hz)", bg='#424242', fg='white', troughcolor='gray')
cut_scale.set(2500)
cut_scale.pack(fill=tk.X)

# Saturation
sat_scale = Scale(right_frame, from_=0, to=3, resolution=0.1, orient=HORIZONTAL, label="Saturation Level", bg='#424242', fg='white', troughcolor='gray')
sat_scale.set(1.5)
sat_scale.pack(fill=tk.X)

# Loading/unloading wave files
load_button = Button(left_frame, text="Load WAV", command=load_wave, bg='#424242', fg='white')
load_button.pack()

unload_button = Button(left_frame, text="Unload WAV", command=unload_wave, bg='#424242', fg='white')
unload_button.pack()

# Play button
play_button = Button(left_frame, text="Play Wave", command=play_sound, bg='#424242', fg='white')
play_button.pack()

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
root.mainloop()
>>>>>>> c7f5cd4 (done attempting to make keyboard)
=======
revert_button = Button(left_frame, text="Revert to Defaults", command=revert_to_defaults, bg='#424242', fg='white')
=======
=======
# Revert settings to default
>>>>>>> 30bf801 (finished comments)
revert_button = Button(left_frame, text="Revert to Defaults", command=default_settings, bg='#424242', fg='white')
>>>>>>> 44bc7b0 (fixed formatting)
revert_button.pack()

# Start measure of notes
startm_button = Button(left_frame, text="Play Measure", command=start_measure, bg='#424242', fg='white')
startm_button.pack()

# Stop measure of notes
stopm_button = Button(left_frame, text="Stop measure", command=stop_measure, bg='#424242', fg='white')
stopm_button.pack()

# Figure for the visualization of the generated waveforms
fig = Figure(figsize=(5, 3), facecolor='#424242')
ax = fig.add_subplot(111)
ax.set_facecolor('#424242')
ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white')
ax.spines['bottom'].set_color('white')
ax.spines['left'].set_color('white')

canvas = FigureCanvasTkAgg(fig, master=right_frame)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack()

# Wraps up processes before program stops
root.protocol("WM_DELETE_WINDOW", on_close)
<<<<<<< HEAD
root.mainloop()
>>>>>>> 751ebde (added loading wave file, sequencer)
=======

root.mainloop()
>>>>>>> 44bc7b0 (fixed formatting)
