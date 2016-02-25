import wave
import audioop
from samplelist import *
from generators import *
import functools

def gen_harmonics(base_freq, num, gamma=1.0):
    return [base_freq * i * (gamma ** (i - 1)) for i in range(1, num + 1)]

def gen_amps(base_amp, num, gamma=0.99):
    return [base_amp * (gamma ** (i - 1)) for i in range(1, num + 1)]

def gen_bass(framerate, freq, amp, periods=80):
    harmonics = gen_harmonics(freq, 5)
    amps = gen_amps(amp, 5)
    partials = [sin_string(framerate, f, amp, periods=periods * f / freq) for f, amp in zip(harmonics, amps)]
    sum = functools.reduce(lambda x, y: audioop.add(x, y, 2), partials)
    return sum
    
def freq_from_note(s):
    base_freq = 55  # a0
    offsets = {
        "a": (0, 0),
        "a#": (1, 0),
        "b": (2, 0),
        "c": (3, -1),
        "c#": (4, -1),
        "d": (5, -1),
        "d#": (6, -1),
        "e": (7, -1),
        "f": (8, -1),
        "f#": (9, -1),
        "g": (10, -1),
        "g#": (11, -1)
    }
    if s[:2] in offsets:
        offset, shift = offsets[s[:2]]
        octave = int(s[2:]) + shift
    else:
        offset, shift = offsets[s[0]]
        octave = int(s[1:]) + shift
    note_number = octave * 12 + offset
    return base_freq * (2 ** (note_number / 12))

def gen_bass_track(framerate, amp=6000):
    notes = ["c1", "c1", "c1", "d#1", "d#1", "d#1", "g#1", "g#1", "g#1", "d1", "d1", "g1"]
    starts = [0, 3/8, 6/8, 2, 2 + 3/8, 2 + 6/8, 4, 4 + 3/8, 4 + 6/8, 6, 6 + 3/8, 6 + 6/8]
    durations = [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]
    track_length = framerate * 8
    result = bytes(track_length * 2)
    for note, start, dur in zip(notes, starts, durations):
        freq = freq_from_note(note)
        periods = dur * freq
        waveform = gen_bass(framerate, freq, amp, periods)
        waveform = complete_silence(waveform, int(start * framerate), track_length)
        result = audioop.add(result, waveform, 2)
    return result
    
def gen_hats_track(framerate, amp=1000):
    starts = [1/4 * i for i in xrange(4 * 8)]
    durations = [1/16] * 4 * 8
    track_length = framerate * 8
    result = bytes(track_length * 2)
    for start, dur in zip(starts, durations):
        hat = noise_string(framerate, -1, amp, int(dur * framerate))
        hat = complete_silence(hat, int(start * framerate), track_length)
        result = audioop.add(result, hat, 2)
    return result

def gen_tom_track(framerate, amp=3000):
    starts = [1/2 * i for i in xrange(2 * 8)]
    track_length = framerate * 8
    result = bytes(track_length * 2)
    for start in starts:
        tom = b"".join([
                square_string(framerate, 50, amp / 1.5, 2),
                square_string(framerate, 40, amp, 1),
                square_string(framerate, 50, amp / 1.5, 2),
                square_string(framerate, 60, amp / 2, 3),
                square_string(framerate, 70, amp / 2.2, 4)
              ])
        tom = complete_silence(tom, int(start * framerate), track_length)
        result = audioop.add(result, tom, 2)
    return result

def bass():
    framerate = 44100
    bass = gen_bass_track(framerate)
    hat = gen_hats_track(framerate)
    tom = gen_tom_track(framerate)
    outdata = audioop.add(bass, hat, 2)
    outdata = audioop.add(outdata, tom, 2)
    
    nframes = len(outdata) // 2
    params = (1, 2, framerate, nframes, "NONE", "not compressed")
    waveout = wave.open("out.wav", "wb")
    waveout.setparams(params)
    waveout.writeframes(outdata)
    
if __name__ == "__main__":
    bass()