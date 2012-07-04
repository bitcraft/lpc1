from lib2d.area import AbstractArea, Area
from lib2d.buildarea import fromTMX
from lib2d.avatar import Avatar, Animation, StaticAnimation
from lib2d.objects import AvatarObject
from lib.hero import Hero
from lib.level import Level
from lib.enemies import *
from lib.misc import *
from lib2d import res

from collections import defaultdict, deque
from pygame import Rect
from itertools import product
import random
import os


world_size = (256, 256)
region_size = (16, 16)


def generateWorld():
    import array

    rect = Rect((0,0), world_size)

    regions = [rect]

    i = 320
    bag = [True, False] * (i/2)

    max_depth = 8
    depth = 0

    while depth < max_depth:
        queue = deque(regions)
        regions = []
        depth += 1

        while bag and queue:
            #random.shuffle(bag)
            rect = queue.pop()
            split = bag.pop()
            w,h = rect.size

            if rect.height > 0:
                r = float(rect.width) / rect.height
                if r < .5:
                    split = False
                elif r > 1.5:
                    split = True

            # True is a horizontal split
            if split:
                d = random.randint(-rect.width/8, rect.width/8)
                w = rect.width/2 + d
                a = Rect(rect.left, rect.top, w, rect.height)
                b = Rect(rect.left + w, rect.top, rect.width - w, rect.height)
            else:
                d = random.randint(-rect.height/8, rect.height/8)
                h = rect.height/2 + d
                a = Rect(rect.left, rect.top, rect.width, h)
                b = Rect(rect.left, rect.top + h, rect.width, rect.height - h)

            regions.append(a)
            regions.append(b)

    # make a 2d array suitable to inject into a a TMX class
    data = [ array.array("B") for i in xrange(self.height) ]

    gid = 0

    # fill the regions
    for rect in regions:
        gid += 1
        rows = xrange(rect.top, rect.bottom)
        cols = xrange(rect.left, rect.right)
        for p in product(rows, cols):
            data[y][x] = gid


def build():

    # build the initial environment
    uni = Area()
    uni.name = 'universe'
    uni.setGUID(0)


    # some characters
    avatar = Avatar()
    ani = Animation("warrior-male-stand.png", "stand", 1, 4)
    avatar.add(ani)
    ani = Animation("warrior-male-walk.png", "walk", [0,1,2,1], 4)
    avatar.add(ani)
    ani = Animation("warrior-male-attack.png", "attack", 4, 4, 60)
    avatar.add(ani)
    avatar.play("walk")
    npc = Hero()
    npc.setName("Rat")
    npc.setAvatar(avatar)
    npc.setGUID(1)
    npc.size = (16,16,18)
    uni.add(npc)


    # levels
    #level = fromTMX(uni, "level1.tmx")
    #level.setName("Level 1")
    #level.setGUID(5001)

    level = Area()
    level.setGUID(5001)
    uni.add(level)


    level.add(npc)

    return uni
