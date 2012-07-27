from lib2d import res, quadtree, vec, context, bbox
from lib2d.physics import *
from lib2d.utils import *
import pygame, itertools





class PlatformerMixin(object):
    """
    Mixin class that contains methods to translate world coordinates to screen
    or surface coordinates.
    """

    def toRect(self, bbox):
        return pygame.Rect((bbox.y, bbox.z, bbox.width, bbox.height))


    def rectToBody(self, rect):
        newbbox = (0, rect.x, rect.y, 1, rect.width, rect.height)
        return physicsbody.Body(newbbox, (0,0), (0,0), 0)


    def precompute(self, start, end, step):
        """
        run through various values to fill the vector cache with useful
        values
        """
        def frange(start, end, step):
            while start <= end:
                print start
                yield start
                start = round(start + step, self.precision)


        for x in frange(start, end, step):
            vec.Vec2d((0, x)) * self.timestep


    def update(self, time):
        for body in (b for b in self.bodies if b not in self.sleeping):
            body.acc += self.gravity_delta

            # rounding improves memoization at expense of accuracy
            body.acc.y = round(body.acc.y, self.precision)
            body.vel += body.acc * self.timestep
            y, z = body.vel

            if not y==0:
                self.moveBody(body, (0, y, 0))

            if z < 0:
                old_bbox = body.bbox
                self.moveBody(body, (0, 0, z))

                # true when there is a collision
                if old_bbox is body.bbox:
                    if abs(body.vel.y) > .2:
                        body.acc.y = 0
                        body.vel.y = -body.vel.y * .2
                    else:
                        body.acc.y = 0
                        body.vel.y = 0
                        self.sleeping.append(body)
 
            elif z > 0:
                self.moveBody(body, (0, 0, z))



class PhysicsGroup(context.Context):
    """
    object mangages a list of physics bodies and moves them around to simulate
    simple physics.  Currently, only gravity and simple movement is implemented
    without friction or collision handling.

    static bodies are simply called 'geometry' and handled slightly different
    from dynamic bodies.

    the dimensions of your objects are important!  internally, collision
    detection against static bodies is handled by pygame rects, which cannot
    handle floats.  this means that the smallest body in the game must be at
    least a 1x1x1 meter cube.

    For speed, only 2 axises are checked for collisions:
        using the adventure mixin, this will be the xy plane
        using the platformer mixin, this will be the zy plane

    a word on the coordinate system:
        coordinates are 'right handed'
        x axis moves toward viewer
        y axis move left right
        z axis is height

    This follows classical conventions, but is somewhat different from how
    pygame handles regular sprites.
    """

    def __init__(self, scaling, timestep, gravity, bodies, geometry, precision=2):
        self.scaling = scaling
        self.gravity = vec.Vec2d(gravity)
        self.bodies = [ self.scaleBody(b, scaling) for b in bodies ]
        self.geometry = quadtree.FastQuadTree(geometry)
        self.precision = precision

        pygame.mixer.set_num_channels(32)

        # static bodies are used when iterating over the group
        # so we need to transform them to bboxes
        self.staticBodies = [ self.scaleBody(self.rectToBody(r), scaling)
                              for r in geometry ]
        self.sleeping = []

        self.setTimestep(timestep)
        self.precompute(-10.0, 10.0, 1/(10.0**self.precision))


    def __iter__(self):
        return itertools.chain(self.bodies, self.staticBodies)


    def scaleBody(self, body, scale):
        body.bbox = body.bbox.scale(scale, scale, scale)
        return body


    def dynamicBodies(self):
        return iter(self.bodies)


    def add(self, *bodies):
        if all(isinstance(b, Body) for b in bodies):
            self.bodies.extend(bodies)
        else:
            raise TypeError


    def wakeBody(self, body):
        try:
            self.sleeping.remove(body)
        except:
            pass

    
    def setTimestep(self, time):
        self.timestep = time
        self.gravity_delta = self.gravity * time
        self.gravity_delta.y = round(self.gravity_delta.y, self.precision)


    def moveBody(self, body, (x, y, z), clip=True):
        newbbox = body.bbox.move(x, y, z)
        if not self.testCollision(newbbox):
            body.bbox = newbbox


    def testCollision(self, bbox):
        return bool(self.geometry.hit(self.toRect(bbox)))



class PlatformerPhysicsGroup(PhysicsGroup, PlatformerMixin):
    pass
