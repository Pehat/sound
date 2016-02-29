from abc import abstractmethod
import math
import wave
from samplelist import list_to_str

class InputJack(object):
    def __init__(self):
        self.source = None

    def connect(self, output_jack):
        self.source = output_jack
        
    def disconnect(self):
        self.source = None
        
    def get(self):
        return self.source.get()
   
   
class OutputJack(object):
    @abstractmethod
    def get(self):
        pass
    
    
class ConstJack(OutputJack):
    def __init__(self, value):
        self.value = value
        
    def get(self):
        return self.value
        

class TimeJack(OutputJack):
    def __init__(self):
        self.value = 0
        
    def get(self):
        return self.value
        
    def set(self, value):
        self.value = value
        

class AdderJack(OutputJack):
    def __init__(self, jack_count):
        self.jacks = [InputJack() for i in range(jack_count)]
        self.weights = [InputJack() for i in range(jack_count)]
        
    def get(self):
        return sum(jack.get() * weight.get() for jack, weight in zip(self.jacks, self.weights))

        
class SinJack(OutputJack):
    def __init__(self):
        self.t = InputJack()
        self.a = InputJack()
        self.w = InputJack()
        
    def get(self):
        return self.a.get() * math.sin(2 * math.pi * self.w.get() * self.t.get())
    

class SquareJack(OutputJack):
    def __init__(self):
        self.t = InputJack()
        self.a = InputJack()
        self.w = InputJack()
        
    def get(self):
        phase = int(self.w.get() * self.t.get() * 2) & 1
        phase = -1 + phase * 2
        return self.a.get() * phase
    
# class ADSRJack(OutputJack):
    # def __init__(self):
        # self.time = InputJack()
        # self.source = InputJack()
        # self.attack = InputJack()
        # self.delay = InputJack()
        # self.sustain_level = InputJack()
        # self.sustain_time = InputJack()
        # self.release = InputJack()
        # ??????????
    # def get(self):
        # t = self.time.get()
        # a = self.attack.get()
        # d = self.decay.get()
        # sl = self.sustain_level.get()
        # st = self.sustain_time.get()
        # if t < a:
            # return self.source.get() * t / a
        # elif t < a + d:
            # return self.source.get() *  
        # a  1
        # a+d sl
        # (a - t) * sl / d 
        
        

class FileJack(InputJack):
    def __init__(self, filename, framerate, timer, duration):
        self.filename = filename
        self.framerate = framerate
        self.duration = duration
        self.timer = timer
        
    def save(self):
            with wave.open(self.filename, 'wb') as output_file:
                output_buffer = []
                samples_count = int(self.duration * self.framerate)
                output_file.setparams((1, 2, self.framerate, samples_count, "NONE", "not compressed"))
                for i in range(samples_count):
                    self.timer.set(i / self.framerate)
                    output_buffer.append(self.get())
                output_file.writeframes(list_to_str(map(int, output_buffer)))
                    
        
        
if __name__ == "__main__":
    t = TimeJack()
    
    lfo_freq = ConstJack(4)
    lfo_amp = ConstJack(220)
    lfo = SquareJack()
    lfo.t.connect(t)
    lfo.w.connect(lfo_freq)
    lfo.a.connect(lfo_amp)
    
    lfo_bias = ConstJack(220)
    lfo_sum = AdderJack(2)
    lfo_sum.jacks[0].connect(lfo)
    lfo_sum.jacks[1].connect(lfo_bias)
    lfo_sum.weights[0].connect(ConstJack(1))
    lfo_sum.weights[1].connect(ConstJack(1))
    
    amp = ConstJack(4000)  
    
    g = SinJack()
    g.t.connect(t)
    g.w.connect(lfo_sum)
    g.a.connect(amp)
    
    fj = FileJack("out.wav", 44100, t, 1)
    fj.connect(g)
    fj.save()
    