"""Generate the driver bench board (D24): a DRV8311H channel and an SS6343M channel.

    /usr/bin/python3 hardware/driver-bench/gen_pcb.py

Runs with the system Python that KiCad's `pcbnew` module is installed for
(KiCad 9). Unlike the prototype frame, this board doesn't come from the CAD:
it's a small 2-layer bench board for the test kit, defined here (parts, nets,
placement) and routed by the small grid router below. Writes the board,
`netlist.txt` (the schematic, as a netlist) and `bom.csv`.

- U1 DRV8311H (TI, WQFN-24 3x3, 0.4 mm): hardware variant, MODE tied to
  AVDD (3x PWM, the lower 5 A OCP level), SLEW tied to AVDD, GAIN to AGND,
  CSAREF on AVDD, current-sense outputs unused. INHx <- PWM_x; nSLEEP and
  INLA/B/C tied together on EN1 (low: asleep, outputs Hi-Z).
- U2 SS6343M (LeadPower, QFN-24 3x4, 0.4 mm): ENA/B/C and nSLEEP tied on
  EN2, PWMA/B/C <- PWM_x.
- J1 1x10 2.54 mm to the WeAct RP2350B: PWM_A/B/C are shared by both
  channels; each channel has its own enable and fault line (10 kOhm
  pull-downs on PWM and EN, 10 kOhm pull-ups on the open-drain faults to 3V3).
- J2/J3 1x3 2.54 mm motor headers (one per channel; move the motor plug).
- J4 1x2 2.54 mm VM input: 5 V from USB (USB-C breakout through the power
  meter) or the bench supply (4.75 V test).

UNTESTED. Run DRC and check everything (footprints against the datasheets,
especially the SS6343M's) before ordering.
"""

import heapq
import math
from pathlib import Path

import numpy as np
import pcbnew
from pcbnew import FromMM, ToMM, VECTOR2I

HERE = Path(__file__).parent
OUT = HERE / "driver-bench.kicad_pcb"
FP_LIB = Path("/usr/share/kicad/footprints")

ORIGIN = (100.0, 80.0)        # KiCad page position of the board's top-left corner
W, H = 56.0, 40.0             # board size, mm (y down, as in KiCad)
CORNER_R = 2.0
TRACK = 0.2                   # signal tracks
POWER_W = 0.5                 # VM, GND and motor phases, where there's room
CLR = 0.16                    # router clearance (DRC rule: 0.15)
DRC_CLR = 0.15
EDGE = 0.4                    # copper to board edge
VIA_D, VIA_DRILL = 0.6, 0.3
RES = 0.05                    # router grid
M = 0.0375                    # grid margin (>= half a cell diagonal)
POWER = {"VM", "GND", "OUT1A", "OUT1B", "OUT1C", "OUT2A", "OUT2B", "OUT2C"}

board = pcbnew.BOARD()
ds = board.GetDesignSettings()
board.SetCopperLayerCount(2)
ds.SetCopperLayerCount(2)
ds.m_TrackMinWidth = FromMM(TRACK)
ds.m_MinClearance = FromMM(DRC_CLR)
ds.m_CopperEdgeClearance = FromMM(0.3)
ds.m_ViasMinSize = FromMM(VIA_D)
ds.m_MinThroughDrill = FromMM(VIA_DRILL)
ds.SetBoardThickness(FromMM(1.6))
nc = ds.m_NetSettings.GetDefaultNetclass()
nc.SetClearance(FromMM(DRC_CLR))
nc.SetTrackWidth(FromMM(TRACK))
nc.SetViaDiameter(FromMM(VIA_D))
nc.SetViaDrill(FromMM(VIA_DRILL))


def pt(x, y):
    return VECTOR2I(FromMM(ORIGIN[0] + x), FromMM(ORIGIN[1] + y))


def mm(v):
    return (ToMM(v.x) - ORIGIN[0], ToMM(v.y) - ORIGIN[1])


