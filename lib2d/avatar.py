"""
Copyright 2010, 2011  Leif Theden


This file is part of lib2d.

lib2d is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

lib2d is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with lib2d.  If not, see <http://www.gnu.org/licenses/>.
"""


from objects import GameObject
import res, animation

import pygame
import sys
from math import pi, radians, ceil
from itertools import product
from random import randint

from pygame.transform import flip

import time




class Avatar(GameObject):
    """
    Avatar is a sprite-like class that supports multiple animations, animation
    controls, directions, is pickleable, and doesn't require images to be
    loaded.

    update must be called occasionally for animations and rotations to work.
    """

    time_update = True

    def __init__(self, animations):
        GameObject.__init__(self)
        self.default      = None
        self.callback     = None    # called when animation finishes
        self.curImage     = None    # cached for drawing ops
        self.curFrame     = None    # current frame number
        self.curAnimation = None
        self.animations   = {}
        self.loop_frame = 0
        self.looped     = 0
        self.loop       = -1
        self.timer      = 0.0
        self.flip       = 0
        self.ttl = 0
        self._prevAngle = None
        self._rect = None

        for animation in animations:
            self.add(animation)
            self.animations[animation.name] = animation

        self.setDefault(animations[0])
        self.play()

    def _updateCache(self):
        angle = self.getOrientation()

        self.curImage = self.curAnimation.getImage(self.curFrame, angle) 
        self._rect = self.curImage.get_rect()
        if self.flip: self.curImage = flip(self.curImage, 1, 0)


    def get_rect(self):
        self._updateCache()
        return self._rect


    def get_size(self):
        self._updateCache()
        return self._rect.get_size()



    def draw(self, surface, rect):
        surface.blit(self.image, rect.topleft)


    @property
    def rect(self):
        self._updateCache()
        return self._rect


    @property
    def image(self):
        self._updateCache()
        return self.curImage


    @property
    def state(self):
        return (self.curAnimation, self.curFrame)


    def unload(self):
        self.curImage = None


    def update(self, time):
        """
        call this as often as possible with a time.  the units in the
        animation files must match the units provided here.  ie: milliseconds.
        """

        self.timer += time

        while (self.timer >= self.ttl):
            if self.ttl < 0:
                self.paused = 1
                return

            self.timer -= self.ttl

            self.ttl, self.curFrame = self.curAnimation.advance()

            
    def stop(self):
        """
        pauses the current animation and runs the callback if needed.
        """

        self.reset()
        self.doCallback()


    def doCallback(self):
        if self.callback:
            self.callback[0](*self.callback[1])


    def reset(self):
        """
        sets defaults of the avatar.
        """

        if len(self.animations) == 0:
            return 
        self.play(self.default)


    def isPlaying(self, name):
        if isinstance(name, animation.Animation):
            if name == self.curAnimation: return True
        else:
            if self.getAnimation(name) == self.curAnimation: return True
        return False


    def play(self, name=None, start_frame=0, loop=-1, loop_frame=0, \
             callback=None, arg=[]):

        if isinstance(name, animation.Animation):
            if name == self.curAnimation: return
            self.curAnimation = name
        elif name is None:
            name = self.default
        else:
            temp = self.getAnimation(name)
            if temp == self.curAnimation: return
            self.curAnimation = temp

        self.loop = loop
        self.loop_frame = loop_frame
        self.paused = False
        self.timer  = 0
        self.looped = 0

        if callback:
            self.callback = (callback, arg)

        self.setFrame(start_frame)


    def remove(self, other):
        playing = False
        if isinstance(other, (animation.Animation, animation.StaticAnimation)):
            if self.isPlaying(other):
                playing = True
            del self.animations[other.name]
        
        GameObject.remove(self, other)

        # handle when there are no animations left
        if len(self.animations) == 0:
            self.callback = None
            self.curAnimation = None
            self.curImage = None
            self.curFrame = None
            self.default = None
            self._is_paused = True
        elif playing:
            self.setDefault(self.animations.keys()[0])
            self.reset()


    def getAnimation(self, name):
        """
        return the animation for this name.
        """

        try:
            return self.animations[name]
        except:
            raise


    def setDefault(self, name):
        """
        set the defualt animation to play if the avatar has nothing else to do
        """

        if isinstance(name, (animation.Animation, animation.StaticAnimation)):
            self.default = name
        else:
            try:
                self.default = self.getAnimation(name)
            except KeyError:
                return


    def __str__(self):
        return "<Avatar %s>" % id(self)



