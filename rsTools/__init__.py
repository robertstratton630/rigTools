import maya.cmds as cmds
from rsTools.utils import singleton
from utils import deformers
from ui.shelves import _shelvesData
from ui import shelves, widgets
from core import facial
from core import deformation
from core import animation
from rsTools.utils.osUtils import enviroments
import os
import core
import ui
import utils

# reload base files

reload(core)
reload(ui)
reload(utils)


# form core
reload(animation)
reload(deformation)
reload(facial)

# from ui
reload(shelves)
reload(widgets)
reload(_shelvesData)

# from utils
reload(deformers)

# create singleton for laoding enviroments
env = singleton.loadEnviromentSingleton()


# run this scriptJob to store previous enviroments
job = -1
if not cmds.scriptJob(exists=job):
    job = cmds.scriptJob(
        e=["quitApplication", enviroments.cache_enviroment], protected=True)
