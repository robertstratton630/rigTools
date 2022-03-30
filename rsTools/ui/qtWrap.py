from Qt import QtCore, QtWidgets, QtGui
from Qt.QtWidgets import QTreeWidgetItem
from Qt.QtGui import QIcon
from Qt.QtGui import QPixmap
from shiboken2 import wrapInstance
import os

import maya.cmds as cmds
import maya.OpenMayaUI as omui
import pymel.core as pm

from cStringIO import StringIO
import xml.etree.ElementTree as xml

import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

# get qobject + name


def getQtObject(mayaName, castType=None):
    pointer = omui.MQtUtil.findControl(mayaName)
    castType = castType or QtCore.QObject

    if pointer is None:
        pointer = omui.MQtUtil.findLayout(mayaName)
        castType = QtWidgets.QWidget
    if pointer is None:
        pointer = omui.MQtUtil.findMenuItem(mayaName)
    if pointer is not None:
        return wrapInstance(long(pointer), castType), omui.MQtUtil.fullName(long(pointer))
    return None

# get main window


def getMayaMainWindow():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


def load_ui_type(ui_file):
    """This function converts a '.ui' file into a '.py' file live.
    This means that all UI's are derived from a QT designer ui files that are converted directly to form the UI.
    This keeps a live connection between the '.ui' file and the actul UI in maya. Meaning that any edit or a change to the UI base needs to be done only from the QT designer, without any further action by the user.
    It reruns a baseClass and a formClass to be used when creating any UI."""

    parsed = xml.parse(ui_file)
    widget_class = parsed.find('widget').get('class')
    form_class = parsed.find('class').text
    with open(ui_file, 'r') as f:
        o = StringIO()
        frame = {}
        pyside2uic.compileUi(f, o, indent=0)
        pyc = compile(o.getvalue(), '<string>', 'exec')
        exec pyc in frame

        # Fetch the base_class and form class based on their type in the xml from design
        form_class = frame['Ui_{0}'.format(form_class)]
        base_class = eval('QtWidgets.{0}'.format(widget_class))

    # return;baseClass, formClass
    return form_class, base_class


def buildFormBaseClassForUI(script_dir, rel_path):
    abs_file_path = os.path.join(script_dir, rel_path)
    form_class, base_class = load_ui_type(abs_file_path)

    # return;baseClass, formClass
    return form_class, base_class
