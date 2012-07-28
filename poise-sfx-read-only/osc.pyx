"""
Buffer rendering code. Renders waveforms as floats into a numpy buffer.

Renderers all take the following arguments:

offset: the offset to begin rendering the wave at. Measured in samples.
size: number of samples to render
buffer: a pre-existing numpy float buffer to render into.

Other options that they may have...

freq: The frequency of the wave in Hz
gain: The gain of the wave in decibels (0dB is a peak to peak intensity of 2.0 (-1.0 to 1.0))
"""

cdef float pi = 3.14159265328

def sine(int offset, int size, np.ndarray buffer, float freq=440.0, float gain=0.0):
    """Return a buffer with a sine wave in it. The buffer is size long and starts at 'offset'
    samples in. The wave has a frequency of 'freq' Hz. 'gain' is the amplitude of the wave with
    0dB being full scale (maximum intensity 1.0)."""
    assert buffer.dtype == DTYPE
    assert buffer.shape[0] >= size
    
    cdef float toffset = offset * SAMPLE_TIME
    cdef float tsize = size * SAMPLE_TIME
    
    cdef float val=0.0
    cdef int i=0
    cdef float ti = toffset
    cdef float wavelength = 1.0/freq
    
    cdef int divexp
    cdef int div
    
    cdef float multi = db(gain)
    
    for i in range(size):
        # quickly bring back into range 0 - wavelength
        ti = frange( ti, 0.0, wavelength)
        
        # calculate sin value
        val = sin( 2.0*pi*ti/wavelength )
        
        # store with gain
        buffer[i] = (val * multi)
        
        # increase dt
        ti += SAMPLE_TIME
        
    return buffer
    
def sawtooth(int offset, int size, np.ndarray buffer, float freq=440.0, float gain=0.0):
    """Return a buffer with a sawtooth waveform in it. The render is windowed according to 'offset' and 'size' """
    assert buffer.dtype == DTYPE
    assert buffer.shape[0] >= size
    
    cdef float toffset = offset * SAMPLE_TIME
    cdef float tsize = size * SAMPLE_TIME
    cdef float ti = toffset
    cdef float tend = toffset+tsize
    cdef int i=0
    cdef float val = 0.0
    cdef float wavelength = 1.0/freq
    cdef float multi = db(gain)
    for i in range(size):
        # quickly bring back into range 0 - wavelength
        ti = frange( ti, 0.0, wavelength)
        # work out value
        val = 2.0*ti/wavelength-1.0
        
        buffer[i] = val * multi
        
        ti += SAMPLE_TIME
        
    return buffer

def square(int offset, int size, np.ndarray buffer, float freq=440.0, float gain=0.0):
    """Return a buffer with a square waveform in it."""
    assert buffer.dtype == DTYPE
    assert buffer.shape[0] >= size
    
    # value for signal
    cdef float signal = 1.0 * dB(gain)
    
    # time conversions
    cdef float toffset = offset * SAMPLE_TIME
    cdef float tsize = size * SAMPLE_TIME
    cdef float ti = toffset
    cdef float tend = toffset+tsize
    
    # counter across our buffer
    cdef int i=0
    cdef float wavelength = 1.0/freq
    
    for i in range(size):
        # quickly bring back into range 0 - wavelength
        ti = frange( ti, 0.0, wavelength)
        
        # if we are less than 1/2 wavelength, -ve. else +ve
        if ti<wavelength/2.0:
            buffer[i] = -signal
        else:
            buffer[i] = signal
            
        ti += SAMPLE_TIME
    
    return buffer

def triangle(int offset, int size, np.ndarray buffer, float freq=440.0, float gain=0.0):
    """Return a buffer with a sawtooth waveform in it. The render is windowed according to 'offset' and 'size' """
    assert buffer.dtype == DTYPE
    assert buffer.shape[0] >= size
    
    cdef float toffset = offset * SAMPLE_TIME
    cdef float tsize = size * SAMPLE_TIME
    cdef float ti = toffset
    cdef float tend = toffset+tsize
    cdef int i=0
    cdef float val = 0.0
    cdef float wavelength = 1.0/freq
    for i in range(size):
        # quickly bring back into range 0 - wavelength
        ti = frange( ti, 0.0, wavelength)
        
        # work out value
        if ti<wavelength/4.0:
            val = ti * (4.0/wavelength)
        elif ti<3.0*wavelength/4.0:
            val = ti * (-4.0/wavelength) + 2.0
        else:
            val = ti * (4.0/wavelength) -4.0
        
        buffer[i] = val * dB(gain)
        
        ti += SAMPLE_TIME
        
    return buffer
    
def silence(int offset, int size, np.ndarray buffer ):
    """Return a buffer with silence in it"""
    assert buffer.dtype == DTYPE
    assert buffer.shape[0] >= size
    
    for i in range(size):
        buffer[i] = 0.0

    return buffer
    
def noise(int offset, int size, np.ndarray buffer, gain=0.0 ):
    """Return a buffer with white noise in it"""
    assert buffer.dtype == DTYPE
    assert buffer.shape[0] >= size
    
    cdef float multi = db(gain)
    for i in range(size):
        buffer[i] = (2.0*crand()-1.0)*multi

    return buffer