# --- Outline: rounded rectangle
def edge(shape, **kw):
    s = pcbnew.PCB_SHAPE(board, shape)
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(FromMM(0.1))
    for k, v in kw.items():
        getattr(s, "Set" + k)(pt(*v))
    board.Add(s)


r = CORNER_R
for a, b in (((r, 0), (W - r, 0)), ((W, r), (W, H - r)), ((W - r, H), (r, H)), ((0, H - r), (0, r))):
    edge(pcbnew.SHAPE_T_SEGMENT, Start=a, End=b)
for cx, cy in ((W - r, r), (W - r, H - r), (r, H - r), (r, r)):
    sx, sy = (1 if cx > W / 2 else -1), (1 if cy > H / 2 else -1)
    s = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_ARC)
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(FromMM(0.1))
    s.SetArcGeometry(pt(cx + sx * r, cy), pt(cx + sx * r * 0.7071, cy + sy * r * 0.7071), pt(cx, cy + sy * r))
    board.Add(s)

# --- Parts: ref, (library, footprint), value, x, y, rotation, LCSC, {pad: net}
QFN_DRV = ("Package_DFN_QFN", "Texas_RRW0024A_WQFN-24-1EP_3x3mm_P0.4mm_EP1.9x1.9mm")
QFN_SS = ("Package_DFN_QFN", "QFN-24-1EP_3x4mm_P0.4mm_EP1.65x2.65mm")
C0603 = ("Capacitor_SMD", "C_0603_1608Metric")
C0805 = ("Capacitor_SMD", "C_0805_2012Metric")
R0603 = ("Resistor_SMD", "R_0603_1608Metric")
HDR = ("Connector_PinHeader_2.54mm", "PinHeader_1x{:02d}_P2.54mm_Vertical")
HOLE = ("MountingHole", "MountingHole_3.2mm_M3")

U1X, U1Y = 16.0, 16.97        # the RRW's 5-pin sides sit 0.13 mm off center: keep pads on the grid
U2X, U2Y = 40.0, 17.0
JY = 36.5                     # J1 row
J1X = 16.57                   # J1 pin 1
J1_NETS = ["GND", "PWM_A", "PWM_B", "PWM_C", "EN1", "FLT1", "3V3", "FLT2", "EN2", "GND"]
jx = {n: J1X + 2.54 * i for i, n in enumerate(J1_NETS) if n != "GND"}

