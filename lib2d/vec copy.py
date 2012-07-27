################## http://www.pygame.org/wiki/2DVectorClass ##################
import operator
import math


class Vec3d(object):
    """
    3d vector class.  Not complete.
    """
    __slots__ = ['_x', '_y', '_z']

    def __init__(self, x_or_tuple, y=None, z=None):
        if y is not None and z is not None:
            self._x, self._y, self._z = x_or_tuple, y, z
        elif len(x_or_tuple) == 3:
            self._x, self._y, self._z = x_or_tuple
        else:
            raise ValueError

    def __len__(self):
        return 3

    def __getitem__(self, key):
        if key == 0:
            return self._x
        elif key == 1:
            return self._y
        elif key == 2:
            return self._z
        else:
            raise IndexError("Invalid subscript "+str(key)+" to Vec3d")

    # Addition
    def __add__(self, other):
        if isinstance(other, Vec3d):
            return Vec3d(self._x+other.x, self._y+other.y, self._x+other.x)
        elif hasattr(other, "__getitem__"):
            return Vec3d(self._x+other[0], self._y+other[1], self._z+other[2])
        else:
            return Vec3d(self._x + other, self._y + other, self._z + other)
    __radd__ = __add__

    # Subtraction
    def __sub__(self, other):
        if isinstance(other, Vec3d):
            return Vec3d(self._x-other.x, self._y-other.y, self._x-other.x)
        elif hasattr(other, "__getitem__"):
            return Vec3d(self._x-other[0], self._y-other[1], self._z-other[2])
        else:
            return Vec3d(self._x - other, self._y - other, self._z - other)
    def __rsub__(self, other):
        if isinstance(other, Vec3d):
            return Vec3d(other.x-self._x, other.y-self._y, other.z - self._z)
        if (hasattr(other, "__getitem__")):
            return Vec3d(other[0]-self._x, other[1]-self._y, other[2]-self._z)
        else:
            return Vec3d(other - self._x, other - self._y, other - self._z)



    @property
    def x(self):
        return self._x


    @property
    def y(self):
        return self._y


    @property
    def z(self):
        return self._z



