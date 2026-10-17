"""Generate the prototype frame PCB (2 keys) from the CAD geometry.

    .venv/bin/python cad/build.py --no-render       # writes cad/out/proto_frame_pcb.json
    /usr/bin/python3 hardware/proto-frame/gen_pcb.py

Runs with the system Python that KiCad's `pcbnew` module is installed for
(KiCad 9). The board is fully defined here (no schematic): two B3U switches,
three through-hole wire pads (GND, K1, K2) for hand-wiring to the ESP32-S3
dev board, and four M2 holes to hang it from the top plate. The board is
wider than the 2.4" glass so the screw heads and the pads' solder tails sit
off the glass (checked below).

UNTESTED. Run DRC and check everything before ordering.
"""

import json
from pathlib import Path

import pcbnew
from pcbnew import FromMM, VECTOR2I

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
GEOM = json.loads((ROOT / "cad/out/proto_frame_pcb.json").read_text())
OUT = HERE / "proto-frame.kicad_pcb"
FP_LIB = Path("/usr/share/kicad/footprints")

ORIGIN = (100.0, 100.0)   # KiCad page position of CAD (0, 0)
TRACK_W = 0.3
VIA_D, VIA_DRILL = 0.6, 0.3


def pt(x, y):
    """CAD mm (y up) -> KiCad internal units (y down)."""
    return VECTOR2I(FromMM(ORIGIN[0] + x), FromMM(ORIGIN[1] - y))


board = pcbnew.BOARD()
ds = board.GetDesignSettings()
board.SetCopperLayerCount(2)
ds.SetCopperLayerCount(2)
ds.m_TrackMinWidth = FromMM(0.2)
ds.m_MinClearance = FromMM(0.2)
ds.m_CopperEdgeClearance = FromMM(GEOM.get("copper_edge", 0.3))
ds.SetBoardThickness(FromMM(GEOM["thickness"]))


def edge_line(a, b):
    s = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_SEGMENT)
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetStart(pt(*a))
    s.SetEnd(pt(*b))
    s.SetWidth(FromMM(0.1))
    board.Add(s)


def edge_arc(center, start, end):
    s = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_ARC)
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetCenter(pt(*center))
    s.SetStart(pt(*start))
    s.SetEnd(pt(*end))
    s.SetWidth(FromMM(0.1))
    board.Add(s)


def edge_rrect(x0, x1, y0, y1, r):
    """Rounded rectangle on Edge.Cuts (outline or window; windows get the router's radius)."""
    edge_line((x0 + r, y0), (x1 - r, y0))
    edge_line((x1, y0 + r), (x1, y1 - r))
    edge_line((x1 - r, y1), (x0 + r, y1))
    edge_line((x0, y1 - r), (x0, y0 + r))
    # Corners (start/end order matters: KiCad sweeps start -> end clockwise on screen)
    edge_arc((x1 - r, y0 + r), (x1, y0 + r), (x1 - r, y0))
    edge_arc((x1 - r, y1 - r), (x1 - r, y1), (x1, y1 - r))
    edge_arc((x0 + r, y1 - r), (x0, y1 - r), (x0 + r, y1))
    edge_arc((x0 + r, y0 + r), (x0 + r, y0), (x0, y0 + r))


# --- Outline: rounded rectangle, then the windows as internal cutouts
x0, x1, y0, y1 = GEOM["outline"]
edge_rrect(x0, x1, y0, y1, GEOM["corner_r"])
wr = GEOM.get("window_corner_r", 0.5)
for cx, cy, w, h in GEOM["key_windows"] + GEOM["other_windows"]:
    edge_rrect(cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2, wr)

# --- Nets
nets = {}
for name in ("GND", "K1", "K2"):
    n = pcbnew.NETINFO_ITEM(board, name)
    board.Add(n)
    nets[name] = n


def place(lib, name, ref, value, x, y, rot=0.0, lcsc=None):
    fp = pcbnew.FootprintLoad(str(FP_LIB / f"{lib}.pretty"), name)
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetPosition(pt(x, y))
    fp.SetOrientationDegrees(rot)
    if lcsc:
        fp.SetField("LCSC", lcsc)
        fp.GetFieldByName("LCSC").SetVisible(False)
    fp.Reference().SetVisible(False)   # labels are added as plain silkscreen text below
    board.Add(fp)
    return fp


def pad(fp, number):
    return next(p for p in fp.Pads() if p.GetNumber() == str(number))


