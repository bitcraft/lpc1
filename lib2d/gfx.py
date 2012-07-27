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

from vec import Vec2d

from pygame.transform import scale, scale2x
from pygame.display import flip
import pygame, os.path, pprint

"""
a few utilities for making retro looking games by scaling the screen
and providing a few functions for handling screen changes

"""

threaded = 0

DEBUG = False

def debug(text):
    if DEBUG: sys.stdout.write(text)


pixelize = None
pix_scale = 1
screen_dim = None
buffer_dim = None
screen = None
screen_surface = None
update_display = None
double_buffer = False
hwsurface = False
#surface_flags = pygame.FULLSCREEN
surface_flags = 0
#surface_flags = pygame.RESIZABLE


import threading
import Queue
class ScalingThread(threading.Thread):
    def __init__(self, func, arg):
        super(ScalingThread, self).__init__()
        self.func = func
        self.arg = arg
        self.trigger = False
        self.running = True

    def run(self):
        while self.running:
            while not self.trigger:
                pass
            self.func(self.arg)


def hardware_checks():
    """
    TODO: Do some tests to see if we can reliably use hardware sprites
    """
    pass


def init():
    global screen_dim

    # determine if we can use hardware accelerated surfaces or not
    pygame.display.set_caption("robots!")

# is it redundant to have a pygame buffer, and one for pixalization?  maybe...

def update_display_scaled2x(dirty):
    scale2x(screen, screen_surface)
    flip()

def update_display_scaled(dirty):
    scale(screen, screen_dim, screen_surface)
    flip()

def update_display_threaded(dirty):
    global thread
    thread.trigger = True

def set_screen(dim, scale=1, transform=None):

    global pixelize, pix_scale, buffer_dim, screen, update_display, screen_surface, screen_dim

    screen_dim = Vec2d(dim)

    if transform == "scale2x" or transform == "scale":
        set_scale(scale, transform)

    elif transform is None:
        pixelize = False
        pixel_buffer = None
        pix_scale = 1
        buffer_dim = None
        update_display = pygame.display.update
        screen_surface = pygame.display.set_mode(screen_dim, surface_flags)
        screen = screen_surface

def set_scale(scale, transform="scale"):
    from pygame.surface import Surface

    global pixelize, pix_scale, buffer_dim, screen, update_display, screen_surface, screen_dim, thread

    if transform == "scale2x":
        pix_scale = 2
        update_display = update_display_scaled2x
    elif transform == "scale":
        pix_scale = scale
        update_display = update_display_scaled


    if threaded:
        thread = ScalingThread(update_display, None)
        update_display = update_display_threaded
        thread.start()


    pixelize = True
    buffer_dim = tuple([ int(i / pix_scale) for i in screen_dim ])
    screen_surface = pygame.display.set_mode(screen_dim, surface_flags)
    screen = Surface(buffer_dim, surface_flags)
    #screen_surface = pygame.display.set_mode(screen_dim)


def get_rect():
    return pygame.Rect((0,0), buffer_dim)
