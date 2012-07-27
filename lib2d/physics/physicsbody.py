from lib2d import vec, bbox
import collections


class Body(object):
    def __init__(self, thisbbox, acc, vel, o):
        self.bbox = bbox.BBox(thisbbox)
        self.acc = vec.Vec2d(acc)
        self.vel = vec.Vec2d(vel)
        self.o = o
