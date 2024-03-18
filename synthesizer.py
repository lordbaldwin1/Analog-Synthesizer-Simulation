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
import numpy as np
import sounddevice as sd
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

def lowpass(cutoff, sample_rate, order=5):
    x = 0.5 * sample_rate

    normalized_cutoff = cutoff / x

    b, a = butter(order, normalized_cutoff, btype='low', analog=False)

    return b, a

def lp_filter(data, cutoff_freq, sample_rate, order=5):
    b, a = lowpass(cutoff_freq, sample_rate, order=order)

    filtered_data = lfilter(b, a, data)

    return filtered_data

def apply_saturation(wave, level):
    saturated_wave = np.tanh(level * wave)

    return saturated_wave

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

def unload_wave():
    global loaded_wave, loaded_wave_sample_rate

    loaded_wave = None
    loaded_wave_sample_rate = None

def load_wave():
    global loaded_wave, loaded_wave_sample_rate

    filename = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])

    if filename:
        loaded_wave_sample_rate, data = wavfile.read(filename)
        if len(data.shape) > 1:
            data = np.mean(data, axis=1)

        loaded_wave = np.interp(data, (data.min(), data.max()), (-1, 1))

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

def on_close():
    global measure_flag

    measure_flag = False

    if measure_thread and measure_thread.is_alive():
        measure_thread.join()

    root.destroy()

root = tk.Tk()
root.title("basic synth")
dark_grey = '#2a2a2a'
root.configure(bg=dark_grey)

left_frame = Frame(root, bg=dark_grey)
left_frame.pack(side=tk.LEFT, padx=10, pady=10)

right_frame = Frame(root, bg=dark_grey)
right_frame.pack(side=tk.RIGHT, padx=10, pady=10)

waveform_var = IntVar()
waveform_var.set(0)
waveforms = ['Sine Wave', 
             'Square Wave', 
             'Triangle Wave', 
             'Sawtooth Wave', 
             'Combined Wave']

for i, waveform in enumerate(waveforms):
    radiobutton = Radiobutton(left_frame, text=waveform, variable=waveform_var, value=i, bg=dark_grey, fg='white', selectcolor=dark_grey, activebackground=dark_grey, activeforeground='green')
    radiobutton.pack(anchor=tk.W)

fre_scale = Scale(left_frame, from_=100, to=2000, orient=HORIZONTAL, label="Frequency (Hz)", bg='#424242', fg='white', troughcolor='gray')
fre_scale.set(440)
fre_scale.pack(fill=tk.X)

dur_scale = Scale(left_frame, from_=1, to=5, orient=HORIZONTAL, label="Duration (seconds)", bg='#424242', fg='white', troughcolor='gray')
dur_scale.set(2)
dur_scale.pack(fill=tk.X)

lfor_scale = Scale(left_frame, from_=0, to=10, resolution=0.1, orient=HORIZONTAL, label="LFO Rate (Hz)", bg='#424242', fg='white', troughcolor='gray')
lfor_scale.set(0)
lfor_scale.pack(fill=tk.X)

lfod_scale = Scale(left_frame, from_=0, to=100, orient=HORIZONTAL, label="LFO Depth (Percentage of Frequency)", bg='#424242', fg='white', troughcolor='gray')
lfod_scale.set(0)
lfod_scale.pack(fill=tk.X)

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

cut_scale = Scale(right_frame, from_=100, to=5000, orient=HORIZONTAL, label="Cutoff Frequency (Hz)", bg='#424242', fg='white', troughcolor='gray')
cut_scale.set(2500)
cut_scale.pack(fill=tk.X)

sat_scale = Scale(right_frame, from_=0, to=3, resolution=0.1, orient=HORIZONTAL, label="Saturation Level", bg='#424242', fg='white', troughcolor='gray')
sat_scale.set(1.5)
sat_scale.pack(fill=tk.X)

load_button = Button(left_frame, text="Load WAV", command=load_wave, bg='#424242', fg='white')
load_button.pack()

unload_button = Button(left_frame, text="Unload WAV", command=unload_wave, bg='#424242', fg='white')
unload_button.pack()

play_button = Button(left_frame, text="Play Wave", command=play_sound, bg='#424242', fg='white')
play_button.pack()

revert_button = Button(left_frame, text="Revert to Defaults", command=default_settings, bg='#424242', fg='white')
revert_button.pack()

startm_button = Button(left_frame, text="Play Measure", command=start_measure, bg='#424242', fg='white')
startm_button.pack()

stopm_button = Button(left_frame, text="Stop measure", command=stop_measure, bg='#424242', fg='white')
stopm_button.pack()

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

root.protocol("WM_DELETE_WINDOW", on_close)

root.mainloop()