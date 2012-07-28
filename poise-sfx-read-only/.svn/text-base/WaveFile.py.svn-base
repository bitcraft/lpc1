
import wave, ctypes, numpy
import buffers

class WaveFile(object):
    def __init__(self, **kwargs):
        # the presently playing oscilators
        self.oscillators=[]
        
        self.rate = 48000
        
    def add( self, osc, intensity=0 ):
        self.oscillators.append( (osc, intensity) )
        
    def remove( self, osc ):
        keys = [k for k in self.oscillators if k[0]==osc]
        assert len(keys)==1, "There should only be one instance of an oscillator"
        del self.oscillators[keys[0]]
        
    def set_sample_rate(self,rate):
        self.rate = rate
        return buffers.set_sample_rate(rate)
    
    def save(self, fh, length):
        # save this data to a wave file
        data = self._generate_data(length)
    
        numchannels = 1
        sampwidth = 2
        framerate = self.rate
        numframes = length
        comptype = "NONE"
        compname = None
    
        writer = wave.open(fh,"wb")
        writer.setparams( (numchannels, sampwidth, framerate, numframes, comptype, compname) )
        writer.writeframes( data )
        writer.close()
    
    def _generate_data(self, samples, offset=0.0):
    
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
            
        return data
        
