from generators import *
from samplelist import *
import audioop
import wave
import math
import matplotlib
import matplotlib.pyplot
import subprocess
import numpy as np
import cmath

BLOCK_SIZE = 2 ** 13
FFT_BLOCK_SIZE = BLOCK_SIZE
PEAKS_IN_BLOCK = 5

DEBUG_MODE = False


def debug_show_and_play_sample(lblock):
    waveout = wave.open("tmp.wav", "wb")
    waveout.setparams((2, 2, 44100, 531788, 'NONE', 'not compressed'))
    outdata = join_stereo(lblock, lblock)
    waveout.writeframes(outdata)
    waveout.close()
    subprocess.Popen(r"C:\Program Files (x86)\Winamp\winamp.exe tmp.wav")
    
    matplotlib.pyplot.plot(str_to_list(lblock))
    matplotlib.pyplot.show(block=True)
    matplotlib.pyplot.close()


def debug_display_peaks(peaks):
    print "DEBUG: showing peaks"
    matplotlib.pyplot.plot(peaks)
    matplotlib.pyplot.plot(np.argsort(peaks)[-1:], np.sort(peaks)[-1:], 'ro')
    matplotlib.pyplot.show(block=True)
    matplotlib.pyplot.close()
    

def get_peaks_and_phases(lblock):
    print "performing FFT...",
    fft = np.fft.rfft(str_to_list(lblock))
    print "done."
    
    peaks, phases = zip(*[cmath.polar(x) for x in fft])
    effective_length = len(peaks) / 2
    peaks = [x / BLOCK_SIZE for x in peaks[:effective_length]]
    phases = list(phases[:effective_length])
    return peaks, phases
    
    
