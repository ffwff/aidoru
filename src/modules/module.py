class BaseModule:

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.enabled = False

        self.__class__._cbs = set()
        def connect(fn):
            fn(self.enabled)
            self.__class__._cbs.add(fn)
        self.__class__.connect = connect

    # events
    # this is manually implemented rather than using PyQt's signal
    # system because there's no other better way to implement it.
    def _emit(self):
        for cb in self.__class__._cbs:
            cb(self.enabled)

    # states
    def enable(self):
        self.enabled = True
        self._emit()

    def disable(self):
        self.enabled = False
        self._emit()
