from lib2d.ui import Element, VirtualMapElement, VirtualAvatarElement
from lib2d.mouse.tools.mousetool import MouseTool
from lib2d import res


from lib2d.ui import GraphicIcon, RoundMenu


class PanTool(MouseTool, Element):
    def __init__(self, parent):
        MouseTool.__init__(self)
        Element.__init__(self, parent)
        self.drag_origin = None
        self.openMenu = None
        self.avatar_focus = None


    def load(self):
        self.tool_image = res.loadImage("pantool.png")


    def onClick(self, element, point, button):

        if self.avatar_focus is None:
            if isinstance(element, VirtualMapElement):
                self.openMenu = testMenu(element.parent)
                self.openMenu.open(point)

            elif isinstance(element, VirtualAvatarElement):
                self.avatar_focus = element.avatar
                actions = element.avatar.queryActions(None)
                icons = [ GraphicIcon(a.icon, None) for a in actions ]
                menu = RoundMenu(element.parent)
                menu.setIcons(icons)
                point += element.parent.packer.getRect(element).topleft
                menu.open(point)

            else:
                element.onClick(point, button)

        else:
            # pathfind?
            self.avatar_focus = None 


    def onDrag(self, element, point, button, origin):
        if isinstance(element, VirtualMapElement):
            if not origin == self.drag_origin:
                self.drag_origin = origin
                self.drag_initial_center = element.camera.extent.center

            dx, dy = origin - point
            cx, cy = self.drag_initial_center
            element.camera.center((cx+dy, cy+dx, 0))


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
