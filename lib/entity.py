from lib2d.objects import AvatarObject


class InteractiveObject(AvatarObject):
    """
    these objects supply a list of actions that other objects can call
    """

    def __init__(self, avatar, builders):
        AvatarObject.__init__(self, avatar)
        self.actionBuilders = builders


    def queryActions(self, caller):
        actions = []
        for builder in self.actionBuilders:
            actions.extend(builder.get_actions(caller, None))
        return actions


class Entity(InteractiveObject):
    """
    Game object that is capable of containing other objects and moving/being
    moved
    """

    def __init__(self, avatar, builders, face):
        super(Entity, self).__init__(avatar, builders)
        self.faceImage = face

