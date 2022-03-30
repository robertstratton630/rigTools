import inspect

from . import _shelvesData
from . import shelf as _shelf
from . import shelfButton as _shelfButton

'''
        from rsTools.ui.shelves import shelfBuilder
        shelfBuilder.buildRiggingShelf()
'''


def buildShelfFromList(name, objects):
    # create item list and object
    items = list()
    shelf = _shelf.Shelf(name)

    if shelf.exists:
        shelf.destroy_shelf()

    def isButton(o): return inspect.isclass(o) and issubclass(
        o, _shelfButton.ShelfButton)  # create lamda to check if object
    for obj in objects:
        if str(obj) in ("sep", "|", "separator", "seperator"):
            items.append("separator")
        elif isButton(obj):
            items.append(obj(parentShelf=shelf))
        elif inspect.ismodule(obj):
            items += [member(parentShelf=shelf)
                      for member in dir(obj) if isButton(obj)]
        else:
            pass

    shelf._items = items
    shelf.create_shelf()

    return shelf


def buildRiggingShelf():
    buttonList = [_shelvesData.about.aboutShelfButton,
                  "seperator",
                  _shelvesData.hub.hubShelfButton,
                  _shelvesData.assetChecker.AssetCheckerShelfButton,
                  "seperator",
                  _shelvesData.skeleton.skeletonShelfButton,
                  _shelvesData.anim.animShelfButton,
                  _shelvesData.deformation.deformersShelfButton,
                  _shelvesData.controlLib.controlLibShelfButton,
                  "seperator",
                  _shelvesData.skin.skinShelfButton,
                  _shelvesData.weightmap.weightmapShelfButton,
                  "seperator",
                  _shelvesData.rename.renameShelfButton,
                  _shelvesData.rigTag.rigTagShelfButton,
                  _shelvesData.rigConnect.rigConnectShelfButton,
                  "seperator",
                  _shelvesData.pose.poseShelfButton
                  ]

    return buildShelfFromList("RiggingShelf", buttonList)
