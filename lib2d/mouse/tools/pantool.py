from lib2d.ui import Element, VirtualMapElement, VirtualAvatarElement
from lib2d.ui import GraphicIcon, RoundMenu
from lib2d.image import Image, ImageTile
from lib2d.mouse.tools.mousetool import MouseTool
from lib2d import res

import pygame



class PanTool(MouseTool, Element):
    def __init__(self, parent):
        MouseTool.__init__(self)
        Element.__init__(self, parent)
        self.drag_origin = None
        self.openMenu = None
        self.focus_entity = None
        self.entity_icon = None


    def load(self):
        self.tool_image = res.loadImage("pantool.png")


    def onClick(self, element, point, button):

        if self.focus_entity is None:
            if isinstance(element, VirtualMapElement):
                if self.openMenu:
                    self.openMenu.close()

                self.openMenu = testMenu(element)
                self.openMenu.open(point)

            elif isinstance(element, VirtualAvatarElement):
                self.onSelectEntity(element.avatar)
                #actions = element.avatar.queryActions(None)
                #icons = [ GraphicIcon(a.icon, None) for a in actions ]
                #menu = RoundMenu(element)
                #menu.setIcons(icons)
                #menu.open(point)

            else:
                element.onClick(point, button)

        # THERE IS AN ENTITY FOCUSED
        else:
            if isinstance(element, VirtualMapElement):
                if self.openMenu:
                    self.openMenu.close()

                self.openMenu = movementMenu(element)
                self.openMenu.focus_entity = self.focus_entity
                self.openMenu.open(point)
                self.onSelectEntity(None)   # clear the focus


            else:
                self.onSelectEntity(None)   # clear the focus


    def onSelectEntity(self, entity=None):
        self.focus_entity = entity

        if self.entity_icon:
            self.parent.removeElement(self.entity_icon)
            self.entity_icon = None

        if entity:
            w, h = self.parent.rect.size
            icon = GraphicIcon(entity.faceImage, None)
            icon.rect = pygame.Rect(w-32,0,32,32)
            icon.load()
            self.parent.addElement(icon)
            self.entity_icon = icon


    def onDrag(self, element, point, button, origin):
        if isinstance(element, VirtualMapElement):
            if not origin == self.drag_origin:
                self.drag_origin = origin
                self.drag_initial_center = element.camera.extent.center

            dx, dy = point - origin
            cx, cy = self.drag_initial_center
            element.camera.center((cx-dy, cy-dx, 0))



def movementMenu(parent):
    def closer(icon):
        parent.parent.removeElement(icon)
        icon.unload()


    def func(menu):
        import lib.blacksmith as b
        menu.close()

        camera = menu.parent.camera
        body0 = camera.area.getBody(menu.focus_entity)
        endpoint = camera.surfaceToWorld(menu.anchor)
        path = camera.area.pathfind(body0.bbox.bottomcenter, endpoint)
        print path 


        image = Image("path.png")

        for node in path:
            y, x = node
            icon = GraphicIcon(image, closer)
            icon.load()
            icon.rect = pygame.Rect(x*16, y*16, 16, 16)
            menu.parent.parent.addElement(icon) 


    image = ImageTile("spellicons.png", tile=(20,3), tilesize=(32,32))

    m = RoundMenu(parent)
    a = GraphicIcon(image, func, [m])
    m.setIcons([a])
    return m



def testMenu(parent):
    def func(menu):
        import lib.blacksmith as b
        menu.close()

        anvil = b.Anvil()
        anvil.loadAll()
        x, y, z = menu.parent.camera.surfaceToWorld(menu.anchor)
        x -= 16
        y -= 16
        menu.parent.camera.area.add(anvil)
        menu.parent.camera.area.setPosition(anvil, (x, y, z))


    image = Image("grasp.png")

    m = RoundMenu(parent)
    a = GraphicIcon(image, func, [m])
    b = GraphicIcon(image, func, [m])
    c = GraphicIcon(image, func, [m])
    d = GraphicIcon(image, func, [m])
    m.setIcons([a,b,c,d])
    return m