PARTS = [
    # Channel 1: DRV8311H, rotated so its inputs face J1 and its outputs face J2
    ("U1", QFN_DRV, "DRV8311HRRWR", U1X, U1Y, 270, "C5218862", {
        1: "FLT1", 2: "AVDD1", 6: "CP1", 7: "VM", 8: "VM", 9: "GND", 10: "OUT1A", 11: "OUT1B", 12: "OUT1C",
        13: "PWM_C", 14: "PWM_B", 15: "PWM_A", 16: "GND", 17: "AVDD1", 18: "EN1", 19: "EN1", 20: "EN1",
        21: "GND", 22: "AVDD1", 23: "AVDD1", 24: "EN1", 25: "GND"}),
    ("C1", C0805, "22uF 25V", 10.6, 11.0, 90, "C45783", {1: "VM", 2: "GND"}),
    ("C2", C0805, "22uF 25V", 12.9, 11.0, 90, "C45783", {1: "VM", 2: "GND"}),
    ("C3", C0603, "100nF", 12.0, 14.4, 0, "C14663", {1: "VM", 2: "GND"}),
    ("C4", C0603, "100nF", 15.4, 12.2, 90, "C14663", {1: "CP1", 2: "VM"}),
    ("C5", C0603, "1uF", 19.4, 21.6, 90, "C15849", {1: "AVDD1", 2: "GND"}),
    ("C6", C0603, "100nF", 18.8, 11.8, 90, "C14663", {1: "AVDD1", 2: "GND"}),
    # Channel 2: SS6343M, inputs toward J1, outputs toward J3
    ("U2", QFN_SS, "SS6343M-QF-TP", U2X, U2Y, 90, "C5370899", {
        1: "EN2", 2: "EN2", 3: "EN2", 4: "PWM_A", 5: "PWM_B", 6: "PWM_C", 7: "VM", 8: "GND", 9: "OUT2A",
        10: "OUT2B", 11: "OUT2C", 12: "GND", 13: "VM", 14: "VCP2", 15: "GND", 16: "VM", 18: "V3P3_2",
        20: "FLT2", 24: "EN2", 25: "GND"}),
    ("C7", C0805, "22uF 25V", 43.4, 12.0, 90, "C45783", {1: "VM", 2: "GND"}),
    ("C8", C0805, "22uF 25V", 45.7, 12.0, 90, "C45783", {1: "VM", 2: "GND"}),
    ("C9", C0603, "100nF", 43.0, 21.2, 90, "C14663", {1: "VM", 2: "GND"}),
    ("C10", C0603, "1uF", 41.0, 11.8, 90, "C15849", {1: "VCP2", 2: "VM"}),
    ("C11", C0603, "4.7uF", 37.6, 11.8, 90, "C19666", {1: "V3P3_2", 2: "GND"}),
    # Inputs: pull-downs on PWM and EN, pull-ups on the faults
    ("R2", R0603, "10k", jx["PWM_A"], 31.0, 90, "C25804", {1: "PWM_A", 2: "GND"}),
    ("R3", R0603, "10k", jx["PWM_B"], 31.0, 90, "C25804", {1: "PWM_B", 2: "GND"}),
    ("R4", R0603, "10k", jx["PWM_C"], 31.0, 90, "C25804", {1: "PWM_C", 2: "GND"}),
    ("R5", R0603, "10k", jx["EN1"], 31.0, 90, "C25804", {1: "EN1", 2: "GND"}),
    ("R6", R0603, "10k", jx["FLT1"], 31.0, 90, "C25804", {1: "FLT1", 2: "3V3"}),
    ("R7", R0603, "10k", jx["FLT2"], 31.0, 90, "C25804", {1: "FLT2", 2: "3V3"}),
    ("R8", R0603, "10k", jx["EN2"], 31.0, 90, "C25804", {1: "EN2", 2: "GND"}),
    # Input bulk
    ("C12", C0805, "22uF 25V", 33.0, 4.0, 0, "C45783", {1: "VM", 2: "GND"}),
    # Headers (through-hole; soldered by hand, like the breakouts' headers)
    ("J1", (HDR[0], HDR[1].format(10)), "RP2350B", J1X, JY, 90, None,
     {i + 1: n for i, n in enumerate(J1_NETS)}),
    ("J2", (HDR[0], HDR[1].format(3)), "MOTOR 1", 4.0, U1Y - 2.54, 0, None,
     {1: "OUT1A", 2: "OUT1B", 3: "OUT1C"}),
    ("J3", (HDR[0], HDR[1].format(3)), "MOTOR 2", 52.0, U2Y - 2.54, 0, None,
     {1: "OUT2C", 2: "OUT2B", 3: "OUT2A"}),
    ("J4", (HDR[0], HDR[1].format(2)), "5V IN", 26.73, 4.0, 90, None, {1: "VM", 2: "GND"}),
    ("H1", HOLE, "M3", 4.0, 4.0, 0, None, {}),
    ("H2", HOLE, "M3", W - 4.0, 4.0, 0, None, {}),
    ("H3", HOLE, "M3", 4.0, H - 4.0, 0, None, {}),
    ("H4", HOLE, "M3", W - 4.0, H - 4.0, 0, None, {}),
]

nets = {}


def net(name):
    if name not in nets:
        n = pcbnew.NETINFO_ITEM(board, name)
        board.Add(n)
        nets[name] = n
    return nets[name]


