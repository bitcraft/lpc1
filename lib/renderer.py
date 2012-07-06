from lib2d.tilemap import BufferedTilemapRenderer
from lib2d.objects import AvatarObject
from pygame import Rect, draw

import weakref


def screenSorter(a):
    return a[-1].x


class LevelCamera(object):
    """
    The level camera manages sprites on the screen and a tilemap renderer.
    When creating a level camera, you must pass a rect that defiens the area
    of the surface/screen that is is drawing to.  Various values are cached to
    give a modest speed improvement, so this is a hard limitation.
    """

    def __init__(self, area, rect):
        rect = Rect(rect)
        self.rect = rect    # area of screen it occupies
        self.area = area    # area of the map to be viewed
        self.set_extent(rect)

        # create a renderer for the map
        self.maprender = BufferedTilemapRenderer(area.tmxdata, rect.size)

        # translate tiled map coordinates to world coordinates (swap x & y)
        self.map_height = area.tmxdata.tilewidth * area.tmxdata.width
        self.map_width = area.tmxdata.tileheight * area.tmxdata.height
        self.blank = True

        # add the avatars
        #for child in self.area.getChildren():
        ##    if isinstance(child, AvatarObject):
        #        child.avatar.update(0)              # hack to re-init avatar

        self.ao = self.refreshAvatarObjects()
 

    def refreshAvatarObjects(self):
        return [ i for i in self.area.bodies.keys() if hasattr(i, "avatar")]
        

    # HACK
    def getAvatarObjects(self):
        if self.area.changedAvatars:
            self.area.changedAvatars = False
            self.ao = self.refreshAvatarObjects()
        return self.ao


    def set_extent(self, extent):
        """
        the camera caches some values related to the extent, so it becomes
        nessessary to call this instead of setting the extent directly.
        """

        # our game world swaps the x and y axis, so we translate it here
        x, y, w, h = Rect(extent)
        self.extent = Rect(0, 0, h, w)

        self.half_width = self.extent.width / 2
        self.half_height = self.extent.height / 2
        self.width  = self.extent.width
        self.height = self.extent.height
        self.zoom = 1.0


    def update(self, time):
        self.maprender.update(None)
        for ao in self.refreshAvatarObjects():
            if ao: 
                # HACK
                try:
                   ao.avatar.update(time)
                except:
                    pass


    def center(self, (x, y, z)):
        """
        center the camera on a world location.
        expects to be in world coordinates (x & y axis swapped)
        """

        self.extent.center = (x, y)
        self.maprender.center(self.worldToSurface((x,y,z)))

        return



        if self.map_height > self.height:
            if x < self.half_height:
                x = self.half_height

            elif x > self.map_height - self.half_height:
                x = self.map_height - self.half_height
        else:
            x = self.map_height / 2

        if self.map_width > self.width:
            if y < self.half_width:
                y = self.half_width

            elif y > self.map_width - self.half_width - 1:
                y = self.map_width - self.half_width - 1

        else:
            y = self.map_width / 2




    def clear(self, surface):
        raise NotImplementedError


    def draw(self, surface):
        avatarobjects = self.refreshAvatarObjects()

        onScreen = []

        if self.blank:
            self.blank = False
            self.maprender.blank = True

        self.maprender.redraw()

        # quadtree collision testing would be good here
        for a in avatarobjects:
            bbox = self.area.getBBox(a)
            x, y, z, d, w, h = bbox
            x, y = self.worldToSurface((x, y, z))
            xx, yy = a.avatar.axis
            x += xx
            y += yy
            if self.extent.colliderect((x, y, w, h)):
                onScreen.append((a.avatar.image, Rect(self.worldToScreen((x, y)), (w, h)), 1, a, bbox))

        # should not be sorted every frame
        onScreen.sort(key=screenSorter)

        return self.maprender.draw(surface, self.rect, onScreen)

        dirty = self.maprender.draw(surface, self.rect, onScreen)

        clip = surface.get_clip()
        surface.set_clip(self.rect)

        #for (x, y, w, h) in self.area.geoRect:
        #    draw.rect(surface, (128,128,255), \
        #    (self.toScreen(self.worldToSurface((0, x, y))), (w, h)), 1)

        for i, r, l, a, b in onScreen:
            x, y, z, d, w, h, = b
            x, y = self.toScreen(self.worldToSurface((x, y, z+h)))
            draw.rect(surface, (255,128,128), (x, y, w, h), 1)

        surface.set_clip(clip)
        return dirty


    def worldToScreen(self, (x, y)):
        """
        Transform the world to coordinates on the screen
        """

        return (x - self.extent.left + self.rect.left,
                y - self.extent.top + self.rect.top)


    def worldToSurface(self, (x, y, z)):
        """
        Translate world coordinates to coordinates on the surface
        underlying area is based on 'right handed' 3d coordinate system
        xy is horizontal plane, with x pointing toward observer
        z is the vertical plane
        """


        return self.area.worldToPixel((x, y, z))


    def surfaceToWorld(self, (x, y)):
        """
        Transform surface coordinates to coordinates in the world
        surface coordinates take into account the camera's extent
        """

        return self.area.pixelToWorld((x+self.extent.top,y+self.extent.left))
