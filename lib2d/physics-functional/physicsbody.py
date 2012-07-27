from lib2d import vec, bbox
import collections



Body = collections.namedtuple("Body", "bbox acc vel o")

def new(newbbox, acc, vel, o):
    return Body(bbox.BBox(newbbox), vec.Vec2d(acc), vec.Vec2d(vel), o)




