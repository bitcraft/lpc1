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


class Pane(object):
    """
    object capable of interacting with the mouse
    """
    pass


class MouseTool(object):
    def onClick(self, pane, point, button):
        pass


    def onDrag(self, pane, point, button, origin):
        pass


    def onHover(self, pane, point):
        pass



class PanTool(MouseTool):
    def __init__(self):
        self.drag_origin = None


    def onClick(self, pane, point, button):
        self.drag_origin = None


    def onDrag(self, pane, point, button, origin):
        if self.drag_origin == None:
            x, y = self.rect.width / 2, self.rect.height / 2
            self.drag_origin = self.camera.surfaceToWorld((x, y))

        x, y, z = self.drag_origin
        dy, dx = point[0] - start[0], point[1] - start[1]
        self.camera.center((x-dx, y-dy, z))


    def onHover(self, pane, point):
        pass
        #wp = self.camera.surfaceToWorld(point)
        #ws = self.camera.worldToSurface(wp)


class PaneManager(object):
    """
    Handles pnaes and mouse tools
    """

    def __init__(self, rect):
        self.panes = []
        self.areas = []
        self.rect = pygame.Rect(rect)

        self.mouse_tool = PanTool()

        #mouse hack
        self.drag_start = None
        self.drag_vp = None

    def addArea(self, area):
        if area not in self.areas:
            self.areas.append(area)
            area.load()

            # load the children
            for child in area.getChildren():
                child.load()

            # load sounds from area
            for filename in area.soundFiles:
                SoundMan.loadSound(filename)


    def new(self, area, follow):
        if area not in self.areas:
            self.addArea(area)

        if len(self.panes) == 0:
            rect = self.rect.copy()

        elif len(self.panes) == 1:
            rect = self.rect.copy()
            rect.height = rect.height / 2
            rect = rect.move((0, rect.height))

        elif len(self.panes) == 2:
            w = self.rect.width / 2
            h = self.rect.height / 2
            rect = self.rect.copy()
            # WARNING!!!! 3 panes does not work

        elif len(self.panes) == 3:
            w = self.rect.width / 2
            h = self.rect.height / 2
            self.panes[0].rect = pygame.Rect(0,0,w,h)
            self.panes[1].rect = pygame.Rect(w,0,w,h)
            self.panes[2].rect = pygame.Rect(0,h,w,h)
            rect = pygame.Rect(w,h,w,h)           
 
        vp = ViewPort(area, follow)
        vp.rect = rect
        self.panes.append(vp)


    def draw(self, surface):
        dirty = []
        for i, pane in enumerate(self.panes):
            dirty.extend(pane.draw(surface, pane.rect))

        return dirty


    def getRects(self):
        """ return a list of rects that split the viewports """
        return [ pane.rect for pane in self.panes ]


    def update(self, time):
        [ vp.update(time) for vp in self.panes ]
        [ area.update(time) for area in self.areas ]
        

    def findViewport(self, point):
        for vp in self.panes:
            if vp.rect.collidepoint(point):
                return vp


    def handle_commandlist(self, cmdlist):
        for cls, cmd, arg in cmdlist:
            if cmd == CLICK1:
                state, pos = arg
                vp = self.findViewport(pos)
                if vp:
                    pos = (pos[0] - vp.rect.left, pos[1] - vp.rect.top)
                    if state == BUTTONDOWN:
                        self.drag_start = pos
                        self.drag_vp = vp
                        self.mouse_tool.onClick(vp, pos, 1)

                    elif state == BUTTONHELD:
                        if vp == self.drag_vp:
                            self.mouse_tool.onDrag(vp, pos, 1, self.drag_start)

            elif cmd == CLICK2:
                pass
            elif cmd == MOUSEPOS:
                vp = self.findViewport(arg)
                if vp:
                    pos = (arg[0] - vp.rect.left, arg[1] - vp.rect.top)
                    self.mouse_tool.onHover(vp, pos)


class ViewPort(Pane):
    """
    View is the view of one specific game entity
    """

    def __init__(self, area, follow):
        self.background = (109, 109, 109)
        self.foreground = (0, 0, 0)
        self.area = area
        self.follow = follow
        self.blank = True
        self.rect = None
        self.camera = None


    def setRect(self, rect):
        self.rect = rect
        self.blank = True    # causes the camera to be reinitialized in draw()


    def draw(self, surface, rect):
        self.rect = rect

        if self.blank:
            self.blank = False
            x, y, w, h = rect
            self.camera = LevelCamera(self.area, (0, 0, w, h))
            self.camera.draw(surface, rect)
            return self.rect
            
        else:
            return self.camera.draw(surface, rect)


    def update(self, time):
        self.camera.update(time)


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

        # get the root and the hero from it
        root = self.area.getRoot()
        self.hero = root.getChildByGUID(1)
        self.hero.move_speed = 16

        # add the hero to this map if it isn't ready there
        if not self.area.hasChild(self.hero):
            self.area.add(self.hero)

        hero_body = self.area.getBody(self.hero)

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
        self.vpmanager = PaneManager(surface.get_rect())
        self.vpmanager.new(self.area, self.hero)
        self.vpmanager.new(self.area, self.hero)
        self.vpmanager.new(self.area, self.hero)
        self.vpmanager.new(self.area, self.hero)


    def draw(self, surface):
        if self.blank:
            self.blank = False
            self.buildViewports(surface)

        self.vpmanager.draw(surface)

        for rect in self.vpmanager.getRects():
            self.border.draw(surface, rect.inflate(6,6))


    def update(self, time):
        if self.blank: return
        self.vpmanager.update(time)


    def handle_commandlist(self, cmdlist):
        if self.blank: return
        self.vpmanager.handle_commandlist(cmdlist)


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


