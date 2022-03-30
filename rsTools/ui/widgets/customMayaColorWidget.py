
class CustomMayaColorButton(QtWidgets.QWidget):

    # add a signal so you can update outside of widget
    color_changed = QtCore.Signal(QtGui.QColor)

    def __init__(self, color=QtCore.Qt.white, parent=None):
        super(CustomMayaColorButton, self).__init__(parent)
        self.setObjectName("CustomMayaColorButton")
        self.create_control()
        self.set_size(50, 14)
        self.set_color(color)

    def create_control(self):
        """ 1) Create the colorSliderGrp """
        window = cmds.window()
        color_slider_name = cmds.colorSliderGrp()

        """ 2) Find the colorSliderGrp widget """
        self._color_slider_obj = omui.MQtUtil.findControl(color_slider_name)
        if self._color_slider_obj:
            self._color_slider_widget = wrapInstance(
                long(self._color_slider_obj), QtWidgets.QWidget)

            """ 3) Reparent the colorSliderGrp widget to this widget """
            main_layout = QtWidgets.QVBoxLayout(self)
            main_layout.setObjectName("main_layout")
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.addWidget(self._color_slider_widget)

            """ 4) Identify/store the colorSliderGrp’s child widgets (and hide if necessary)  """
            # children = self._color_slider_widget.children()
            # for child in children:
            #     print(child)
            #     print(child.objectName())
            # print("---")

            self._slider_widget = self._color_slider_widget.findChild(
                QtWidgets.QWidget, "slider")
            if self._slider_widget:
                self._slider_widget.hide()

            self._color_widget = self._color_slider_widget.findChild(
                QtWidgets.QWidget, "port")

            cmds.colorSliderGrp(self.get_full_name(), e=True,
                                changeCommand=partial(self.on_color_changed))

        cmds.deleteUI(window, window=True)

    def get_full_name(self):
        return omui.MQtUtil.fullName(long(self._color_slider_obj))

    def set_size(self, width, height):
        self._color_slider_widget.setFixedWidth(width)
        self._color_widget.setFixedHeight(height)

    def set_color(self, color):
        color = QtGui.QColor(color)

        cmds.colorSliderGrp(self.get_full_name(), e=True, rgbValue=(
            color.redF(), color.greenF(), color.blueF()))
        self.on_color_changed()

    def get_color(self):
        # color = cmds.colorSliderGrp(self._color_slider_widget.objectName(), q=True, rgbValue=True)
        color = cmds.colorSliderGrp(
            self.get_full_name(), q=True, rgbValue=True)

        color = QtGui.QColor(color[0] * 255, color[1] * 255, color[2] * 255)
        return color

    def on_color_changed(self, *args):
        self.color_changed.emit(self.get_color())
