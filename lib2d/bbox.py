from vec import Vec3d
import collections


def intersect(a, b):
    return (((a.back   >= b.back   and a.back   < b.front)   or
             (b.back   >= a.back   and b.back   < a.front))  and
            ((a.left   >= b.left   and a.left   < b.right)   or 
             (b.left   >= a.left   and b.left   < a.right))  and
            ((a.bottom >= b.bottom and a.bottom < b.top)     or
             (b.bottom >= a.bottom and b.bottom < a.top)))

# BUG: collisions on right side are not correct


class BBox(tuple):
    """
    Rect-like Immutable class for defining area in 3d space.

    Once created cannot be modified.
    Operations that would change the bbox will return a new one.
    Hashable.

    Many of the methods here have not been extensively tested, but most should
    work as expected.
    """

    __slots__ = []


    def __new__(cls, *arg):
        """
        arg can be another bbox object
        an object with a 'bbox' attribute
        a list of six numbers: x, y, z, d, w, h
        a tuple that defines the bbox
        a list of two tuples: (x, y, z), (d, w, h)
        """


        # hack!!!
        if len(arg) == 1:
            arg = arg[0]

        if isinstance(arg, BBox):
            return tuple.__new__(cls, arg)

        elif isinstance(arg, (list, tuple)):
            if len(arg) == 2:
                self._x, self._y, self._z = arg[0]
                self._d, self._w, self._h = arg[1]
            elif len(arg) == 6:
                return tuple.__new__(cls, arg)
            else:
                raise ValueError, arg

        elif hasattr(arg, 'bbox'):
            self._x, self._y, self._z, self._d, self._w, self._h = arg.bbox

        else:
            raise ValueError, arg

        return tuple.__new__(cls, arg)

    def copy(self):
        return BBox(self)


    def move(self, x, y, z):
        return BBox(self[0] + x, self[1] + y, self[2] + z,
                    self[3],     self[3],     self[5])


    def inflate(self, x, y, z):
        return BBox((self._x - x / 2, self._y - y / 2, self._z - z / 2,
                     self._d + x,     self._w + y,     self._h + z))


    def clamp(self):
        raise NotImplementedError


    def clip(self, other):
        raise NotImplementedError


    def union(self, other):
        raise NotImplementedError

 
    def unionall(self, *rects):
        raise NotImplementedError


    def fit(self):
        raise NotImplementedError


    def normalized(self):
        """
        return a normalized bbox of this one
        """
        x, y, z, d, w, h = self
        if d < 0:
            x += d
            d = -d
        if w < 0:
            y += w
            w = -w
        if h < 0:
            z += h
            h = -h
        return Rect(x, y, z, d, w, h)


    def contains(self, other):
        raise NotImplementedError
        other = BBox(other)
        # this is not correct!
        return ((self._x <= other.back) and
                (self._y <= other.top) and
                (self._z <= other.front) and
                (self._x + self._w >= other.right) and
                (self._y + self._h >= other.bottom) and
                (self._z + self._d >= other.back) and
                (self._x + self._w > other.left) and
                (self._y + self._h > other.top) and
                (self._z + self._d > other.front))


    def collidepoint(self, (x, y, z)):
        return (x >= self._x and x < self._x + self._d and 
                y >= self._y and y < self._y + self._w and
                z >= self._z and z < self._z + self._h)


    def collidebbox(self, other):
        return intersect(self, BBox(other))


    def collidelist(self, l):
        for i, bbox in enumerate(l):
            if intersect(self, bbox):
                return i
        return -1


    def collidelistall(self, l):
        return [ i for i, bbox in enumerate(l)
                if intersect(self, bbox) ]


    def collidedict(self):
        raise NotImplementedError


    def collidedictall(self):
        raise NotImplementedError


    @property
    def back(self):
        return self._x


    @property
    def left(self):
        return self._y


    @property
    def bottom(self):
        return self._z


    @property
    def front(self):
        return self._x + self._d


    @property
    def right(self):
        return self._y + self._w


    @property
    def top(self):
        return self._z + self._h


    @property
    def size(self):
        return self._d, self._w, self._h


    @property
    def origin(self):
        return Vec3d(self._x, self._y, self._z)


    @property
    def bottomcenter(self):
        return Vec3d(self._x+self._d/2, self._y+self._w/2, self._z)


    @property
    def topcenter(self):
        return Vec3d(self._x+self._d/2, self._y+self._w/2, self._z+self._h)


    @property
    def center(self):
        return Vec3d(self._x+self._d/2, self._y+self._w/2, self._z+self._h/2)


    @property
    def x(self):
        return self[0]


    @property
    def y(self):
        return self[1]


    @property
    def z(self):
        return self[2]


    @property
    def depth(self):
        return self[3]


    @property
    def width(self):
        return self[4]


    @property
    def height(self):
        return self[5]
