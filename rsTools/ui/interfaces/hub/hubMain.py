import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import os

from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets
from functools import partial
from shiboken2 import wrapInstance

# get path info
import rsTools.utils.osUtils.enviroments as env
import rsTools.utils.scene.topNode as topNodeUtil
import rsTools.utils.transforms.transforms as tUtils

from rsTools.glob import *
from rsTools.ui import qtWrap
from rsTools.ui.widgets.customImageWidget import CustomImageWidget
from rsTools.ui.widgets.folderSelectWidget import FolderSelectWidget
from rsTools.utils import nurbs


#from .enviromentPage import EnviromentPageWidget
from rsTools.ui.interfaces.hub._hubEnviromentMenu import hubProjectAsset
from rsTools.ui.interfaces.hub._hubEnviromentMenu import hubProjectMenu
from rsTools.ui.interfaces.hub._hubEnviromentMenu import hubProjectRootMenu

from rsTools.ui.widgets.stateDrivenWidgets.pickerWidget import PickerWidget
from rsTools.utils.osUtils import osUtils
from rsTools.utils.osUtils import shotBuild

from rsTools.core.skeleton import skeletonAsset

import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class Hub(QtWidgets.QDialog):

    WINDOW_TITLE = "Asset Manager"

    def __init__(self, parent=qtWrap.getMayaMainWindow()):
        super(Hub, self).__init__(parent)

        self.setObjectName("Asset Manager")
        self.setWindowTitle(self.WINDOW_TITLE)
        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^
                                QtCore.Qt.WindowContextHelpButtonHint)
        elif cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self._w = 900
        self._h = 700
        _r = float(self._w)/32.0

        self._mainButtonWidgets = list()

        self.setMinimumSize(self._w, self._h)

        # env.loadCacheEnviroments()

        self._page = 0

        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.create_styleSheets()
        # self.create_contextMenus()

    def create_widgets(self):

        # project labels
        kwargs = {"textSize": 14,
                  "textAlign": QtCore.Qt.AlignLeft,
                  "background": False
                  }
        project = env.get_project_rootpath()

        pathName = ""
        try:
            new = project.split("\\")
            pathName = ".."+new[-2]+"\\"+new[-1]
        except:
            pathName = project

        # create the project labels
        self._rootProjectLabel = CustomImageWidget(self.width()/2.5, 22, text="ROOT:        {0}".format(
            pathName), imagePath=os.path.join(g_rs_path_image_shelf, "default.svg"), **kwargs)
        self._projectLabel = CustomImageWidget(self.width()/2.5, 22, text="PROJECT:   {0}".format(
            env.get_project_show()), imagePath=os.path.join(g_rs_path_image_shelf, "default.svg"), **kwargs)
        self._assetLabel = CustomImageWidget(self.width()/2.5, 22, text="ASSET:       {0}".format(
            env.get_project_show_asset()), imagePath=os.path.join(g_rs_path_image_shelf, "default.svg"), **kwargs)

        # create the label context menus

        self._hubProjectRootMenu = hubProjectRootMenu(self._rootProjectLabel)
        self._projectMenu = hubProjectMenu(self._projectLabel)
        self._projectAssetMenu = hubProjectAsset(self._assetLabel)

        self._boxGroup = QtWidgets.QGroupBox()

        # create the side panel buttons
        self.createButtonPanelWidgets(["Gather", "Release", "Set", "Delete"])

        # create all the widgets and stacked widgets
        self.gatherPageWidget = QtWidgets.QWidget()
        self.releasePageWidget = QtWidgets.QWidget()
        self.setPageWidget = QtWidgets.QWidget()
        self.deletePageWidget = QtWidgets.QWidget()

        self.stackedWidget = QtWidgets.QStackedWidget(self)
        self.stackedWidget.addWidget(self.gatherPageWidget)
        self.stackedWidget.addWidget(self.releasePageWidget)
        self.stackedWidget.addWidget(self.setPageWidget)
        self.stackedWidget.addWidget(self.deletePageWidget)

        self.buildGatherUI()
        self.buildReleaseUI()
        self.buildSetUI()
        self.buildDeleteUI()

    def create_layout(self):
        self._labelLayout = QtWidgets.QVBoxLayout()
        self._labelLayout.addWidget(self._rootProjectLabel)
        self._labelLayout.addWidget(self._projectLabel)
        self._labelLayout.addWidget(self._assetLabel)
        self._labelLayout.setContentsMargins(0, 0, 0, 0)
        self._labelLayout.setSpacing(0)
        self._labelLayout.setAlignment(QtCore.Qt.AlignLeft)

        self.createButtonPanelLayout()
        self._boxGroup.setLayout(self._mainButtonLayout)

        self._mainHLayout = QtWidgets.QHBoxLayout()
        self._mainHLayout.addWidget(self._boxGroup)
        # self._mainHLayout.addLayout(self._stackLayout)
        self._mainHLayout.addWidget(self.stackedWidget)

        # main layout
        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.addLayout(self._labelLayout)
        self._layout.addLayout(self._mainHLayout)

    def create_connections(self):
        self._projectMenu.update.connect(self.event_projectUpdated)
        self._hubProjectRootMenu.update.connect(self.event_projectRootUpdated)
        self._projectAssetMenu.update.connect(self.event_projectAssetUpdated)

    def event_projectRootUpdated(self):
        # nice name for root path
        project = env.get_project_rootpath()
        new = project.split("\\")
        pathName = "...."
        try:
            pathName = ".."+new[-2]+"\\"+new[-1]
        except:
            pathName = project

        self._rootProjectLabel.updateText("ROOT:        {0}".format(pathName))
        self._projectLabel.updateText(
            "PROJECT:   {0}".format(env.get_project_show()))
        self._assetLabel.updateText(
            "ASSET:       {0}".format(env.get_project_show_asset()))
        self._projectMenu.rebuild()
        self._projectAssetMenu.rebuild()

        self.populateDeleteUI()
        self.populateGatherUI()
        self.populateReleaseUI()
        self.populateSetUI()

    def event_projectUpdated(self):
        self._projectLabel.updateText(
            "PROJECT:   {0}".format(env.get_project_show()))
        self._assetLabel.updateText(
            "ASSET:       {0}".format(env.get_project_show_asset()))
        self._projectAssetMenu.rebuild()

        self.populateDeleteUI()
        self.populateGatherUI()
        self.populateReleaseUI()
        self.populateSetUI()

    def event_projectAssetUpdated(self):
        self._assetLabel.updateText(
            "ASSET:       {0}".format(env.get_project_show_asset()))
        self._projectAssetMenu.rebuild()

        self.populateDeleteUI()
        self.populateGatherUI()
        self.populateReleaseUI()
        self.populateSetUI()

    def createButtonPanelWidgets(self, buttonLabels=None):
        for i, name in enumerate(buttonLabels):
            widget = QtWidgets.QPushButton(name)
            widget.setCheckable(True)
            widget.setMinimumSize(50, self.height()/len(buttonLabels)*0.6)
            widget.clicked.connect(partial(self.event_setPage, i))
            self._mainButtonWidgets.append(widget)

            widget.setStyleSheet('''
                                            QPushButton { 
                                                background-color: rgba(100,150,200,20); 
                                                padding-top:5px; 
                                                border-radius: 2px; 
                                                margin-top: 0.5em;
                                            }  
                                            
                                            QPushButton::checked
                                            {
                                                background-color: rgba(200,150,200,50); 
                                            }
                                            
                                            ''')

    def createButtonPanelLayout(self):
        self._mainButtonLayout = QtWidgets.QVBoxLayout()
        for w in self._mainButtonWidgets:
            self._mainButtonLayout.addWidget(w)
        return self._mainButtonLayout

    def event_setPage(self, pageNum):
        self._page = pageNum

        for w in self._mainButtonWidgets:
            if not w == self._mainButtonWidgets[pageNum]:
                w.setChecked(False)

        self.populatePage(self._page)

    def populatePage(self, pageNum):

        self.stackedWidget.setCurrentIndex(pageNum)

        if pageNum == 0:
            self.populateGatherUI()
        elif pageNum == 1:
            self.populateReleaseUI()
        elif pageNum == 2:
            self.populateSetUI()
        else:
            self.populateDeleteUI()

    def populateGatherUI(self):
        self.gather_treeElement.clear()
        self.gather_treeElementType.clear()
        self.gather_treeVersion.clear()

        path = os.path.join(env.get_project_show_asset_path(), "Release")
        subFolders = osUtils.get_subdirs(path)

        for f in subFolders:
            pathAssets = os.path.join(path, f)
            assets = osUtils.get_subdirs(pathAssets)
            if assets:
                item = QtWidgets.QTreeWidgetItem([f])
                self.gather_treeElement.addTopLevelItem(item)

    def populateReleaseUI(self):
        self.release_treeElement.clear()
        self.release_treeElementType.clear()
        self.release_treeVersion.clear()

        # get all sets in scene

        sets = cmds.ls("rigHubSet*", set=True)
        setType = []
        if sets:
            for s in sets:
                setType.append(shotBuild.getSetAssetType(s))

        setType = list(set(setType))
        for s in setType:
            item = QtWidgets.QTreeWidgetItem([s])
            self.release_treeElement.addTopLevelItem(item)

    def populateSetUI(self):
        self.sets_treeElement.clear()
        self.sets_treeElementExisting.clear()

        # populate the core asset types
        setsList = shotBuild.getAssetSetList()
        for s in setsList:
            item = QtWidgets.QTreeWidgetItem([s])
            self.sets_treeElement.addTopLevelItem(item)

    def populateDeleteUI(self):
        pass

    def buildGatherUI(self):

        verticalLayout = QtWidgets.QVBoxLayout()

        treeLayout = QtWidgets.QHBoxLayout()

        # the tree views
        self.gather_treeElement = QtWidgets.QTreeWidget()
        self.gather_treeElement.setMinimumSize(300, self.height()/1.5)
        self.gather_treeElement.setFocusPolicy(QtCore.Qt.NoFocus)

        gather_header = self.gather_treeElement.headerItem()
        gather_header.setText(0, "AssetType")

        self.gather_treeElementType = QtWidgets.QTreeWidget()
        self.gather_treeElementType.setMinimumSize(300, self.height()/1.5)
        self.gather_treeElementType.setFocusPolicy(QtCore.Qt.NoFocus)
        gather_header = self.gather_treeElementType.headerItem()
        gather_header.setText(0, "Element")

        self.gather_treeVersion = QtWidgets.QTreeWidget()
        self.gather_treeVersion.setMinimumSize(50, self.height()/1.5)
        self.gather_treeVersion.setMaximumWidth(70)
        self.gather_treeVersion.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.gather_treeVersion.setFocusPolicy(QtCore.Qt.NoFocus)

        gather_header = self.gather_treeVersion.headerItem()
        gather_header.setText(0, "Version")

        treeLayout.addWidget(self.gather_treeElement)
        treeLayout.addWidget(self.gather_treeElementType)
        treeLayout.addWidget(self.gather_treeVersion)

        buttonlayout = QtWidgets.QHBoxLayout()
        self.gather_buttonImport = QtWidgets.QPushButton("Import")
        self.gather_buttonReference = QtWidgets.QPushButton("Reference")
        buttonlayout.addWidget(self.gather_buttonImport)
        buttonlayout.addWidget(self.gather_buttonReference)
        # buttonlayout.stretch(False)
        # buttonlayout.setAlignment(QtCore.Qt.AlignRight)

        self.gather_commentBox = QtWidgets.QTextEdit()
        self.gather_commentBox.setReadOnly(True)

        verticalLayout.addLayout(treeLayout)
        verticalLayout.addSpacing(40)
        verticalLayout.addWidget(self.gather_commentBox)
        verticalLayout.addLayout(buttonlayout)

        self.gatherPageWidget.setLayout(verticalLayout)

        self.gather_treeElement.itemSelectionChanged.connect(
            self.event_gather_treeElement)
        self.gather_treeElementType.itemSelectionChanged.connect(
            self.event_gather_treeElementType)
        self.gather_treeVersion.itemSelectionChanged.connect(
            self.event_gather_treeVersion)

        self.gather_buttonImport.clicked.connect(self.event_gather_import)
        self.gather_buttonReference.clicked.connect(
            self.event_gather_reference)

    def buildReleaseUI(self):

        verticalLayout = QtWidgets.QVBoxLayout()

        treeLayout = QtWidgets.QHBoxLayout()

        # the tree views
        self.release_treeElement = QtWidgets.QTreeWidget()
        self.release_treeElement.setMinimumSize(300, self.height()/1.5)
        self.release_treeElement.setFocusPolicy(QtCore.Qt.NoFocus)

        release_header = self.release_treeElement.headerItem()
        release_header.setText(0, "AssetType")

        self.release_treeElementType = QtWidgets.QTreeWidget()
        self.release_treeElementType.setMinimumSize(300, self.height()/1.5)
        self.release_treeElementType.setFocusPolicy(QtCore.Qt.NoFocus)
        release_header = self.release_treeElementType.headerItem()
        release_header.setText(0, "Element")

        self.release_treeVersion = QtWidgets.QTreeWidget()
        self.release_treeVersion.setMinimumSize(50, self.height()/1.5)
        self.release_treeVersion.setMaximumWidth(70)
        self.release_treeVersion.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.release_treeVersion.setFocusPolicy(QtCore.Qt.NoFocus)

        release_header = self.release_treeVersion.headerItem()
        release_header.setText(0, "Version")

        treeLayout.addWidget(self.release_treeElement)
        treeLayout.addWidget(self.release_treeElementType)
        treeLayout.addWidget(self.release_treeVersion)

        self.release_buttonRelease = QtWidgets.QPushButton("Release")

        self.release_commentBox = QtWidgets.QTextEdit()
        self.release_commentBox.setEnabled(False)

        verticalLayout.addLayout(treeLayout)
        verticalLayout.addSpacing(40)
        verticalLayout.addWidget(self.release_commentBox)
        verticalLayout.addWidget(self.release_buttonRelease)

        self.releasePageWidget.setLayout(verticalLayout)

        self.release_treeElement.itemSelectionChanged.connect(
            self.event_release_treeElement)
        self.release_treeElementType.itemSelectionChanged.connect(
            self.event_release_treeElementType)

        self.release_buttonRelease.clicked.connect(self.event_release_button)

    def buildSetUI(self):

        # the tree views
        self.sets_treeElement = QtWidgets.QTreeWidget()
        self.sets_treeElement.setMinimumSize(300, self.height()/1.5)
        self.sets_treeElement.setFocusPolicy(QtCore.Qt.NoFocus)

        sets_header = self.sets_treeElement.headerItem()
        sets_header.setText(0, "AssetType")

        verticalLayout = QtWidgets.QVBoxLayout()
        self.sets_treeElementExisting = QtWidgets.QTreeWidget()
        self.sets_treeElementExisting.setMinimumSize(300, self.height()/1.5)
        self.sets_treeElementExisting.setFocusPolicy(QtCore.Qt.NoFocus)
        sets_header = self.sets_treeElementExisting.headerItem()
        sets_header.setText(0, "Existing Set Names")

        self.sets_label = QtWidgets.QLabel("Create New SetName")
        self.sets_lineEdit = QtWidgets.QLineEdit()
        self.sets_label.setAlignment(QtCore.Qt.AlignLeft)
        self.sets_combo = QtWidgets.QComboBox()
        self.sets_combo.addItems(["LODa", "LODb", "LODc", "LODd", "LODe"])

        self.sets_picker = PickerWidget(labelName="select TopNode")

        lineLayout = QtWidgets.QHBoxLayout()

        lineLayout.addWidget(self.sets_label)
        lineLayout.addWidget(self.sets_lineEdit)
        lineLayout.addWidget(self.sets_combo)

        pickLayout = QtWidgets.QVBoxLayout()
        pickLayout.addWidget(self.sets_picker)
        verticalSpacer = QtWidgets.QSpacerItem(
            10, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        pickLayout.addItem(verticalSpacer)

        pickLayout.addLayout(lineLayout)

        verticalLayout.addWidget(self.sets_treeElementExisting)

        verticalSpacer = QtWidgets.QSpacerItem(
            30, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        verticalLayout.addItem(verticalSpacer)

        verticalLayout.addLayout(pickLayout)

        verticalLayout.setSpacing(5)

        verticalLayout.setContentsMargins(0, 0, 0, 0)
        verticalLayout.setAlignment(QtCore.Qt.AlignVCenter)

        hLayout = QtWidgets.QHBoxLayout()
        hLayout.addWidget(self.sets_treeElement)
        hLayout.addLayout(verticalLayout)

        self.sets_pushButton = QtWidgets.QPushButton("Create Set")
        self.sets_pushButton.setMinimumHeight(50)

        vLayout = QtWidgets.QVBoxLayout()
        vLayout.addLayout(hLayout)
        vLayout.addLayout(verticalLayout)
        vLayout.addWidget(self.sets_pushButton)

        self.setPageWidget.setLayout(vLayout)

        self.sets_treeElement.itemSelectionChanged.connect(
            self.event_sets_treeElement)
        self.sets_treeElementExisting.itemSelectionChanged.connect(
            self.event_sets_treeElementExisting)
        self.sets_pushButton.clicked.connect(self.event_sets_createSet)

    def buildDeleteUI(self):
        pass

    '''''''''''''''''''''''''''''''''
     EVENTS
    '''''''''''''''''''''''''''''''''

    def event_release_treeElement(self):
        self.release_treeElementType.clear()
        self.release_treeVersion.clear()

        item = self.release_treeElement.currentItem().text(0)
        sets = cmds.ls("rigHubSet*{0}*".format(item), set=True)

        assetNames = []
        for s in sets:
            name = shotBuild.getSetAssetName(s)
            item = QtWidgets.QTreeWidgetItem([name])
            self.release_treeElementType.addTopLevelItem(item)

        self.release_commentBox.clear()
        self.release_commentBox.clearFocus()
        self.release_commentBox.setEnabled(False)

    def event_release_treeElementType(self):
        self.release_treeVersion.clear()

        assetType = self.release_treeElement.currentItem().text(0)
        element = self.release_treeElementType.currentItem().text(0)

        versions = shotBuild.getAssetVersions(
            env.get_project_show(), env.get_project_show_asset(), assetType, element)

        nextV = "v1"
        if versions:
            vLast = versions[-1]
            v = vLast.split("v")[1]
            nextV = "v"+str(int(v)+1)

        item = QtWidgets.QTreeWidgetItem([nextV])
        self.release_treeVersion.addTopLevelItem(item)
        self.release_treeVersion.setCurrentItem(
            self.release_treeVersion.topLevelItem(0))
        self.release_commentBox.setEnabled(True)
        self.release_commentBox.setPlaceholderText("Add Comment here")

    def event_release_button(self):

        assetType = self.release_treeElement.currentItem().text(0)
        element = self.release_treeElementType.currentItem().text(0)
        version = self.release_treeVersion.currentItem().text(0)
        comment = self.release_commentBox.toPlainText()
        if assetType and element and version:
            if comment:
                # stuff
                path = os.path.join(env.get_project_show_asset_path(
                ), "Release", assetType, element, version)
                os.makedirs(path)
                path = os.path.join(path, element+"_"+version+".ma")

                if assetType == "mayaScene":
                    shotBuild.exportScene(path, False)
                    shotBuild.saveMetaData(path, assetType,)
                else:
                    setName = "rigHubSet_"+assetType+"_"+element
                    cmds.select(setName, ne=True, replace=True)

                    # save scene
                    import rsTools.utils.scene.optimize as optimize
                    optimize.optimizeScene()
                    shotBuild.exportScene(path, True)

                    # save metadata
                    data = {"comment": comment}
                    path = os.path.join(env.get_project_show_asset_path(
                    ), "Release", assetType, element, version, "metaData.json")

                    topNode = topNodeUtil.getTopNodes(
                        assetType, element=element)[0]
                    shotBuild.saveMetaData(path, topNode, assetType, **data)

                _logger.info("Asset Released To: {0}".format(path))

            else:
                _logger.warning("Please add a release comment")

        else:
            _logger.warning("Please Select your asset to wish to release")

    def event_gather_treeElement(self):
        self.gather_treeVersion.clear()
        self.gather_commentBox.clear()
        self.gather_commentBox.clearFocus()

        item = self.gather_treeElement.currentItem().text(0)
        assets = shotBuild.findAssets(
            env.get_project_show(), env.get_project_show_asset(), item)

        if assets is not None:
            self.gather_treeElementType.clear()
            for a in assets:
                item = QtWidgets.QTreeWidgetItem([a])
                self.gather_treeElementType.addTopLevelItem(item)

    def event_gather_treeElementType(self):
        self.gather_commentBox.clear()
        self.gather_commentBox.clearFocus()

        self.gather_treeVersion.clear()
        assetType = self.gather_treeElement.currentItem().text(0)
        element = self.gather_treeElementType.currentItem().text(0)

        versions = shotBuild.getAssetVersions(
            env.get_project_show(), env.get_project_show_asset(), assetType, element)

        if versions:
            versions.reverse()
            for a in versions:
                item = QtWidgets.QTreeWidgetItem([a])
                self.gather_treeVersion.addTopLevelItem(item)
        else:
            item = QtWidgets.QTreeWidgetItem(["None"])
            self.gather_treeVersion.addTopLevelItem(item)

        self.gather_treeVersion.setCurrentItem(
            self.gather_treeVersion.topLevelItem(0))

    def event_gather_treeVersion(self):
        assetType = self.gather_treeElement.currentItem().text(0)
        element = self.gather_treeElementType.currentItem().text(0)
        version = self.gather_treeVersion.currentItem().text(0)

        path = os.path.join(env.get_project_show_asset_path(
        ), "Release", assetType, element, version, "metaData.json")
        # load commet data
        comment = shotBuild.loadMetaData(path, "comment")
        self.gather_commentBox.setText(comment)

    def event_gather_import(self):
        assetType = self.gather_treeElement.currentItem().text(0)
        element = self.gather_treeElementType.currentItem().text(0)
        version = self.gather_treeVersion.currentItem().text(0)

        fileName = element+"_"+version+".ma"
        path = os.path.join(env.get_project_show_asset_path(
        ), "Release", assetType, element, version, fileName)

        shotBuild.importScene(path)

    def event_gather_reference(self):
        assetType = self.gather_treeElement.currentItem().text(0)
        element = self.gather_treeElementType.currentItem().text(0)
        version = self.gather_treeVersion.currentItem().text(0)

        fileName = element+"_"+version+".ma"
        path = os.path.join(env.get_project_show_asset_path(
        ), "Release", assetType, element, version, fileName)

        ns = {"model": "model",
              "rigSkeleton": "rs",
              "rigPuppet": "rp",
              "rigBound": "rb"}

        shotBuild.referenceScene(path, ns[assetType])

    def event_sets_treeElement(self):
        item = self.sets_treeElement.currentItem().text(0)
        assets = shotBuild.findAssets(
            env.get_project_show(), env.get_project_show_asset(), item)

        if assets is not None:
            self.sets_treeElementExisting.clear()
            for a in assets:
                item = QtWidgets.QTreeWidgetItem([a])
                self.sets_treeElementExisting.addTopLevelItem(item)

    def event_sets_treeElementExisting(self):
        item = self.sets_treeElementExisting.currentItem().text(0)

        try:
            item = item.split("LOD")[0]
        except:
            pass
        self.sets_lineEdit.setText(item)

    def event_sets_createSet(self):
        coreName = self.sets_lineEdit.text()
        lod = self.sets_combo.currentText()
        topNode = self.sets_picker.text()
        assetType = self.sets_treeElement.currentItem().text(0)

        project = env.get_project_show()

        if coreName and topNode is not None:

            if assetType == "model":
                shotBuild.createModelSet(assetType, coreName+lod, topNode)
            elif assetType == "rigSkeleton":
                topNodeName = project+"_"+assetType+"_"+coreName+lod+"_GRP"
                rigSkeletonAsset = skeletonAsset.SkeletonAsset(
                    topNodeName, topNode)
            else:
                shotBuild.createSet(assetType, coreName+lod, topNode)
        else:
            _logger.warning("Set could not be created")

    def closeEvent(self, e):
        if isinstance(self, Hub):
            super(Hub, self).closeEvent(e)

    def create_styleSheets(self):

        # box group
        self._boxGroup.setStyleSheet('''
                                        QGroupBox { 
                                            background-color: rgba(100,150,200,20); 
                                            padding-top:5px; 
                                            border-radius: 6px; 
                                            margin-top: 0.5em;
                                        }  ''')


win = None


def run():
    global win
    if win:
        win.close()
    win = Hub(parent=qtWrap.getMayaMainWindow())
    win.show()


if __name__ == "__main__":

    try:
        test.close()  # pylint: disable=E0601
        test.deleteLater()
    except:
        pass

    test = Hub()
    test.show()
