from renderer import LevelCamera
from misc import Lift

from lib2d.gamestate import GameState
from lib2d.statedriver import driver as sd
from lib2d.buttons import *
from lib2d.signals import *
from lib2d.vec import Vec2d
from lib2d.quadtree import QuadTree, FrozenRect
from lib2d import res, gui
import pytmx

from random import randint
from math import sqrt, atan2
from operator import itemgetter
from itertools import ifilter
import pygame
import os.path

import time


debug = 1

movt_fix = 1/sqrt(2)


def getNearby(thing, d):
    p = thing.parent
    body = p.getBody(thing)
    bbox = body.bbox.inflate(64,d,d)
    x1, y1, z1 = body.bbox.center
    nearby = []
    for other in p.testCollideObjects(bbox, skip=[body]): 
        x2, y2, z2 = other.bbox.center
        dist = sqrt(pow(x1-x2, 2) + pow(y1-y2, 2) + pow(z1-z2, 2))
        nearby.append((d, (other.parent, other)))

    return [ i[1] for i in sorted(nearby) ]


class SoundManager(object):
    def __init__(self):
        self.sounds = {}
        self.last_played = {}

    def loadSound(self, filename):
        self.sounds[filename] = res.loadSound(filename)
        self.last_played[filename] = 0

    def play(self, filename, volume=1.0):
        now = time.time()
        if self.last_played[filename] + .05 <= now:
            self.last_played[filename] = now
            sound = self.sounds[filename]
            sound.set_volume(volume)
            sound.play()

    def unload(self):
        self.sounds = {}
        self.last_played = {}


SoundMan = SoundManager()


# GLOBAL LEET SKILLS
hero_body = None
state = None



class ViewPortManager(object):
    def __init__(self, rect):
        self.viewports = []
        self.rect = pygame.Rect(rect)


    def new(self, area, follow):
        if len(self.viewports) == 0:
            rect = self.rect.copy()
        elif len(self.viewports) == 1:
            rect = self.rect.copy()
            rect.height = rect.height / 2
            self.viewports[0].rect = rect
            rect = rect.move((0, rect.height))
        elif len(self.viewports) == 2:
            rect = self.rect.copy()
            pass

        vp = ViewPort(area, follow, rect) 
        self.viewports.append(vp)


    def draw(self, surface):
        return 
        dirty = []
        for vp in self.viewports:
            dirty.extend(vp.draw(surface))

        for vp in self.viewports:
            pygame.draw.rect(surface, (120,120,120), vp.rect, 1)

        return dirty


    def update(self, time):
        [ vp.update(time) for vp in self.viewports ]
        

    def findViewport(self, point):
        for vp in self.viewports:
            if vp.rect.collidepoint(point):
                return vp


    def handle_commandlist(self, cmdlist):
        for cls, cmd, arg in cmdlist:
            if cmd == CLICK1:
                if isinstance(arg, tuple):
                    state, pos = arg
                    vp = self.findViewport(pos)
                    if vp:
                        x, y = pos
                        x -= vp.rect.left
                        y -= vp.rect.top
                        vp.onClick((x, y))
                else:
                    state = arg

            elif cmd == CLICK2:
                pass
            elif cmd == MOUSEPOS:
                pass


class ViewPort(object):
    """
    View is the view of one specific game entity
    """

    def __init__(self, area, follow, rect):
        self.background = (109, 109, 109)
        self.foreground = (0, 0, 0)
        self.area = area
        self.follow = follow
        self.rect = rect
        self.blank = True
        self.camera = None


    def onClick(self, point):
        print "clickes", self, point


    def onHover(self, point):
        pass


    def resize(self, rect):
        pass


    def draw(self, surface):
        if self.blank:
            self.blank = False
            sw, sh = surface.get_size()
            surface.fill(self.background)
            self.camera = LevelCamera(self.area, self.rect, tmxdata=self.area.tmxdata)
            self.camera.draw(surface)
            return [((0,0), (sw, sh))]
            
        else:
            self.camera.center(self.area.getPosition(self.follow))
            #return self.camera.draw(surface)
            self.camera.draw(surface)



    def update(self, time):
        #self.camera.update(time)
        pass



class Node(object):
    def __init__(self, parent, left, right):
        self.parent = parent
        self.left = left
        self.right = right

