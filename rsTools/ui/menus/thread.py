from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets
from time import time


class ProviderThread(QtCore.QThread):

    def __init__(self, _callable):
        self._provider = _callable
        self._items = [{"label": "Loading ..", "enabled": False}]
        super(ProviderThread, self).__init__()


class ThreadProvider(QtCore.QObject):
    _update = QtCore.Signal()

    def __init__(self, _callable, cache, parent):
        super(ThreadProvider, self).__init__()

        self._parent = parent
        self._thread = ProviderThread(_callable)
        self._thread.finished.connect(self._update)
        self._cache = max(2.0, cache)
        self._pass = False
        self._last = 0

    def __call__(self):
        if not self._pass and (time() - self._last) > self._cache:
            self._pass = True
            if not self._thread.isRunning():
                self._thread.start()
        return self._thread.items()

    def update(self):
        self._last = time()
        self._pass = False
        self._update.emit()
