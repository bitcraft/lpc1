import buffers, numpy
from buffers import dB
from buffers import sine as sine_render_c

from lib import pod

class adsr(pod):
    def __init__(self, source, attack=0.4, decay=0.8, sustain=2.0, release=2.5, again=0.0, sgain=-6.0, noisefloor=-96.0):
        super(adsr,self).__init__()
        self.source = source
        self.params = (attack,decay,sustain,release,again,sgain,noisefloor)
        
    def send(self,length):
        # adjust buffer
        assert isinstance(length, int)
        self.buffer = self.source.send(length)
        self.buffer = buffers.adsr(self.offset, length, self.buffer, *self.params)
        self.offset += length
        return self.buffer
       
