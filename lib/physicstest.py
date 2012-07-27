from lib2d.buttons import *
from lib2d.signals import *
from lib2d.physics import *
from lib2d import res, ui, gfx, context

import pygame, math, time, random, collections


zoom = 1.0
xshift = 10 * zoom
yshift = 140 * zoom


def translate(bbox):
    return pygame.Rect(bbox.y*zoom, -bbox.z*zoom-bbox.height*zoom,
                       bbox.width*zoom, bbox.height*zoom)


class PhysicsTest(context.Context):
    def activate(self):
        bodies = []
        geometry = []
        self.dirty = collections.deque([])
        self.time = 0

        width = 240
        for y in range(0, width/2):
            cube = physicsbody.Body((0,y*2,y+40,2,1,4), (0,0), (0,0), 0)
            bodies.append(cube)
            geometry.append(pygame.Rect(y*2,0,2,10))

        self.group = PhysicsGroup(0.006, (0,9.8), bodies, geometry)


    def draw(self, surface):
        w, h = surface.get_size()
        tempdirty = collections.deque([])

        surface.lock()
        for color, dirty in self.dirty:
            for rect in dirty:
                pygame.draw.rect(surface, (color*2,color*4,color*6), rect)

            if color > 0:
                color -= 16
                tempdirty.appendleft((color, dirty))

        self.dirty = tempdirty

        dirty = []
        for body in self.group:
            rect = translate(body.bbox).move(xshift, yshift)
            z =  math.sin(self.time/400.0*math.pi) / math.pi * 32 + 16
            y = (float(rect.y) / h * 192) + z
            x = (float(rect.x) / w * 255)
            if y < 0: y = 0
            if x < 0: x = 0
            if x > 255: x = 255
            if y > 255: y = 255
            if z > 92: z = 92

            pygame.draw.rect(surface, (255-y,z*3,x), rect)
            dirty.append(rect)
            #rect = self.group.toRect(body.bbox)
            #pygame.draw.rect(surface, (y,z,x), rect)
            #print rect

        surface.unlock()
        self.dirty.appendleft((32, dirty))


    def impulse(self):
        for body in self.group.dynamicBodies():
            if body.acc.y == 0:
                body.vel.y = random.triangular(0,2)
                self.group.wakeBody(body)


    def handle_commandlist(self, cmdlist):
        for cls, cmd, arg in cmdlist:
            if arg == BUTTONDOWN:
                if cmd == P1_ACTION1:
                    self.impulse()   


    def update(self, time):
        self.time += time
        self.group.update(time)
