import json

CONFIG = json.loads(open('config.json').read())


class Panel(object):
    def __init__(self):
        pass

    def update(self):
        pass

    def paint(self, surface):
        pass

    def up_pressed(self):
        pass

    def down_pressed(self):
        pass

    def center_pressed(self):
        pass