fps = {}
for ref, (lib, name), value, x, y, rot, lcsc, pads in PARTS:
    fp = pcbnew.FootprintLoad(str(FP_LIB / f"{lib}.pretty"), name)
    if fp is None:
        raise SystemExit(f"footprint {lib}:{name} not found")
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetPosition(pt(x, y))
    fp.SetOrientationDegrees(rot)
    if lcsc:
        fp.SetField("LCSC", lcsc)
        fp.GetFieldByName("LCSC").SetVisible(False)
    fp.Value().SetVisible(False)
    fp.Reference().SetVisible(False)
    for p in fp.Pads():
        if p.GetNumber() and int(p.GetNumber()) in pads:
            p.SetNet(net(pads[int(p.GetNumber())]))
    board.Add(fp)
    fps[ref] = fp

# Thermal vias in each exposed pad (to the bottom ground pour)
EP_VIAS = {"U1": [(-0.5, -0.5), (0.5, -0.5), (-0.5, 0.5), (0.5, 0.5)],
           "U2": [(-0.55, -0.4), (0.55, -0.4), (-0.55, 0.4), (0.55, 0.4)]}

# --- Router: an A* on a RES grid over both copper layers. Every copper shape is
# painted into one grid per clearance class with the id of its net: a node is
# free for net n if it's empty or n's own. Paths are then pulled straight.
NX, NY = int(round(W / RES)) + 1, int(round(H / RES)) + 1
LAYERS = (pcbnew.F_Cu, pcbnew.B_Cu)
INFL = {"trk": TRACK / 2 + CLR + M, "via": VIA_D / 2 + CLR + M, "pwr": POWER_W / 2 + CLR + M}
grid = {c: np.full((2, NX, NY), -1, dtype=np.int32) for c in INFL}
XS = np.arange(NX) * RES
YS = np.arange(NY) * RES
net_id = {}


def nid(name):
    return net_id.setdefault(name, len(net_id))


for c, infl in INFL.items():                      # board edge (and the rounded corners, roughly)
    lim = EDGE + infl - CLR - M
    gx, gy = np.meshgrid(XS, YS, indexing="ij")
    bad = (gx < lim) | (gy < lim) | (gx > W - lim) | (gy > H - lim)
    for cx, cy in ((r, r), (W - r, r), (r, H - r), (W - r, H - r)):
        q = (np.abs(gx - cx) <= r) & (np.abs(gy - cy) <= r) & ((gx - cx) * (cx - W / 2) > 0) \
            & ((gy - cy) * (cy - H / 2) > 0)
        bad |= q & (np.hypot(gx - cx, gy - cy) > r - lim)
    grid[c][:, bad] = -2


def paint(kind, geom, n, layers):
    """kind: 'rect' (cx, cy, hw, hh), 'seg' (x0, y0, x1, y1, hw) or 'circ' (cx, cy, r)."""
    if kind == "rect":
        cx, cy, hw, hh = geom
        bb = (cx - hw, cy - hh, cx + hw, cy + hh)
    elif kind == "seg":
        x0, y0, x1, y1, hw = geom
        bb = (min(x0, x1) - hw, min(y0, y1) - hw, max(x0, x1) + hw, max(y0, y1) + hw)
    else:
        cx, cy, rr = geom
        bb = (cx - rr, cy - rr, cx + rr, cy + rr)
    for c, infl in INFL.items():
        i0, i1 = max(0, int((bb[0] - infl) / RES)), min(NX, int((bb[2] + infl) / RES) + 2)
        j0, j1 = max(0, int((bb[1] - infl) / RES)), min(NY, int((bb[3] + infl) / RES) + 2)
        if i0 >= i1 or j0 >= j1:
            continue
        gx, gy = np.meshgrid(XS[i0:i1], YS[j0:j1], indexing="ij")
        if kind == "rect":
            d = np.hypot(np.maximum(np.abs(gx - cx) - hw, 0), np.maximum(np.abs(gy - cy) - hh, 0))
        elif kind == "seg":
            dx, dy = x1 - x0, y1 - y0
            ll = dx * dx + dy * dy
            t = np.clip(((gx - x0) * dx + (gy - y0) * dy) / ll, 0, 1) if ll > 0 else 0
            d = np.hypot(gx - (x0 + t * dx), gy - (y0 + t * dy)) - hw
        else:
            d = np.hypot(gx - cx, gy - cy) - rr
        mask = d < infl
        for li in layers:
            g = grid[c][li, i0:i1, j0:j1]
            sub = g[mask]
            g[mask] = np.where(sub == -1, n, np.where(sub == n, n, -2))


