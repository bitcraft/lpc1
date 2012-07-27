import res
from pathfinding.astar import Node
from objects import GameObject
from quadtree import QuadTree, FrozenRect
from pygame import Rect
from bbox import BBox
from pathfinding import astar
from lib2d.signals import *
from vec import Vec2d, Vec3d
import math

cardinalDirs = {"north": math.pi*1.5, "east": 0.0, "south": math.pi/2, "west": math.pi}



def pathfind(self, start, destination):
    """Pathfinding for the world.  Destinations are 'snapped' to tiles.
    """

    def NodeFactory(pos):
        x, y = pos[:2]
        l = 0
        return Node((x, y))

        try:
            if self.tmxdata.getTileGID(x, y, l) == 0:
                node = Node((x, y))
            else:
                return None
        except:
            return None
        else:
            return node

    start = self.worldToTile(start)
    destination = self.worldToTile(destination)
    path = astar.search(start, destination, NodeFactory)
    return path


class PathfindingSentinel(object):
    """
    this object watches a body move and will adjust the movement as needed
    used to move a body when a path is set for it to move towards
    """

    def __init__(self, body, path):
        self.body = body
        self.path = path
        self.dx = 0
        self.dy = 0

    def update(self, time):
        if worldToTile(bbox.origin) = self.path[-1]:
            pos = path.pop()
            theta = math.atan2(self.destination[1], self.destination[0])
            self.destination = self.position + self.destination
            self.dx = self.speed * cos(theta)
            self.dy = self.speed * sin(theta) 

        self.area.movePosition(self.body, (seldf.dx, self.dy, 0))


class CollisionError(Exception):
    pass


class ExitTile(FrozenRect):
    def __init__(self, rect, exit):
        FrozenRect.__init__(self, rect)
        self._value = exit

    def __repr__(self):
        return "<ExitTile ({}, {}, {}, {}): {}>".format(
            self._left,
            self._top,
            self._width,
            self._height,
            self._value)


class Body(object):
    """
    hashable, immutable class to simulate simple physics
    """

    def __init__(self, bbox, acc, vel, o, parent=None):
        self.parent = parent
        self.bbox = bbox
        self.oldbbox = bbox
        self.acc = acc
        self.vel = vel
        self.o = o
        self._isFalling = False
        self._sleeping = False

    def __repr__(self):
        if self.parent:
            return "<Body: {}>".format(self.parent.name)
        else:
            return "<Body: {}>".format(self.parent)

    @property
    def gravity(self):
        return self.parent.gravity


    @property
    def pushable(self):
        try:
            return self.parent.pushable
        except AttributeError:
            return True


    @property
    def isFalling(self):
        return self._isFalling


    @isFalling.setter
    def isFalling(self, value):
        self._isFalling = value
        try:
            self.parent.isFalling = value
        except AttributeError:
            pass


class AbstractArea(GameObject):
    pass


class Sound(object):
    """
    Class that manages how sounds are played and emitted from the area
    """

    def __init__(self, filename, ttl):
        self.filename = filename
        self.ttl = ttl
        self._done = 0
        self.timer = 0

    def update(self, time):
        if self.timer >= self.ttl:
            self._done = 1
        else:
            self.timer += time

    @property
    def done(self):
        return self._done



class AdventureMixin(object):
    """
    Mixin class that contains methods to translate world coordinates to screen
    or surface coordinates.
    The methods will translate coordinates of the tiled map

    TODO: manipulate the tmx loader to swap the axis
    """

    def tileToWorld(self, (x, y, z)):
        xx = int(x) * self.tmxdata.tileheight
        yy = int(y) * self.tmxdata.tilewidth
        return xx, yy, z


    def pixelToWorld(self, (x, y)):
        return Vec3d(y, x, 0)


    def toRect(self, bbox):
        # return a rect that represents the object on the xy plane
        # currently this is used for geometry collision detection
        return Rect((bbox.x, bbox.y, bbox.depth, bbox.width))


    def worldToPixel(self, (x, y, z)):
        return Vec2d((y, x))


    def worldToTile(self, (x, y, z)):
        xx = int(x) / self.tmxdata.tilewidth
        yy = int(y) / self.tmxdata.tileheight
        zz = 0
        return xx, yy, zz


    """
    the underlying physics 'engine' is only capable of calculating
    physics on 2 axises.  so, we just calculate the xy plane and fake the z
    axis
    """
    def applyForce(self, body, (x, y, z)):
        body.acc += Vec2d(x, y)


    def updatePhysics(self, body, time):
        """
        basic physics
        """
     
        time = time / 100

        if body.gravity:
            body.acc += Vec2d((0, 9.8)) * time
    
        body.vel = body.acc * time
        y, z = body.vel

        if not y==0:
            self.movePosition(body, (0, y, 0))

        if z > 0: 
            falling = self.movePosition(body, (0, 0, z))
            if falling:
                body.isFalling = True
                self._grounded[body] = False
            else:
                if body.isFalling:
                    body.parent.fallDamage(body.vel.y)
                body.isFalling = False
                self._grounded[body] = True
                if int(body.vel.y) >= 1:
                    body.acc.y = -body.acc.y * .2
                else:
                    body.acc.y = 0
        elif z < 0:
            flying = self.movePosition(body, (0, 0, z))
            if flying:
                self._grounded[body] = False
                body.isFalling = True


    def setForce(self, body, (x, y, z)):
        body.acc = Vec2d(x, y)


