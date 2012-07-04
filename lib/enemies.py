from lib2d.objects import AvatarObject, GameObject
from lib2d.avatar import Animation, Avatar
from lib2d import res
from random import randint, choice

import gc



laserFlavour = \
"""You've been lasered.  Maybe you can duck it?
That's one heck of a hair cut!
My eyes!!!
Duck and cover!
Pew! Pew! Pew!
If only you could avoid the laser...""".split("\n")


bossFlavour = \
"""You choke on the bullets in the back of your throat.
As you die, you take "be shot" off your mental bucket list.
Bullets tear through your flesh.
Hot bullets tear through your entire body.
Should have brought the bullet proof vest.
You feel one thousand bullets tear through your body.""".split("\n")


class Laser(GameObject):
    def __init__(self):
        GameObject.__init__(self)
        self.ttl = 60
        self.time = 0

    def update(self, time):
        self.time += time
        if self.time >= self.ttl:
            self.destroy()
        self.parent.flash(self.parent.getBody(self).bbox.center)


class LaserRobot(AvatarObject):
    sounds = ["ex0.wav", "warn.wav", "select1.wav", "powerdown.wav"]

    def __init__(self):
        AvatarObject.__init__(self)
        self.rate = 4000
        self.time = 0
        self.warned = False
        self.pushable = True
        self.activated = False
        self.dying = False


    def activate(self):
        self.activated = True
        self.parent.emitSound("select1.wav", thing=self)


    def update(self, time):
        #if self.isFalling and self.isAlive and not self.dying:
        #    self.die()

        #if not self.isAlive:
        #    self.destroy()

        if not self.activated: return

        self.time += time
        if self.time >= self.rate:
            self.time -= self.rate
            if self.warned:
                self.warned = False
                self.shoot()
            else:
                self.warned = True
                self.warn()


    def die2():
        body0 = self.parent.getBody(self)
        body1 = self.parent.getBody(self.bolt)
        self.parent.unjoin(body0, body1)
        self.isAlive = False


    def die(self):
        self.bolt = AvatarObject()
        self.bolt.name = "self.bolt"
        avatar = Avatar()
        ani = Animation("electrify.png", "electrify", 2, 1, 50)
        avatar.add(ani)
        avatar.play("electrify", loop=6, callback=self.die2)
        self.bolt.setAvatar(avatar)
        self.parent.add(self.bolt)
        body0 = self.parent.getBody(self)
        body1 = self.parent.getBody(self.bolt)
        x, y, z, d, w, h = body0.bbox
        self.parent.setBBox(self.bolt, (x, y, z, 1, w, h))
        self.parent.join(body0, body1)
        ani.load()
        self.dying = True
        self.parent.emitSound("powerdown.wav", thing=self)


    def warn(self):
        self.avatar.play("warn", loop=4)
        self.parent.emitSound("warn.wav", thing=self)


    def shoot(self):
        boss = [ i for i in self.parent.getChildren() if isinstance(i, Boss) ]
        hero = self.parent.getChildByGUID(1)
        bbox = self.parent.getBody(self).bbox.inflate(0,128,0)

        if boss:
            boss = boss.pop()
            if bbox.collidebbox(self.parent.getBody(boss).bbox):
                boss.hit()

        laser = Laser()
        self.parent.add(laser, bbox.center)
        if bbox.collidebbox(self.parent.getBody(hero).bbox):
            if not hero.avatar.isPlaying("crouch") and hero.isAlive:
                self.parent.emitText(choice(laserFlavour), thing=self)
                hero.die()

        self.parent.emitSound("ex0.wav", thing=self)
        self.avatar.play("shoot", loop=0)


class Boss(AvatarObject):
    sounds = ["crash1.wav"]
    

    def __init__(self):
        AvatarObject.__init__(self)
        self.rate = 1000
        self.time = 0
        self.pushable = False
        self.dying = False
        self.dead = False


    def update(self, time):
        if self.isAlive or self.dying:
            self.time += time

        if self.isAlive:
            if self.time >= self.rate:
                self.time -= self.rate
                self.shoot()

        elif self.dying and not self.dead:
            if self.time >= 140:
                self.die()
                self.dead = True


    def die2(self):
        self.avatar.play("dead") 
        body = self.parent.getBody(self)
        body.bbox = body.bbox.move(0,0, -32)


    def die(self):
        self.avatar.play("dying", loop=0, callback=self.die2)


    def hit(self):
        hero = self.parent.getChildByGUID(1)
        self.parent.emitSound("crash1.wav", thing=self)
        self.parent.emitText("Blinded, the boss keels over, muttering something, and dies.", thing=self)
        self.parent.emitText("A green key drops on the ground and you pick it up.", thing=self)
        for i in self.inventory:
            self.removeThing(i)
            hero.addThing(i)
        self.isAlive = False
        self.dying = True
        self.time = 0


    def shoot(self):
        robots = [ self.parent.getBody(i).bbox for i in self.parent.getChildren() if isinstance(i, LaserRobot) ]
        hero = self.parent.getChildByGUID(1)
        bbox = self.parent.getBody(self).bbox.inflate(0,320,0)
        if bbox.collidebbox(self.parent.getBody(hero).bbox):
            if any([ bbox.collidebbox(i) for i in robots ]):
                self.parent.emitText("Bullets smash into the robot, but are bounced off and scattered all over the room.", thing=self)

            elif hero.isAlive:
                self.parent.emitText(choice(bossFlavour), thing=self)
                hero.die()

        self.avatar.play("shoot", loop=0)
        self.parent.emitSound("crash1.wav", thing=self)
