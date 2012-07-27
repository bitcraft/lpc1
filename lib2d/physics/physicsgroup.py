from lib2d import quadtree, vec, context, bbox
from lib2d.physics import *
from lib2d.utils import *
import pygame, itertools


def rectToBody(rect):
    newbbox = (0, rect.x, rect.y, 1, rect.width, rect.height)
    return physicsbody.Body(newbbox, (0,0), (0,0), 0)


class AdventureMixin(object):
    """
    Mixin class that contains methods to translate world coordinates to screen
    or surface coordinates.
    """

    def toRect(self, bbox):
        return pygame.Rect((bbox.y, bbox.z, bbox.width, bbox.height))


class PhysicsGroup(context.Context, AdventureMixin):
    """
    object mangages a list of physics bodies and moves them around to simulate
    simple physics.  Currently, only gravity and simple movement is implemented
    without friction or collision handling.

    static bodies are simply called 'geometry' and handled slightly different
    from dynamic bodies.

    For speed, only 2 axises are checked for collisions:
        using the adventure mixin, this will be the xy plane
        using the platformer mixin, this will be the zy plane

    a word on the coordinate system:
        coordinates are 'right handed'
        x axis moves toward viewer
        y axis move left right
        z axis is height

    This follows classical conventions, but is somewhat different from how
    pygame handles regular sprites.  When specifying group geometry, keep in
    mind that you will have to first translate the rects by rotating them
    clockwise 90 degrees.
    """

    def __init__(self, timestep, gravity, bodies, geometry):
        self.gravity = vec.Vec2d((gravity[0], -gravity[1]))
        self.bodies = bodies
        self.geometry = quadtree.FastQuadTree(geometry)

        # static bodies are used when iterating over the group
        # so we need to transform them to bboxes
        self.staticBodies = [ rectToBody(r) for r in geometry ]
        self.sleeping = []

        self.setTimestep(timestep)


    def __iter__(self):
        return itertools.chain(self.bodies, self.staticBodies)


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


    def update(self, time):
        for body in (b for b in self.bodies if b not in self.sleeping):
            body.acc += self.gravity_delta

            # rounding improves memoization at expense of accuracy
            body.acc.y = round(body.acc.y, 1)
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


    def moveBody(self, body, (x, y, z), clip=True):
        newbbox = body.bbox.move(x, y, z)
        if not self.testCollision(newbbox):
            body.bbox = newbbox


    def testCollision(self, bbox):
        return bool(self.geometry.hit(self.toRect(bbox)))