class PlatformerMixin(object):
    """
    Mixin class is suitable for platform  games
    """

    def toRect(self, bbox):
        # return a rect that represents the object on the zy plane
        return Rect((bbox.y, bbox.z+bbox.height, bbox.width, bbox.height))


    """
    the underlying physics 'engine' is only capable of calculating 2 axises.
    for platform type games, we use the zy plane for calculations
    """
    def updatePhysics(self, body, time):
        """
        basic physics
        """
     
        time = time / 100

        body.vel = body.acc * time
        x, y = body.vel

        if not y==0 or x==0:
            self.movePosition(body, (x, y, 0))


    def grounded(self, body):
        try:
            return self._grounded[body]
        except:
            return False


    def applyForce(self, body, (x, y, z)):
        body.acc += Vec2d(y, z)



class Area(AbstractArea, AdventureMixin):
    """
    3D environment for things to live in.
    Includes basic pathfinding, collision detection, among other things.

    You will need to specify the appropriate 'mixin' class to get full features

    uses a quadtree for fast collision testing with level geometry.

    there are a few hacks to be aware of:
        bodies move in 3d space, but level geometry is 2d space
        when using pygame rects, the y value maps to the z value in the area

    a word on the coordinate system:
        coordinates are 'right handed'
        x axis moves toward viewer
        y axis move left right
        z axis is height

    NOTE: some of the code is specific for maps from the tmxloader
    """

    def defaultPosition(self):
        return BBox(0,0,0,1,1,1)

    def defaultSize(self):
        # TODO: this cannot be hardcoded!
        return (10, 8)


    def __init__(self):
        AbstractArea.__init__(self)
        self.geometry = {}
        self.bodies = {}
        self.joins = []
        self.sounds = []
        self.soundFiles = []
        self.inUpdate = False
        self._addQueue = []
        self._removeQueue = []
        self._addQueue = []

        import quadtree
        self.geometry[layer] = quadtree.FastQuadTree(rects)
        self.geoRect = rects

    @classmethod
    def load(self):
        import pytmx

        print "area load"

        self.tmxdata = pytmx.tmxloader.load_pygame(
                       self.mappath, force_colorkey=(128,128,0))

        return 

        # quadtree for handling collisions with exit tiles
        rects = []
        for guid, param in self.exits.items():
            try:
                x, y, l = param[0]
            except:
                continue

            rects.append(ExitTile((x,y,
                self.tmxdata.tilewidth, self.tmxdata.tileheight), guid))

        # get sounds from tiles
        for i, layer in enumerate(self.tmxdata.tilelayers):
            props = self.tmxdata.getTilePropertiesByLayer(i)
            for gid, tileProp in props:
                for key, value in tileProp.items():
                    if key[4:].lower() == "sound":
                        self.soundFiles.append(value)

        # get sounds from objects
        for i in [ i for i in self.getChildren() if i.sounds ]:
            self.soundFiles.extend(i.sounds)

        #self.exitQT = QuadTree(rects)

        return Area()


    def add(self, thing, pos=None):
        if pos is None:
            pos = self.defaultPosition().origin

        body = Body(BBox(pos, thing.size), Vec2d(0,0), Vec2d(0,0), 0.0, \
                    parent=thing)

        self.bodies[thing] = body
        AbstractArea.add(self, thing)
        self.changedAvatars = True


    def remove(self, thing):
        if self.inUpdate:
            self._removeQueue.append(thing)
            return

        AbstractArea.remove(self, thing)
        del self.bodies[thing]
        self.changedAvatars = True

        # hack
        try:
            self.drawables.remove(thing)
        except (ValueError, IndexError):
            pass


    def movePosition(self, body, (x, y, z), push=True, clip=True):

        """Attempt to move a body in 3d space.

        Args:
            body: (body): body to move
            (x, y, z): difference of position to move
        
        Kwargs:
            push: if True, then any colliding objects will be moved as well
            caller: part of callback for object that created request to move

        Returns:
            None

        Raises:
            CollisionError  


        This function will emit a bodyRelMove event if successful. 
        """

        if not isinstance(body, Body):
            raise ValueError, "must supply a body"

        movable = 0
        originalbbox = body.bbox
        newbbox = originalbbox.move(x, y, z)

        # collides with level geometry, cannot move
        #if self.testCollideGeometry(newbbox) and clip:
        #    return False

        # test for collisions with other bodies
        collide = self.testCollideObjects(newbbox)
        try:
            collide.remove(body)
        except:
            pass

        # find things we are joined to
        joins = [ i[1] for i in self.joins if i[0] == body ]

        # if joined, then add it to collisions and treat it is if being pushed
        if joins:
            collide.extend(b for b in joins if not b == body)
            push = True

        # handle collisions with bodies
        if collide:

            # are we pushing something?
            if push and all([ other.pushable for other in collide ]):

                # we are able to move
                body.oldbbox = body.bbox
                body.bbox = newbbox

                # recursively push other bodies
                for other in collide:
                    if not self.movePosition(other, (x, y, z), push=True):
                        # we collided, so just go back to old position
                        body.oldbbox = originalbbox
                        body.bbox = originalbbox
                        return False

            else:
                if clip: return False

        else:
            body.oldbbox = body.bbox
            body.bbox = newbbox


    def emitText(self, text, pos=None, thing=None):
        if pos==thing==None:
            raise ValueError, "emitText requires a position or thing"

        if thing:
            pos = self.bodies[thing].bbox.center
        emitText.send(sender=self, text=text, position=pos)
        self.messages.append(text)


    def emitSound(self, filename, pos=None, thing=None, ttl=350):
        if pos==thing==None:
            raise ValueError, "emitSound requires a position or thing"

        self.sounds = [ s for s in self.sounds if not s.done ]
        if filename not in [ s.filename for s in self.sounds ]:
            if thing:
                pos = self.bodies[thing].bbox.center
            emitSound.send(sender=self, filename=filename, position=pos)
            self.sounds.append(Sound(filename, ttl))


    def update(self, time):
        self.inUpdate = True
        self.time += time

        [ sound.update(time) for sound in self.sounds ]

        for thing, body in self.bodies.items():
            self.updatePhysics(body, time)
            thing.update(time)

        # awkward looping allowing objects to be added/removed during update
        self.inUpdate = False
        [ self.add(thing) for thing in self._addQueue ] 
        self._addQueue = []
        [ self.remove(thing) for thing in self._removeQueue ] 
        self._removeQueue = []


    def testCollideGeometry(self, bbox):
        """
        test if a bbox collides with the layer geometry
        uses a quadtree to test static geometry
        """

        layer = 0

        try:
            rect = self.toRect(bbox)
            hit = self.geometry[layer].hit(rect)
            con = self.extent.contains(rect)
            return bool(hit) or not bool(con)

        except KeyError:
            msg = "Area Layer {} does not have a collision layer"
            print msg.format(layer)
            return False

            raise Exception, msg.format(layer)


    def testCollideObjects(self, bbox, skip=[]):
        """
        this could be optimized to use a quadtree,  spatial hash, etc
        """

        bboxes = []
        bodies = []

        for body in self.bodies.values():
            if not body in skip:
                bboxes.append(body.bbox)
                bodies.append(body)

        return [ bodies[i] for i in bbox.collidelistall(bboxes) ]


    def _sendBodyMove(self, body, caller, force=None):
        position = body.bbox.origin
        bodyAbsMove.send(sender=self, body=body, position=position, caller=caller, force=force)

    
    #  CLIENT API  --------------

    def join(self, body0, body1):
        self.joins.append((body0, body1))


    def unjoin(self, body0, body1):
        self.joins.remove((body0, body1))


    def getBody(self, thing):
        return self.bodies[thing]

