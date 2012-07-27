from lib2d import quadtree, vec, context, bbox
from lib2d.physics import *
import pygame, itertools


def rectToBody(rect):
    newbbox = (0, rect.left, rect.bottom, 1, rect.width, rect.height)
    return physicsbody.new(newbbox, (0,0), (0,0), 0)


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

    def __init__(self, gravity, bodies, geometry):
        self.gravity = vec.Vec2d(gravity)
        self.bodies = bodies
        self.geometry = quadtree.FastQuadTree(geometry)

        # static bodies are used when iterating over the group
        # so we need to transform them to bboxes
        self.staticBodies = [ rectToBody(r) for r in geometry ]
        self.sleeping = []


    def __iter__(self):
        return itertools.chain(self.bodies, self.staticBodies)


    def dynamicBodies(self):
        return iter(self.bodies)


    def add(self, *bodies):
        if all(isinstance(b, Body) for b in bodies):
            self.bodies.extend(bodies)
        else:
            raise TypeError


    def update(self, time):
        """
        time is expected to be in ms, just like what a pygame clock returns
        """

        time = time / 1000.0
        bodies = []

        for body in self.bodies:
            acc = body.acc + (self.gravity * time)
            vel = body.vel + acc * time
            body = physicsbody.new(body.bbox, acc, vel, body.o)
            y, z = body.vel

            if not y==0:
                body = self.moveBody(body, (0, y, 0))

            if z > 0: 
                tempbody = self.moveBody(body, (0, 0, z))
                if tempbody is body:
                    vel = (tempbody.vel.x, -tempbody.vel.y * 0.9)
                    body = physicsbody.new(tempbody.bbox, tempbody.acc, vel, body.o)
                else:
                    body = tempbody
 
            elif z < 0:
                body = self.moveBody(body, (0, 0, z))

            bodies.append(body)

        self.bodies = bodies


    def moveBody(self, body, (x, y, z), clip=True):
        newbbox = body.bbox.move(x, y, z)
        if self.testCollision(newbbox):
            return body
        else:
            return physicsbody.new(newbbox, body.acc, body.vel, body.o)


    def testCollision(self, bbox):
        layer = 0

        try:
            rect = self.toRect(bbox)
            hit = self.geometry.hit(rect)
            return bool(hit)

        except KeyError:
            msg = "Area Layer {} does not have a collision layer"
            print msg.format(layer)
            return False

            raise Exception, msg.format(layer)
 
