from Qt import QtCore, QtGui, QtWidgets
import os


class CustomImageWidget(QtWidgets.QLabel):
    def __init__(self, width=None, height=None, imagePath=None, text=None, parent=None, **kwargs):
        super(CustomImageWidget, self).__init__(parent)

        self._title = text
        self.image_path = imagePath
        self._width = self.width()
        self._height = self.height()

        if width:
            self._width = width
        if height:
            self._height = height

        self._textSize = kwargs.get("textSize", self._width/len(self._title))
        self._textAlign = kwargs.get("textAlign", QtCore.Qt.AlignRight)
        self._backGround = kwargs.get("background", False)
        self._color = kwargs.get("color", [38, 232, 232])

        self.textColor = QtGui.QColor(
            self._color[0], self._color[1], self._color[2])

        self.setFixedSize(self._width, self._height)

        self._r = 1

        self._title = text
        self.backgroundColor = QtCore.Qt.black

        self.create_widgets()

    def create_widgets(self):
        image = QtGui.QImage(self.image_path)
        image = image.scaled(self._width, self._height,
                             QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)
        self.pixmap = QtGui.QPixmap()
        self.pixmap.convertFromImage(image)

        self._label = QtWidgets.QLabel()
        self._label.setPixmap(self.pixmap)
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        if self._title:
            if self._backGround:
                self._paintBackground(painter)

            painter.drawPixmap(self.rect(), self.pixmap)
            factor = painter.fontMetrics().size(0, self._title).width()

            painter.setFont(QtGui.QFont(
                "Vendana", self._textSize, QtGui.QFont.ExtraBold))

            painter.setPen(self.textColor)
            painter.setOpacity(0.9)
            painter.drawText(QtCore.QRect(0, 0, self._width,
                                          self._height), self._textAlign, self._title)

    def _paintBackground(self, painter, ratio=1.0):
        _rectanglePath = QtGui.QPainterPath()
        _rectanglePath.moveTo(0.0, 0.0)
        _rectanglePath.addRoundedRect(
            1, 1, self._width*ratio, self._height*ratio, self._width*ratio*0.1, self._height*ratio*0.1)
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)

        c = QtGui.QColor(255, 255, 255)
        _gradient = QtGui.QLinearGradient(0, 0, self._width/2, self._height)
        _gradient.setColorAt(0, c)
        _gradient.setColorAt(1, c.darker(200))
        painter.fillPath(_rectanglePath, QtGui.QBrush(_gradient))

    def updateText(self, text):
        self._title = text
        self.update()
