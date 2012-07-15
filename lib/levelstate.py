from renderer import LevelCamera

from lib2d.gamestate import GameState
from lib2d.buttons import *
from lib2d.signals import *
from lib2d import res, ui

import pygame, math, time


"""
FUTURE:
    Create immutable types when possible to reduce headaches when threading
"""

debug = 1
movt_fix = 1/math.sqrt(2)


def getNearby(thing, d):
    p = thing.parent
    body = p.getBody(thing)
    bbox = body.bbox.inflate(64,d,d)
    x1, y1, z1 = body.bbox.center
    nearby = []
    for other in p.testCollideObjects(bbox, skip=[body]): 
        x2, y2, z2 = other.bbox.center
        dist = math.sqrt(pow(x1-x2, 2) + pow(y1-y2, 2) + pow(z1-z2, 2))
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
state = None


class LevelUI(ui.UserInterface):
    pass



class LevelState(GameState):
    """
    This state is where the player will move the hero around the map
    interacting with npcs, other players, objects, etc.

    much of the work done here is in the Standard UI class.
    """

    def __init__(self, parent, area, startPosition=None):
        GameState.__init__(self, parent)
        self.area = area


    def activate(self):
        self.ui = LevelUI()
        vpm = ui.Frame(self.ui, ui.GridPacker())
        vpm.addElement(ui.ViewPort(self.area))
        self.ui.addElement(vpm)


    def draw(self, surface):
        self.ui.draw(surface)


    def handle_commandlist(self, cmdlist):
        self.ui.handle_commandlist(cmdlist)


@receiver(emitText)
def displayText(sender, **kwargs):
    x1, y1, z1 = kwargs['position']
    x2, y2, z2 = hero_body.bbox.origin
    d = math.sqrt(pow(x1-x2, 2) + pow(y1-y2, 2) + pow(z1-z2, 2))
    state.updateText = True


@receiver(emitSound)
def playSound(sender, **kwargs):
    x1, y1, z1 = kwargs['position']
    x2, y2, z2 = hero_body.bbox.origin
    d = math.sqrt(pow(x1-x2, 2) + pow(y1-y2, 2) + pow(z1-z2, 2))
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

    if state is None:
        return


@receiver(bodyWarp)
def bodyWarp(sender, **kwargs):
    area = sender
    body = kwargs['body']
    destination = kwargs['destination']
    state = kwargs['caller']

    if state is None:
        return

    if body == state.hero:
        #sd.push(WorldState(destination))
        #sd.done()
        pass

