from Qt import QtCore, QtGui, QtWidgets
from shiboken2 import wrapInstance
import os
import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.cmds as cmds
from functools import partial

# get path info
from rsTools.glob import *
from rsTools.utils import nurbs
from rsTools.ui import qtWrap
from rsTools.ui.widgets.folderSelectWidget import FolderSelectWidget
from rsTools.ui.widgets.customImageWidget import CustomImageWidget
import rsTools.utils.osUtils.enviroments as env
import rsTools.utils.transforms.transforms as tUtils


#from .enviromentPage import EnviromentPageWidget
from rsTools.ui.interfaces.hub._hubEnviromentMenu import hubProjectMenu
from rsTools.ui.interfaces.hub._hubEnviromentMenu import hubProjectRootMenu
from rsTools.ui.interfaces.hub._hubEnviromentMenu import hubProjectAsset

from rsTools.utils.osUtils import shotBuild
from rsTools.utils.osUtils import osUtils
from rsTools.ui.widgets.stateDrivenWidgets.pickerWidget import PickerWidget

import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class ModelCompareUI(QtWidgets.QDialog):

    WINDOW_TITLE = "Model Compare"

    def __init__(self, parent=qtWrap.getMayaMainWindow()):
        super(ModelCompareUI, self).__init__(parent)

        self.setObjectName("Model Compare")
        self.setWindowTitle(self.WINDOW_TITLE)
        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^
                                QtCore.Qt.WindowContextHelpButtonHint)
        elif cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self._w = 700
        self._h = 500

        self.state = 0

        self.setMinimumSize(self._w, self._h)

        self.createWidgets()
        self.createLayout()

    def createWidgets(self):

        # project labels
        kwargs = {"textSize": 14,
                  "textAlign": QtCore.Qt.AlignLeft,
                  "background": False,
                  "color": [255, 255, 0]
                  }

        # create the project labels
        self._compareALabel = CustomImageWidget(100, 22, text="CompareA", imagePath=os.path.join(
            g_rs_path_image_shelf, "default.svg"), **kwargs)
        self._compareBLabel = CustomImageWidget(self.width(
        )/2, 22, text="CompareB", imagePath=os.path.join(g_rs_path_image_shelf, "default.svg"), **kwargs)

        self.build_compareA()
        self.build_compareB()

        self.dataField = QtWidgets.QTextEdit()

        self.pushButton = QtWidgets.QPushButton("Validate")
        self.pushButton.setMinimumHeight(50)
        self.pushButton.clicked.connect(self.event_pushButton)

        self.checkBoxButton = QtWidgets.QCheckBox("Use Scene")
        self.checkBoxButton.clicked.connect(self.event_checkBox)

        exist = cmds.objExists("rigHubSet_geometryCache")
        if not exist:
            self.checkBoxButton.setEnabled(False)
            self.checkBoxButton.setChecked(False)

        self.geoMatchTree = QtWidgets.QListWidget()
        self.geoMatchTree.setMinimumSize(300, self.height()/1.5)
        self.geoMatchTree.setFocusPolicy(QtCore.Qt.NoFocus)

        self.geoErrorTree = QtWidgets.QListWidget()
        self.geoErrorTree.setMinimumSize(300, self.height()/1.5)
        self.geoErrorTree.setFocusPolicy(QtCore.Qt.NoFocus)

    def event_checkBox(self):
        if self.checkBoxButton.isChecked():
            self.comboA_job.setEnabled(False)
            self.comboA_elementName.setEnabled(False)
            self.comboA_elementVersion.setEnabled(False)
            self.comboA_asset.setEnabled(False)
        else:
            self.comboA_job.setEnabled(True)
            self.comboA_elementName.setEnabled(True)
            self.comboA_elementVersion.setEnabled(True)
            self.comboA_asset.setEnabled(True)

    def event_pushButton(self):

        projectA = self.comboA_job.currentText()
        assetA = self.comboA_asset.currentText()
        elementA = self.comboA_elementName.currentText()
        versionA = self.comboA_elementVersion.currentText()

        projectB = self.comboB_job.currentText()
        assetB = self.comboB_asset.currentText()
        elementB = self.comboB_elementName.currentText()
        versionB = self.comboB_elementVersion.currentText()

        root = env.get_project_rootpath()

        pathA = None
        pathB = None

        if not self.checkBoxButton.isChecked():
            pathA = os.path.join(
                root, projectA, assetA, "release", "model", elementA, versionA, "metaData.json")

        pathB = os.path.join(root, projectB, assetB, "release",
                             "model", elementB, versionB, "metaData.json")

        topoMatches = shotBuild.compareModelTopologyMetaData(pathA, pathB)
        setMatches = shotBuild.compareModelSetMetaData(pathA, pathB)

        setColor = [100, 100, 100, 0.05]
        topoColor = [100, 100, 100, 0.05]

        self.geoMatchTree.clear()
        self.geoErrorTree.clear()

        if topoMatches:
            topoColor = [255.0, 0.0, 0.0, 0.5]
            if isinstance(topoMatches, str):
                self.geoErrorTree.addItem(topoMatches)
            else:
                self.geoErrorTree.addItems(topoMatches)

            self.rightBox.setEnabled(True)
        else:
            topoColor = [0.0, 255.0, 0.0, 0.5]
            self.geoErrorTree.addItem("TOPOLOGY MATCHING")
            self.rightBox.setEnabled(False)

        if setMatches:
            setColor = [255.0, 0.0, 0.0, 0.5]
            if isinstance(setMatches, str):
                self.geoMatchTree.addItem(setMatches)
            else:
                self.geoMatchTree.addItems(setMatches)
            self.leftBox.setEnabled(True)
        else:
            setColor = [0.0, 255.0, 0.0, 0.5]
            self.geoMatchTree.addItem("SETS MATCHING")
            self.leftBox.setEnabled(False)

        self.styleSheet_geometrySetCheck(setColor, topoColor)

        pass

    def createLayout(self):
        mainlayout = QtWidgets.QHBoxLayout(self)

        compareALayout = QtWidgets.QHBoxLayout()
        compareALayout.addWidget(self._compareALabel)
        compareALayout.addWidget(self.checkBoxButton)
        compareALayout.setAlignment(QtCore.Qt.AlignLeft)

        vertical = QtWidgets.QVBoxLayout()
        vertical.addLayout(compareALayout)

        vertical.addLayout(self.layoutA)
        vertical.setSpacing(5)
        vertical.setContentsMargins(0, 0, 0, 0)
        vertical.setAlignment(QtCore.Qt.AlignTop)

        verticalSpacer = QtWidgets.QSpacerItem(5, 20)
        vertical.addItem(verticalSpacer)
        vertical.addWidget(self._compareBLabel)
        vertical.addLayout(self.layoutB)
        verticalSpacer = QtWidgets.QSpacerItem(5, 50)
        vertical.addItem(verticalSpacer)

        validationLayout = QtWidgets.QHBoxLayout()

        self.leftBox = QtWidgets.QGroupBox('Set Differences')
        leftLayout = QtWidgets.QHBoxLayout()
        leftLayout.addWidget(self.geoMatchTree)
        leftLayout.setSpacing(0)
        leftLayout.setContentsMargins(8, 8, 8, 8)
        self.leftBox.setLayout(leftLayout)

        self.rightBox = QtWidgets.QGroupBox('Incorrect VertCounts')
        rightLayout = QtWidgets.QHBoxLayout()
        rightLayout.addWidget(self.geoErrorTree)
        rightLayout.setSpacing(0)
        rightLayout.setContentsMargins(8, 8, 8, 8)
        self.rightBox.setLayout(rightLayout)

        validationLayout.addWidget(self.leftBox)
        validationLayout.addWidget(self.rightBox)

        self.styleSheet_mainGroup()

        vertical.addLayout(validationLayout)
        vertical.addWidget(self.pushButton)

        mainlayout.addLayout(vertical)

        self.styleSheet_geometrySetCheck(
            [100, 100, 100, 0.05], [100, 100, 100, 0.05])

    def build_compareA(self):
        self.layoutA = QtWidgets.QHBoxLayout()

        # get jobs
        root = env.get_project_rootpath()
        jobs = osUtils.get_subdirs(root)

        kwargs = {"textSize": 10,
                  "textAlign": QtCore.Qt.AlignLeft,
                  "background": False,
                  }

        # default display settings
        root = env.get_project_rootpath()
        allProjects = osUtils.get_subdirs(root)
        currentProject = env.get_project_show()
        assets = shotBuild.getProjectAssets(currentProject)
        elements = shotBuild.getProjectAssetsByType(
            currentProject, env.get_project_show_asset(), "model")
        versions = ""

        if assets and elements:
            versions = shotBuild.getAssetVersions(
                currentProject, env.get_project_show_asset(), "model", elements[0])
            versions.reverse()

        self.labelA_job = CustomImageWidget(50, 15, text="Project ", imagePath=os.path.join(
            g_rs_path_image_shelf, "default.svg"), **kwargs)
        self.comboA_job = QtWidgets.QComboBox()
        self.comboA_job.addItems(allProjects)
        self.comboA_job.setCurrentText(env.get_project_show())

        self.labelA_asset = CustomImageWidget(45, 15, text="Asset ", imagePath=os.path.join(
            g_rs_path_image_shelf, "default.svg"), **kwargs)
        self.comboA_asset = QtWidgets.QComboBox()
        self.comboA_asset.addItems(assets)
        self.comboA_asset.setCurrentText(env.get_project_show_asset())

        self.labelA_elementName = CustomImageWidget(50, 15, text="Element ", imagePath=os.path.join(
            g_rs_path_image_shelf, "default.svg"), **kwargs)
        self.comboA_elementName = QtWidgets.QComboBox()
        self.comboA_elementName.addItems(elements)
        try:
            self.comboA_elementName.setCurrentText(elements[0])
        except:
            pass

        self.labelA_elementVersion = CustomImageWidget(
            50, 15, text="Version ", imagePath=os.path.join(g_rs_path_image_shelf, "default.svg"), **kwargs)
        self.comboA_elementVersion = QtWidgets.QComboBox()
        self.comboA_elementVersion.addItems(versions)
        try:
            self.comboA_elementVersion.setCurrentText(versions[0])
        except:
            pass

        self.layoutA.addWidget(self.labelA_job)
        self.layoutA.addWidget(self.comboA_job)
        self.layoutA.addWidget(self.labelA_asset)
        self.layoutA.addWidget(self.comboA_asset)
        self.layoutA.addWidget(self.labelA_elementName)
        self.layoutA.addWidget(self.comboA_elementName)
        self.layoutA.addWidget(self.labelA_elementVersion)
        self.layoutA.addWidget(self.comboA_elementVersion)

        self.comboA_job.currentIndexChanged.connect(
            self.event_projectChanged_A)
        self.comboA_asset.currentIndexChanged.connect(
            self.event_assetChanged_A)
        self.comboA_elementName.currentIndexChanged.connect(
            self.event_elementChanged_A)

    def build_compareB(self):
        self.layoutB = QtWidgets.QHBoxLayout()

        # get jobs
        root = env.get_project_rootpath()
        jobs = osUtils.get_subdirs(root)

        # default display settings
        currentProject = env.get_project_show()
        assets = shotBuild.getProjectAssets(currentProject)
        elements = shotBuild.getProjectAssetsByType(
            currentProject, env.get_project_show_asset(), "model")
        versions = ""
        if assets and elements:
            versions = shotBuild.getAssetVersions(
                currentProject, env.get_project_show_asset(), "model", elements[0])
            versions.reverse()

        kwargs = {"textSize": 10,
                  "textAlign": QtCore.Qt.AlignLeft,
                  "background": False,
                  }

        self.labelB_job = CustomImageWidget(50, 15, text="Project", imagePath=os.path.join(
            g_rs_path_image_shelf, "default.svg"), **kwargs)
        self.comboB_job = QtWidgets.QComboBox()
        self.comboB_job.addItems(jobs)
        self.comboB_job.setCurrentText(currentProject)

        self.labelB_asset = CustomImageWidget(45, 15, text="Asset ", imagePath=os.path.join(
            g_rs_path_image_shelf, "default.svg"), **kwargs)
        self.comboB_asset = QtWidgets.QComboBox()
        self.comboB_asset.addItems(assets)
        self.comboB_asset.setCurrentText(env.get_project_show_asset())

        self.labelB_elementName = CustomImageWidget(50, 15, text="Element", imagePath=os.path.join(
            g_rs_path_image_shelf, "default.svg"), **kwargs)
        self.comboB_elementName = QtWidgets.QComboBox()
        self.comboB_elementName.addItems(elements)
        try:
            self.comboB_elementName.setCurrentText(elements[0])
        except:
            pass

        self.labelB_elementVersion = CustomImageWidget(
            50, 15, text="Version", imagePath=os.path.join(g_rs_path_image_shelf, "default.svg"), **kwargs)
        self.comboB_elementVersion = QtWidgets.QComboBox()
        self.comboB_elementVersion.addItems(versions)

        self.layoutB.addWidget(self.labelB_job)
        self.layoutB.addWidget(self.comboB_job)
        self.layoutB.addWidget(self.labelB_asset)
        self.layoutB.addWidget(self.comboB_asset)
        self.layoutB.addWidget(self.labelB_elementName)
        self.layoutB.addWidget(self.comboB_elementName)
        self.layoutB.addWidget(self.labelB_elementVersion)
        self.layoutB.addWidget(self.comboB_elementVersion)

        self.comboB_job.currentIndexChanged.connect(
            self.event_projectChanged_B)
        self.comboB_asset.currentIndexChanged.connect(
            self.event_assetChanged_B)
        self.comboB_elementName.currentIndexChanged.connect(
            self.event_elementChanged_B)

    def event_projectChanged_A(self):
        newProject = self.comboA_job.currentText()
        assets = shotBuild.getProjectAssets(newProject)

        self.comboA_asset.clear()
        self.comboA_elementName.clear()
        self.comboA_elementVersion.clear()
        self.comboA_asset.addItems(assets)

        if assets:
            elements = shotBuild.getProjectAssetsByType(
                newProject, assets[0], "model")
            if elements:
                self.comboA_elementName.addItems(elements)
                versions = shotBuild.getAssetVersions(
                    newProject, assets[0], "model", elements[0])
                versions.reverse()
                self.comboA_elementVersion.addItems(versions)

    def event_projectChanged_B(self):
        newProject = self.comboB_job.currentText()
        assets = shotBuild.getProjectAssets(newProject)

        self.comboB_asset.clear()
        self.comboB_elementName.clear()
        self.comboB_elementVersion.clear()
        self.comboB_asset.addItems(assets)

        if assets:
            elements = shotBuild.getProjectAssetsByType(
                newProject, assets[0], "model")
            if elements:
                self.comboB_elementName.addItems(elements)
                versions = getAssetVersions(
                    newProject, assets[0], "model", elements[0])
                versions.reverse()
                self.comboB_elementVersion.addItems(versions)

    def event_assetChanged_A(self):
        self.comboA_elementName.clear()
        self.comboA_elementVersion.clear()

        project = self.comboA_job.currentText()
        asset = self.comboA_asset.currentText()

        elements = shotBuild.getProjectAssetsByType(project, asset, "model")
        if elements:
            self.comboA_elementName.addItems(elements)
            versions = shotBuild.getAssetVersions(
                project, asset, "model", elements[0])
            versions.reverse()
            self.comboA_elementVersion.addItems(versions)

    def event_assetChanged_B(self):
        self.comboB_elementName.clear()
        self.comboB_elementVersion.clear()

        project = self.comboB_job.currentText()
        asset = self.comboB_asset.currentText()

        elements = shotBuild.getProjectAssetsByType(project, asset, "model")
        if elements:
            self.comboB_elementName.addItems(elements)
            versions = shotBuild.getAssetVersions(
                project, asset, "model", elements[0])
            versions.reverse()
            self.comboB_elementVersion.addItems(versions)

    def event_elementChanged_A(self):
        self.comboA_elementVersion.clear()

        project = self.comboA_job.currentText()
        asset = self.comboA_asset.currentText()
        element = self.comboA_elementName.currentText()
        versions = shotBuild.getAssetVersions(project, asset, "model", element)

        if versions:
            versions.reverse()
            self.comboA_elementVersion.addItems(versions)

    def event_elementChanged_B(self):
        self.comboB_elementVersion.clear()

        project = self.comboB_job.currentText()
        asset = self.comboB_asset.currentText()
        element = self.comboB_elementName.currentText()
        versions = shotBuild.getAssetVersions(project, asset, "model", element)

        if versions:
            versions.reverse()
            self.comboB_elementVersion.addItems(versions)

    def styleSheet_mainGroup(self):
        self.leftBox.setStyleSheet('''QGroupBox { 
                                                    background: rgba(60,120,150, 50); 
                                                    background-image: None; 
                                                    border-image: None; 
                                                    padding-top:5px; 
                                                    border: 1px solid #1D1927; 
                                                    border-radius: 6px; 
                                                    margin-top: 0.5em;
                                            } 
                                            QGroupBox::title { 
                                                    subcontrol-origin: margin; 
                                                    left: 10px; 
                                                    padding: 0 3px 0 3px;
                                            } 
                                            QGroupBox::indicator {
                                                    width: 0px; 
                                                    height: 0px;
                                            } 
                                            QToolTip {
                                                    border-radius: 6px; 
                                                    border: 2px dashed #FFFFFF; 
                                                    padding: 2px; 
                                                    background: #674E4F; 
                                                    color: #FFFFFF
                                            }
                                        ''')

        self.rightBox.setStyleSheet('''QGroupBox { 
                                                    background: rgba(60,120,150, 50); 
                                                    background-image: None; 
                                                    border-image: None; 
                                                    padding-top:5px; 
                                                    border: 1px solid #1D1927; 
                                                    border-radius: 6px; 
                                                    margin-top: 0.5em;
                                            } 
                                            QGroupBox::title { 
                                                    subcontrol-origin: margin; 
                                                    left: 10px; 
                                                    padding: 0 3px 0 3px;
                                            } 
                                            QGroupBox::indicator {
                                                    width: 0px; 
                                                    height: 0px;
                                            } 
                                            QToolTip {
                                                    border-radius: 6px; 
                                                    border: 2px dashed #FFFFFF; 
                                                    padding: 2px; 
                                                    background: #674E4F; 
                                                    color: #FFFFFF
                                            }
                                        ''')

    def styleSheet_geometrySetCheck(self, leftColor, rightColor):

        lColor = 'rgba({0},{1},{2},{3})'.format(
            leftColor[0], leftColor[1], leftColor[2], leftColor[3])
        rColor = 'rgba({0},{1},{2},{3})'.format(
            rightColor[0], rightColor[1], rightColor[2], rightColor[3])

        self.geoMatchTree.setStyleSheet('''QListWidget {
                                                background-color: rgba(%s,%s,%s,%s);     

                                        } 
                                        QListWidget::item:alternate {
                                                background: #2E302E;
                                        } 
                                        QListWidget::item:selected  {
                                                background: #6D6C5C;
                                        }
                                    ''' % (lColor[0], lColor[1], lColor[2], lColor[3]))

        self.geoErrorTree.setStyleSheet('''QListWidget {
                                                background-color: rgba(%s,%s,%s,%s);
                                                border-radius: 10px; 
                                        } 
                                        QListWidget::item:alternate{
                                                background: #2E302E;
                                        } 
                                        QListWidget::item:selected {
                                                background: #6D6C5C;
                                        }
                                    ''' % (rColor[0], rColor[1], rColor[2], rColor[3]))

        # Update the style

        event = QtCore.QEvent(QtCore.QEvent.StyleChange)
        QtWidgets.QApplication.sendEvent(self.geoMatchTree, event)

        self.geoMatchTree.update()
        self.geoMatchTree.updateGeometry()


modelCompareUI = None


def run():
    global modelCompareUI
    if modelCompareUI:
        modelCompareUI.close()
    modelCompareUI = ModelCompareUI(parent=qtWrap.getMayaMainWindow())
    modelCompareUI.show()


if __name__ == "__main__":

    try:
        ui.close()  # pylint: disable=E0601
        ui.deleteLater()
    except:
        pass

    ui = ModelCompareUI()
    ui.show()