def decompose(swave, framerate, instruments=[tri_string, square_string, sin_string, saw_string]):
    matches = {}
    sample_width = 2
    total_samples = len(swave) / sample_width
    block_start = 0
    block_end = min(total_samples, block_start + BLOCK_SIZE)
    
    next_block = None
    
    while block_end - block_start == BLOCK_SIZE:
        if next_block is None:
            lblock = swave[block_start * sample_width:block_end * sample_width]
        else:
            lblock = next_block
        
        if DEBUG_MODE:
            debug_show_and_play_sample(lblock)
            
            
        noisy_block = False
        for j in xrange(PEAKS_IN_BLOCK):
            if next_block is None:
                peaks, phases = get_peaks_and_phases(lblock)
            else:
                peaks = next_peaks
                phases = next_phases
            
            if DEBUG_MODE:
                debug_display_peaks(peaks)

            peak = max(peaks)
            #TODO: normal level detection
            if peak < 1:
                print "too quiet."
                noisy_block = False
                continue
            peak_index = peaks.index(peak)
            phase = phases[peak_index]
            peaks[peak_index] = 0
            
            next_block = swave[block_end * sample_width:(2 * block_end - block_start) * sample_width]
            next_peaks, next_phases = get_peaks_and_phases(next_block)
            next_phase = next_phases[peak_index]
            phase_delta = next_phase - phase
                     
            freq_res = float(framerate) / FFT_BLOCK_SIZE
            base_freq = (peak_index + phase_delta / (2 * math.pi)) * freq_res
                        
            peak = 1000
            
            periods = int(BLOCK_SIZE * base_freq / framerate)
            
            wavelength = int(framerate / base_freq)
            window_left = max(0, block_start - wavelength / 2)
            window_right = min(total_samples, block_end + wavelength / 2)
            window = swave[window_left * sample_width:window_right * sample_width]
            
            dc_offset = sum(str_to_list(window)) * sample_width / len(window)
            window = audioop.bias(window, sample_width, -dc_offset)
            
            best_offset = None
            best_factor = None
            best_periods = 0
            best_freq = base_freq
            best_rms = audioop.rms(window, sample_width)
            best_instrument = 0
            
            
            for p in xrange(1, periods):
                for inst, wavegen in enumerate(instruments):
                    
                    freq = base_freq
                    pattern = wavegen(framerate, freq, peak, p)
                    
                    offset, factor = audioop.findfit(window, pattern)
                    #window_pattern = window[offset * sample_width:offset * sample_width + len(pattern)]
                    window_pattern = window
                    pattern = complete_silence(pattern, offset, len(window) / sample_width)
                    
                    fitted_pattern = audioop.mul(pattern, sample_width, -factor)
                    applied_pattern = audioop.add(window_pattern, fitted_pattern, sample_width)
                    dc_offset = sum(str_to_list(applied_pattern)) * sample_width / len(applied_pattern)
                    applied_pattern = audioop.bias(applied_pattern, sample_width, -dc_offset)
                    
                    rms = audioop.rms(applied_pattern, sample_width)
                    
                    
                    # if DEBUG_MODE and p > 3:
                        # print "debug: ", p, freq, rms, best_rms, offset
                        # matplotlib.pyplot.plot(str_to_list(window_pattern), 'b')
                        # matplotlib.pyplot.plot(str_to_list(fitted_pattern), 'r')
                        # matplotlib.pyplot.plot(str_to_list(applied_pattern), 'g')
                        
                        # matplotlib.pyplot.show()
                        # matplotlib.pyplot.close()
                        
                    if ((best_rms > 0) and (rms < best_rms * 1.02)) or (best_rms == rms == 0):
                        best_rms = rms
                        best_periods = p
                        best_factor = factor
                        best_offset = offset + window_left
                        best_instrument = inst
                        best_freq = freq
            
            print "found: ", best_periods, best_freq, best_rms
            if not best_freq in matches:
                matches[best_freq] = []
                
            if  best_periods < 3:
                
                #block_start = max(best_offset, block_start + 1)
                #block_end = min(total_samples, block_start + BLOCK_SIZE)
                block_start = block_end
                block_end = min(total_samples, block_start + BLOCK_SIZE)
                noisy_block = True
                
                print "too short period"
                break
            
            if not best_factor:
                print "no waveforms found."
                continue
            amp = best_factor * peak
            wavegen = instruments[best_instrument]
            print "%5.2f Hz at level %5.2f for %4i periods" % (best_freq, amp, best_periods)
            matches[best_freq].append((best_offset, amp, best_periods, best_instrument))
            pattern = wavegen(framerate, best_freq, -int(amp), best_periods)
            complement = complete_silence(pattern, best_offset, total_samples)
            
            if DEBUG_MODE:
                waveout = wave.open("tmp.wav", "wb")
                waveout.setparams((2, 2, 44100, 531788, 'NONE', 'not compressed'))
                outdata = join_stereo(pattern, pattern)
                waveout.writeframes(outdata)
                waveout.close()
                subprocess.Popen(r"C:\Program Files (x86)\Winamp\winamp.exe tmp.wav")
                
                matplotlib.pyplot.plot(str_to_list(swave[block_start * sample_width:block_end * sample_width]))
                matplotlib.pyplot.plot(str_to_list(complement[block_start * sample_width:block_end * sample_width]), 'r')
                matplotlib.pyplot.show(block=True)
                matplotlib.pyplot.close()
            
            
            
            swave = audioop.add(swave, complement, sample_width)
            
            
                
                
        if not noisy_block:
            block_start = block_end
            block_end = min(total_samples, block_start + BLOCK_SIZE)
        print block_start, block_end
        print "block processed."
        
    result = audioop.mul(swave, sample_width, 0)
    for best_freq, notes in matches.iteritems():
        for note in notes:
            offset, amp, periods, best_instrument = note
            wavegen = instruments[best_instrument]
            pattern = wavegen(framerate, best_freq, amp, periods)
            prepared_sample = complete_silence(pattern, offset, len(result) / 2)
            result = audioop.add(result, prepared_sample, sample_width)
    return result
    
    
def test():
    wavedata = wave.open("under.wav")
    params = wavedata.getparams()
    print params
    sleft, sright = split_stereo(wavedata.readframes(params[3]))
    framerate = params[2]
    rleft = decompose(sleft, framerate)
    #rright = decompose(sright, framerate)
    rright = rleft
    
    waveout = wave.open("out.wav", "wb")
    waveout.setparams(params)
    outdata = join_stereo(rleft, rright)
    waveout.writeframes(outdata)
    
if __name__ == "__main__":
    test()