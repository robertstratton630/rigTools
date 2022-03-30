import maya.cmds as cmds
import maya.mel as mel


def createCurve(name, transforms):
    node = cmds.createNode("rigCurve", n=name+"_RCN")
    if transforms:
        for i, t in enumerate(transforms):
            cmds.connectAttr(
                t+".worldMatrix[0]", node+".inMatrix[{0}]".format(i))
            cmds.connectAttr(t+".translate", node +
                             ".inTranslate[{0}]".format(i))

    curve = cmds.createNode("nurbsCurve", n=name+"_CRV")
    cmds.connectAttr(node+".outputCurve", curve+".create")
    return node


createCurve("test", cmds.ls(sl=True))


'''

global proc string rig_createBuildCurve(string $name,string $transforms[],string $args)
{

	string $node = `createNode -n "rig_buildCurve#" rig_buildCurve`;

	int $i=0;
	for ($t in $transforms)
	{
		rig_connect(($t+".worldMatrix[0]"),($node+".inMatrix["+$i+"]"));
		rig_connect(($t+".translate"),($node+".inTranslate["+$i+"]"));
		$i++;
	}

	string $curveData = `createNode nurbsCurve -name ($name+"Shape")`;
	rig_connect(($node+".outputCurve"),($curveData+".create"));
	return $node;
}
'''
