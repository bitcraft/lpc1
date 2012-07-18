from lib2d.ui import Element, VirtualMapElement, VirtualAvatarElement
from lib2d.ui import GraphicIcon, RoundMenu
from lib2d.mouse.tools.mousetool import MouseTool
from lib2d import res

import pygame



class PanTool(MouseTool, Element):
    def __init__(self, parent):
        MouseTool.__init__(self)
        Element.__init__(self, parent)
        self.drag_origin = None
        self.openMenu = None
        self.entity_focus = None


    def load(self):
        self.tool_image = res.loadImage("pantool.png")


    def onClick(self, element, point, button):

        if self.entity_focus is None:
            if isinstance(element, VirtualMapElement):
                if self.openMenu:
                    self.openMenu.close()

                self.openMenu = testMenu(element)
                self.openMenu.open(point)

            elif isinstance(element, VirtualAvatarElement):
                self.onSelectEntity(element.avatar)
                actions = element.avatar.queryActions(None)
                icons = [ GraphicIcon(a.icon, None) for a in actions ]
                menu = RoundMenu(element)
                menu.setIcons(icons)
                menu.open(point)

            else:
                element.onClick(point, button)

        else:
            # pathfind?
            self.entity_focus = None 


    def onSelectEntity(self, entity):
        self.entity_focus = entity
        self.setInfoIcon(entity.faceImage)


    def setInfoIcon(self, surface):
        icon = GraphicIcon(surface, None)
        w, h = self.parent.get_size()
        self.parent.addElement(icon, pygame.Rect(w-32,0,0,0))


    def onDrag(self, element, point, button, origin):
        if isinstance(element, VirtualMapElement):
            if not origin == self.drag_origin:
                self.drag_origin = origin
                self.drag_initial_center = element.camera.extent.center

            dx, dy = point - origin
            cx, cy = self.drag_initial_center
            element.camera.center((cx-dy, cy-dx, 0))


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


    image = res.loadImage("grasp.png")

    m = RoundMenu(parent)
    a = GraphicIcon(image, func, [m])
    b = GraphicIcon(image, func, [m])
    c = GraphicIcon(image, func, [m])
    d = GraphicIcon(image, func, [m])
    m.setIcons([a,b,c,d])
    return m