pad_info = {}                                     # (ref, pad) -> (net, cx, cy, hw, hh, layers)
for ref, fp in fps.items():
    for p in fp.Pads():
        bb = p.GetBoundingBox()
        x0, y0 = mm(bb.GetOrigin())
        x1, y1 = mm(bb.GetEnd())
        cx, cy, hw, hh = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
        name = p.GetNetname()
        if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
            paint("circ", (cx, cy, hw + 0.3), -2, (0, 1))   # hole + a little: nothing nearby
            continue
        layers = [i for i, L in enumerate(LAYERS) if p.IsOnLayer(L)]
        if not name:
            paint("rect", (cx, cy, hw, hh), -2, layers)     # unused pins (SOx, NC): keep off them
            continue
        paint("rect", (cx, cy, hw, hh), nid(name), layers)
        pad_info.setdefault((ref, p.GetNumber()), (name, cx, cy, hw, hh, layers))

tracks = []                                       # (net, layer, (x0, y0), (x1, y1), width)
vias = []                                         # (net, (x, y))


def add_track(name, li, a, b, w=TRACK):
    tracks.append([name, li, a, b, w])
    paint("seg", (*a, *b, w / 2), nid(name), (li,))


def via_ok(at, n):
    """Holes stay apart (JLC's hole spacing); an existing via of the same net can be reused."""
    for vn, (vx, vy) in vias:
        d = math.hypot(vx - at[0], vy - at[1])
        if d < 0.01:
            return vn == n
        if d < VIA_D + 0.35:
            return False
    return True


def add_via(name, at):
    if any(math.hypot(v[1][0] - at[0], v[1][1] - at[1]) < 0.01 for v in vias):
        return
    vias.append((name, at))
    paint("circ", (*at, VIA_D / 2), nid(name), (0, 1))


for ref, offs in EP_VIAS.items():
    x, y = mm(fps[ref].GetPosition())
    for dx, dy in offs:
        add_via("GND", (x + dx, y + dy))


stubs, tied, on_ep = [], set(), set()


def qfn_stubs(ref, reach=0.5):
    """Escape stubs: every connected pin gets a straight stub out past its pad (ground
    pins go inward onto the exposed pad instead), and neighbouring pins on one net are
    tied at their stub ends, so the router starts clear of the chip's 0.4 mm pitch."""
    cx, cy = mm(fps[ref].GetPosition())
    _, ex, ey, ehw, ehh, _ = pad_info[(ref, "25")]
    ends = {}
    for (rf, num), (name, px, py, hw, hh, _l) in pad_info.items():
        if rf != ref or num == "25":
            continue
        horiz = hw > hh
        d = (1 if px > cx else -1, 0) if horiz else (0, 1 if py > cy else -1)
        inside = abs(py - ey) < ehh - 0.15 if horiz else abs(px - ex) < ehw - 0.15
        if name == "GND" and inside:
            end = (ex + d[0] * (ehw - 0.3), py) if horiz else (px, ey + d[1] * (ehh - 0.3))
            add_track(name, 0, (px, py), end)
            on_ep.add((ref, num))
            continue
        half = hw if horiz else hh
        end = (px + d[0] * (half + reach), py + d[1] * (half + reach))
        add_track(name, 0, (px, py), end)
        stubs.append(tracks[-1])
        ends[int(num)] = (name, end)
    for a, (na, ea) in ends.items():
        b = 1 if a == 24 else a + 1
        if b in ends and ends[b][0] == na:
            add_track(na, 0, ea, ends[b][1])
            tied.update((ea, ends[b][1]))


