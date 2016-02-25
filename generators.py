from samplelist import *
import math
from math import sin, modf
import random

xrange = range

def square_string(framerate, freq, amp, periods=1):
    sample_length = int(periods * framerate / freq)
    result = []
    
    for i in xrange(sample_length):
        if int(i * 2 * freq / framerate) & 1:
            result.append(int(-amp))
        else:
            result.append(int(amp))
    return list_to_str(result)


def sin_string(framerate, freq, amp, periods=1):
    sample_length = int(periods * framerate / freq)
    result = []
    
    for i in xrange(sample_length):
        result.append(int(amp * sin(2 * math.pi * i * periods / sample_length)))
    return list_to_str(result)


def saw_string(framerate, freq, amp, periods=1):
    sample_length = int(periods * framerate / freq)
    result = []
    for i in xrange(sample_length):
        result.append(int(amp * (modf(float(i) * periods / sample_length)[0] * 2 - 1)))
    return list_to_str(result)
    

def tri_string(framerate, freq, amp, periods=1):
    sample_length = int(periods * framerate / freq)
    result = []
    for i in xrange(sample_length):
        result.append(int(amp * (abs(modf(float(i) * periods / sample_length)[0] - 0.5) * 4 - 1)))
    return list_to_str(result)
    
def noise_string(framerate, freq, amp, sample_length):
    result = []
    for i in xrange(sample_length):
        result.append(int(amp * random.random()))
    return list_to_str(result)