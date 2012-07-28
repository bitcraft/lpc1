"""

POISE
=====
Python Oldskool Ingame Sound Effects

Support library. Quickly calculates buffers. manipulates buffers. 

This cython extension renders and manipulates data in numpy arrays in a very fast way.

use like:

Python 2.5.2 Stackless 3.1b3 060516 (python-2.52:61022, Feb 27 2008, 16:52:03) 
[GCC 4.0.1 (Apple Computer, Inc. build 5341)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import poise
>>> import numpy
>>> a = numpy.zeros([100],numpy.float)
>>> a
array([ 0.,  0.,  0.,  0.,  ...
                        ...,  0.,  0.,  0.])
                        
# render 
>>> poise.sine(0,50,a)
array([ 0.        ,  0.00766983,  0.01687299,  0.02607472,  0.03527424,
        0.04447077,  0.05366354 ....
               ,  0.        ])

"""

#
# numerical python import
#
import numpy as np
cimport numpy as np

#
# the data type for sound samples
#
DTYPE = np.float
ctypedef np.int_t DTYPE_t

import math

#
# module constants
#
cdef float SAMPLE_RATE = 48000.
cdef float SAMPLE_TIME = 1.0/SAMPLE_RATE
cdef float NOISE_FLOOR = -96.0

def set_sample_rate( float rate ):
    """Set the sample rate used by the poise functions to 'rate'."""
    SAMPLE_RATE = rate

include "func.pyx"
include "osc.pyx"
include "envelope.pyx"
