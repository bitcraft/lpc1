from pytmx import tmxloader, buildDistributionRects
from lib2d.area import Area
from lib2d.bbox import BBox
from lib2d import res
from pygame import Rect

from lib.misc import *


def fromTMX(parent, mapname):
    """Create a new area from a tmx map

    This body (called parent) must already be connected to the data tree,
    otherwise body loading will not work and area building will fail.
    """

    # for platformer maps
    def toWorld(data, (x, y, z)):
        """ translate tiled map coordinates to world coordinates """
        return z, x*data.tileheight, (y-2)*data.tilewidth


    area = Area()
    parent.add(area)
    area.setParent(parent)
    area.mappath = res.mapPath(mapname)
    data = tmxloader.load_tmx(area.mappath)


    for gid, prop in data.tile_properties.items():
        try:
            prop['guid'] = int(prop['guid'])
        except KeyError:
            pass

    # set the boundries (extent) of this map
    area.setExtent(((0,0),
        (data.width * data.tilewidth, data.height * data.tileheight)))

    props = data.getTilePropertiesByLayer(-1)

    """
    print "GID MAP:"
    for k in sorted(data.gidmap.keys()):
        print "  {}: {}\t{}".format(k,
                                    data.gidmap[k],
                                    data.getTilePropertiesByGID(data.gidmap[k]))
    """

    # load the level geometry from the 'control' layer 
    rects = []
    for rect in buildDistributionRects(data, "Control", real_gid=1):
        # translate the tiled coordinates to world coordinates
        # for platformers
        x, y, sx, sy = rect
        rects.append(Rect(x,y,sx,sy))
    area.setLayerGeometry(0, rects)


    # load the npc's and place them in the default positions 
    npcs = [ p for p in props if p[1].get('group', None) == 'npc' ] 

    for (gid, prop) in npcs:
        pos = data.getTileLocation(gid)
        if len(pos) > 1:
            msg = "control gid: {} is used in more than one locaton"
            raise Exception, msg.format(gid)

        x, y, z = toWorld(data, pos.pop())
        body = area._parent.getChildByGUID(int(prop['guid']))
        area.add(body, (0, y, z))
        area.setOrientation(body, "south")


    # load the items and place them where they should go
    # items can have duplicate entries
    items = [ p for p in props if p[1].get('group', None) == 'item' ]
    done = [] 

    for (gid, prop) in items:
        if gid in done: continue
        done.append(gid)

        locations = data.getTileLocation(gid)
        body = area._parent.getChildByGUID(int(prop['guid']))
        copy = False

        for pos in locations:
            # bodies cannot exists in multiple locations, so a copy is
            # made for each
            if copy:
                body = body.copy()

            x, y, z = toWorld(data, pos)
            # boss hack
            if int(prop['guid']) == 516:
                z -= 32

            area.add(body, (0, y, z))
            area.setOrientation(body, "south")
            copy = True 


    # hack to load elevators
    items = [ p for p in props if 768 < p[1]['guid'] < 1025 ]

    for (gid, prop) in items:
        pos = data.getTileLocation(gid)
        if len(pos) > 1:
            msg = "control gid: {} is used in more than one locaton"
            raise Exception, msg.format(gid)

        x, y, z = toWorld(data, pos.pop())
        body = area._parent.getChildByGUID(int(prop['guid']))
        area.add(body, (0, y, z))
        area.setOrientation(body, "south")


    # hack to load elevators' buttons
    items = [ p for p in props if 256 < p[1]['guid'] < 513 ]
    done = [] 

    for (gid, prop) in items:
        if gid in done: continue
        done.append(gid)

        locations = data.getTileLocation(gid)
        original = area._parent.getChildByGUID(int(prop['guid']))
        copy = False

        for pos in locations:
            # bodies cannot exists in multiple locations, so a copy is
            # made for each
            if copy:
                body = original.copy()
            else:
                body = original            

            x, y, z = toWorld(data, pos)
            body.liftGUID = prop['guid'] + 512
            area.add(body, (0, y-6, z+17))
            area.setOrientation(body, "south")
            copy = True 

    # load the terminals and place them in the default positions 
    terms = [ p for p in props if 1280 < p[1]['guid'] < 1537 ] 
    done = []

    for (gid, prop) in terms:
        done.append(gid)

        locations = data.getTileLocation(gid)
        original = area._parent.getChildByGUID(int(prop['guid']))
        copy = False

        for pos in locations:
            # bodies cannot exists in multiple locations, so a copy is
            # made for each
            if copy:
                body = original.copy()
            else:
                body = original            

            x, y, z = toWorld(data, pos)
            body.liftGUID = prop['guid'] + 512
            area.add(body, (0, y, z+17))
            area.setOrientation(body, "south")
            copy = True 


    # load the closed doors and place them in the default positions 
    terms = [ p for p in props if 1536 < p[1]['guid'] < 1600 ] 

    for (gid, prop) in terms:
        pos = data.getTileLocation(gid)
        if len(pos) > 1:
            msg = "control gid: {} is used in more than one locaton"
            raise Exception, msg.format(gid)

        x, y, z = toWorld(data, pos.pop())
        body = area._parent.getChildByGUID(int(prop['guid']))
        area.add(body, (0, y, z-16))
        area.setOrientation(body, "south")


    #haccckk
    for lift in [ i for i in area.getChildren() if isinstance(i, Lift) ]:
        body = lift.parent.getBody(lift)
        body.bbox = body.bbox.move(0,0,1)

    pushback = ['Desk', 'Callbutton', 'Terminal']

    for i in [ i for i in area.getChildren() if i.name in pushback ]:
        print "pushing back", i
        body = lift.parent.getBody(i)
        print body.bbox
        body.bbox = body.bbox.move(-16,0,0)
        print body.bbox

    # handle the exits
    # here only the exits and positions are saved
    # another class will have to finalize the exits by adding a ref to
    # guid of the other area
    #exits = [ p for p in props if p[1].get('group', None) == 'door' ]
    #for gid, prop in exits:
    #    x, y, l = toWorld(data, data.getTileLocation(gid)[0])
    #    area.exits[prop['guid']] = ((x, y, l), None)

    return area

