from lib2d.objects import InteractiveObject, GameObject
from lib2d.avatar import Animation
from lib2d import res
from random import randint, choice

from lib.enemies import *


text = {}
text['take'] = "You take a {} from {}."
text['useKey'] = "You use the {} on the door."
text['locked'] = "This door requires {}."
text['blocked'] = "You attempt to close the door, but you are in the doorway and it refuses to shut"
text['difused'] = "You frantically enter the password.  Bomb is difused, now run!"


termMootFlavour = \
"""You press a few blinking buttons, but nothing seems to happen.
Click, click, click.  Nothing.
Is this thing even working?
Hitting keys at random has caused nothing to happen.
As you watch the terminal, you wish you were somewhere else.""".split("\n")


liftKillFlavour = \
"""Wow, they should install a guard or something...
The lift smashes you into the floor.
Watch your head!  The lift crashes into your head, killing you instantly.""".split("\n")


class InventoryObject(InteractiveObject):
    """
    holds stuff
    """

    def use(self, user):
        for i in self.inventory:
            user.parent.emitText(text['take'].format(i.name, self.name), thing=self)
            self.removeThing(i)
            user.addThing(i)


class Lift(InteractiveObject):
    sounds = ["lift.wav"]
    gravity = False

    def __init__(self):
        InteractiveObject.__init__(self)
        self.direction = 0
        self.caller = None
        self.destination = None


    def animate(self):
        self.avatar.play("glow", loop=1)
        self.parent.emitSound("lift.wav", ttl=1000, thing=self) 


    def update(self, time):
        body = self.parent.getBody(self)
        if self.destination:
            self.parent.movePosition(body, (0,0,self.direction), clip=False)
            self.animate()
            bottom = int(body.bbox.bottom)
            if bottom == self.destination:
                d = self.destination - body.bbox.bottom
                self.parent.movePosition(body, (0,0,d))
                self.cancelCall()

            hero = self.parent.getChildByGUID(1)
            if self.direction == 1 and hero.isAlive:
                hero_body = hero.parent.getBody(hero)
                if body.bbox.move(0,0,16).collidebbox(hero_body.bbox):
                    self.parent.emitText(choice(liftKillFlavour), thing=self)
                    hero.die()


    def cancelCall(self):
        if self.caller: 
            self.caller.off()

        self.destination = None
        self.caller = None
        self.direction = None


    def call(self, dest, caller=None):
        bbox = self.parent.getBody(self).bbox
        if dest > bbox.bottom:
            self.caller = caller
            self.destination = int(dest)
            self.direction = 1
        elif dest < bbox.bottom:
            self.caller = caller
            self.destination = int(dest)
            self.direction = -1
        elif caller:
            caller.off() 


class BrokenLift(Lift):
    def update(self, time):
        Lift.update(self, time)
        body = self.parent.getBody(self)
        if body.bbox.top <= 25 and not self.gravity:
            self.parent.emitSound("crash1.wav", thing=self)
            self.parent.emitText("Looks like the lift is broken...", thing=self)
            self.parent.emitText("Well that was fun.", thing=self)
            self.parent.emitText("Game Over", thing=self)
            self.cancelCall()
            self.gravity = True


class Callbutton(InteractiveObject):
    sounds = ['pushbutton.wav']
    gravity = False
    resetDelay = 300

    def __init__(self):
        InteractiveObject.__init__(self)
        self.state = 0
        self.time = 0


    def use(self, user=None):
        self.on()
        body = self.parent.getBody(self)
        lift = self.parent.getChildByGUID(self.liftGUID) 
        lift.call(body.bbox.top, caller=self)


    def update(self, time):
        if not self.state == 2: return

        self.time += time
        if self.time >= self.resetDelay:
            self.forceOff()
            self.time = 0


    def forceOff(self):
        self.avatar.play("off")
        self.state = 0


    def off(self):
        self.state = 2


    def on(self):
        self.state = 1
        self.parent.emitSound("pushbutton.wav", thing=self)
        self.avatar.play("on")