class LevelState(GameState):
    """
    This state is where the player will move the hero around the map
    interacting with npcs, other players, objects, etc.

    Expects to load a specially formatted TMX map created with Tiled.
    Layers:
        Control Tiles
        Upper Partial Tiles
        Lower Partial Tiles
        Lower Full Tiles

    The control layer is where objects and boundries are placed.  It will not
    be rendered.  Your map must not have any spaces that are open.  Each space
    must have a tile in it.  Blank spaces will not be rendered properly and
    will leave annoying trails on the map.

    The control layer must be created with the utility included with lib2d.  It
    contains metadata that lib2d can use to layout and position objects
    correctly.

    """

    def __init__(self, area, startPosition=None):
        GameState.__init__(self)
        self.area = area
        global state
        state = self


    def activate(self):
        global hero_body

        self.blank = True
        self.background = (109, 109, 109)
        self.foreground = (0, 0, 0)

        self.msgFont = pygame.font.Font((res.fontPath("volter.ttf")), 9)
        self.border = gui.GraphicBox("dialog2-h.png", hollow=True)
        self.borderFilled = gui.GraphicBox("dialog2.png")
        self.vpmanager = None
        self.input_changed = True

        # allow the area to get needed data
        self.area.load()

        # load the children
        for child in self.area.getChildren():
            child.load()

        # get the root and the hero from it
        root = self.area.getRoot()
        self.hero = root.getChildByGUID(1)
        self.hero.move_speed = 16

        # add the hero to this map if it isn't ready there
        if not self.area.hasChild(self.hero):
            self.area.add(self.hero)

        hero_body = self.area.getBody(self.hero)

        # load sounds from area
        for filename in self.area.soundFiles:
            SoundMan.loadSound(filename)

        self.reactivate()


    def deactivate(self):
        res.fadeoutMusic(1000)

        # unload the children
        for child in self.area.getChildren():
            child.unload()

        # unload sounds
        SoundMan.unload()   

 
    def reactivate(self):
        pygame.mouse.set_visible(True)


    def buildViewports(self, surface):
        self.vpmanager = ViewPortManager(surface.get_rect())
        self.vpmanager.new(self.area, self.hero)
        self.vpmanager.new(self.area, self.hero)


    def draw(self, surface):
        if self.blank:
            self.blank = False
            self.buildViewports(surface)

        self.vpmanager.draw(surface)

        if self.input_changed:
            print "chc"
            self.input_changed = False
            world_size = 320, 240
            region_size = 32, 32

            import random
            from collections import deque
            from pygame import Rect
            rect = Rect((0,0), world_size)

            regions = [rect]

            i = 320
            bag = [True, False] * (i/2)

            max_depth = 8
            depth = 0

            while depth < max_depth:
                queue = deque(regions)
                regions = []
                depth += 1

                while bag and queue:
                    #random.shuffle(bag)
                    rect = queue.pop()
                    split = bag.pop()
                    w,h = rect.size

                    if rect.height > 0:
                        r = float(rect.width) / rect.height
                        if r < .5:
                            split = False
                        elif r > 1.5:
                            split = True

                    # True is a horizontal split
                    if split:
                        d = random.randint(-rect.width/8, rect.width/8)
                        w = rect.width/2 + d
                        a = Rect(rect.left, rect.top, w, rect.height)
                        b = Rect(rect.left + w, rect.top, rect.width - w, rect.height)
                    else:
                        d = random.randint(-rect.height/8, rect.height/8)
                        h = rect.height/2 + d
                        a = Rect(rect.left, rect.top, rect.width, h)
                        b = Rect(rect.left, rect.top + h, rect.width, rect.height - h)

                    regions.append(a)
                    regions.append(b)


            surface.fill((0,0,0))
            for rect in regions:
                pygame.draw.rect(surface, (random.randint(128,255),random.randint(128, 255),128), rect, 1)


    def update(self, time):
        if self.blank: return

        self.area.update(time)
        self.vpmanager.update(time)


    def handle_commandlist(self, cmdlist):
        if self.blank: return

        self.vpmanager.handle_commandlist(cmdlist)

        for cls, cmd, arg in cmdlist:
            # these actions will not repeat if button is held
            if arg == BUTTONDOWN:
                self.input_changed = True


@receiver(emitText)
def displayText(sender, **kwargs):
    x1, y1, z1 = kwargs['position']
    x2, y2, z2 = hero_body.bbox.origin
    d = sqrt(pow(x1-x2, 2) + pow(y1-y2, 2) + pow(z1-z2, 2))
    state.updateText = True


@receiver(emitSound)
def playSound(sender, **kwargs):
    x1, y1, z1 = kwargs['position']
    x2, y2, z2 = hero_body.bbox.origin
    d = sqrt(pow(x1-x2, 2) + pow(y1-y2, 2) + pow(z1-z2, 2))
    try:
        vol = 1/d * 20 
    except ZeroDivisionError:
        vol = 1.0
    if vol > .02:
        SoundMan.play(kwargs['filename'], volume=vol)


@receiver(bodyAbsMove)
def bodyMove(sender, **kwargs):
    area = sender
    body = kwargs['body']
    position = kwargs['position']
    state = kwargs['caller']

    if state == None:
        return

    if body == state.hero:
        state.camera.center(position)


@receiver(bodyWarp)
def bodyWarp(sender, **kwargs):
    area = sender
    body = kwargs['body']
    destination = kwargs['destination']
    state = kwargs['caller']

    if state == None:
        return

    if body == state.hero:
        sd.push(WorldState(destination))
        sd.done()


