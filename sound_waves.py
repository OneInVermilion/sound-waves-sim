"""
sin - monotone sound

wave + wave2 = both waves at the same time
"""

import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt

SAMPLE_FREQ = 44100 #how frequent are the measurments of the wave array happening by sounddevice. not related to sound wave

FREQUENCY = 440 #sound wave
LENGTH = 1 #sound length, seconds
AMPLITUDE = 0.1 #sound volume or wave amplitude multiplier

#Notes
NOTE_NAMES = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "*"] #all notes and silence in the end
NOTE_NAMES_ALT = ["LA", "LA#", "TI", "DO", "DO#", "RE", "RE#", "MI", "FA", "FA#", "SO", "SO#", "*"]
ALPHA = np.power(2, 1/12) #multiply by this to get next note
NOTE_FREQS = [0]*12
for i in range(12):
    NOTE_FREQS[i] = 440 * np.power(ALPHA, i)
#NOTE_FREQS.append(0)

#mathematical functions
def get_periods_distance(frequency, sample_frequency, periods=1):
    return int(sample_frequency/frequency) * periods

def round_step(num, step):
    return np.round(num / step) * step

def match_wave_size(wave, len_needed):
    if len_needed <= len(wave):
        return wave[:len_needed]
    add = len_needed - len(wave)
    return np.concatenate([wave, np.empty(add)])

#soundwave functions
def tone(length, frequency, sample_freq, amplitude):
    wave = np.linspace(0, length, int(length * sample_freq))
    wave = np.sin(2 * np.pi * frequency * wave)
    return wave * amplitude

def whitenoise(length, sample_freq, amplitude):
    wave = np.random.uniform(-1, 1, int(length * sample_freq))
    return wave * amplitude

def squarewave(length, frequency, sample_freq, amplitude, wave=np.ndarray(0)):
    if wave.shape == np.ndarray(0).shape:
        wave = tone(length, frequency, sample_freq, amplitude)
    wave = np.sign(wave) * amplitude
    return wave

def crush(length, frequency, sample_freq, amplitude, wave=np.ndarray(0), degree=0.05):
    if wave.shape == np.ndarray(0).shape:
        wave = tone(length, frequency, sample_freq, amplitude)
    wave = round_step(wave, degree)
    return wave

def cutoff(length, frequency, sample_freq, amplitude, wave=np.ndarray(0), period_cutoff=0.75):
    if wave.shape == np.ndarray(0).shape:
        wave = tone(length, frequency, sample_freq, amplitude)
    cutoff = int(get_periods_distance(frequency, sample_freq, period_cutoff))
    repetitions = len(wave) // cutoff
    wave = np.tile(wave[:cutoff], repetitions)
    wave = np.concatenate([wave, np.tile(0, length * sample_freq - cutoff * repetitions)])
    return wave

#quick access functions
def qw(wave_type, wave=np.ndarray(0), deg=0.05, cut=0.75): #quick wave
    match wave_type:
        case "tone":
            wave = tone(LENGTH, FREQUENCY, SAMPLE_FREQ, AMPLITUDE)
        case "whitenoise":
            wave = whitenoise(LENGTH, SAMPLE_FREQ, AMPLITUDE)
        case "squarewave":
            wave = squarewave(LENGTH, FREQUENCY, SAMPLE_FREQ, AMPLITUDE, wave)
        case "crush":
            wave = crush(LENGTH, FREQUENCY, SAMPLE_FREQ, AMPLITUDE, wave, deg)
        case "cutoff":
            wave = cutoff(LENGTH, FREQUENCY, SAMPLE_FREQ, AMPLITUDE, wave, cut)
        case _:
            pass
    return wave

#display functions
def play_wave(wv, sample_frequency, wait=False):
    sd.play(wv, sample_frequency)
    if wait: sd.wait()

def plot_wave(wv, size=-1):
    if size < 0: size = len(wv)
    size = min(len(wv), size)
    x = np.linspace(0, 1, len(wv))[:size]
    y = wv[:size]
    plt.plot(x, y)
    plt.show()

#Notation: "note:octave:length = note; [SPACE] = next note; * = pause"; Example: "c:1:1 d:1:1 ** e:1:1 f:1:1 ** g:1:1 a:2:1 ** b:2:1 c:2:3"
def notes_to_wave(length, sample_frequency, volume, notes_str, octave_shift=0, note_names_alt=False):
    notes_arr = notes_str.upper().split(" ")
    waves_arr = []
    for n in notes_arr:
        l = 1
        vol_mult = 1
        names = NOTE_NAMES if not note_names_alt else NOTE_NAMES_ALT
        if "*" not in n:
            values = n.split(":")
            f = NOTE_FREQS[names.index(values[0])]
            f *= np.power(2, (float(values[1]) + octave_shift))
            l = int(values[2])
        else:
            f = 0
            l = len(n)
            vol_mult = 0
        note = tone(length * l, f, sample_frequency, volume * vol_mult)
        waves_arr.append(note)
    waves_all = np.concatenate(waves_arr)
    return waves_all

#wv = qw("tone")
#play_wave(wv, SAMPLE_FREQ)
#plot_wave(wv, get_periods_distance(FREQUENCY, SAMPLE_FREQ))

notes = "g:1:3 e:1:3 c:1:3 g:0:3 a:1:1 b:1:1 c:1:1 a:1:2 c:1:1 g:0:3 ***"
notes += " d:1:3 g:1:3 e:1:3 c:1:3 a:1:1 b:1:1 c:1:1 d:1:2 e:1:1 d:1:3 **"
notes += " e:1:1 f:1:1 e:1:1 d:1:1 g:1:2 e:1:1 d:1:1 c:1:2 ** d:1:1 e:1:2 c:1:1 a:1:2 c:1:1 a:1:1 g:0:2 **"
notes += " g:0:1 c:1:2 e:1:1 d:1:2 g:0:1 c:1:2 e:1:1 d:1:1 e:1:1 f:1:1 g:1:1 e:1:1 c:1:1 d:1:2 g:0:1 c:1:4 **"
song = notes_to_wave(0.3, SAMPLE_FREQ, AMPLITUDE, notes)
play_wave(song, SAMPLE_FREQ, True)
