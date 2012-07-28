import buffers, numpy
from buffers import dB
from buffers import sine as sine_render
from buffers import sawtooth as sawtooth_render
from buffers import square as square_render
from buffers import triangle as triangle_render
from buffers import noise as noise_render
from buffers import silence as silence_render

from lib import pod
        
class oscillator(pod):
    RENDER_FUNC = None
    
    def __init__(self, freq=440.0, gain=0.0):
        super(oscillator,self).__init__()
        self.freq = freq
        self.gain = gain
        
    def send(self,length):
        # adjust buffer
        assert isinstance(length, int)
        self._grow_buffer(length)
        self.RENDER_FUNC(self.offset, length, self.buffer, self.freq, self.gain)
        self.offset += length
        return self.buffer
        
class sine(oscillator):
    RENDER_FUNC = sine_render

class sawtooth(oscillator):
    RENDER_FUNC = sawtooth_render

class square(oscillator):
    RENDER_FUNC = square_render

class triangle(oscillator):
    RENDER_FUNC = triangle_render
    
class silence(oscillator):
    def send(self,length):
        # adjust buffer
        assert isinstance(length, int)
        self._grow_buffer(length)
        silence_render(self.offset, length, self.buffer)
        self.offset += length
        return self.buffer
    
class noise(oscillator):
    def __init__(self, gain=0.0):
        super(oscillator,self).__init__()
        self.gain = gain
        
    def send(self,length):
        # adjust buffer
        assert isinstance(length, int)
        self._grow_buffer(length)
        noise_render(self.offset, length, self.buffer, self.gain)
        self.offset += length
        return self.buffer
