from lib2d.buttons import *
from lib2d.signals import *
from lib2d.physics import *
from lib2d import res, ui, gfx, context

import pygame, math, time, random, collections


zoom = 1
xshift = 10 * zoom
yshift = 250 * zoom



background = (192,192,192)


# platform games (yz plane)
def translate2(bbox):
    return pygame.Rect(bbox[1]*zoom, -bbox[2]*zoom-bbox.height*zoom,
                       bbox[4]*zoom, bbox[5]*zoom)


# adventure games (xy plane + z)
def translate(bbox):
    return pygame.Rect(bbox[1]*zoom, -bbox[0]*zoom-bbox.depth*zoom-bbox[2]/2,
                       bbox[4]*zoom, bbox[3]*zoom)


class PhysicsTest(context.Context):
    def activate(self):
        bodies = []
        geometry = []
        self.dirty = collections.deque([])
        self.time = 0
        self.blank = True

        width = 240
        for y in range(0, width/2):
            cube = physicsbody.Body3((y,y*2,y+40,2,2,4), (0,0,0), (0,0,0), 0)
            bodies.append(cube)
        
        geometry.append(bbox.BBox((0,0,0,2,width,0)))
        geometry.append(bbox.BBox((0,0,0,width,2,0)))
        geometry.append(bbox.BBox((0,width,0,width,2,0)))
        geometry.append(bbox.BBox((width,0,0,2,width,0)))

        self.group = AdventurePhysicsGroup(1, 0.006, -9.8, bodies, geometry)


    def draw(self, surface):
        if self.blank:
            surface.fill(background)
            self.blank = False

        w, h = surface.get_size()

        surface.lock()
        [ pygame.draw.rect(surface, background, rect) for rect in self.dirty ]

        self.dirty = []
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

            # draw shadow
            if body.bbox.z > 0:
                shadow = rect.move(0, body.bbox.z/2)
                self.dirty.append(pygame.draw.rect(surface, (0,0,0), shadow))

            self.dirty.append(pygame.draw.rect(surface, (255-y,z*3,x), rect)) 

        surface.unlock()


    def impulse(self):
        for body in self.group.dynamicBodies():
            if body.acc.z == 0:
                body.vel.x = round(random.triangular(-.5,.5), self.group.precision)
                body.vel.y = round(random.triangular(-.5,.5), self.group.precision)
                body.vel.z = round(random.triangular(0,1.5), self.group.precision)
                self.group.wakeBody(body)


    def handle_commandlist(self, cmdlist):
        for cls, cmd, arg in cmdlist:
            if arg == BUTTONDOWN:
                if cmd == P1_ACTION1:
                    self.impulse()   


    def update(self, time):
        self.time += time
        self.group.update(time)
