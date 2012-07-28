"""

POISE
=====
Python Oldskool Ingame Sound Effects

Support library. Quickly calculates buffers. manipulates buffers. 
"""
import random

cdef int NUM_SINE_VALUES = 8192
cdef np.ndarray SINE_TABLE = np.zeros([NUM_SINE_VALUES, 1], dtype=DTYPE)

cdef fill_sine():
    """this fills our static lookup array for our highspeed sin function"""
    cdef int x
    cdef float theta
    for x in range(NUM_SINE_VALUES):
        theta = float(x)*2.*math.pi/(float(NUM_SINE_VALUES))
        SINE_TABLE[x] = math.sin(theta)

# run on import to fill table
fill_sine()

# calculate sin by looking up the closest value
cdef sin(float theta):
    cdef float x = theta*float(NUM_SINE_VALUES)/(2.*math.pi) + 2.0 * math.pi / float(NUM_SINE_VALUES)
    cdef float answer = SINE_TABLE[int(x)%NUM_SINE_VALUES]
    return answer
    
cdef sin_true(float theta):
    cdef float answer = math.sin(theta)
    return answer
    
cdef cos(float theta):
    return sin(theta+math.pi/4.0)

# turn decibel into a multiplier
cdef db(float gain=0.0):
    cdef float db = 10.0 ** ( gain / 20.0 )
    return db

def dB(float gain=0.0):
    return db(gain)

# window theta
cdef frange( float var, float min, float max ):
    cdef float wavelength = max - min
    cdef int div
    cdef int divexp
    
    if var<wavelength:
        return var
    
    # quickly bring back into range min to max
    for divexp in range(5,-1,-1):
        div = 10 ** divexp
        while var>wavelength*float(div):
            var -= wavelength*float(div)
            
    return var

cdef int NUM_RAND_VALUES = 16384 * 4
cdef np.ndarray RAND_TABLE = np.zeros([NUM_RAND_VALUES, 1], dtype=DTYPE)
cdef int rand_offset = 0

cdef fill_rand():
    """this fills our static lookup array for our highspeed sin function"""
    cdef int xr
    for xr in range(NUM_RAND_VALUES):
        RAND_TABLE[xr] = random.random()
    
# run on import to fill table
fill_rand()

cdef float crand():
    cdef float result
    global rand_offset
    
    rand_offset+= 1
    if rand_offset >= NUM_RAND_VALUES:
        rand_offset = 0
    
    result = RAND_TABLE[rand_offset]
    return result