for ref in EP_VIAS:
    qfn_stubs(ref)


def node(x, y):
    return int(round(x / RES)), int(round(y / RES))


def free(c, li, i, j, n):
    v = grid[c][li, i, j]
    return v == -1 or v == n


DIRS = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
        (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)]
VIA_COST = 20.0


def astar(name, src, dst, box_margin=6.0):
    """src/dst: pad keys. Returns a list of (layer, i, j) or None."""
    n = nid(name)
    _, sx, sy, shw, shh, sl = pad_info[src]
    _, tx, ty, thw, thh, tl = pad_info[dst]
    bcost = 1.0 if name == "GND" else 2.0          # keep the bottom mostly for the ground pour
    lo_i, lo_j = node(min(sx, tx) - box_margin, min(sy, ty) - box_margin)
    hi_i, hi_j = node(max(sx, tx) + box_margin, max(sy, ty) + box_margin)
    lo_i, lo_j, hi_i, hi_j = max(lo_i, 0), max(lo_j, 0), min(hi_i, NX - 1), min(hi_j, NY - 1)

    def inside(i, j, cx, cy, hw, hh):
        # inside the pad's inscribed square, so round and oval pads count too
        return abs(i * RES - cx) <= min(0.7 * hw, hw - 0.05) and abs(j * RES - cy) <= min(0.7 * hh, hh - 0.05)

    ti, tj = node(tx, ty)

    def h(i, j):
        dx, dy = abs(i - ti), abs(j - tj)
        return (max(dx, dy) - min(dx, dy)) + 1.414 * min(dx, dy)

    openq, g, came = [], {}, {}
    i0, j0 = node(sx - shw, sy - shh)
    i1, j1 = node(sx + shw, sy + shh)
    for li in sl:
        for i in range(i0, i1 + 1):
            for j in range(j0, j1 + 1):
                if inside(i, j, sx, sy, shw, shh) and free("trk", li, i, j, n):
                    s = (li, i, j)
                    g[s] = 0.0
                    heapq.heappush(openq, (h(i, j), 0.0, s))
    while openq:
        f, gc, s = heapq.heappop(openq)
        if gc > g.get(s, 1e18):
            continue
        li, i, j = s
        if li in tl and inside(i, j, tx, ty, thw, thh):
            path = [s]
            while path[-1] in came:
                path.append(came[path[-1]])
            return path[::-1]
        mult = bcost if li == 1 else 1.0
        for di, dj, c in DIRS:
            a, b = i + di, j + dj
            if not (lo_i <= a <= hi_i and lo_j <= b <= hi_j) or not free("trk", li, a, b, n):
                continue
            if di and dj and not (free("trk", li, a, j, n) or free("trk", li, i, b, n)):
                continue
            t = (li, a, b)
            ng = gc + c * mult
            if ng < g.get(t, 1e18):
                g[t] = ng
                came[t] = s
                heapq.heappush(openq, (ng + h(a, b), ng, t))
        o = 1 - li
        if free("via", 0, i, j, n) and free("via", 1, i, j, n) and via_ok((i * RES, j * RES), name):
            t = (o, i, j)
            ng = gc + VIA_COST
            if ng < g.get(t, 1e18):
                g[t] = ng
                came[t] = s
                heapq.heappush(openq, (ng + h(i, j), ng, t))
    return None


def seg_free(c, li, a, b, n):
    """Every point along a-b is on a node that's free for n (class c)."""
    ln = math.hypot(b[0] - a[0], b[1] - a[1])
    k = max(1, int(ln / (RES / 2)))
    for s in range(k + 1):
        x = a[0] + (b[0] - a[0]) * s / k
        y = a[1] + (b[1] - a[1]) * s / k
        i, j = node(x, y)
        if not (0 <= i < NX and 0 <= j < NY) or not free(c, li, i, j, n):
            return False
    return True


