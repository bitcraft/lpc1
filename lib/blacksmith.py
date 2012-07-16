from lib2d.objects import AvatarObject
from lib2d import avatar, animation

# pygoap already has a nice action/object class
from pygoap import actions
from pygoap.actionstates import *



class InteractiveObject(AvatarObject):
    def queryActions(self, other):
        return self.actions


class Action(object):
    pass


class TimerObject(object):
    pass



def Anvil():
    anvilAnimation = animation.StaticAnimation("anvil.png", 'idle')
    anvilAvatar = avatar.Avatar([anvilAnimation])
    anvil = InteractiveObject(anvilAvatar)
    return anvil


