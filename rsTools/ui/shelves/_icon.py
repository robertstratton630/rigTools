import logging

from Qt import QtCore
from Qt import QtGui
from Qt import QtSvg
def _isdark(c): return (0.2126*c[0] + 0.7152*c[1] + 0.0722*c[2]) < 120


logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.DEBUG)
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class DefaultIcon(QtGui.QIconEngine):

    __status_colors__ = {"success": QtGui.QColor(45, 220, 90),
                         "warning": QtGui.QColor(210, 180, 45),
                         "error": QtGui.QColor(220, 60, 75),
                         "default": QtGui.QColor(180, 180, 180)}

    __progress_colors__ = {"success": QtGui.QColor(45, 220, 90),
                           "warning": QtGui.QColor(210, 180, 45),
                           "error": QtGui.QColor(220, 60, 75),
                           "default": QtGui.QColor(180, 180, 180)}

    def __init__(self, title=None, icon=None, color=(90, 90, 90), status="default", progress=None, titleFontSize=None):
        self._title = title
        _logger.debug(self._title)

        self._status = status
        self._icon = icon
        if self._icon:
            self._svgRender = QtSvg.QSvgRenderer(self._icon)

        try:
            color = [int(c) for c in color]
        except:
            color = (90, 90, 90)

        self._color = QtGui.QColor(*color)
        self._progress = progress
        self._titleFontSize = titleFontSize

        _logger.debug("title: {0} color: {1} status: {2}".format(
            self._title, self._color, self._status))

        super(DefaultIcon, self).__init__()

    # pure virtual fuction which is automatically called from engine
    def paint(self, painter, rect, mode, state):
        _w = rect.width()
        _r = float(_w)/32.0
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_Clear)
        painter.fillRect(rect, QtCore.Qt.white)
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_Source)
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_Source)
        painter.fillRect(rect, QtGui.QColor(68, 68, 68)
                         )  # sets the border color

        self._paintBackground(painter, mode, _r)  # paint background color
        self._paintProgress(painter, _r)

        # get the background color depending on mode
        color = self.backgroundColor(mode)
        color = color.lighter(300) if _isdark(
            self._color.getRgb()) else color.darker(300)

        if self._icon:
            self._svgRender.render(painter, QtCore.QRectF(rect))

        if self._title:
            fontSize = _r*15
            if self._titleFontSize:
                fontSize = self._titleFontSize

            painter.setFont(QtGui.QFont("Vendana", _r*15))

            factor = (32-_r*8)/painter.fontMetrics().size(0,
                                                          self._title).width()
            if factor < 1:
                factor = max(0.25, factor)
                f = painter.font()
                f.setPointSizeF(f.pointSizeF()*factor)
                painter.setFont(f)
            h = painter.fontMetrics().size(0, self._title).height()

            # if button is active, check color to make text black or white
            if mode == QtGui.QIcon.Active:
                color = color.lighter(150) if _isdark(
                    self._color.getRgb()) else color.darker(180)

            painter.setPen(color)
            painter.drawText(QtCore.QRect(0, (32*_r-h)/2, 32*_r, h),
                             QtCore.Qt.AlignCenter, self._title)

    def backgroundColor(self, mode=QtGui.QIcon.Normal):
        c = self._color
        if mode == QtGui.QIcon.Disabled:
            QtGui.QColor.fromHsv(
                self._color.hue(), self._color.hsvSaturation()*0.12, self._color.value()*0.7)
        elif self._status not in (None, "default") and self._progress is None:
            c = self.__status_colors__.get(self._status, self._color)
        return c

    def _paintBackground(self, painter, mode, ratio=1.0):
        _rectanglePath = QtGui.QPainterPath()
        _rectanglePath.moveTo(0.0, 0.0)
        _rectanglePath.addRoundedRect(
            1, 1, 30*ratio, 30*ratio, 3*ratio, 3*ratio)
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)
        _gradient = QtGui.QLinearGradient(0, 0, 0, 32)

        c = self.backgroundColor(mode)
        _gradient.setColorAt(0, c)
        _gradient.setColorAt(1, c.darker(150))
        painter.fillPath(_rectanglePath, QtGui.QBrush(_gradient))

    def _paintProgress(self, painter, ratio=1.0):
        if self._progress is None:
            return

        painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceAtop)
        _progessPath = QtGui.QPainterPath()
        _progessPath.moveTo(0.0, 0.0)
        _progessPath.addRoundedRect(
            2*ratio, 28*ratio, 28*ratio, 3*ratio, ratio, ratio)
        painter.fillPath(_progessPath, QtGui.QBrush(
            QtGui.QColor(0, 0, 0, 115)))
        _progressPath = QtGui.QPainterPath()
        _progressPath.moveTo(0.0, 0.0)
        _progessPath.addRoundedRect(
            2*ratio, 28*ratio, int(28)*ratio*self._progress, 3*ratio, ratio, ratio)
        painter.fillPath(_progessPath, QtGui.QBrush(self.__progress_colors__.get(
            self._status or "default", QtGui.QColor(130, 130, 130))))
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)
