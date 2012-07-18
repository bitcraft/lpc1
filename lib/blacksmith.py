from lib2d.image import Image
from lib2d import avatar, animation, res

from entity import Entity

# pygoap already has a nice action/object class
from pygoap import actions
from pygoap.actionstates import *

import pygame


class TimedAction(actions.CallableAction):

    def __init__(self, caller, duration, **kwargs):
        super(TimedAction, self).__init__(caller, **kwargs)
        self.time = 0
        self.duration = duration
        self.icon = res.loadTile("spellicons.png", (32,32), (6,10))
        self.icon = pygame.transform.scale(self.icon, (16,16))


    def update(self, time):
        super(HardenAction, self).update(time)
        self.time += time 
        if self.time >= duration:
            self.finish()


    def onFinish(self):
        print self, "finished"




# =====  ITEM: ANVIL  =========================================================

class HardenAction(TimedAction):
    icon = Image("anvil.png")

class hardenBuilder(actions.ActionBuilder):
    def get_actions(self, caller, bb):
        return [ self.build_action(caller) ]

    def build_action(self, caller):
        action = HardenAction(caller, 300)
        return action


harden = hardenBuilder()

def Anvil():
    anvilAnimation = animation.StaticAnimation("anvil.png", 'idle')
    anvilAvatar = avatar.Avatar([anvilAnimation])
    anvil = Entity(anvilAvatar, [harden], Image("anvil.png"))
    return anvil


# =============================================================================
# =====  ITEM: FURNACE  =======================================================

def Furnace():
    pass


# =============================================================================
