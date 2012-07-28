import pyglet
pyglet.options['audio'] = ('openal', 'silent')

from pyglet.media.procedural import ProceduralSource, AudioData

import numpy, sys
import ctypes, math
import buffers

class PygletSource(ProceduralSource):
    def __init__(self, **kwargs):
        super(PygletSource,self).__init__(duration=99999999999999, **kwargs)
        
        # the presently playing oscilators
        self.oscillators=[]
        
        # set the cython extension rendering rate to this pyglet rate
        buffers.set_sample_rate(self.sample_rate)
        
    def add( self, osc, intensity=0 ):
        self.oscillators.append( (osc, intensity) )
        
    def remove( self, osc ):
        keys = [k for k in self.oscillators if k[0]==osc]
        assert len(keys)==1, "There should only be one instance of an oscillator"
        del self.oscillators[keys[0]]
        
    @property
    def sample_rate(self):
        return self.audio_format.sample_rate
    
    def _get_audio_data(self, bytes):
        bytes = min(bytes, self._max_offset - self._offset)
        if bytes <= 0:
            return None
            
        # make our buffers word aligned
        if bytes%2:
            bytes+=1
        
        timestamp = float(self._offset) / self._bytes_per_second
        duration = float(bytes) / self._bytes_per_second
        data = self._generate_data(bytes, self._offset)
        self._offset += bytes
        is_eos = self._offset >= self._max_offset

        return AudioData(data,
                         bytes,
                         timestamp,
                         duration)
    
    def _generate_data(self, bytes, offset):
        #print bytes, offset
        if self._bytes_per_sample == 1:
            samples = bytes
            data = (ctypes.c_ubyte * bytes)()
            
            bias = 127
            amplitude = 127
        else:   
            # divide it all by two to make it into samples
            samples = bytes >> 1
            offset = offset >> 1
            data = (ctypes.c_short * samples)()
        
            bias = 0    
            amplitude = 32767
        
        store = numpy.zeros([samples], numpy.float)
        for osc,intensity in self.oscillators:
            buff = osc.send( samples )
            
            # adjust gain on buffer
            buff = buffers.gain( offset, samples, buff, gain=intensity )
    
            # accumulate
            store += buff[:samples]
    
        FLOAT_MAX = 1.0
        for i in range(samples):
            value = store[i]
            s=((value/FLOAT_MAX)*float(amplitude) + float(bias))
                
            data[i] = int(s)
            #print data[i],",",
            # remove finished oscillators
            
        return data
        
