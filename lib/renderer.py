from lib2d.tilemap import BufferedTilemapRenderer
from lib2d.objects import AvatarObject, GameObject
from lib2d.ui import Element
from lib2d import vec

from pygame import Rect, draw
import weakref


def screenSorter(a):
    return a[-1].x


class AvatarLayer(GameObject):
    def __init__(self, area, extent):
        self.area = area


class LevelCamera(Element):
    """
    The level camera manages sprites on the screen and a tilemap renderer.


    'extent' expects the rect to be in surface coordinates of the map:
        x = horizontal
        y = vertical
        (0,0) is top left pixel

    it will be mangled some to use the 3d coordinate system of the engine
    """

    name = 'LevelCamera'

    def __init__(self, parent, area, extent):
        Element.__init__(self, parent)

        self.area = area
        self.set_extent(extent)

        # axis swap
        h, w = self.extent.size

        # create a renderer for the map
        self.maprender = BufferedTilemapRenderer(area.tmxdata, (w, h))
        self.maprender.center((w/2, h/2))

        # translate tiled map coordinates to world coordinates (swap x & y)
        self.map_height = area.tmxdata.tilewidth * area.tmxdata.width
        self.map_width = area.tmxdata.tileheight * area.tmxdata.height
        self.blank = True

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
        x, y, w, h = extent
        self.extent = Rect(y, x, h, w)

        self.half_width = self.extent.width / 2
        self.half_height = self.extent.height / 2
        self.width  = self.extent.width
        self.height = self.extent.height
        self.zoom = 1.0


    def center(self, (x, y, z)):
        """
        center the camera on a world location.
        expects to be in world coordinates (x & y axis swapped)
        """

        self.extent.center = (x, y)
        x += self.extent.left       #hack
        y += self.extent.top        #hack
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


    def draw(self, surface, rect):
        onScreen = []

        avatarobjects = self.refreshAvatarObjects()

        if self.blank:
            self.blank = False
            self.maprender.blank = True

        # quadtree collision testing would be good here
        for a in avatarobjects:
            bbox = self.area.getBBox(a)
            x, y, z, d, w, h = bbox
            pos = self.worldToSurface((x, y, z))
            onScreen.append((a.avatar.image, Rect(pos, (w, h)), 1, a, bbox))

        # should not be sorted every frame
        onScreen.sort(key=screenSorter)

        return self.maprender.draw(surface, rect, onScreen)


    def worldToSurface(self, (x, y, z)):
        """
        Translate world coordinates to coordinates on the surface
        underlying area is based on 'right handed' 3d coordinate system
        xy is horizontal plane, with x pointing toward observer
        z is the vertical plane
        """

        xx, yy = self.area.worldToPixel((x, y, z))
        return vec.Vec2d(xx - self.extent.top, yy - self.extent.left)


    def surfaceToWorld(self, (x, y)):
        """
        Transform surface coordinates to coordinates in the world
        surface coordinates take into account the camera's extent
        """

        return self.area.pixelToWorld((x+self.extent.top,y+self.extent.left))
