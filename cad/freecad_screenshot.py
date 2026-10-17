"""Open a STEP file in the FreeCAD GUI and save screenshots, headless.

    xvfb-run -a -s "-screen 0 1920x1080x24" \\
        env CLICKDECK_STEP=cad/out/clickdeck_full.step CLICKDECK_OUT=cad/out/freecad \\
        ~/Applications/freecad/squashfs-root/AppRun cad/freecad_screenshot.py

Writes <CLICKDECK_OUT>_<view>.png for each view below.
"""

import os

import FreeCAD
import FreeCADGui
import ImportGui

step = os.path.abspath(os.environ["CLICKDECK_STEP"])
out = os.path.abspath(os.environ["CLICKDECK_OUT"])

# View changes are animated by default; screenshots would catch them mid-way.
FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View").SetBool(
    "UseNavigationAnimations", False)

doc = FreeCAD.newDocument("clickdeck")
ImportGui.insert(step, doc.Name)
doc.recompute()

gui_doc = FreeCADGui.getDocument(doc.Name)
view = gui_doc.activeView()
view.setCameraType("Perspective")
FreeCADGui.runCommand("Std_DrawStyle", 0)  # "As is" (shaded with edges per object)

def look(direction):
    """Point the camera along `direction` (camera -> scene) with z up."""
    d = FreeCAD.Vector(*direction).normalize()
    z = d * -1                                   # camera's local +z points back at the viewer
    x = FreeCAD.Vector(0, 0, 1).cross(z).normalize()
    y = z.cross(x)
    view.setCameraOrientation(FreeCAD.Rotation(x, y, z, "ZYX"))


# (name, direction from the camera into the scene); user sits at -y
views = [
    ("three_quarter", (-0.55, 0.75, -0.42)),  # from front-right, above
    ("front", (0.0, 0.67, -0.74)),            # roughly the user's eye line
    ("side", (-1.0, 0.0, 0.0)),               # from the right
]
for name, direction in views:
    look(direction)
    view.fitAll()
    FreeCADGui.updateGui()
    view.saveImage(f"{out}_{name}.png", 1600, 1000, "White")
    print("saved", f"{out}_{name}.png")

os._exit(0)
