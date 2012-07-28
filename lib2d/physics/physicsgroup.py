from lib2d import res, quadtree, vec, context, bbox, euclid
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
        return physicsbody.Body2(newbbox, (0,0), (0,0), 0)


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



class AdventureMixin(object):
    """
    Mixin class that contains methods to translate world coordinates to screen
    or surface coordinates.
    """

    # accessing the bbox by index much faster than accessing by attribute
    def toRect(self, bbox):
        return pygame.Rect((bbox[0], bbox[1], bbox[3], bbox[4]))


    def rectToBody(self, rect):
        newbbox = (rect.x, rect.y, 0, rect.width, rect.height, 0)
        return physicsbody.Body3(newbbox, (0,0,0), (0,0,0), 0)


    def precompute(self, start, end, step):
        """
        run through various values to fill the vector cache with useful
        values
        """
        def frange(start, end, step):
            while start <= end:
                yield start
                start = round(start + step, self.precision)


        for x in frange(start, end, step):
            vec.Vec2d((0, x)) * self.timestep


    def update(self, time):
        for body in (b for b in self.bodies if b not in self.sleeping):
            body.acc += self.gravity_delta

            # rounding improves memoization at expense of accuracy
            #body.acc.y = round(body.acc.y, self.precision)
            body.vel += body.acc * self.timestep
            x, y, z = body.vel

            if not x==0:
                if not self.moveBody(body, (x, 0, 0)):
                    if abs(body.vel.x) > .2:
                        body.acc.x = 0
                        body.vel.x = -body.vel.x * .2
                    else:
                        body.acc.x = 0
                        body.vel.x = 0
                        #self.sleeping.append(body)

            if not y==0:
                if not self.moveBody(body, (0, y, 0)):
                    if abs(body.vel.y) > .2:
                        body.acc.y = 0
                        body.vel.y = -body.vel.y * .2
                    else:
                        body.acc.y = 0
                        body.vel.y = 0
                        #self.sleeping.append(body)

            if z < 0:
                if not self.moveBody(body, (0, 0, z)):
                    if abs(body.vel.z) > .2:
                        body.acc.z = 0
                        body.vel.z = -body.vel.z * .2
                    else:
                        body.acc.z = 0
                        body.vel.z = 0
                        #self.sleeping.append(body)
 
            elif z > 0:
                self.moveBody(body, (0, 0, z))

            if body.bbox.z == 0:
                body.vel.x = body.vel.x * self.ground_friction
                body.vel.y = body.vel.y * self.ground_friction


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
        the bboxes passed to geometry will be translated into the correct type

    a word on the coordinate system:
        coordinates are 'right handed'
        x axis moves toward viewer
        y axis move left right
        z axis is height

    """

    def __init__(self, scaling, timestep, gravity, bodies, geometry, precision=2):
        self.scaling = scaling
        self.gravity = euclid.Vector3(0,0,gravity)
        self.bodies = bodies
        self.precision = precision
        self.sleeping = []
        self.staticBodies = []
        [ self.scaleBody(b, scaling) for b in self.bodies ]

        rects = []
        for bbox in geometry:
            body = physicsbody.Body3(bbox, (0,0,0), (0,0,0), 0)
            self.scaleBody(body, scaling)
            self.staticBodies.append(body)
            rects.append(self.toRect(body.bbox))

        self.geometry = quadtree.FastQuadTree(rects)

        self.setTimestep(timestep)
        #self.precompute(-10.0, 10.0, 1/(10.0**self.precision))


    def __iter__(self):
        return itertools.chain(self.bodies, self.staticBodies)


    def scaleBody(self, body, scale):
        body.bbox.scale(scale, scale, scale)


    def dynamicBodies(self):
        return iter(self.bodies)


    def wakeBody(self, body):
        try:
            self.sleeping.remove(body)
        except:
            pass

    
    def setTimestep(self, time):
        self.timestep = time
        self.gravity_delta = self.gravity * time
        self.ground_friction = pow(.001, self.timestep)
        #self.gravity_delta.y = round(self.gravity_delta.y, self.precision)


    def moveBody(self, body, (x, y, z), clip=True):
        body.bbox.move(x, y, z)
        if self.testCollision(body.bbox):
            if body.bbox[2] < 0:
                body.bbox[2] = 0.0
                body.bbox.move(-x, -y, 0)
            else:
                body.bbox.move(-x, -y, -z)
            return False
        return True

    def testCollision(self, bbox):
        # for adventure games
        if bbox[2] < 0:
            return True
        return bool(self.geometry.hit(self.toRect(bbox)))



class PlatformerPhysicsGroup(PhysicsGroup, PlatformerMixin):
    pass


class AdventurePhysicsGroup(PhysicsGroup, AdventureMixin):
    pass
