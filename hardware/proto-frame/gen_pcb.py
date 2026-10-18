"""Generate the prototype frame PCB (rev C, 2 keys on the Waveshare 7B) from the CAD geometry.

    .venv/bin/python cad/build.py --no-render       # writes cad/out/proto_frame_pcb.json
    /usr/bin/python3 hardware/proto-frame/gen_pcb.py

Runs with the system Python that KiCad's `pcbnew` module is installed for
(KiCad 9). The board is fully defined here (no schematic): the full build's
two top-left keys, cut out of the full frame PCB at the 7B's top-left corner.

- Four B3U footprints: SW1/SW2 under the key windows (the full build's
  switches), SW3/SW4 above them, the second-switch option for the D8 force
  test (one switch vs two per key). Each switch has its own pad.
- Five through-hole wire pads (K1, GND, K1B, K2B, K2) on the back margin,
  off the glass, for hand-wiring to the Rev 0.5 board.
- M2 holes: pan-head screws only where the head is off the glass (left and
  back edges); countersunk holes (JLC countersink option, 90°) over the
  glass, so those heads sit flush with the underside. One of them is at the
  strip crossing between the keys, like the full build's interior supports.

The board refuses to build if a pan-head hole or a pad's solder tail lands
over the glass, and keeps copper off the countersinks.

UNTESTED. Run DRC and check everything before ordering.
"""

import json
import math
from pathlib import Path

import pcbnew
from pcbnew import FromMM, VECTOR2I

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
GEOM = json.loads((ROOT / "cad/out/proto_frame_pcb.json").read_text())
OUT = HERE / "proto-frame.kicad_pcb"
FP_LIB = Path("/usr/share/kicad/footprints")

ORIGIN = (200.0, 150.0)   # KiCad page position of CAD (0, 0); the board sits at the 7B's top-left
TRACK_W = 0.3
VIA_D, VIA_DRILL = 0.6, 0.3
PAN_HEAD_D = 3.8          # M2 pan head, bears on the underside
CSK_KEEPOUT = GEOM["csk_head"][0] / 2 + 0.3     # copper stays off the countersink (both layers)


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
for name in ("GND", "K1", "K2", "K1B", "K2B"):
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


def path(points, net, layer=pcbnew.F_Cu):
    for a, b in zip(points, points[1:]):
        track(a, b, net, layer)


def via(at, net):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pt(*at))
    v.SetWidth(FromMM(VIA_D))
    v.SetDrill(FromMM(VIA_DRILL))
    v.SetNet(net)
    board.Add(v)


def keepout(cx, cy, r, layers):
    """Rule area (no tracks, vias or pour) around a hole: countersinks, screw heads."""
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True)
    z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True)
    z.SetDoNotAllowCopperPour(True)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(False)
    ls = pcbnew.LSET()
    for layer in layers:
        ls.AddLayer(layer)
    z.SetLayerSet(ls)
    poly = z.Outline()
    poly.NewOutline()
    for k in range(24):
        a = 2 * math.pi * k / 24
        poly.Append(pt(cx + r * math.cos(a), cy + r * math.sin(a)))
    board.Add(z)


# --- Switches: SW1/SW2 under the windows (the full build's), SW3/SW4 above them
# (second-switch option). The left one of each pair is turned 180° so its
# signal pad (2) faces left.
(s1x, s1y), (s2x, s2y) = GEOM["switches"]
sw = [place("Button_Switch_SMD", "SW_SPST_B3U-1000P", "SW1", "B3U-1000P", s1x, s1y, 180, "C231329"),
      place("Button_Switch_SMD", "SW_SPST_B3U-1000P", "SW2", "B3U-1000P", s2x, s2y, 0, "C231329")]
sig = ["K1", "K2"]
if GEOM.get("switches_b"):
    (s3x, s3y), (s4x, s4y) = GEOM["switches_b"]
    sw += [place("Button_Switch_SMD", "SW_SPST_B3U-1000P", "SW3", "B3U-1000P", s3x, s3y, 180, "C231329"),
           place("Button_Switch_SMD", "SW_SPST_B3U-1000P", "SW4", "B3U-1000P", s4x, s4y, 0, "C231329")]
    sig += ["K1B", "K2B"]
for fp, s in zip(sw, sig):
    pad(fp, 1).SetNet(nets["GND"])
    pad(fp, 2).SetNet(nets[s])

# --- Wire pads (through-hole, so wires solder from either side), off the glass
tp = "TestPoint_THTPad_D1.5mm_Drill0.7mm"
tps = {}
for i, (name, (px, py)) in enumerate(GEOM["pads"].items()):
    if name not in nets:
        continue
    if name in ("K1B", "K2B") and not GEOM.get("switches_b"):
        continue
    tps[name] = place("TestPoint", tp, f"TP{i + 1}", name, px, py)
    pad(tps[name], 1).SetNet(nets[name])

