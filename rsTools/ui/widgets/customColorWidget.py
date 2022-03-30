
class CustomColorButton(QtWidgets.QLabel):

    color_changed = QtCore.Signal()

    def __init__(self, color=QtCore.Qt.white, parent=None):
        super(CustomColorButton, self).__init__(parent)

        self._color = QtGui.QColor()  # Invalid color

        self.set_size(50, 14)
        self.set_color(color)

    def set_size(self, width, height):
        self.setFixedSize(width, height)

    def set_color(self, color):
        color = QtGui.QColor(color)

        if self._color != color:
            self._color = color

            pixmap = QtGui.QPixmap(self.size())
            pixmap.fill(self._color)
            self.setPixmap(pixmap)

            self.color_changed.emit()

    def get_color(self):
        return self._color

    def select_color(self):
        color = QtWidgets.QColorDialog.getColor(
            self.get_color(), self, options=QtWidgets.QColorDialog.DontUseNativeDialog)
        if color.isValid():
            self.set_color(color)

    def mouseReleaseEvent(self, mouse_event):
        if mouse_event.button() == QtCore.Qt.LeftButton:
            self.select_color()