def track(a, b, net, layer=pcbnew.F_Cu, width=TRACK_W):
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(pt(*a))
    t.SetEnd(pt(*b))
    t.SetWidth(FromMM(width))
    t.SetLayer(layer)
    t.SetNet(net)
    board.Add(t)


def via(at, net):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pt(*at))
    v.SetWidth(FromMM(VIA_D))
    v.SetDrill(FromMM(VIA_DRILL))
    v.SetNet(net)
    board.Add(v)


# --- Switches. SW1 is turned 180° so its signal pad (2) faces left.
(s1x, s1y), (s2x, s2y) = GEOM["switches"]
sw1 = place("Button_Switch_SMD", "SW_SPST_B3U-1000P", "SW1", "B3U-1000P", s1x, s1y, 180, "C231329")
sw2 = place("Button_Switch_SMD", "SW_SPST_B3U-1000P", "SW2", "B3U-1000P", s2x, s2y, 0, "C231329")
pad(sw1, 1).SetNet(nets["GND"])
pad(sw1, 2).SetNet(nets["K1"])
pad(sw2, 1).SetNet(nets["GND"])
pad(sw2, 2).SetNet(nets["K2"])

# --- Wire pads (through-hole, so wires solder from either side)
mx = x1 - 3.0
tp = "TestPoint_THTPad_D1.5mm_Drill0.7mm"
p_k1 = place("TestPoint", tp, "TP1", "K1", -mx, s1y)
p_gnd = place("TestPoint", tp, "TP2", "GND", -mx, 2.0)
p_k2 = place("TestPoint", tp, "TP3", "K2", mx, s2y)
pad(p_k1, 1).SetNet(nets["K1"])
pad(p_gnd, 1).SetNet(nets["GND"])
pad(p_k2, 1).SetNet(nets["K2"])

# --- Mounting holes (M2, non-plated)
for i, (hx, hy) in enumerate(GEOM["mount_holes"]):
    place("MountingHole", "MountingHole_2.2mm_M2", f"H{i + 1}", "M2", hx, hy)

# Nothing that sticks out under the board (screw heads, solder tails) may sit over the glass
gx, gy = GEOM.get("glass_half", (0.0, 0.0))
for name, (px, py), rad in ([(f"H{i + 1}", h, 3.8 / 2) for i, h in enumerate(GEOM["mount_holes"])]
                            + [("TP1", (-mx, s1y), 0.75), ("TP2", (-mx, 2.0), 0.75), ("TP3", (mx, s2y), 0.75)]):
    if abs(px) - rad < gx + 0.3 and abs(py) - rad < gy + 0.3:
        raise SystemExit(f"{name} at ({px:.2f}, {py:.2f}) is over the glass (+-{gx:.2f} x +-{gy:.2f})")

# --- Routing. The strip between the key windows and the knob-display
# window is the only channel, so: K1/K2 run out along it on the top layer,
# GND joins the two switches on top and leaves on the bottom layer.
def pos(p):
    v = p.GetPosition()
    return (pcbnew.ToMM(v.x) - ORIGIN[0], ORIGIN[1] - pcbnew.ToMM(v.y))


track(pos(pad(sw1, 2)), pos(pad(p_k1, 1)), nets["K1"])
track(pos(pad(sw2, 2)), pos(pad(p_k2, 1)), nets["K2"])
track(pos(pad(sw1, 1)), pos(pad(sw2, 1)), nets["GND"])
gv = (pos(pad(sw1, 1))[0] + 1.6, s1y)
via(gv, nets["GND"])
corner_x = -(x1 - 5.5)
gnd_pad = pos(pad(p_gnd, 1))
track(gv, (corner_x, s1y), nets["GND"], pcbnew.B_Cu)
track((corner_x, s1y), (corner_x, gnd_pad[1]), nets["GND"], pcbnew.B_Cu)
track((corner_x, gnd_pad[1]), gnd_pad, nets["GND"], pcbnew.B_Cu)

# --- Silkscreen
def text(s, x, y, size=1.0, layer=pcbnew.F_SilkS):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(s)
    t.SetPosition(pt(x, y))
    t.SetLayer(layer)
    t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size)))
    t.SetTextThickness(FromMM(size * 0.15))
    board.Add(t)


text("clickdeck proto frame", 0, y0 + 1.6, 0.9)
text("rev B  UNTESTED", 0, y1 - 1.6, 0.9)
text("K1", -mx, s1y - 1.8, 0.8)
text("GND", -mx, 2.0 + 1.8, 0.8)
text("K2", mx, s2y - 1.8, 0.8)

board.Save(str(OUT))
print("wrote", OUT)
