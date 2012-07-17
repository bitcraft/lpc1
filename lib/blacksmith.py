from lib2d.objects import AvatarObject
from lib2d import avatar, animation, res

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


class HardenAction(TimedAction):
    icon_name = "anvil.png"


class hardenBuilder(actions.ActionBuilder):
    def get_actions(self, caller, bb):
        return [ self.build_action(caller) ]

    def build_action(self, caller):
        action = HardenAction(caller, 300)
        return action

harden = hardenBuilder()



class InteractiveObject(AvatarObject):
    """
    these objects supply a list of actions that other objects can call
    """

    def __init__(self, avatar, builders):
        AvatarObject.__init__(self, avatar)
        self.actionBuilders = builders


    def queryActions(self, caller):
        actions = []
        for builder in self.actionBuilders:
            actions.extend(builder.get_actions(caller, None))
        return actions


def Anvil():
    anvilAnimation = animation.StaticAnimation("anvil.png", 'idle')
    anvilAvatar = avatar.Avatar([anvilAnimation])
    anvil = InteractiveObject(anvilAvatar, [harden])
    return anvil


