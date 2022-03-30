import pymel.core as pm
import maya.cmds as cmds
import rsTools.utils.transforms.transforms as tUtils


def optimizeScene():
    tUtils.cleanAllShapeNodes()

    pm.mel.source('cleanUpScene')
    pm.mel.scOpt_performOneCleanup({
        'setsOption',
        'nurbsSrfOption',
        'partitionOption',
        'animationCurveOption',
        'deformerOption',
        'unusedSkinInfsOption',
        'brushOption',
        'shaderOption',
        'shadingNetworksOption'
    }
    )