def commit(name, path):
    """Pull the path straight per layer run, then add its tracks and vias."""
    n = nid(name)
    runs, cur = [], [path[0]]
    for s in path[1:]:
        if s[0] != cur[-1][0]:
            runs.append(cur)
            cur = [s]
        else:
            cur.append(s)
    runs.append(cur)
    for k, run in enumerate(runs):
        li = run[0][0]
        pts = [(i * RES, j * RES) for _, i, j in run]
        out = [pts[0]]
        a = 0
        while a < len(pts) - 1:
            b = len(pts) - 1
            while b > a + 1 and not seg_free("trk", li, pts[a], pts[b], n):
                b -= 1
            out.append(pts[b])
            a = b
        for p0, p1 in zip(out, out[1:]):
            if p0 != p1:
                add_track(name, li, p0, p1)
        if k < len(runs) - 1:
            add_via(name, out[-1])


def mst(keys):
    """Prim's tree over the pads of one net (edges in routing order)."""
    done, rest, edges = [keys[0]], list(keys[1:]), []
    while rest:
        best = min(((a, b) for a in done for b in rest),
                   key=lambda e: math.dist(pad_info[e[0]][1:3], pad_info[e[1]][1:3]))
        edges.append(best)
        done.append(best[1])
        rest.remove(best[1])
    return edges


by_net = {}
for key, (name, *_rest) in pad_info.items():
    by_net.setdefault(name, []).append(key)
# Ground pins with a stub onto their exposed pad are joined already, and the exposed
# pads join the pour through their vias (DRC checks the pour connects them)
by_net["GND"] = [k for k in by_net["GND"] if k not in on_ep and k[1] != "25"]

ORDER = ["EN1", "FLT1", "AVDD1", "EN2", "CP1", "VCP2", "V3P3_2", "FLT2", "PWM_A", "PWM_B", "PWM_C",
         "OUT1A", "OUT1B", "OUT1C", "OUT2A", "OUT2B", "OUT2C", "3V3", "VM", "GND"]
assert set(ORDER) == set(by_net), set(by_net) ^ set(ORDER)
failed = []
for name in ORDER:
    for a, b in mst(by_net[name]):
        p = astar(name, a, b) or astar(name, a, b, box_margin=60.0)
        if p is None:
            failed.append(f"{name}: {a} -> {b}")
            continue
        commit(name, p)

# Escape stubs the route didn't use (it left from inside the pad) would dangle: drop them
ends_used = {}
for t in tracks:
    if not any(t is s_ for s_ in stubs):
        for p_ in (t[2], t[3]):
            ends_used[(round(p_[0], 3), round(p_[1], 3))] = True
for _, at in vias:
    ends_used[(round(at[0], 3), round(at[1], 3))] = True
for s_ in stubs:
    e = (round(s_[3][0], 3), round(s_[3][1], 3))
    if s_[3] not in tied and e not in ends_used:
        tracks.remove(s_)

# Widen power tracks where there's room: split into short pieces, widen each that clears
for t in [t for t in tracks if t[0] in POWER]:
    name, li, a, b, w = t
    ln = math.hypot(b[0] - a[0], b[1] - a[1])
    k = max(1, int(ln / 0.5))
    pieces = [((a[0] + (b[0] - a[0]) * s / k, a[1] + (b[1] - a[1]) * s / k),
               (a[0] + (b[0] - a[0]) * (s + 1) / k, a[1] + (b[1] - a[1]) * (s + 1) / k)) for s in range(k)]
    tracks.remove(t)
    for p0, p1 in pieces:
        wide = seg_free("pwr", li, p0, p1, nid(name))
        add_track(name, li, p0, p1, POWER_W if wide else TRACK)

for name, li, a, b, w in tracks:
    tr = pcbnew.PCB_TRACK(board)
    tr.SetStart(pt(*a))
    tr.SetEnd(pt(*b))
    tr.SetWidth(FromMM(w))
    tr.SetLayer(LAYERS[li])
    tr.SetNet(net(name))
    board.Add(tr)