class Key(InteractiveObject):
    pass


class Terminal(InteractiveObject):
    sounds = ['terminal.wav']
    gravity = False
    activated = False


    def use(self, user=None):
        self.animate()

    def animate(self):
        self.avatar.play('glow', loop=2)
        self.parent.emitSound("terminal.wav", thing=self)


class WakeTerminal(Terminal):
    def use(self, user):
        area = user.parent
        if self.activated:
            area.emitText("Your face is still throbbing from when you last hit the terminal with it.", thing=self)

        else:
            self.activated = True
            bots = [ i for i in self.parent.getChildren() if isinstance(i, LaserRobot) ]
            for bot in bots:
                bot.activate()
            area.emitText("Surprisingly, hitting your face against the keypad seemed to do something.", thing=self)

        self.animate()


class DeadTerminal(Terminal):
    def use(self, user):
        area = user.parent
        area.emitText(choice(termMootFlavour), thing=self)
        self.animate()


class BombTerminal(Terminal):
    sounds = ['ex1.wav']

    def use(self, user):
        area = user.parent
        area.emitText("Looks like they crossed the wires somewhere...", thing=self)
        self.animate()
        hero = self.parent.getChildByGUID(1)
        hero.die()
        hero.parent.flash(hero.parent.getBody(hero).bbox.center)
        self.parent.emitSound("ex1.wav", thing=self)


class PasswordTerminal(Terminal):
    def use(self, user):
        area = user.parent
        self.animate()
        area.emitText("Oh, so 'knockers' is the password", thing=self)
        hero = self.parent.getChildByGUID(1)
        hero.hasPassword = True


class DefuseTerminal(Terminal):
    def use(self, user):
        area = user.parent
        self.animate()
        hero = self.parent.getChildByGUID(1)
        if self.activated:
            area.emitText(choice(termMootFlavour), thing=self)
        else:
            self.activated = True
            if hero.hasPassword:
                area.emitText(text['difused'], thing=self)
                [ setattr(i, "isAlive", False) for i in self.parent.getChildren() if isinstance(i, Bomb) ]
            else:
                area.emitText("WHAT?  IT NEEDS A PASSWORD!?!", thing=self)
 

class Door(InteractiveObject):
    sounds = ['door-open.wav', 'door-close.wav']
    pushable = False


    def __init__(self):
        InteractiveObject.__init__(self)
        self.state = 0
        self.key = None


    def use(self, user=None):
        if self.key and user:
            if self.key in [ i for i in user.getChildren() ]:
                self.parent.emitText(text['useKey'].format(self.key.name), thing=self)
                self.toggle(user)
            else:
                self.parent.emitText(text['locked'].format(self.key.name), thing=self)
        else:
            self.toggle()


    def toggle(self, user=None):
        if self.state:
            if user:
                body0 = self.parent.getBody(self)
                body1 = self.parent.getBody(user)
                if (body0 in self.parent.testCollideObjects(body1.bbox.inflate(64,0,0))):
                    self.parent.emitText(text['blocked'], thing = self)
                else:
                    self.off()
            else:
                self.off()
        else:
            self.on()


    def forceOff(self):
        self.avatar.play("closed")
        self.state = 0
        body = self.parent.getBody(self)
        body.bbox = body.bbox.move(16,0,0)


    def forceOn(self):
        self.avatar.play("opened")
        self.state = 3
        body = self.parent.getBody(self)
        body.bbox = body.bbox.move(-16,0,0)


    def off(self):
        self.parent.emitSound("door-close.wav", thing=self)
        self.avatar.play("closing", loop=0, callback=self.forceOff)
        self.state = 2


    def on(self):
        self.parent.emitSound("door-open.wav", thing=self)
        self.avatar.play("opening", loop=0, callback=self.forceOn)
        self.state = 1


