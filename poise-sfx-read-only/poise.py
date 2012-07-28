"""

POISE
=====
Python Oldskool Ingame Sound Effects

Support library. Quickly calculates buffers. manipulates buffers. 

This cython extension renders and manipulates data in numpy arrays in a very fast way.

use like:

>>> import poise
>>> 
"""

import buffers
import osc
import envelope
from WaveFile import WaveFile

import wave

BUFFER_START_SIZE = 256*1024
FLOAT_MAX = 1.0
