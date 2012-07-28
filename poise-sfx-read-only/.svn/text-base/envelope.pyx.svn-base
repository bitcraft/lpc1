"""
envelopes adjusts the volume envelope over a sound
"""

def adsr(   int offset, int size, np.ndarray buffer, 
            float attack=0.1,float decay=0.1,float sustain=1.0, float release=0.5, 
            float again=0.0, float sgain=0.0, float noisefloor=NOISE_FLOOR ):
    """applies the specified envelope to the buffer. Old analogue synth style ADSR envelope.
    attack: attack time in seconds
    decay: decay time in seconds
    sustain: sustain time in seconds
    release: release time in seconds
    again: peak attack gain in dB
    sgain: sustain gain level in dB
    noisefloor: how quiet is total silence in dB
    """
    assert buffer.dtype == DTYPE
    assert buffer.shape[0] >= size
    
    # convert to time
    cdef float toffset = offset * SAMPLE_TIME
    cdef float tsize = size * SAMPLE_TIME
    cdef float ti = toffset
    cdef float tend = toffset+tsize
    cdef int i=0
    cdef float gain=0.0
    
    while i<size:
        if ti<attack:
            #attack portion
            gain = ((again - noisefloor)/attack)*ti + noisefloor
            
        elif ti>=attack and ti<attack+decay:
            #decay portion
            gain = ((sgain - again)/decay)*(ti-attack) + again
        
        elif ti>=attack+decay and ti<attack+decay+sustain:
            #sustain portion
            gain = sgain
        
        elif ti>=attack+decay+sustain and attack+decay+sustain+release:
            #release portion
            gain = ((noisefloor - sgain)/release)*(ti-attack-decay-sustain) + sgain
        
        else:
            #end
            gain = noisefloor
        
        buffer[i] *= dB(gain)
        
        ti += SAMPLE_TIME
        i += 1
        
    return buffer
    
def gain( int offset, int size, np.ndarray buffer, float gain=0.0 ):
    """Ajdust the gain on a buffer acording to the passed in gain value."""
    assert buffer.dtype == DTYPE
    assert buffer.shape[0] >= size
    
    cdef i=0
    for i in range(size):
        buffer[i] *= dB(gain)

    return buffer
    
def fade( int offset, int size, np.ndarray buffer, float prefade=0.0, gainfrom=0.0, fadelength=1.0, gainto=NOISE_FLOOR ):
    """Fade a sound from one volume to another. Fade is linear in the dB scale.
    
    prefade: how long before the fade begins in seconds
    gainfrom: the initial gain level before the fade begins
    fadelength: how long the fade occurs over
    gainto: the final gain levelin the fade
    """
    assert buffer.dtype == DTYPE
    assert buffer.shape[0] >= size
    
    # time conversions
    cdef float toffset = offset * SAMPLE_TIME
    cdef float tsize = size * SAMPLE_TIME
    cdef float ti = toffset
    cdef float tend = toffset+tsize
    
    # counter across our buffer
    cdef int i=0
    cdef float gain=0.0
    
    for i in range(size):
        # if we are less than 1/2 wavelength, -ve. else +ve
        if ti<prefade:
            gain = gainfrom
        elif ti<prefade+fadelength:
            # fade
            gain = ((gainto - gainfrom)/fadelength) * (ti-prefade) + gainfrom
        else:
            gain = gainto
            
        buffer[i] *= dB(gain)
            
        ti += SAMPLE_TIME
    
    return buffer
    