class Bomb(GameObject):
    size = (16, 16, 16)
    gravity = False

    def __init__(self):
        GameObject.__init__(self)
        self.time = 300000
        self.warned = 0
        self.isAlive = True

    # GIANT MACRO HACK
    def update(self, time):
        if not self.isAlive: return
        hero = self.parent.getChildByGUID(1)

        if self.time < 0:
            self.parent.emitText("The bomb explodes, filling every room with poison gas.", thing=hero)
            self.parent.flash(hero.parent.getBody(hero).bbox.center)
            hero.die()
            self.isAlive = False
        elif self.time < 1000 and not self.warned==1000:
            self.warned = 1000
            self.parent.emitText("Only 1 second left until the bomb goes off!", thing=hero)
        elif self.time < 2000 and not self.warned==2000:
            self.warned = 2000
            self.parent.emitText("Only 2 seconds left until the bomb goes off!", thing=hero)
        elif self.time < 3000 and not self.warned==3000:
            self.warned = 3000
            self.parent.emitText("Only 3 seconds left until the bomb goes off!", thing=hero)
        elif self.time < 4000 and not self.warned==4000:
            self.warned = 4000
            self.parent.emitText("Only 4 seconds left until the bomb goes off!", thing=hero)
        elif self.time < 5000 and not self.warned==5000:
            self.warned = 5000
            self.parent.emitText("Only 5 seconds left until the bomb goes off!", thing=hero)
        elif self.time < 6000 and not self.warned==6000:
            self.warned = 6000
            self.parent.emitText("Only 6 seconds left until the bomb goes off!", thing=hero)
        elif self.time < 7000 and not self.warned==7000:
            self.warned = 7000
            self.parent.emitText("Only 7 seconds left until the bomb goes off!", thing=hero)
        elif self.time < 8000 and not self.warned==8000:
            self.warned = 8000
            self.parent.emitText("Only 8 seconds left until the bomb goes off!", thing=hero)
        elif self.time < 9000 and not self.warned==9000:
            self.warned = 9000
            self.parent.emitText("Only 9 seconds left until the bomb goes off!", thing=hero)
        elif self.time < 10000 and not self.warned==10000:
            self.warned = 10000
            self.parent.emitText("Only 10 seconds left until the bomb goes off!", thing=hero)
            self.parent.emitText("You are going to have to hurry!", thing=hero)
        elif self.time < 15000 and not self.warned==15000:
            self.warned = 15000
            self.parent.emitText("Only 15 seconds left until the bomb goes off!", thing=hero)
            self.parent.emitText("You are going to have to hurry!", thing=hero)
        elif self.time < 30000 and not self.warned==30000:
            self.warned = 30000
            self.parent.emitText("Only 30 seconds left until the bomb goes off!", thing=hero)
            self.parent.emitText("You are going to have to hurry!", thing=hero)
        elif self.time < 45000 and not self.warned==45000:
            self.warned = 45000
            self.parent.emitText("Only 45 seconds left until the bomb goes off!", thing=hero)
            self.parent.emitText("You are going to have to hurry!", thing=hero)
        elif self.time < 60000 and not self.warned==60000:
            self.warned = 60000
            self.parent.emitText("Only 1 minutes left until the bomb goes off!", thing=hero)
            self.parent.emitText("You are going to have to hurry!", thing=hero)
        elif self.time < 120000 and not self.warned==120000:
            self.warned = 120000
            self.parent.emitText("Only 2 minutes left until the bomb goes off!", thing=hero)
            self.parent.emitText("You are going to have to hurry!", thing=hero)
        elif self.time < 180000 and not self.warned==180000:
            self.warned = 180000
            self.parent.emitText("Only 3 minutes left until the bomb goes off!", thing=hero)
            self.parent.emitText("You start to feel nervous...", thing=hero)
        elif self.time < 240000 and not self.warned==240000:
            self.warned = 240000
            self.parent.emitText("Only 4 minutes left until the bomb goes off!", thing=hero)
            self.parent.emitText("Better hurry!", thing=hero)
        elif self.time >= 300000 and not self.warned==300000:
            self.warned = 300000
            self.parent.emitText("Only 5 minutes left until the bomb goes off!", thing=hero)

        self.time -= time
