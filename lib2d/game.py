#!/usr/bin/env python

from lib2d import res
import pygame

from lib2d.statedriver import StateDriver
from lib2d import gfx, config


class Game(object):
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        gfx.init()
        self.sd = StateDriver(self)

    def get_screen(self):
        return gfx.screen

    def start(self):
        pass


