from lib2d.objects import AvatarObject
from lib.misc import *



fallFlavour = \
"""You leapt before you looked.
You forgot how to levitate.
You left your wings back at base.
The results are in: gravity still exists.
The ground came at you a little to quickly.""".split("\n")



class Hero(AvatarObject):
    def __init__(self):
        AvatarObject.__init__(self)
        self.gravity = True
        self.pushable = True
        self.held = None
        self.hasPassword = False


    def die(self):
        self.parent.emitText("You are dead.", thing=self)
        self.avatar.play("die", loop_frame=2)
        self.isAlive = False
        body = self.parent.getBody(self)
        body.acc.x = 0


    def fallDamage(self, dmg):
        if dmg > 1.5:
            self.parent.emitText(choice(fallFlavour), thing=self)
            self.die()
