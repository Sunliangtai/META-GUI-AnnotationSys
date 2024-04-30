from utils import read_json, write_json


class Element:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class Word(Element):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)


class Wrapper(Element):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)


class Layout(Element):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)


class Action:
    def __init__(self, action_type, action_attr, target: Element):
        self.action_type = action_type
        self.acttion_attr = action_attr
        self.target = target