class Vec2d(object):
    """2d vector class, supports vector and scalar operators,
       and also provides a bunch of high level functions
       """
    __slots__ = ['_x', '_y']
 
    def __init__(self, x_or_pair, y = None):
        if y is None:
            self._x = x_or_pair[0]
            self._y = x_or_pair[1]
        else:
            self._x = x_or_pair
            self._y = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

 
    def __len__(self):
        return 2
 
    def __getitem__(self, key):
        if key == 0:
            return self._x
        elif key == 1:
            return self._y
        else:
            raise IndexError("Invalid subscript "+str(key)+" to Vec2d")
 
    # String representaion (for debugging)
    def __repr__(self):
        return 'Vec2d(%s, %s)' % (self._x, self._y)
 
    # Comparison
    def __eq__(self, other):
        if hasattr(other, "__getitem__") and len(other) == 2:
            return self._x == other[0] and self._y == other[1]
        else:
            return False
 
    def __ne__(self, other):
        if hasattr(other, "__getitem__") and len(other) == 2:
            return self._x != other[0] or self._y != other[1]
        else:
            return True
 
    def __nonzero__(self):
        return bool(self._x or self._y)
 
    # Generic operator handlers
    def _o2(self, other, f):
        "Any two-operator operation where the left operand is a Vec2d"
        if isinstance(other, Vec2d):
            return Vec2d(f(self._x, other.x),
                         f(self._y, other.y))
        elif (hasattr(other, "__getitem__")):
            return Vec2d(f(self._x, other[0]),
                         f(self._y, other[1]))
        else:
            return Vec2d(f(self._x, other),
                         f(self._y, other))
 
    def _r_o2(self, other, f):
        "Any two-operator operation where the right operand is a Vec2d"
        if (hasattr(other, "__getitem__")):
            return Vec2d(f(other[0], self._x),
                         f(other[1], self._y))
        else:
            return Vec2d(f(other, self._x),
                         f(other, self._y))
 
    def _io(self, other, f):
        "inplace operator"
        if (hasattr(other, "__getitem__")):
            self._x = f(self._x, other[0])
            self._y = f(self._y, other[1])
        else:
            self._x = f(self._x, other)
            self._y = f(self._y, other)
        return self
 
    # Addition
    def __add__(self, other):
        if isinstance(other, Vec2d):
            return Vec2d(self._x + other.x, self._y + other.y)
        elif hasattr(other, "__getitem__"):
            return Vec2d(self._x + other[0], self._y + other[1])
        else:
            return Vec2d(self._x + other, self._y + other)
    __radd__ = __add__
 
    # Subtraction
    def __sub__(self, other):
        if isinstance(other, Vec2d):
            return Vec2d(self._x - other.x, self._y - other.y)
        elif (hasattr(other, "__getitem__")):
            return Vec2d(self._x - other[0], self._y - other[1])
        else:
            return Vec2d(self._x - other, self._y - other)
    def __rsub__(self, other):
        if isinstance(other, Vec2d):
            return Vec2d(other.x - self._x, other.y - self._y)
        if (hasattr(other, "__getitem__")):
            return Vec2d(other[0] - self._x, other[1] - self._y)
        else:
            return Vec2d(other - self._x, other - self._y)

    # Multiplication
    def __mul__(self, other):
        if isinstance(other, Vec2d):
            return Vec2d(self._x*other.x, self._y*other.y)
        if (hasattr(other, "__getitem__")):
            return Vec2d(self._x*other[0], self._y*other[1])
        else:
            return Vec2d(self._x*other, self._y*other)
    __rmul__ = __mul__
 
    # Division
    def __div__(self, other):
        return self._o2(other, operator.div)
    def __rdiv__(self, other):
        return self._r_o2(other, operator.div)
    def __idiv__(self, other):
        return self._io(other, operator.div)
 
    def __floordiv__(self, other):
        return self._o2(other, operator.floordiv)
    def __rfloordiv__(self, other):
        return self._r_o2(other, operator.floordiv)
    def __ifloordiv__(self, other):
        return self._io(other, operator.floordiv)
 
    def __truediv__(self, other):
        return self._o2(other, operator.truediv)
    def __rtruediv__(self, other):
        return self._r_o2(other, operator.truediv)
    def __itruediv__(self, other):
        return self._io(other, operator.floordiv)
 
    # Modulo
    def __mod__(self, other):
        return self._o2(other, operator.mod)
    def __rmod__(self, other):
        return self._r_o2(other, operator.mod)
 
    def __divmod__(self, other):
        return self._o2(other, operator.divmod)
    def __rdivmod__(self, other):
        return self._r_o2(other, operator.divmod)
 
    # Exponentation
    def __pow__(self, other):
        return self._o2(other, operator.pow)
    def __rpow__(self, other):
        return self._r_o2(other, operator.pow)
 
    # Bitwise operators
    def __lshift__(self, other):
        return self._o2(other, operator.lshift)
    def __rlshift__(self, other):
        return self._r_o2(other, operator.lshift)
 
    def __rshift__(self, other):
        return self._o2(other, operator.rshift)
    def __rrshift__(self, other):
        return self._r_o2(other, operator.rshift)
 
    def __and__(self, other):
        return self._o2(other, operator.and_)
    __rand__ = __and__
 
    def __or__(self, other):
        return self._o2(other, operator.or_)
    __ror__ = __or__
 
    def __xor__(self, other):
        return self._o2(other, operator.xor)
    __rxor__ = __xor__
 
    # Unary operations
    def __neg__(self):
        return Vec2d(operator.neg(self._x), operator.neg(self._y))
 
    def __pos__(self):
        return Vec2d(operator.pos(self._x), operator.pos(self._y))
 
    def __abs__(self):
        return Vec2d(abs(self._x), abs(self._y))
 
    def __invert__(self):
        return Vec2d(-self._x, -self._y)
 
    # vectory functions
    def get_length_sqrd(self):
        return self._x**2 + self._y**2
 
    def get_length(self):
        return math.sqrt(self._x**2 + self._y**2)
    def __setlength(self, value):
        length = self.get_length()
        self._x *= value/length
        self._y *= value/length
    length = property(get_length, __setlength, None, "gets or sets the magnitude of the vector")
 
    def rotated(self, angle_degrees):
        radians = math.radians(angle_degrees)
        cos = math.cos(radians)
        sin = math.sin(radians)
        x = self._x*cos - self._y*sin
        y = self._x*sin + self._y*cos
        return Vec2d(x, y)
 
    def get_angle(self):
        if (self.get_length_sqrd() == 0):
            return 0
        return math.atan2(self._y, self._x)

    def get_angle_between(self, other):
        cross = self._x*other[1] - self._y*other[0]
        dot = self._x*other[0] + self._y*other[1]
        return math.degrees(math.atan2(cross, dot))
 
    def normalized(self):
        length = self.length
        if length != 0:
            return self/length
        return Vec2d(self)
 
    def normalize_return_length(self):
        length = self.length
        if length != 0:
            self._x /= length
            self._y /= length
        return length
 
    def perpendicular(self):
        return Vec2d(-self._y, self._x)
 
    def perpendicular_normal(self):
        length = self.length
        if length != 0:
            return Vec2d(-self._y/length, self._x/length)
        return Vec2d(self)
 
    def dot(self, other):
        return float(self._x*other[0] + self._y*other[1])
 
    def get_distance(self, other):
        return math.sqrt((self._x - other[0])**2 + (self._y - other[1])**2)
 
    def get_dist_sqrd(self, other):
        return (self._x - other[0])**2 + (self._y - other[1])**2
 
    def projection(self, other):
        other_length_sqrd = other[0]*other[0] + other[1]*other[1]
        projected_length_times_other_length = self.dot(other)
        return other*(projected_length_times_other_length/other_length_sqrd)
 
    def cross(self, other):
        return self._x*other[1] - self._y*other[0]
 
    def interpolate_to(self, other, range):
        return Vec2d(self._x + (other[0] - self._x)*range, self._y + (other[1] - self._y)*range)
 
    def convert_to_basis(self, x_vector, y_vector):
        return Vec2d(self.dot(x_vector)/x_vector.get_length_sqrd(), self.dot(y_vector)/y_vector.get_length_sqrd())
 
    def __getstate__(self):
        return [self._x, self._y]
 
    def __setstate__(self, dict):
        self._x, self._y = dict
 

