class BaseModule(object):

    def __init__(self, name):
        self.name = name
        self.enabled = False

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False