for name, at in vias:
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pt(*at))
    v.SetWidth(FromMM(VIA_D))
    v.SetDrill(FromMM(VIA_DRILL))
    v.SetNet(net(name))
    board.Add(v)

# --- Ground pour on both layers (solid pad connections)
for L in LAYERS:
    z = pcbnew.ZONE(board)
    z.SetLayer(L)
    z.SetNet(net("GND"))
    z.SetLocalClearance(FromMM(0.25))
    z.SetMinThickness(FromMM(0.25))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    poly = z.Outline()
    poly.NewOutline()
    for x, y in ((0.3, 0.3), (W - 0.3, 0.3), (W - 0.3, H - 0.3), (0.3, H - 0.3)):
        poly.Append(pt(x, y))
    board.Add(z)


# --- Silkscreen
def text(s, x, y, size=1.0, rot=0.0, layer=pcbnew.F_SilkS):
    """Silkscreen text (mirrored on the bottom layer, so it reads from below)."""
    t = pcbnew.PCB_TEXT(board)
    t.SetText(s)
    t.SetPosition(pt(x, y))
    t.SetLayer(layer)
    t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size)))
    t.SetTextThickness(FromMM(size * 0.15))
    t.SetTextAngleDegrees(rot)
    t.SetMirrored(layer == pcbnew.B_SilkS)
    board.Add(t)


for i, n in enumerate(J1_NETS):
    text(n.replace("PWM_", ""), J1X + 2.54 * i, JY - 2.3 if i % 2 else JY + 2.4, 0.8)
for k, ph in enumerate("ABC"):                  # phase letters beside each motor header pin
    text(ph, 1.7, U1Y - 2.54 + 2.54 * k, 0.8)
    text("CBA"[k], W - 1.7, U2Y - 2.54 + 2.54 * k, 0.8)
text("DRV8311H", U1X, 24.5, 1.0)
text("SS6343M", U2X, 24.5, 1.0)
text("5V  GND", 28.0, 6.4, 0.8)
text("clickdeck driver bench  UNTESTED", W / 2, 27.0, 0.8)
text("one motor channel enabled at a time", W / 2, 1.6, 0.8, layer=pcbnew.B_SilkS)

board.Save(str(OUT))
filled = pcbnew.LoadBoard(str(OUT))                # the filler needs a board loaded from disk
pcbnew.ZONE_FILLER(filled).Fill(filled.Zones())
filled.Save(str(OUT))

# --- Netlist (the schematic for this board) and the JLC BOM
lines = ["# driver-bench netlist (generated by gen_pcb.py; UNTESTED)", ""]
for name in sorted(by_net):
    pins = sorted({f"{ref}.{p}" for ref, p in by_net[name]} | {f"{ref}.{p}" for (ref, p), v in pad_info.items()
                                                               if v[0] == name})
    lines.append(f"{name}: {' '.join(pins)}")
lines += ["", "Not connected: U1.3 U1.4 U1.5 (SOC, SOB, SOA: current-sense outputs, unused), "
          "U2.17 U2.19 U2.21 U2.22 U2.23 (NC)", ""]
(HERE / "netlist.txt").write_text("\n".join(lines))
rows = {}
for ref, (lib, name), value, *_x, lcsc, _p in PARTS:
    if lcsc:
        rows.setdefault((value, name, lcsc), []).append(ref)
bom = ["Comment,Designator,Footprint,LCSC"]
bom += [f"{v},\"{','.join(refs)}\",{fpn},{c}" for (v, fpn, c), refs in rows.items()]
(HERE / "bom.csv").write_text("\n".join(bom) + "\n")
print("wrote", OUT, f"({len(tracks)} tracks, {len(vias)} vias)")
if failed:
    raise SystemExit("unrouted:\n  " + "\n  ".join(failed))