# --- Mounting holes (M2, non-plated): pan-head off the glass, countersunk over it
holes = [(h, False) for h in GEOM["mount_holes_pan"]] + [(h, True) for h in GEOM["mount_holes_csk"]]
for i, ((hx, hy), csk) in enumerate(holes):
    place("MountingHole", "MountingHole_2.2mm_M2", f"H{i + 1}", "M2 countersunk 90°" if csk else "M2", hx, hy)
    if csk:
        keepout(hx, hy, CSK_KEEPOUT, (pcbnew.F_Cu, pcbnew.B_Cu))
    else:
        keepout(hx, hy, PAN_HEAD_D / 2 + 0.2, (pcbnew.B_Cu,))

# Nothing that sticks out under the board (pan screw heads, solder tails) may sit over the glass
gx0, gx1, gy0, gy1 = GEOM["glass_rect"]
check = ([(f"H{i + 1}", h, PAN_HEAD_D / 2) for i, (h, csk) in enumerate(holes) if not csk]
         + [(n, GEOM["pads"][n], 0.75) for n in tps])
for name, (px, py), rad in check:
    if gx0 - 0.3 < px + rad and px - rad < gx1 + 0.3 and gy0 - 0.3 < py + rad and py - rad < gy1 + 0.3:
        raise SystemExit(f"{name} at ({px:.2f}, {py:.2f}) is over the glass {GEOM['glass_rect']}")


def pos(p):
    v = p.GetPosition()
    return (pcbnew.ToMM(v.x) - ORIGIN[0], ORIGIN[1] - pcbnew.ToMM(v.y))


# --- Routing. The countersink at the strip crossing between the keys blocks the
# front strip, so each key's signal and ground leave on its own side: key 1
# (left) along the left margin, key 2 along the right margin. Signals on top,
# ground on the bottom layer, joined by a bus along the back margin.
pad_y = GEOM["pads"]["K1"][1]
bus_y = pad_y - 2.45                       # GND bus (bottom), between the second switches and the pads
k1x = GEOM["pads"]["K1"][0]
right_x = x1 - 1.3                         # signal channel inside the right edge (top layer)
gnd_rx = right_x - 0.6                     # ground riser beside it (bottom layer)
gnd_lx = k1x - 1.5                         # ground riser on the left margin (bottom layer)
path([pos(pad(sw[0], 2)), (k1x, s1y), pos(pad(tps["K1"], 1))], nets["K1"])
k2 = pos(pad(tps["K2"], 1))
path([pos(pad(sw[1], 2)), (right_x, s2y), (right_x, bus_y + 1.0), (k2[0], bus_y + 1.0), k2], nets["K2"])
gl = (pos(pad(sw[0], 1))[0] + 1.7, s1y)    # vias just outside each front switch's ground pad
gr = (pos(pad(sw[1], 1))[0] - 1.7, s2y)
track(pos(pad(sw[0], 1)), gl, nets["GND"])
track(pos(pad(sw[1], 1)), gr, nets["GND"])
via(gl, nets["GND"])
via(gr, nets["GND"])
path([gl, (gnd_lx, s1y), (gnd_lx, bus_y), (gnd_rx, bus_y), (gnd_rx, s2y), gr], nets["GND"], pcbnew.B_Cu)
g_pad = pos(pad(tps["GND"], 1))
track((g_pad[0], bus_y), g_pad, nets["GND"], pcbnew.B_Cu)
if GEOM.get("switches_b"):
    for fp, name in ((sw[2], "K1B"), (sw[3], "K2B")):
        a = pos(pad(fp, 2))
        track(a, (a[0], pad_y), nets[name])
        g = pos(pad(fp, 1))
        track(g, (g[0], bus_y), nets["GND"])
        via((g[0], bus_y), nets["GND"])


# --- Silkscreen
def text(s, x, y, size=1.0, layer=pcbnew.F_SilkS, rot=0.0):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(s)
    t.SetPosition(pt(x, y))
    t.SetLayer(layer)
    t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size)))
    t.SetTextThickness(FromMM(size * 0.15))
    t.SetTextAngleDegrees(rot)
    board.Add(t)


ky = GEOM["key_windows"][0][1]
text("clickdeck proto frame rev C  UNTESTED", (x0 + GEOM["key_windows"][0][0] - 9.3) / 2, ky, 0.8, rot=90)
for name in tps:
    px, py = GEOM["pads"][name]
    text(name, px, py + 1.5, 0.8)
if GEOM.get("switches_b"):
    text("SW3/SW4: 2nd switch option", (s3x + s4x) / 2, s3y + 2.0, 0.8)

board.Save(str(OUT))
print("wrote", OUT)
