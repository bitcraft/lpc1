from lib2d import vec, bbox, euclid
import collections


class Body2(object):
    def __init__(self, thisbbox, acc, vel, o):
        self.bbox = bbox.BBox(thisbbox)
        self.acc = vec.Vec2d(acc)
        self.vel = vec.Vec2d(vel)
        self.o = o


class Body3(object):
    def __init__(self, thisbbox, acc, vel, o):
        self.bbox = bbox.BBox(thisbbox)
        self.acc = euclid.Vector3(*acc)
        self.vel = euclid.Vector3(*vel)
        self.o = o

