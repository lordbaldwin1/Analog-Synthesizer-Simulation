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

fs = 44100
loaded_wave = None
loaded_wave_fs = None
is_sequencer_playing = False
sequencer_thread = None

sequence_notes = [440, 494, 523, 587, 659, 698, 784]
sequence_durations = [0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4]
note_interval = 0.5

def sequencer():
    global is_sequencer_playing
    while is_sequencer_playing:
        for note, duration in zip(sequence_notes, sequence_durations):
            if not is_sequencer_playing:
                break
            play_synthesized_tone(note, duration)
            time.sleep(note_interval)

def play_synthesized_tone(freq, duration):
    if not is_sequencer_playing:
        return
    global loaded_wave, loaded_wave_fs
    lfo_rate = lfo_rate_scale.get()
    lfo_depth = lfo_depth_scale.get() / 100
    attack = attack_scale.get() / 100
    decay = decay_scale.get() / 100
    sustain = sustain_scale.get() / 100
    release = release_scale.get() / 100
    cutoff_freq = cutoff_scale.get()
    saturation_level = saturation_scale.get()
    adsr = (attack, decay, sustain, release)

    if waveform_var.get() == 4:
        wave = sum([generate_wave(form, freq, duration, lfo_rate, lfo_depth) for form in ['sine', 'square', 'sawtooth', 'triangle']]) / 4
    else:
        forms = ['sine', 'square', 'triangle', 'sawtooth']
        selected_form = forms[waveform_var.get()]
        wave = generate_wave(selected_form, freq, duration, lfo_rate, lfo_depth)

    enveloped_wave = envelope(adsr, wave)
    filtered_wave = low_pass_filter(enveloped_wave, cutoff_freq, fs)
    saturated_wave = apply_saturation(filtered_wave, saturation_level)
    sd.play(saturated_wave, fs)
    sd.wait()

def start_sequencer():
    global is_sequencer_playing, sequencer_thread
    if not is_sequencer_playing:
        is_sequencer_playing = True
        sequencer_thread = threading.Thread(target=sequencer)
        sequencer_thread.start()

def stop_sequencer():
    global is_sequencer_playing
    is_sequencer_playing = False
    if sequencer_thread:
        sequencer_thread.join()

def generate_wave(form, freq, duration, lfo_rate, lfo_depth, wave=None):
    duration_int = int(fs * duration)
    t = np.linspace(0, duration, duration_int, False)

    two_pi = 2 * np.pi
    lfo_frequency = two_pi * lfo_rate
    lfo = np.sin(lfo_frequency * t) * lfo_depth * freq
    modulated_freq = freq + lfo
    
    if wave is not None:
        wave_product = wave * (1 + lfo)
        return wave_product
    else:
        if form == 'sine':
            wave_sine = np.sin(two_pi * modulated_freq * t)
            return wave_sine
        elif form == 'square':
            wave_square = np.sign(np.sin(two_pi * modulated_freq * t))
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

