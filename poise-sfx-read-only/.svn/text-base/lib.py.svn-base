
import numpy

class pod(object):
    """This is a generator that we inherit from to build the component POISE modules"""
    def __init__(self):
        self.offset = 0             # our present position
        self.buffer = None
        
    def __iter__(self):
        return self
        
    def next(self):
        raise StopIteration
        
    def send(self, length):
        raise StopIteration
        
    def _grow_buffer(self, length):
        """If the buffer size is less than length, allocate a new buffer the size of length. 
        zeros the buffer if it is reallocated"""
        if self.buffer == None or self.buffer.shape[0] < length:
            self.buffer = numpy.zeros( [length], numpy.float )