def lowpass(cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normalized_cutoff = cutoff / nyquist
    b, a = butter(order, normalized_cutoff, btype='low', analog=False)
    return b, a

def low_pass_filter(data, cutoff_freq, fs, order=5):
    b, a = lowpass(cutoff_freq, fs, order=order)
    filtered_data = lfilter(b, a, data)
    return filtered_data

def apply_saturation(wave, level):
    saturated_wave = np.tanh(level * wave)
    return saturated_wave

def play_sound():
    global loaded_wave, loaded_wave_fs

    freq = frequency_scale.get()
    if loaded_wave is None:
        duration = duration_scale.get()
    else:
        duration = len(loaded_wave) / loaded_wave_fs
    lfo_rate = lfo_rate_scale.get()
    lfo_depth = lfo_depth_scale.get() / 100
    attack = attack_scale.get() / 100
    decay = decay_scale.get() / 100
    sustain = sustain_scale.get() / 100
    release = release_scale.get() / 100
    cutoff_freq = cutoff_scale.get()
    saturation_level = saturation_scale.get()

    adsr = (attack, decay, sustain, release)

    if loaded_wave is not None:
        wave = generate_wave(None, freq, duration, lfo_rate, lfo_depth, loaded_wave)
    elif waveform_var.get() == 4:
        wave_forms = ['sine', 'square', 'sawtooth', 'triangle']
        wave = np.zeros(int(fs * duration))
        for form in wave_forms:
            wave += generate_wave(form, freq, duration, lfo_rate, lfo_depth) / 4
    else:
        forms = ['sine', 'square', 'triangle', 'sawtooth']
        selected_form = forms[waveform_var.get()]
        wave = generate_wave(selected_form, freq, duration, lfo_rate, lfo_depth)

    enveloped_wave = envelope(adsr, wave)
    filtered_wave = low_pass_filter(enveloped_wave, cutoff_freq, fs)
    saturated_wave = apply_saturation(filtered_wave, saturation_level)

    if loaded_wave is not None:
        sd.play(saturated_wave, loaded_wave_fs)
    else:
        sd.play(saturated_wave, fs)

    ax.clear()
    time_array = np.linspace(0, duration, len(saturated_wave))
    ax.plot(time_array, saturated_wave)
    ax.set_title('Generated Waveform')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Amplitude')
    canvas.draw()

def unload_wave():
    global loaded_wave, loaded_wave_fs
    loaded_wave = None
    loaded_wave_fs = None

def load_wave():
    global loaded_wave, loaded_wave_fs
    filename = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
    if filename:
        loaded_wave_fs, data = wavfile.read(filename)
        if len(data.shape) > 1:
            data = np.mean(data, axis=1)
        loaded_wave = np.interp(data, (data.min(), data.max()), (-1, 1))

def revert_to_defaults():
    frequency_scale.set(440)
    duration_scale.set(2)
    lfo_rate_scale.set(0)
    lfo_depth_scale.set(0)
    attack_scale.set(10)
    decay_scale.set(20)
    sustain_scale.set(60)
    release_scale.set(10)
    cutoff_scale.set(2500)
    saturation_scale.set(1.5)
    waveform_var.set(0)

def on_close():
    global is_sequencer_playing
    is_sequencer_playing = False

    if sequencer_thread and sequencer_thread.is_alive():
        sequencer_thread.join()

    root.destroy()

root = tk.Tk()
root.title("Sound Synthesizer")
dark_grey = '#2a2a2a'
root.configure(bg=dark_grey)

left_frame = Frame(root, bg=dark_grey)
left_frame.pack(side=tk.LEFT, padx=10, pady=10)

right_frame = Frame(root, bg=dark_grey)
right_frame.pack(side=tk.RIGHT, padx=10, pady=10)

waveform_var = IntVar()
waveform_var.set(0)
waveforms = ['Sine Wave', 'Square Wave', 'Triangle Wave', 'Sawtooth Wave', 'Combined Wave']
for i, waveform in enumerate(waveforms):
    radiobutton = Radiobutton(left_frame, text=waveform, variable=waveform_var, value=i, bg=dark_grey, fg='white', selectcolor=dark_grey, activebackground=dark_grey, activeforeground='green')
    radiobutton.pack(anchor=tk.W)

frequency_scale = Scale(left_frame, from_=100, to=2000, orient=HORIZONTAL, label="Frequency (Hz)", bg='#424242', fg='white', troughcolor='gray')
frequency_scale.set(440)
frequency_scale.pack(fill=tk.X)

duration_scale = Scale(left_frame, from_=1, to=5, orient=HORIZONTAL, label="Duration (seconds)", bg='#424242', fg='white', troughcolor='gray')
duration_scale.set(2)
duration_scale.pack(fill=tk.X)

lfo_rate_scale = Scale(left_frame, from_=0, to=10, resolution=0.1, orient=HORIZONTAL, label="LFO Rate (Hz)", bg='#424242', fg='white', troughcolor='gray')
lfo_rate_scale.set(0)
lfo_rate_scale.pack(fill=tk.X)

lfo_depth_scale = Scale(left_frame, from_=0, to=100, orient=HORIZONTAL, label="LFO Depth (Percentage of Frequency)", bg='#424242', fg='white', troughcolor='gray')
lfo_depth_scale.set(0)
lfo_depth_scale.pack(fill=tk.X)

attack_scale = Scale(right_frame, from_=0, to=100, orient=HORIZONTAL, label="Attack (%)", bg='#424242', fg='white', troughcolor='gray')
attack_scale.set(10)
attack_scale.pack(fill=tk.X)

decay_scale = Scale(right_frame, from_=0, to=100, orient=HORIZONTAL, label="Decay (%)", bg='#424242', fg='white', troughcolor='gray')
decay_scale.set(20)
decay_scale.pack(fill=tk.X)

sustain_scale = Scale(right_frame, from_=0, to=100, orient=HORIZONTAL, label="Sustain (level)", bg='#424242', fg='white', troughcolor='gray')
sustain_scale.set(60)
sustain_scale.pack(fill=tk.X)

release_scale = Scale(right_frame, from_=0, to=100, orient=HORIZONTAL, label="Release (%)", bg='#424242', fg='white', troughcolor='gray')
release_scale.set(10)
release_scale.pack(fill=tk.X)

cutoff_scale = Scale(right_frame, from_=100, to=5000, orient=HORIZONTAL, label="Cutoff Frequency (Hz)", bg='#424242', fg='white', troughcolor='gray')
cutoff_scale.set(2500)
cutoff_scale.pack(fill=tk.X)

saturation_scale = Scale(right_frame, from_=0, to=3, resolution=0.1, orient=HORIZONTAL, label="Saturation Level", bg='#424242', fg='white', troughcolor='gray')
saturation_scale.set(1.5)
saturation_scale.pack(fill=tk.X)

load_button = Button(left_frame, text="Load WAV", command=load_wave, bg='#424242', fg='white')
load_button.pack()

unload_button = Button(left_frame, text="Unload WAV", command=unload_wave, bg='#424242', fg='white')
unload_button.pack()

play_button = Button(left_frame, text="Play", command=play_sound, bg='#424242', fg='white')
play_button.pack()

revert_button = Button(left_frame, text="Revert to Defaults", command=revert_to_defaults, bg='#424242', fg='white')
revert_button.pack()

start_seq_button = Button(left_frame, text="Start Sequencer", command=start_sequencer, bg='#424242', fg='white')
start_seq_button.pack()

stop_seq_button = Button(left_frame, text="Stop Sequencer", command=stop_sequencer, bg='#424242', fg='white')
stop_seq_button.pack()

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