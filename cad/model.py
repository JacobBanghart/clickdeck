"""Parametric models for clickdeck.

Coordinates: x to the right, y toward the back (the user sits at -y), z up.
The origin is the center of the display's active area, at the case floor.
Every assembly is a list of `Item`s; `explode` is how many EXPLODE steps a
part moves up in the exploded views.
"""

import math
from dataclasses import dataclass

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    BuildSketch,
    Color,
    Compound,
    Cone,
    Cylinder,
    Locations,
    Mode,
    Part,
    Plane,
    Polygon,
    Rot,
    Sphere,
    Vector,
    Pos,
    Rectangle,
    RectangleRounded,
    Circle,
    Sketch,
    extrude,
    fillet,
)

import params as P

MIN = (Align.CENTER, Align.CENTER, Align.MIN)

# Colors
C_CASE = Color(0.16, 0.16, 0.18)
C_PLATE = Color(0.10, 0.10, 0.11)
C_PCB = Color(0.05, 0.36, 0.20)
C_PANEL = Color(0.22, 0.22, 0.24)
C_SCREEN = Color(0.02, 0.03, 0.06)
C_CAP = Color(0.80, 0.92, 1.00, 0.35)
C_SWITCH = Color(0.85, 0.85, 0.82)
C_CHIP = Color(0.05, 0.05, 0.05)
C_MOTOR = Color(0.62, 0.64, 0.68)
C_MAGNET = Color(0.75, 0.30, 0.25)
C_KNOB = Color(0.25, 0.25, 0.28)
C_STANDOFF = Color(0.80, 0.70, 0.35)
C_SCREW = Color(0.55, 0.57, 0.62)
C_CABLE = Color(0.85, 0.30, 0.20)
C_FOOT = Color(0.12, 0.12, 0.12)
C_BRASS = Color(0.78, 0.62, 0.30)
TILE_COLORS = [
    Color(0.95, 0.45, 0.20), Color(0.25, 0.60, 0.95), Color(0.40, 0.80, 0.35),
    Color(0.90, 0.30, 0.55), Color(0.95, 0.80, 0.25), Color(0.55, 0.40, 0.90),
]
C_KNOB_TILE = Color(0.15, 0.75, 0.75)


@dataclass
class Item:
    part: Part
    label: str
    color: Color
    explode: int = 0


# --------------------------------------------------------------------------
# Vertical stack. Everything is derived from the knob: the motor sets how
# high the top plate is, and the key stack hangs down from the top plate.
# --------------------------------------------------------------------------
@dataclass
class Stack:
    floor_top: float
    bp_bot: float          # backplane (D23); the prototype stack has no backplane (= knob_pcb)
    bp_top: float
    knob_pcb_bot: float    # module PCB (the motor or encoder sits on it)
    knob_pcb_top: float
    motor_bot: float
    motor_top: float
    plate_bot: float
    plate_top: float
    flange_top: float
    flange_bot: float
    sw_top: float
    pcb_top: float
    pcb_bot: float
    glass: float
    cap_top: float


def make_stack(floor_t: float, plate_t: float, modular: bool = True) -> Stack:
    """modular: the full build's knob slots (D23): the backplane BP_UNDER above the floor,
    its pogo pins, then the module PCB POGO_WORK above it. Otherwise (prototype) the old
    single knob board KNOB_UNDER_CLEAR above the floor."""
    if modular:
        bp_bot = floor_t + P.BP_UNDER
        bp_top = bp_bot + P.PCB_T
        knob_pcb_bot = bp_top + P.POGO_WORK
    else:
        knob_pcb_bot = floor_t + P.KNOB_UNDER_CLEAR
        bp_bot, bp_top = knob_pcb_bot, knob_pcb_bot + P.PCB_T
    knob_pcb_top = knob_pcb_bot + P.PCB_T
    motor_bot = knob_pcb_top + P.MT6701[2] + P.SENSOR_GAP + P.MAGNET_H
    motor_top = motor_bot + P.MOTOR_H
    adapter_h = P.ADAPTER_H if P.KNOB_STYLE == "shaft_adapter" else P.HUB_FLANGE_T
    plate_bot = motor_top + adapter_h + P.MOTOR_TO_PLATE
    plate_top = plate_bot + plate_t
    flange_top = plate_bot - P.CAP_TO_PLATE
    flange_bot = flange_top - P.FLANGE_T
    sw_top = flange_bot - P.NUB_H
    pcb_top = sw_top - P.SW_H
    pcb_bot = pcb_top - P.PCB_T
    glass = pcb_bot - P.GLASS_GAP
    return Stack(floor_t, bp_bot, bp_top, knob_pcb_bot, knob_pcb_top, motor_bot, motor_top,
                 plate_bot, plate_top, flange_top, flange_bot, sw_top,
                 pcb_top, pcb_bot, glass, plate_top + P.CAP_PROTRUDE)


# Switch position relative to its key center (it sits on the PCB strip
# below the key's window).
PCB_WIN = P.CAP_SIZE + 2 * (P.CAP_CLEAR + P.PCB_WIN_EXTRA)     # frame PCB key window
SW_DY = -(PCB_WIN / 2 + P.SW_EDGE_MARGIN + P.SW_W / 2)
TAB_REACH = (-SW_DY - P.CAP_SIZE / 2) + P.NUB_D / 2 + 0.25


def check_key_fit(pitch: float, below_gap_edge: float | None = None) -> list[str]:
    """Return warnings if the switch or tab doesn't fit between keys."""
    warnings = []
    window = PCB_WIN
    strip = pitch - window
    sw_far = -SW_DY + P.SW_W / 2
    if sw_far + P.SW_EDGE_MARGIN > pitch - window / 2:
        warnings.append(
            f"switch does not fit in the {strip:.1f} mm strip between key rows")
    if P.CAP_SIZE / 2 + TAB_REACH + 0.5 > pitch - P.CAP_SIZE / 2:
        warnings.append("cap tab comes within 0.5 mm of the next row's cap")
    if 2 * P.LIP_W + 0.5 > pitch - P.CAP_SIZE:
        warnings.append("side lips of neighboring caps collide")
    return warnings


# --------------------------------------------------------------------------
# Parts
# --------------------------------------------------------------------------
def key_stop_geometry(nubs: int = 1) -> dict:
    """Cap features in cap coordinates (x, y from the key center), for the
    down-stop check (keystack.cap_max_drop) and for drawing the cap.

    feet: down-stop points (on the PCB after KEY_STOP_GAP); nubs: switch
    contacts; flange_top: points that hit the top plate if the cap rises;
    bottom: corners of the cap's bottom face (the part nearest the glass).
    feet_boxes: (x0, x1, y0, y1) footprints of the stop feet.
    """
    c = P.CAP_SIZE / 2
    lip_out = c + P.LIP_W
    rail = (lip_out - P.STOP_RAIL_W, lip_out)
    lug_y0, lug_y1 = PCB_WIN / 2 + 0.3, c + P.STOP_LUG_REACH    # foot over the PCB, 0.3 inside its edge
    lx0, lx1 = P.STOP_LUG_X
    hl = P.LIP_LEN / 2
    boxes = []
    for sx in (-1, 1):
        boxes.append(tuple(sorted((sx * rail[0], sx * rail[1]))) + (-hl, hl))
        boxes.append(tuple(sorted((sx * lx0, sx * lx1))) + (lug_y0, lug_y1))
    feet = []
    for x0, x1, y0, y1 in boxes:
        feet += [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]
    flange = []
    for sx in (-1, 1):
        flange += [(sx * (c - 0.5), -hl), (sx * lip_out, -hl), (sx * (c - 0.5), hl), (sx * lip_out, hl)]
        flange += [(sx * lx0, c - 0.25), (sx * lx1, c - 0.25), (sx * lx0, lug_y1), (sx * lx1, lug_y1)]
    tab_y = [(-c - TAB_REACH, -c + 0.5)]
    nub_pts = [(0.0, SW_DY)]
    if nubs == 2:
        tab_y.append((c - 0.5, c + TAB_REACH))
        nub_pts.append((0.0, -SW_DY))
    for y0, y1 in tab_y:
        flange += [(sx * P.TAB_W / 2, y) for sx in (-1, 1) for y in (y0, y1)]
    k = c - P.CAP_EDGE_R * (1 - 1 / math.sqrt(2))
    bottom = [(sx * k, sy * k) for sx in (-1, 1) for sy in (-1, 1)] + [(0, c), (0, -c), (c, 0), (-c, 0)]
    return dict(feet=feet, feet_boxes=boxes, nubs=nub_pts, flange_top=flange, bottom=bottom)


def key_cap(st: Stack, nubs: int = 1) -> Part:
    """Clear cap: body through the plate and PCB window, a tab with a domed nub
    over the switch (nubs=2: a second tab and nub at the back, for the
    prototype's two-switch test), side lips under the plate (retention), and
    the down-stop: rails under the lips and lugs at the back corners whose feet
    stop KEY_STOP_GAP above the frame PCB."""
    cap_bot = st.pcb_bot
    body = Box(P.CAP_SIZE, P.CAP_SIZE, st.cap_top - cap_bot, align=MIN)
    body = fillet(body.edges().filter_by(Axis.Z), P.CAP_EDGE_R)
    body = fillet(body.edges().group_by(Axis.Z)[-1], P.CAP_TOP_FILLET)
    body = Pos(0, 0, cap_bot) * body
    c = P.CAP_SIZE / 2
    a, h = P.NUB_D / 2, P.NUB_H
    r = (a * a + h * h) / (2 * h)
    for sy in ((-1, 1) if nubs == 2 else (-1,)):
        body += Pos(0, sy * (c + TAB_REACH / 2 - 0.25), st.flange_bot) * Box(
            P.TAB_W, TAB_REACH + 0.5, P.FLANGE_T, align=MIN)
        # Domed nub (spherical cap): tolerant of small cap/switch misalignment
        ny = -sy * SW_DY
        body += (Pos(0, ny, st.flange_bot - h + r) * Sphere(r)) & (
            Pos(0, ny, st.flange_bot - h) * Box(P.NUB_D + 0.1, P.NUB_D + 0.1, h + 0.01, align=MIN))
    for sx in (-1, 1):
        body += Pos(sx * (c + P.LIP_W / 2 - 0.25), 0, st.flange_bot) * Box(
            P.LIP_W + 0.5, P.LIP_LEN, P.FLANGE_T, align=MIN)
        lx0, lx1 = P.STOP_LUG_X
        body += Pos(sx * (lx0 + lx1) / 2, (c - 0.25 + c + P.STOP_LUG_REACH) / 2, st.flange_bot) * Box(
            lx1 - lx0, P.STOP_LUG_REACH + 0.25, P.FLANGE_T, align=MIN)
    foot_bot = st.pcb_top + P.KEY_STOP_GAP
    for x0, x1, y0, y1 in key_stop_geometry(nubs)["feet_boxes"]:
        body += Pos((x0 + x1) / 2, (y0 + y1) / 2, foot_bot) * Box(
            x1 - x0, y1 - y0, st.flange_bot - foot_bot + 0.01, align=MIN)
    return body


def key_guide_length(st: Stack) -> float:
    """Engagement of the cap guide (D8, B3): the plate's key hole and its skirt, from the
    plate top down to KEY_GUIDE_GAP above the frame PCB."""
    return st.plate_top - (st.pcb_top + P.KEY_GUIDE_GAP)


def key_guide_sketch(nubs: int = 1) -> Sketch:
    """Plan of the guide skirt around one cap (cap coordinates): a ring KEY_GUIDE_WALL
    wide around the cap body, KEY_GUIDE_CLEAR off it, cut away (KEY_GUIDE_POCKET clear)
    where the cap's lips, tab and lugs, the next row's tab and the switches pass. The
    cap slides straight up and down in it; there is no pivot."""
    c, g, m = P.CAP_SIZE / 2, P.KEY_GUIDE_CLEAR, P.KEY_GUIDE_POCKET
    w_in = P.CAP_SIZE + 2 * g + P.HOLE_COMP
    r_in = P.CAP_EDGE_R + g
    w_out, r_out = w_in + 2 * P.KEY_GUIDE_WALL, r_in + P.KEY_GUIDE_WALL
    far = 5.0
    lx0, lx1 = P.STOP_LUG_X
    with BuildSketch() as sk:
        RectangleRounded(w_out, w_out, r_out)
        RectangleRounded(w_in, w_in, r_in, mode=Mode.SUBTRACT)
        for sx in (-1, 1):                         # side lips and their down-stop rails
            with Locations((sx * (c + far / 2 - 0.5), 0)):
                Rectangle(far + 1, P.LIP_LEN + 2 * m, mode=Mode.SUBTRACT)
            with Locations((sx * (lx0 + lx1) / 2, c + far / 2 - 0.5)):   # back lugs
                Rectangle(lx1 - lx0 + 2 * m, far + 1, mode=Mode.SUBTRACT)
        for sy in (-1, 1):                         # front: own tab and switch; back: the next
            with Locations((0, sy * (c + far / 2 - 0.5))):   # row's tab (and a second tab)
                Rectangle(P.TAB_W + 2 * m, far + 1, mode=Mode.SUBTRACT)
    return sk.sketch


def key_guides(st: Stack, key_xy, nubs: int = 1) -> Part:
    """Guide skirts for every key, to fuse onto the top plate's underside."""
    ring = key_guide_sketch(nubs)
    z0 = st.pcb_top + P.KEY_GUIDE_GAP
    out = None
    for x, y in key_xy:
        r = Pos(x, y, z0) * extrude(ring, amount=st.plate_bot - z0 + 0.01)
        out = r if out is None else out + r
    return out


def switch(st: Stack) -> Part:
    base = Box(P.SW_L, P.SW_W, P.SW_H - 0.35, align=MIN)
    stem = Pos(0, 0, P.SW_H - 0.35) * Cylinder(0.6, 0.35, align=MIN)
    return Pos(0, 0, st.pcb_top) * (base + stem)


def frame_pcb_sketch(rect: tuple[float, float, float, float],
                     key_xy: list[tuple[float, float]],
                     win_xy: list[tuple[float, float]],
                     win_size: tuple[float, float],
                     holes_xy: list[tuple[float, float]] = (),
                     pin_xy: list[tuple[float, float]] = ()) -> Sketch:
    """2D outline of the frame PCB: outer rectangle minus all windows and mount holes.

    rect = (xmin, xmax, ymin, ymax). Also exported as DXF for KiCad. Windows get
    PCB_WIN_R inside corners (what the router can mill).
    """
    x0, x1, y0, y1 = rect
    w = PCB_WIN
    e = 2 * P.PCB_WIN_EXTRA
    with BuildSketch() as sk:
        with Locations(((x0 + x1) / 2, (y0 + y1) / 2)):
            RectangleRounded(x1 - x0, y1 - y0, 1.5)
        with Locations(*key_xy):
            RectangleRounded(w, w, P.PCB_WIN_R, mode=Mode.SUBTRACT)
        if win_xy:
            with Locations(*win_xy):
                RectangleRounded(win_size[0] + e, win_size[1] + e, P.PCB_WIN_R, mode=Mode.SUBTRACT)
        if holes_xy:
            with Locations(*holes_xy):
                Circle(P.FRAME_MOUNT_HOLE_D / 2, mode=Mode.SUBTRACT)
        if pin_xy:
            with Locations(*pin_xy):
                Circle(P.FRAME_PIN_D / 2 + 0.05, mode=Mode.SUBTRACT)
    return sk.sketch


def plate_sketch(outline: tuple[float, float, float, float], radius: float,
                 key_xy, win_xy, win_size, knob_xy,
                 holes_xy=(), hole_d: float = 3.2, small_holes_xy=(),
                 small_hole_d: float = P.FRAME_MOUNT_HOLE_D, win_ledge: float = 0.0,
                 openings=()) -> Sketch:
    """Top plate outline. win_ledge: the knob windows' through-holes are this much
    smaller per side (the ledge their covers sit on; the pocket above is cut in 3D).
    openings: knob slot openings (cx, cy, w, h) (D23)."""
    x0, x1, y0, y1 = outline
    w = P.CAP_SIZE + 2 * P.KEY_GUIDE_CLEAR + P.HOLE_COMP     # the key holes are the cap guide (D8)
    with BuildSketch() as sk:
        with Locations(((x0 + x1) / 2, (y0 + y1) / 2)):
            RectangleRounded(x1 - x0, y1 - y0, radius)
        with Locations(*key_xy):
            RectangleRounded(w, w, P.CAP_EDGE_R + P.KEY_GUIDE_CLEAR, mode=Mode.SUBTRACT)
        with Locations(*win_xy):
            RectangleRounded(win_size[0] - 2 * win_ledge, win_size[1] - 2 * win_ledge,
                             1.0, mode=Mode.SUBTRACT)
        if knob_xy:
            with Locations(*knob_xy):
                Circle(knob_hole_d() / 2, mode=Mode.SUBTRACT)
        for cx, cy, w_, h_ in openings:
            with Locations((cx, cy)):
                RectangleRounded(w_, h_, 1.3, mode=Mode.SUBTRACT)
        if holes_xy:
            with Locations(*holes_xy):
                Circle(hole_d / 2, mode=Mode.SUBTRACT)
        if small_holes_xy:
            with Locations(*small_holes_xy):
                Circle(small_hole_d / 2, mode=Mode.SUBTRACT)
    return sk.sketch


def knob_hole_d() -> float:
    if P.KNOB_STYLE == "shaft_adapter":
        return P.PLATE_SHAFT_HOLE_D
    return P.KNOB_HUB_D + P.KNOB_HUB_HOLE_CLEAR + P.HOLE_COMP


def tapered_knob() -> Part:
    """Knob body, bottom at z=0: tapered, wider at the top."""
    knob = Cone(P.KNOB_BOT_D / 2, P.KNOB_TOP_D / 2, P.KNOB_H, align=MIN)
    knob = fillet(knob.edges().group_by(Axis.Z)[-1], 0.8)
    return knob - Pos(0, P.KNOB_TOP_D / 2 - 2.5, P.KNOB_H - 0.5) * Cylinder(0.8, 2, align=MIN)


def d_shape(r: float, flat: float, h: float) -> Part:
    """Round r with a flat at distance `flat` from the axis on the +y side, bottom at z=0."""
    return Cylinder(r, h, align=MIN) - Pos(0, flat, -1) * Box(4 * r, 4 * r, h + 2,
                                                              align=(Align.CENTER, Align.MIN, Align.MIN))


def hub_screw_xy(x: float, y: float) -> list[tuple[float, float]]:
    r = P.HUB_SCREW_BC / 2
    return [(x + r * math.cos(math.radians(a)), y + r * math.sin(math.radians(a))) for a in (0, 90, 180, 270)]


def motor_screw_xy(x: float, y: float) -> list[tuple[float, float]]:
    r = P.MOTOR_SCREW_BC / 2
    return [(x + r * math.cos(math.radians(a)), y + r * math.sin(math.radians(a)))
            for a in (45, 135, 225, 315)]


def motor_pin_xy(x: float, y: float) -> list[tuple[float, float]]:
    r = P.MOTOR_SCREW_BC / 2
    return [(x - r, y), (x + r, y)]


def knob_parts(st: Stack, x: float, y: float, n: int, screws: list | None = None) -> list[Item]:
    """What sits on top of the motor bell, for the chosen KNOB_STYLE."""
    knob_z = st.plate_top + P.KNOB_GAP
    if P.KNOB_STYLE == "shaft_adapter":
        shaft_top = knob_z + P.KNOB_BORE_DEPTH
        disc = Cylinder(P.ADAPTER_D / 2, P.ADAPTER_H, align=MIN)
        shaft = Pos(0, 0, P.ADAPTER_H) * Cylinder(
            P.KNOB_BORE_D / 2, shaft_top - st.motor_top - P.ADAPTER_H, align=MIN)
        flat = Pos(P.SHAFT_FLAT - P.KNOB_BORE_D / 2 + 5, 0, P.ADAPTER_H + 4) * Box(
            10, 10, 50, align=MIN)
        adapter = Pos(x, y, st.motor_top) * (disc + shaft - flat)
        knob = tapered_knob() - Cylinder(P.KNOB_BORE_D / 2, P.KNOB_BORE_DEPTH, align=MIN)
        return [Item(adapter, f"knob{n}_shaft_adapter", C_STANDOFF, 3),
                Item(Pos(x, y, knob_z) * knob, f"knob{n}_d_shaft_knob", C_KNOB, 6)]
    # Integrated: a hub screwed to the bell (flange + 4 M2 into the bell's threaded
    # holes, centered by a spigot in the shaft bore) reaches up through the plate.
    # The knob cap presses onto its D-flat (torque) and three crush ribs (retention),
    # so caps pull straight off and the plate lifts over the hubs.
    hub_top = knob_z + P.KNOB_HUB_ENGAGE
    ft = P.HUB_FLANGE_T
    flat = P.KNOB_HUB_FLAT - P.KNOB_HUB_D / 2
    flange = Cylinder(P.HUB_FLANGE_D / 2, ft, align=MIN)
    column = Pos(0, 0, ft - 0.01) * d_shape(P.KNOB_HUB_D / 2, flat, hub_top - st.motor_top - ft + 0.01)
    spigot = Pos(0, 0, -1.0) * Cylinder(P.SHAFT_BORE / 2 - 0.1, 1.01, align=MIN)
    hub = flange + column + spigot
    hd, hh = P.M2_CSK_HEAD
    for sx, sy in hub_screw_xy(0, 0):
        hub -= Pos(sx, sy, -1) * Cylinder(P.M2_CLEAR / 2, ft + 2, align=MIN)
        hub -= Pos(sx, sy, ft - hh) * Cylinder(hd / 2 + 0.1, hh + 1, align=MIN)
    hub = Pos(x, y, st.motor_top) * hub
    if screws is not None:
        top = st.motor_top + ft
        # Countersunk M2: nominal length includes the head; tip stays inside the bell top
        nominal = max(n_ for n_ in STD_LENGTHS if n_ - hh <= ft - hh + P.BELL_THREAD_DEPTH - 0.3)
        for k, (sx, sy) in enumerate(hub_screw_xy(x, y)):
            screws.append(Screw(f"screw_hub{n}_{k}", "", sx, sy, top - hh, False, nominal - hh,
                                P.M2_CSK_HEAD, f"knob{n}_motor_2204", "module_sub",
                                engage=(0.8, P.BELL_THREAD_DEPTH - 0.3), style="countersunk",
                                nominal=nominal))
    cap = tapered_knob()
    rb = P.KNOB_HUB_D / 2 + 0.1
    bore = d_shape(rb, flat + 0.1, P.KNOB_HUB_ENGAGE)
    cap -= bore
    rr = 0.4
    for a in (0, 180, 270):                       # crush ribs on the round part of the bore
        c = P.KNOB_HUB_D / 2 - P.KNOB_HUB_RIB + rr
        rib = Pos(c * math.cos(math.radians(a)), c * math.sin(math.radians(a)), 0) * Cylinder(
            rr, P.KNOB_HUB_ENGAGE - 0.5, align=MIN)
        cap += rib & Cylinder(rb + 0.05, P.KNOB_HUB_ENGAGE, align=MIN)
    return [Item(hub, f"knob{n}_hub", C_STANDOFF, 3),
            Item(Pos(x, y, knob_z) * cap, f"knob{n}_knob", C_KNOB, 6)]


def press_switch_y(y: float) -> float:
    """Center y of a haptic module's press switch, mid-way across its fixed front border."""
    t = P.MODULE_TONGUE / 2 + P.MODULE_SLOT
    return y - (t + P.MODULE_FRONT) / 2


def motor_2204(x: float, y: float, z: float) -> Part:
    """The 2204 gimbal motor: stator base (bottom at z) and the bell with its hollow shaft."""
    base = Pos(x, y, z) * Cylinder(P.MOTOR_BASE_D / 2, P.MOTOR_BASE_H, align=MIN)
    bell = Cylinder(P.MOTOR_D / 2, P.MOTOR_H - P.MOTOR_BASE_H + 0.5, align=MIN)
    bell = bell - Cylinder(P.SHAFT_BORE / 2, 50, align=MIN)
    return base + Pos(x, y, z + P.MOTOR_BASE_H - 0.5) * bell


def knob_stack(st: Stack, x: float, y: float, n: int, screws: list | None = None) -> list[Item]:
    """Haptic module (D23) parts on its PCB: MT6701, driver, press switch + striker,
    magnet, spacer, 2204 motor, motor header and plug, the spare lead, hub and knob.

    Every board part is on the top side (D6). The motor and the MT6701 sit on the
    tongue; the driver, inverter, header and press switch on the fixed front border
    (D16). The spacer's arm reaches forward over the slot, and an M2 set screw in the
    arm's tip (the striker) presses the switch when the tongue flexes down.
    """
    kpt = st.knob_pcb_top
    sensor = Pos(x, y, kpt) * Box(*P.MT6701, align=MIN)
    py = press_switch_y(y)
    # Driver, inverter and the driver's two 22 µF on the front border, right of the arm
    chips = Pos(x + 6.0, y - 17.4, kpt) * Box(*P.TMC6300, align=MIN)
    chips += Pos(x + 9.2, y - 14.1, kpt) * Box(2.0, 3.1, 1.0, align=MIN)
    for cx in (4.8, 7.4):
        chips += Pos(x + cx, y - 14.0, kpt) * Box(1.25, 2.0, 1.25, align=MIN)
    body = Pos(x, py, kpt) * Box(P.SW_L, P.SW_W, P.SW_H - 0.35, align=MIN)
    stem = Pos(x, py, kpt + P.SW_H - 0.35) * Cylinder(0.6, 0.35, align=MIN)
    # Striker: M2 set screw down through the spacer arm, KNOB_PRESS_GAP above the switch
    sz = kpt + P.SW_H + P.KNOB_PRESS_GAP
    striker = Pos(x, py, sz) * Cylinder(1.0, P.STRIKER_LEN, align=MIN)
    magnet = Pos(x, y, st.motor_bot - P.MAGNET_H) * Cylinder(
        P.MAGNET_D / 2, P.MAGNET_H, align=MIN)
    motor = motor_2204(x, y, st.motor_bot)
    # Spacer ring: sets the sensor gap, locates on two pins in the tongue (centers the magnet)
    sp_h = st.motor_bot - st.knob_pcb_top
    spacer = Cylinder(P.MOTOR_SPACER_OD / 2, sp_h, align=MIN) - Pos(0, 0, -1) * Cylinder(
        P.MOTOR_SPACER_ID / 2, sp_h + 2, align=MIN)
    for sx, sy in motor_screw_xy(0, 0):
        spacer -= Pos(sx, sy, -1) * Cylinder(P.M2_CLEAR / 2 + 0.1, sp_h + 2, align=MIN)
    for sx, sy in motor_pin_xy(0, 0):
        spacer += Pos(sx, sy, -(P.PCB_T - 0.2)) * Cylinder(P.MOTOR_LOCATE_PIN_D / 2, P.PCB_T - 0.19,
                                                          align=MIN)
    # Press arm: forward over the slot to above the press switch, under the motor base
    a0, a1 = P.SW_H + 0.8, sp_h - 0.3
    tip = py - y - 1.5
    r_in = P.MOTOR_SPACER_OD / 2 - 1.0
    spacer += Pos(0, (-r_in + tip) / 2, a0) * Box(P.MOTOR_SPACER_ARM_W, -tip - r_in, a1 - a0,
                                                   align=(Align.CENTER, Align.CENTER, Align.MIN))
    spacer -= Pos(0, py - y, a0 - 1) * Cylinder(P.M2_PILOT / 2, a1 - a0 + 2, align=MIN)
    spacer = Pos(x, y, kpt) * spacer
    if screws is not None:
        # M2 from under the tongue through the spacer into the base; tip stays
        # 0.5 mm short of the bottom of the base's thread (windings above it)
        thru = P.PCB_T + sp_h
        ln = max(n_ for n_ in STD_LENGTHS if n_ - thru <= P.MOTOR_THREAD_DEPTH - 0.5)
        for k, (sx, sy) in enumerate(motor_screw_xy(x, y)):
            screws.append(Screw(f"screw_motor{n}_{k}", "", sx, sy, st.knob_pcb_bot, True, ln,
                                P.M2_HEAD, f"knob{n}_motor_2204", "module_sub",
                                engage=(1.2, P.MOTOR_THREAD_DEPTH - 0.5)))
    # Motor header (vertical SMD 1x3) on the front border, the plug standing on it; the
    # spare lead coils flat in front of the bell, clear of it
    hx, hy = P.MODULE_HEADER_XY
    hw, hd, hh = P.MODULE_HEADER
    header = Pos(x + hx, y + hy, kpt) * Box(hw, hd, hh, align=MIN)
    cw, cd, ch = P.LEAD_COIL
    coil = Pos(x + P.LEAD_COIL_XY[0], y + P.LEAD_COIL_XY[1], kpt + P.LEAD_COIL_Z) * Box(cw, cd, ch, align=MIN)
    return [
        Item(sensor, f"knob{n}_mt6701", C_CHIP, 0),
        Item(chips, f"knob{n}_chips", C_CHIP, 0),
        Item(body + stem, f"knob{n}_press_switch", C_SWITCH, 0),
        Item(striker, f"knob{n}_striker", C_SCREW, 1),
        Item(spacer, f"knob{n}_spacer", C_STANDOFF, 1),
        Item(magnet, f"knob{n}_magnet", C_MAGNET, 1),
        Item(motor, f"knob{n}_motor_2204", C_MOTOR, 2),
        Item(header, f"knob{n}_header", C_CHIP, 0),
        Item(coil, f"cable_motor{n}_coil", C_CABLE, 2),
    ] + knob_parts(st, x, y, n, screws)


def motor_plug(st: Stack, x: float, y: float) -> Part:
    """The motor's 3-pin plug, standing on the module's vertical header."""
    hx, hy = P.MODULE_HEADER_XY
    w, d, h = P.MOTOR_PLUG_UP
    return Pos(x + hx, y + hy, st.knob_pcb_top + P.MODULE_HEADER[2]) * Box(w, d, h, align=MIN)


def lite_heights(st: Stack) -> dict:
    """Lite module (D22, D23) heights: the encoder sits on the module PCB, its shaft tip
    seats in the bottom of the knob's bore, so the knob lands where the haptic knob does."""
    body_top = st.knob_pcb_top + P.ENC_BODY[2]
    shaft_top = body_top + P.ENC_SHAFT_L
    knob_z = st.plate_top + P.KNOB_GAP
    return dict(body_top=body_top, bushing_top=body_top + P.ENC_BUSHING[1], shaft_top=shaft_top,
                knob_z=knob_z, stem_bot=min(shaft_top - P.LITE_KNOB_ENGAGE, knob_z))


def encoder_stack(st: Stack, x: float, y: float, n: int) -> list[Item]:
    """Lite module (D22, D23): a vertical push encoder (EC11 size) on the module PCB and a
    knob whose stem reaches down through the cover's hub hole onto the 6 mm flatted shaft.

    The encoder's push switch is the knob press. The knob is the haptic knob's cap
    shape plus the stem; it seats on the shaft tip, so its top matches the haptic knob.
    """
    h = lite_heights(st)
    bw, bd, bh = P.ENC_BODY
    flat = P.ENC_SHAFT_FLAT[1] - 3.0                  # flat's distance from the axis
    body = Pos(x, y, st.knob_pcb_top) * Box(bw, bd, bh, align=MIN)
    bush = Pos(x, y, h["body_top"]) * Cylinder(P.ENC_BUSHING[0] / 2, P.ENC_BUSHING[1], align=MIN)
    f_len = P.ENC_SHAFT_FLAT[0]
    shaft = Pos(x, y, h["body_top"]) * Cylinder(3.0, P.ENC_SHAFT_L - f_len, align=MIN)
    shaft += Pos(x, y, h["shaft_top"] - f_len) * d_shape(3.0, flat, f_len)
    # Pins (A, C, B at the front; switch at the back) and the two mounting tabs, trimmed under the board
    pins = [(x + dx, y - 7.5) for dx in (-2.5, 0.0, 2.5)] + [(x + dx, y + 7.0) for dx in (-2.5, 2.5)]
    stubs = None
    for px, py in pins + [(x - 6.6, y), (x + 6.6, y)]:
        s = Pos(px, py, st.knob_pcb_bot - P.ENC_PIN_STUB) * Box(0.8, 0.8, P.ENC_PIN_STUB, align=MIN)
        stubs = s if stubs is None else stubs + s
    enc = body + bush + shaft + stubs
    # Knob: the haptic knob's cap plus a stem with a D-bore that bottoms on the shaft tip
    kz, sb = h["knob_z"], h["stem_bot"]
    cap = Pos(0, 0, kz - sb) * tapered_knob() + Cylinder(P.LITE_STEM_D / 2, kz - sb + 0.5, align=MIN)
    rb, depth = 3.0 + 0.1, h["shaft_top"] - sb
    round_l = max(depth - f_len, 0.0)                 # the shaft is round below its flat
    cap -= Pos(0, 0, -0.01) * Cylinder(rb, round_l + 0.02, align=MIN)
    cap -= Pos(0, 0, round_l) * d_shape(rb, flat + 0.1, depth - round_l)
    rr = 0.4
    for a in (0, 180, 270):                           # crush ribs on the round part of the bore
        c = 3.0 - P.KNOB_HUB_RIB + rr
        rib = Pos(c * math.cos(math.radians(a)), c * math.sin(math.radians(a)), 0) * Cylinder(
            rr, depth - 0.5, align=MIN)
        cap += rib & Cylinder(rb + 0.05, depth, align=MIN)
    return [Item(enc, f"knob{n}_encoder", C_MOTOR, 0),
            Item(Pos(x, y, sb) * cap, f"knob{n}_knob", C_KNOB, 6)]


# --------------------------------------------------------------------------
# Knob slots (D23): backplane, slot connector, modules and blanks
# --------------------------------------------------------------------------
def pogo_xy(x: float, y: float) -> list[tuple[float, float]]:
    """Slot connector contacts (pogo pins on the backplane, pads on the module), by row."""
    nc, nr, px, py = P.POGO_GRID
    return [(x + (c - (nc - 1) / 2) * px, y + P.POGO_ROW0 + r * py) for r in range(nr) for c in range(nc)]


def pogo_window() -> tuple[float, float, float, float]:
    """(x0, x1, y0, y1) around the pogo field, from the knob axis: the base's cut-out."""
    nc, nr, px, py = P.POGO_GRID
    m = P.POGO[0] / 2 + 0.6
    hx = (nc - 1) / 2 * px + m
    return (-hx, hx, -P.MODULE_FRONT - 1.0, P.POGO_ROW0 + (nr - 1) * py + m)


def module_pcb_sketch(kind: str) -> Sketch:
    """Module PCB outline (knob axis at the origin). Haptic: a tongue under the motor,
    cut free at the front and sides, joined to the side borders by two torsion necks
    near its back edge (the hinge, D10). Lite: the same outline, solid."""
    w, f, b = P.MODULE_W / 2, P.MODULE_FRONT, P.MODULE_BACK
    t, sl = P.MODULE_TONGUE / 2, P.MODULE_SLOT
    n0, n1 = P.MODULE_NECK
    with BuildSketch() as sk:
        with Locations((0, (b - f) / 2)):
            Rectangle(2 * w, f + b)
        if kind == "haptic":
            with Locations((0, -t - sl / 2)):
                Rectangle(2 * t + 2 * sl, sl, mode=Mode.SUBTRACT)
            for sx in (-1, 1):
                with Locations((sx * (t + sl / 2), (-t - sl + n0) / 2)):
                    Rectangle(sl, n0 + t + sl, mode=Mode.SUBTRACT)
                with Locations((sx * (t + sl / 2), (n1 + b + 1.0) / 2)):
                    Rectangle(sl, b + 1.0 - n1, mode=Mode.SUBTRACT)
            with Locations(*motor_screw_xy(0, 0)):
                Circle(P.M2_CLEAR / 2, mode=Mode.SUBTRACT)
            with Locations(*motor_pin_xy(0, 0)):
                Circle(P.MOTOR_LOCATE_PIN_D / 2 + 0.05, mode=Mode.SUBTRACT)
        for sx in (-1, 1):                         # back corners: room for the cover's back posts
            with Locations((sx * (w + t + sl) / 2 + sx * 0.1, b - 0.5)):
                Rectangle(w - t - sl + 0.2, 1.0 + 0.01, mode=Mode.SUBTRACT)
        holes = [P.MODULE_POSTS[k] for k in P.MODULE_SCREWS if -f < P.MODULE_POSTS[k][1] < b - 1.0]
        if holes:
            with Locations(*holes):
                Circle(P.M2_CLEAR / 2, mode=Mode.SUBTRACT)
    return sk.sketch


def module_base(st: Stack) -> Part:
    """Printed carrier base under the module PCB (knob axis at the origin): POGO_WORK
    thick, so it sets the pogo pins' working height. Open over the pogo field and under
    the tongue (motor screw heads, travel, encoder pin stubs); two key pins of different
    sizes underneath drop into the backplane."""
    w, f, bb = P.MODULE_W / 2, P.MODULE_FRONT, P.MODULE_BASE_BACK
    t = P.MODULE_TONGUE / 2 + P.MODULE_SLOT + 0.2
    x0, x1, y0, y1 = pogo_window()
    h = st.knob_pcb_bot - st.bp_top
    with BuildSketch() as sk:
        with Locations((0, (bb - f) / 2)):
            Rectangle(2 * w, f + bb)
        with Locations(((x0 + x1) / 2, (y0 + y1) / 2)):
            Rectangle(x1 - x0, y1 - y0, mode=Mode.SUBTRACT)
        with Locations((0, (-t + P.MODULE_BACK + 0.2) / 2)):
            Rectangle(2 * t, t + P.MODULE_BACK + 0.2, mode=Mode.SUBTRACT)
        with Locations(*[P.MODULE_POSTS[k] for k in P.MODULE_SCREWS]):
            Circle(P.M2_CLEAR / 2, mode=Mode.SUBTRACT)
    base = Pos(0, 0, st.bp_top) * extrude(sk.sketch, amount=h)
    keys = [k for k in range(len(P.MODULE_POSTS)) if k not in P.MODULE_SCREWS]
    for k, d in zip(keys, P.KEY_PIN_D):
        px, py = P.MODULE_POSTS[k]
        base += Pos(px, py, st.bp_top - P.KEY_PIN_L) * Cylinder(d / 2, P.KEY_PIN_L + 0.01, align=MIN)
    return base


def bezel_size() -> tuple[float, float, float]:
    """Cover top (bezel): half width, front and back edge from the knob axis."""
    g = P.BEZEL_GAP
    return P.SLOT_OPEN[0] - g, P.SLOT_OPEN[1] - g, P.SLOT_OPEN[2] - g


def module_cover(st: Stack, kind: str) -> Part:
    """Printed cover (knob axis at the origin): a bezel flush with the top plate in the
    slot opening (hub hole for a knob, none on a blank), four posts down to the module
    (blank: to the backplane), and a front wall tying the front posts. The two
    retention screws go down through posts 0 and 3, countersunk into the bezel."""
    hw, f, b = bezel_size()
    t = P.TOP_PLATE_T
    cover = Pos(0, (b - f) / 2, st.plate_bot) * extrude(RectangleRounded(2 * hw, f + b, 1.0), amount=t)
    if kind != "blank":
        cover -= Pos(0, 0, st.plate_bot - 1) * Cylinder(knob_hole_d() / 2, t + 2, align=MIN)
    for k, (px, py) in enumerate(P.MODULE_POSTS):
        if kind == "blank":
            z0 = st.bp_top
        else:
            z0 = st.knob_pcb_top if -P.MODULE_FRONT < py < P.MODULE_BACK else st.knob_pcb_bot
        cover += Pos(px, py, z0) * Cylinder(P.MODULE_POST_D / 2, st.plate_bot - z0 + 0.01, align=MIN)
    wz = st.bp_top + P.POGO[1] + 0.5 if kind == "blank" else st.knob_pcb_top + 1.0   # blank: over the free pins
    cover += Pos(0, -f, wz) * Box(2 * hw - 2.0, P.MODULE_WALL, st.plate_bot - wz + 0.01,
                                  align=(Align.CENTER, Align.MIN, Align.MIN))
    hd, hh = P.M2_CSK_HEAD
    for k in P.MODULE_SCREWS:
        px, py = P.MODULE_POSTS[k]
        cover -= Pos(px, py, st.bp_top - 1) * Cylinder(P.M2_CLEAR / 2, st.plate_top - st.bp_top + 2, align=MIN)
        cover -= Pos(px, py, st.plate_top - hh) * Cylinder(hd / 2 + 0.1, hh + 1, align=MIN)
    return cover


def module_screw_nominal(st: Stack) -> int:
    """Countersunk M2 from the bezel top into the insert in the slot boss: the longest
    standard length whose tip stays 0.3 mm above the insert's bottom."""
    bot = st.bp_top - P.INSERT_M2[1]
    return max(n_ for n_ in STD_LENGTHS if st.plate_top - n_ >= bot + 0.3)


def slot_items(st: Stack, x: float, y: float, n: int, kind: str,
               screws: list | None = None) -> tuple[list[Item], list]:
    """Everything in slot n above the backplane (D23): a haptic module, a lite module or a
    blank cover, with its two retention screws. Returns the items and the mated plugs
    (same tuples as full_device's plug list)."""
    items, plugs = [], []
    if kind in ("haptic", "lite"):
        pcb = Pos(x, y, st.knob_pcb_bot) * extrude(module_pcb_sketch(kind), amount=P.PCB_T)
        items += [Item(pcb, f"knob{n}_pcb", C_PCB, 0),
                  Item(Pos(x, y, 0) * module_base(st), f"knob{n}_base", C_STANDOFF, 0)]
        if kind == "haptic":
            items += knob_stack(st, x, y, n, screws)
            plugs.append((f"knob{n}_motor_plug", motor_plug(st, x, y), (0, 0, -1), "motor",
                          f"knob{n}_header", "module_sub", P.MOTOR_PLUG_UP[2]))
        else:
            items += encoder_stack(st, x, y, n)
        items.append(Item(Pos(x, y, 0) * module_cover(st, kind), f"knob{n}_cover", C_PLATE, 4))
    else:
        items.append(Item(Pos(x, y, 0) * module_cover(st, "blank"), f"knob{n}_blank", C_PLATE, 4))
    if screws is not None:
        hd, hh = P.M2_CSK_HEAD
        nom = module_screw_nominal(st)
        for k in P.MODULE_SCREWS:
            px, py = P.MODULE_POSTS[k]
            screws.append(Screw(f"screw_slot{n}_{k}", "", x + px, y + py, st.plate_top - hh, False, nom - hh,
                                P.M2_CSK_HEAD, f"slot_insert_{n}_{k}", "modules",
                                engage=(2.5, P.INSERT_M2[1] - 0.3), style="countersunk", nominal=nom))
    return items, plugs


def backplane(st: Stack, knob_xy: list, slots: tuple, avoid_xy: list = (), screw_xy: list = (),
              tabs: list = (), mcu_xy: tuple | None = None,
              holes_xy: list = ()) -> tuple[list[Item], Sketch]:
    """The backplane (D23): the old knob board's outline and connectors, with a slot
    connector (15 pogo pins) under each knob position instead of the knobs. The slot
    bosses come up through it (they carry the modules' screws and locate the board),
    and each slot has two key-pin holes. Returns parts and the 2D outline (for KiCad).

    screw_xy: its own screw holes (floor bosses). tabs: extra rectangles
    (x0, x1, y0, y1) added to the outline. Pogo pins are drawn at their working
    height under a module, free height elsewhere."""
    xs = [x for x, _ in knob_xy]
    ky = knob_xy[0][1]
    x0, x1 = min(xs) - P.BP_SIDE, max(xs) + P.BP_SIDE
    y0, y1 = ky - P.BP_FRONT, ky + P.BP_BACK
    keys = [k for k in range(len(P.MODULE_POSTS)) if k not in P.MODULE_SCREWS]
    with BuildSketch() as sk:
        with Locations(((x0 + x1) / 2, (y0 + y1) / 2)):
            RectangleRounded(x1 - x0, y1 - y0, 2.0)
        for tx0, tx1, ty0, ty1 in tabs:
            with Locations(((tx0 + tx1) / 2, (ty0 + ty1) / 2 - 0.5)):
                Rectangle(tx1 - tx0, ty1 - ty0 + 1.0)
        with Locations(*screw_xy):
            Circle(P.M2_CLEAR / 2, mode=Mode.SUBTRACT)
        for x, y in knob_xy:
            with Locations(*[(x + P.MODULE_POSTS[k][0], y + P.MODULE_POSTS[k][1]) for k in P.MODULE_SCREWS]):
                Circle(P.BP_BOSS_D / 2 + 0.3, mode=Mode.SUBTRACT)
            for k, d in zip(keys, P.KEY_PIN_D):
                with Locations((x + P.MODULE_POSTS[k][0], y + P.MODULE_POSTS[k][1])):
                    Circle(d / 2 + 0.1, mode=Mode.SUBTRACT)
        r_avoid = max(P.PANEL_POST_D, P.PLATE_POST_D) / 2 + 0.6
        holes = [(x, y) for x, y in avoid_xy
                 if x0 - r_avoid < x < x1 + r_avoid and y0 - r_avoid < y < y1 + r_avoid]
        if holes:
            with Locations(*holes):
                Circle(r_avoid, mode=Mode.SUBTRACT)
        for hx, hy, hd in holes_xy:
            with Locations((hx, hy)):
                Circle(hd / 2, mode=Mode.SUBTRACT)
    board = Pos(0, 0, st.bp_bot) * extrude(sk.sketch, amount=P.PCB_T)
    items = [Item(board, "backplane_pcb", C_PCB, 0)]
    mx, my = mcu_xy or (xs[len(xs) // 2], y1 - 9.0)
    items.append(Item(Pos(mx, my, st.bp_top) * Box(*P.RP2350B, align=MIN), "backplane_rp2350b", C_CHIP, 0))
    d, free, _ = P.POGO
    for n, ((x, y), kind) in enumerate(zip(knob_xy, slots)):
        h = (P.POGO_WORK - 0.005) if kind in ("haptic", "lite") else free
        pins = None
        for px, py in pogo_xy(x, y):
            c = Pos(px, py, st.bp_top) * Cylinder(d / 2, h, align=MIN)
            pins = c if pins is None else pins + c
        items.append(Item(pins, f"backplane_pogo{n}", C_BRASS, 0))
    return items, sk.sketch


def screen(st: Stack, glass_w: float, glass_h: float, glass_t: float,
           aa: tuple[float, float], center_y: float,
           key_xy, win_xy, win_size, label: str,
           back_pcb: tuple[float, float, float] | None = None,
           center_x: float = 0.0) -> list[Item]:
    """Display module with colored placeholders for the key images."""
    items = []
    body = Pos(center_x, center_y, st.glass - glass_t) * Box(glass_w, glass_h, glass_t, align=MIN)
    items.append(Item(body, f"{label}_module", C_PANEL, 1))
    if back_pcb:
        w, h, ox = back_pcb
        pcb = Pos(ox, center_y, st.glass - glass_t - P.PCB_T) * Box(w, h, P.PCB_T, align=MIN)
        items.append(Item(pcb, f"{label}_pcb", C_PCB, 1))
    aa_part = Pos(0, 0, st.glass - 0.02) * Box(*aa, 0.03, align=MIN)
    items.append(Item(aa_part, f"{label}_active_area", C_SCREEN, 1))
    for i, (x, y) in enumerate(key_xy):
        tile = Pos(x, y, st.glass) * Box(P.CAP_SIZE - 3, P.CAP_SIZE - 3, 0.02, align=MIN)
        items.append(Item(tile, f"{label}_image_{i}", TILE_COLORS[i % len(TILE_COLORS)], 1))
    for i, (x, y) in enumerate(win_xy):
        tile = Pos(x, y, st.glass) * Box(win_size[0] - 3, win_size[1] - 3, 0.02, align=MIN)
        items.append(Item(tile, f"{label}_knob_display_{i}", C_KNOB_TILE, 1))
    return items


def standoff(x: float, y: float, z0: float, z1: float, d: float = 5.0) -> Part:
    return Pos(x, y, z0) * Cylinder(d / 2, z1 - z0, align=MIN)


# --------------------------------------------------------------------------
# Layouts
# --------------------------------------------------------------------------
def key_grid(cols: int, rows: int, pitch: float, top_y: float) -> list[tuple[float, float]]:
    return [((c - (cols - 1) / 2) * pitch, top_y - pitch / 2 - r * pitch)
            for r in range(rows) for c in range(cols)]


@dataclass
class Layout:
    key_xy: list
    win_xy: list          # knob display regions (drawn on the screen)
    win_size: tuple
    knob_xy: list
    warnings: list
    cut_xy: list = None   # openings in the frame PCB and top plate
    cut_size: tuple = None


def touch_bar_floor(win_y: float, win_h: float) -> float:
    """Lowest y the motors may reach so the touch band gets TOUCH_BAR_H."""
    if not P.TOUCH_BAR:
        return float("inf")
    return win_y - win_h / 2 - 2 * P.TOUCH_BAR_MARGIN - P.TOUCH_BAR_H


def strip_cut(win_xy, win_size, span: float):
    """Openings in the frame PCB and top plate for the knob displays: one window each."""
    return win_xy, win_size


def full_layout() -> Layout:
    keys = key_grid(P.KEY_COLS, P.KEY_ROWS, P.KEY_PITCH, P.AA_H / 2)
    strip_top = P.AA_H / 2 - P.KEY_ROWS * P.KEY_PITCH
    strip_bot = -P.AA_H / 2
    strip_h = strip_top - strip_bot
    # Clamp so impossible layouts still build and report a warning instead of crashing
    win = (min(P.KNOB_WIN[0], P.AA_W / P.KNOBS - 3), max(min(P.KNOB_WIN[1], strip_h - 4), 4.0))
    knob_pitch = P.AA_W / P.KNOBS
    win_y = (strip_top + strip_bot) / 2
    wins = [((k - (P.KNOBS - 1) / 2) * knob_pitch, win_y) for k in range(P.KNOBS)]
    panel_bot = -P.AA_H / 2 - P.PANEL_BORDER_FRONT
    knob_y = min(panel_bot - P.INNER_CLEAR, touch_bar_floor(win_y, win[1])) - P.MOTOR_D / 2
    knobs = [(x, knob_y) for x, _ in wins]
    warns = check_key_fit(P.KEY_PITCH)
    if strip_h < 10:
        warns.append(f"knob display strip is only {strip_h:.1f} mm tall")
    if knob_pitch < P.MOTOR_D + 1:
        warns.append(f"knob pitch {knob_pitch:.1f} mm < motor diameter + 1 mm")
    if P.KEY_COLS * P.KEY_PITCH > P.AA_W + 0.5:
        warns.append("key grid is wider than the display active area")
    cut_xy, cut_size = strip_cut(wins, win, P.KNOBS * knob_pitch - 4)
    return Layout(keys, wins, win, knobs, warns, cut_xy, cut_size)


def top_plate(psk: Sketch, st: Stack, t: float, L: Layout) -> Part:
    return Pos(0, 0, st.plate_bot) * extrude(psk, amount=t)


def knob_windows(st: Stack, L: Layout, t: float = P.TOP_PLATE_T, ledge_t: float = 0.0) -> list[Item]:
    """Clear covers over the knob displays, flush with the top plate, resting on a
    ledge ledge_t thick at the bottom of each window (0: no ledge, prototype)."""
    w, h = L.cut_size[0] - 0.2, L.cut_size[1] - 0.2
    return [Item(Pos(x, y, st.plate_bot + ledge_t) * extrude(RectangleRounded(w, h, 0.9), amount=t - ledge_t),
                 f"knob_window_{i}", C_CAP, 4) for i, (x, y) in enumerate(L.cut_xy)]


def touch_bar(st: Stack, L: Layout, x_span, motor_edge_y: float,
              recess: float = 0.0) -> tuple[list[Item], float]:
    """Capacitive touch band under the top plate, between the windows and the motors.

    x_span: width (centered) or (x0, x1). recess: the band sits this far up in a
    flat pocket in the plate underside. Returns the parts and the band height
    (0 if it doesn't fit).
    """
    if not P.TOUCH_BAR:
        return [], 0.0
    top = L.cut_xy[0][1] - L.cut_size[1] / 2 - P.TOUCH_BAR_MARGIN
    bot = motor_edge_y + P.TOUCH_BAR_MARGIN
    h = top - bot
    if h < P.TOUCH_BAR_MIN_H:
        L.warnings.append(f"touch band is only {h:.1f} mm tall (min {P.TOUCH_BAR_MIN_H})")
        return [], h
    x0, x1 = (-x_span / 2, x_span / 2) if isinstance(x_span, (int, float)) else x_span
    bar = Pos((x0 + x1) / 2, (top + bot) / 2, st.plate_bot + recess - P.TOUCH_BAR_T) * Box(
        x1 - x0, h, P.TOUCH_BAR_T, align=MIN)
    return [Item(bar, "touch_bar_pcb", C_PCB, 3)], h


@dataclass
class Screw:
    label: str
    kind: str            # e.g. "M3x10 self-tapping"
    x: float
    y: float
    z: float             # where the head bears on the part
    up: bool             # True: inserted from below, shank points up
    length: float
    head: tuple          # (diameter, height)
    target: str          # label of the part it threads into
    step: str            # assembly step that installs it
    engage: tuple = (1.5, None)   # allowed thread engagement in the target (min, max), mm
    pilot: bool = False  # threads into a printed pilot hole that must run past the tip
    style: str = ""      # e.g. "countersunk"; shown in the BOM
    nominal: float | None = None  # catalogue length if it differs from the shank (countersunk)


STD_LENGTHS = (3, 4, 5, 6, 8, 10, 12, 14, 16, 20, 25, 30)


def std_length(needed: float) -> int:
    return next(n for n in STD_LENGTHS if n >= needed - 0.25)


def screw_part(sc: Screw) -> Part:
    hd, hh = sc.head
    d = 3.0 if sc.kind.startswith("M3") else 2.0
    if sc.up:
        head = Pos(sc.x, sc.y, sc.z - hh) * Cylinder(hd / 2, hh, align=MIN)
        shank = Pos(sc.x, sc.y, sc.z) * Cylinder(d / 2 - 0.15, sc.length, align=MIN)
    else:
        head = Pos(sc.x, sc.y, sc.z) * Cylinder(hd / 2, hh, align=MIN)
        shank = Pos(sc.x, sc.y, sc.z - sc.length) * Cylinder(d / 2 - 0.15, sc.length, align=MIN)
    return head + shank


def tool_part(sc: Screw, reach: float = 120.0) -> Part:
    """The screwdriver's path: a shaft from the head outward along the screw axis."""
    hd, hh = sc.head
    if sc.up:
        return Pos(sc.x, sc.y, sc.z - hh - 0.05 - reach) * Cylinder(P.TOOL_D / 2, reach, align=MIN)
    return Pos(sc.x, sc.y, sc.z + hh + 0.05) * Cylinder(P.TOOL_D / 2, reach, align=MIN)


def fillet_path(points, r: float, name: str = "", warnings: list | None = None):
    """Round every corner of a 3D polyline with radius r (a cable's bend).

    Returns dense points. If a corner's arc doesn't fit between its neighbours,
    the radius there is reduced and a warning added (so --strict catches it).
    """
    pts = [Vector(*p) for p in points]
    n = len(pts)
    seg = [(pts[i + 1] - pts[i]).length for i in range(n - 1)]
    phi = [0.0] * n
    want = [0.0] * n                          # tangent length each corner wants
    for i in range(1, n - 1):
        u = (pts[i] - pts[i - 1]).normalized()
        v = (pts[i + 1] - pts[i]).normalized()
        phi[i] = math.acos(max(-1.0, min(1.0, u.dot(v))))
        want[i] = r * math.tan(phi[i] / 2) if phi[i] > 1e-3 else 0.0
    t = list(want)
    for i in range(n - 1):                    # share each segment between its two corners
        need = want[i] + want[i + 1]
        if need > seg[i] > 0:
            f = seg[i] / need
            t[i] = min(t[i], want[i] * f)
            t[i + 1] = min(t[i + 1], want[i + 1] * f)
    out = [pts[0]]
    for i in range(1, n - 1):
        if want[i] <= 0:
            out.append(pts[i])
            continue
        u = (pts[i] - pts[i - 1]).normalized()
        v = (pts[i + 1] - pts[i]).normalized()
        rr = t[i] / math.tan(phi[i] / 2)
        if warnings is not None and rr < r - 0.5:
            warnings.append(f"{name}: bend radius {rr:.1f} mm at corner {i} (minimum {r:.0f} mm)")
        a = pts[i] - u * t[i]
        nn = (v - u * u.dot(v)).normalized()
        c = a + nn * rr
        steps = max(2, int(math.degrees(phi[i]) / 15))
        for k in range(steps + 1):
            al = phi[i] * k / steps
            out.append(c + (nn * (-math.cos(al)) + u * math.sin(al)) * rr)
    out.append(pts[-1])
    return [(p.X, p.Y, p.Z) for p in out]


def path_length(points) -> float:
    return sum((Vector(*b) - Vector(*a)).length for a, b in zip(points, points[1:]))


def cable_clip(x: float, y: float, zc: float, r: float, along_x: bool) -> Part:
    """Printed push-in cable clip on the tray floor: a pedestal up to the cable,
    two prongs either side with small lips the cable snaps past."""
    t, lip = P.CLIP
    gap = r + 0.25
    top = zc + 0.6 * r
    ln = 5.0
    w = 2 * (gap + t)
    part = None
    base_h = zc - r - 0.15 - P.FLOOR
    if base_h > 0.2:
        part = Pos(0, 0, P.FLOOR - 0.01) * Box(w, ln, base_h + 0.01, align=MIN)
    for sx in (-1, 1):
        prong = Pos(sx * (gap + t / 2), 0, P.FLOOR - 0.01) * Box(t, ln, top - P.FLOOR + 0.01, align=MIN)
        lip_b = Pos(sx * (gap - 0.25), 0, top - 0.8) * Box(0.5 + 0.02, ln, 0.8, align=MIN)
        part = (prong + lip_b) if part is None else part + prong + lip_b
    part = Rot(Z=90) * part if along_x else part
    return Pos(x, y, 0) * part


def cable(points: list[tuple[float, float, float]], d: float) -> tuple[Part, float]:
    """A cable as joined cylinders along a path. Returns the part and its length."""
    solids, length = [], 0.0
    pts = [Vector(*points[0])]
    for p in points[1:]:                       # drop near-duplicate points (arc ends)
        if (Vector(*p) - pts[-1]).length > 0.2:
            pts.append(Vector(*p))
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        v = b - a
        solids.append(Plane(origin=a, z_dir=v) * Cylinder(d / 2, v.length, align=MIN))
        if i < len(pts) - 2:
            solids.append(Pos(b) * Sphere(d / 2))
        length += v.length
    try:
        part = solids[0].fuse(*solids[1:]) if len(solids) > 1 else solids[0]
        if part is None or part.volume <= 0:
            raise ValueError
    except Exception:
        part = Compound(children=solids)
    return part, length


def panel_geometry(st: Stack) -> dict:
    """Where the 7B's panel, its display board and their features sit (flat frame).
    The panel's active area is centered at the origin."""
    g = {}
    g["px0"] = px0 = -P.AA_W / 2 - P.PANEL_BORDER_LEFT
    g["px1"] = px1 = px0 + P.PANEL_W
    g["py0"] = py0 = -P.AA_H / 2 - P.PANEL_BORDER_FRONT
    g["py1"] = py1 = py0 + P.PANEL_H
    g["pcx"], g["pcy"] = pcx, pcy = (px0 + px1) / 2, (py0 + py1) / 2
    g["glass_rect"] = (pcx - P.PANEL_GLASS[0] / 2, pcx + P.PANEL_GLASS[0] / 2,
                       pcy - P.PANEL_GLASS[1] / 2, pcy + P.PANEL_GLASS[1] / 2)
    g["panel_back"] = panel_back = st.glass - P.PANEL_T              # the frame's back sheet
    g["panel_z0"] = panel_z0 = panel_back - P.DISPLAY_STANDOFF_H     # M3 tab faces, display board top
    g["dx0"] = dx0 = px0 + P.DISPLAY_PCB_LEFT
    g["dy1"] = dy1 = py1 - P.DISPLAY_PCB_BACK
    g["dpcb_top"] = panel_z0
    g["dpcb_bot"] = dpcb_bot = panel_z0 - P.PCB_T
    g["usb_y"] = dy1 - P.USB_FROM_PCB_BACK
    g["uart_y"] = dy1 - P.UART_USB_FROM_PCB_BACK
    g["usb_z"] = dpcb_bot - P.USB_BELOW_PCB
    g["lowest"] = dpcb_bot - P.DISPLAY_PARTS_H
    g["conn_bot"] = dpcb_bot - P.DISPLAY_CONNECTOR_H
    g["hy"] = (dx0 + P.DISPLAY_PCB[0] - 6, dy1 - P.DISPLAY_CONN_ROW[0], P.DISPLAY_CONN_ROW[1])
    g["j8"] = (dx0 + P.DISPLAY_PCB[0], dy1 - P.DISPLAY_J8_FROM_PCB_BACK, dpcb_bot - P.DISPLAY_J8_BELOW_PCB)
    g["panel_posts"] = [(pcx + sx * P.PANEL_M3_DX / 2, y) for sx in (-1, 1)
                        for y in (py0 + P.PANEL_M3_FROM_FRONT, py1 - P.PANEL_M3_FROM_BACK)]
    g["pin_z"] = dpcb_bot - P.DISPLAY_BUTTON_Z
    return g


def display_items(st: Stack, g: dict, key_xy, win_xy, win_size) -> list[Item]:
    """The 7B: panel module (with its M3 tabs) and Waveshare's ESP32-S3 board under it."""
    dx0, dy1, dpcb_bot, dpcb_top = g["dx0"], g["dy1"], g["dpcb_bot"], g["dpcb_top"]
    sw_, sh_ = P.USB_C_SOCKET[0], P.USB_C_SOCKET[1]
    dpcb = Pos(dx0, dy1, dpcb_bot) * Box(*P.DISPLAY_PCB, P.PCB_T, align=(Align.MIN, Align.MAX, Align.MIN))
    module = Pos(dx0 + 8.0, dy1 - 1, dpcb_bot - 3.1) * Box(18, 25.5, 3.1, align=(Align.MIN, Align.MAX, Align.MIN))
    usb = None
    for y in (g["usb_y"], g["uart_y"]):                       # native USB + USB-to-UART ports
        u = Pos(dx0, y, g["usb_z"]) * Box(7.6, sw_, sh_, align=(Align.MIN, Align.CENTER, Align.CENTER))
        dpcb -= Pos(dx0 - 0.1, y, g["usb_z"]) * Box(7.8, sw_ + 0.4, sh_ + 0.2,
                                                     align=(Align.MIN, Align.CENTER, Align.CENTER))
        usb = u if usb is None else usb + u
    hy_x, hy_y, hy_len = g["hy"]
    hy = Pos(hy_x, hy_y, g["conn_bot"]) * Box(6, hy_len, P.DISPLAY_CONNECTOR_H,
                                              align=(Align.MIN, Align.CENTER, Align.MIN))
    buttons = None
    for name, off in P.DISPLAY_BUTTONS.items():
        # side-actuated tact switch at the back edge, center DISPLAY_BUTTON_Z below the board
        b = Pos(dx0 + off, dy1 - 1.6, dpcb_bot - 2 * P.DISPLAY_BUTTON_Z) * Box(3.5, 3.8, 2 * P.DISPLAY_BUTTON_Z,
                                                                            align=MIN)
        buttons = b if buttons is None else buttons + b
    dboss = None
    for bx_, by_ in ((dx0 + 3.5, dy1 - 3.5), (dx0 + P.DISPLAY_PCB[0] - 3.5, dy1 - 3.5),
                     (dx0 + 3.5, dy1 - P.DISPLAY_PCB[1] + 3.5),
                     (dx0 + P.DISPLAY_PCB[0] - 3.5, dy1 - P.DISPLAY_PCB[1] + 3.5)):
        b_ = Pos(bx_, by_, dpcb_top) * Cylinder(2.0, g["panel_back"] - dpcb_top, align=MIN)
        dboss = b_ if dboss is None else dboss + b_
    items = [Item(dpcb, "display_board_pcb", C_PCB, 1),
             Item(dboss, "display_board_bosses", C_STANDOFF, 1),
             Item(module, "display_board_esp32s3", C_MOTOR, 1),
             Item(usb, "display_board_usb_c", C_MOTOR, 1),
             Item(hy, "display_board_connectors", C_SWITCH, 1),
             Item(buttons, "display_board_buttons", C_CHIP, 1)]
    items += screen(st, P.PANEL_W, P.PANEL_H, P.PANEL_T, (P.AA_W, P.AA_H), g["pcy"],
                    key_xy, win_xy, win_size, "panel7", center_x=g["pcx"])
    mi = [it.label for it in items].index("panel7_module")
    mod = items[mi].part
    for x, y in g["panel_posts"]:                  # M3 tabs below the back sheet (tab + side web)
        sx = 1 if x > g["pcx"] else -1
        mod += Pos(x, y, g["panel_z0"]) * Box(8.0, 8.0, P.PANEL_TAB_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
        mod += Pos(x + sx * 3.5, y, g["panel_z0"]) * Box(1.0, 8.0, g["panel_back"] - g["panel_z0"] + 0.01,
                                                         align=(Align.CENTER, Align.CENTER, Align.MIN))
    items[mi] = Item(mod, "panel7_module", C_PANEL, 1)
    return items


def frame_supports(L: Layout, rect, frame_x1: float, py1: float, px0: float) -> dict:
    """Frame PCB screw positions (D8). pan: off the glass (back edge, left side),
    pan-head M2; csk: everywhere else, countersunk M2 flush with the PCB underside.
    csk_inner: the strip-crossing ones (smaller bosses between the caps)."""
    rows = sorted({y for _, y in L.key_xy}, reverse=True)
    right_x = (frame_x1 + max(x for x, _ in L.key_xy) + PCB_WIN / 2) / 2
    strip = [y - PCB_WIN / 2 - (P.KEY_PITCH - PCB_WIN) / 2 for y in rows]
    pan = [(x, py1 + 2.5) for x in (-50.0, 0.0, 50.0)] + [(px0 - 2.5, y) for y in (0.0, 25.0)]
    kx = sorted(x for x, _ in L.cut_xy)
    webs = [((a + b) / 2, L.cut_xy[0][1]) for a, b in zip(kx, kx[1:])]
    right = [(right_x, y) for y in strip]
    inner = [(x, strip[-2]) for x in P.FRAME_INNER_SUPPORT_X]
    return dict(pan=pan, csk=webs + right, csk_inner=inner)


def full_device(tilt: bool = True, slots: tuple | None = None) -> tuple[list[Item], Layout, dict]:
    """Full device. With tilt=True the slab is angled toward the user on a stand.

    slots: what's in each knob slot, left to right: "haptic", "lite" or "blank"
    (D23; default P.KNOB_SLOTS). Only the slots' contents (and the backplane's pogo
    pins, drawn compressed under a module) differ between configurations.

    Everything is built in the flat (untilted) frame first; assembly steps and
    checks use that frame (see cad/assembly.py).
    """
    slots = tuple(slots or P.KNOB_SLOTS)
    if len(slots) != P.KNOBS or any(k not in P.SLOT_TYPES for k in slots):
        raise ValueError(f"slots must be {P.KNOBS} of {P.SLOT_TYPES}, got {slots}")
    st = make_stack(P.FLOOR, P.TOP_PLATE_T)
    L = full_layout()
    items: list[Item] = []
    screws: list[Screw] = []

    # --- Panel frame, positioned so the active area is centered at the origin
    g = panel_geometry(st)
    px0, px1, py0, py1, pcx = g["px0"], g["px1"], g["py0"], g["py1"], g["pcx"]
    panel_back, panel_z0 = g["panel_back"], g["panel_z0"]
    knob_y = L.knob_xy[0][1]
    kxs = [x for x, _ in L.knob_xy]
    board_front = P.BP_FRONT
    board_back_y = knob_y + P.BP_BACK
    board_x1 = max(kxs) + P.BP_SIDE

    # --- Case outline: symmetric about the key grid
    half_w = max(-px0, px1) + P.INNER_CLEAR
    ix0, ix1 = -half_w, half_w
    iy1 = py1 + P.INNER_CLEAR_BACK
    iy0 = knob_y - max(P.MOTOR_D / 2 + P.INNER_CLEAR + 1.0, board_front + P.INNER_CLEAR, P.SLOT_OPEN[1] + 0.2)
    ox0, ox1, oy0, oy1 = ix0 - P.WALL, ix1 + P.WALL, iy0 - P.WALL, iy1 + P.WALL
    outer = (ox0, ox1, oy0, oy1)
    cx, cy = (ox0 + ox1) / 2, (oy0 + oy1) / 2

    # --- Waveshare's ESP32-S3 board behind the panel (parts facing down)
    dx0, dy1, dpcb_bot = g["dx0"], g["dy1"], g["dpcb_bot"]
    usb_y, usb_z = g["usb_y"], g["usb_z"]
    lowest, conn_bot = g["lowest"], g["conn_bot"]
    pocket = math.ceil(max(0.0, (P.FLOOR + 1.0) - conn_bot) * 2) / 2   # 1 mm clearance, 0.5 mm steps
    if pocket > P.FLOOR - 0.6:
        L.warnings.append(f"display board connectors need a {pocket:.1f} mm floor pocket; "
                          f"floor is only {P.FLOOR} mm")
    if lowest < P.FLOOR + 0.5:
        L.warnings.append(f"display board parts reach {lowest:.1f} mm, below the floor + 0.5 mm")
    hy_x, hy_y, hy_len = g["hy"]

    # --- Positions of posts, bosses and screws
    post_r = P.PLATE_POST_D / 2
    plate_posts = [(sx * (half_w - P.PLATE_POST_INSET), y) for sx in (-1, 1)
                   for y in ((py1 + iy1) / 2, iy0 + P.PLATE_POST_INSET)]
    panel_posts = g["panel_posts"]
    # Backplane: screws at both ends and along the back strip; at the front the slot
    # bosses come up through it and the modules' bases press it down (D23)
    kb_screws = [(sx * (board_x1 - 2.5), knob_y) for sx in (-1, 1)]
    kb_screws += [(x + 7.5, knob_y + 17.5) for x in kxs]
    slot_bosses = [(n, k, x + P.MODULE_POSTS[k][0], knob_y + P.MODULE_POSTS[k][1])
                   for n, x in enumerate(kxs) for k in P.MODULE_SCREWS]
    # Frame PCB: reaches past the panel on the left and back (pan-head screws there)
    frame_y1 = py1 + 4.5
    frame_x0 = px0 - 5.0
    frame_x1 = ix1 - 2.2                          # frame PCB reaches past the panel on the right
    m = P.FRAME_PCB_MARGIN
    rect = (frame_x0, frame_x1, -P.AA_H / 2 - min(m, P.PANEL_BORDER_FRONT), frame_y1)
    fs = frame_supports(L, rect, frame_x1, py1, px0)
    frame_holes = fs["pan"] + fs["csk"] + fs["csk_inner"]
    frame_pins = [(-25.0, py1 + 2.5), (px0 - 2.5, 12.5)]       # locating pins (plate) in NPTH holes
    # BOOTSEL (recovery): on the knob board's left border, pressed through the floor
    boot_xy = (-(board_x1 - 2.5), knob_y + P.BOOTSEL_FROM_KNOB0)

    # --- Internal cabling layout (docs/wiring.md). Every plug is a box: its
    # overmold or housing outside the socket, so the interference checks see it.
    W_usb, H_usb, Ls_usb = P.USB_PLUG_STRAIGHT
    Lra_usb = P.USB_PLUG_RA[2]
    sw_, sh_, sd_ = P.USB_C_SOCKET
    warns = L.warnings
    # USB board: main body in the back-left corner beside the display board, an
    # arm along the back wall to the external port (left of the BOOT/RESET pinholes)
    ub_z0 = P.FLOOR + P.USB_BOARD_Z
    ub_z1 = ub_z0 + P.PCB_T
    ub_x0, ub_x1 = ix0 + 1.2, dx0 - 2.7
    ub_front = 21.0                               # main body front edge
    arm_y0 = dy1 - P.USB_ARM_UNDER                # arm reaches under the display board's back edge
    ext_x = P.USB_EXT_X
    arm_x1 = ext_x + 11.5
    ext_z = ub_z0 + P.PCB_T / 2                   # mid-mount socket: shell centered on the board
    j_disp_x = ub_x0 + 5.3                        # USB-C socket for the display board cable
    gh_usb = (ub_x0 + 15.2, 36.3)                 # JST-GH header (to the knob board), facing front
    ub_screws = [(ub_x0 + 5.5, 31.5), (ub_x1 - 2.5, 41.0), (ext_x - 8.0, 49.2), (ext_x + 7.7, 49.2)]
    with BuildSketch() as usk:
        with Locations(((ub_x0 + ub_x1) / 2, (ub_front + iy1) / 2)):
            Rectangle(ub_x1 - ub_x0, iy1 - ub_front)
        with Locations(((ub_x1 - 1.0 + arm_x1) / 2, (arm_y0 + iy1) / 2)):
            Rectangle(arm_x1 - ub_x1 + 1.0, iy1 - arm_y0)
        for (x, y), r in ([(pp, P.PANEL_POST_D / 2 + 0.6) for pp in panel_posts]
                          + [(pp, post_r + 0.6) for pp in plate_posts]):
            if ub_x0 - r < x < arm_x1 + r and ub_front - r < y < iy1 + r:
                with Locations((x, y)):
                    Circle(r, mode=Mode.SUBTRACT)
        with Locations((ext_x, iy1 - (sd_ + 0.3) / 2)):
            Rectangle(sw_ + 0.3, sd_ + 0.3, mode=Mode.SUBTRACT)    # socket sinks into the board
        with Locations(*ub_screws):
            Circle(P.M2_CLEAR / 2, mode=Mode.SUBTRACT)
    usb_sketch = usk.sketch

    # Backplane connectors: JST-GH (USB link) at the back-left corner; keys FFC
    # (ZIF) and touch (JST-SH, top entry) at the right end; the optional GPIO6
    # link (HY2.0) on the back edge at the right; a slot connector under each knob.
    kpt = st.bp_top
    gh_k = (-board_x1 + 9.3, board_back_y)       # header mouth on the back edge
    zif_y = board_back_y - 2.4                    # ZIF center (also the frame PCB's ZIF)
    zif_x1 = board_x1                             # mouth at the board's right edge
    tch = (board_x1 - 2.5, knob_y + 7.24)
    hyw, hyd, hyh = P.HY_HEADER
    hy_k = (P.HY_KNOB_X, board_back_y)            # GPIO6 header mouth on the back edge
    mid = len(kxs) // 2                          # RP2350B between the middle slots, under the panel
    mcu_xy = ((kxs[mid] + kxs[mid + 1]) / 2, knob_y + 25.0)

    # Cable paths (flat frame). (points, diameter, bend radius, kind, plug ends)
    cpaths = {}
    # Display board cable: right-angle plug on the display board (cable leaves
    # forward), loop in the free bay at the left, straight plug into the USB board
    s7 = (dx0 - Lra_usb + 3.0, usb_y - W_usb / 2, usb_z)
    e7 = (j_disp_x, ub_front - Ls_usb, ub_z1 + sh_ / 2)
    yu, xu = -24.5, s7[0] - 2 * P.USB_BEND_R      # U-turn: bottom line and return run
    cpaths["cable_usb_display"] = (
        [s7, (s7[0], yu, 11.0), (xu, yu, 11.0), (xu, -12.0, 10.0), (e7[0], -4.5, e7[2]), e7],
        P.USB_CABLE_D, P.USB_BEND_R, "usb", ("plug_display_usb", "plug_usb_board_display"))
    # USB link to the knob board (JST-GH 8-pin): between the two USB-C plugs, under the loop
    sg = (gh_usb[0], gh_usb[1] - P.GH_PLUG[2], ub_z1 + P.GH_PLUG[1] / 2)
    eg = (gh_k[0], gh_k[1] + P.GH_PLUG[2], kpt + P.GH_PLUG[1] / 2)
    cpaths["cable_usb_knob_gh"] = (
        [sg, (sg[0], 16.0, 8.6), (sg[0], 0.0, 7.0), (sg[0] - 4.0, -14.0, 4.7),
         (eg[0], -21.0, 4.7), (eg[0], eg[1] + 3.5, eg[2]), eg],
        P.GH_CABLE_D, 3.0, "gh", ("plug_usb_board_gh", "plug_knob_gh"))
    # Keys FFC: frame PCB ZIF (top side, right edge) down past the panel into the knob board's ZIF
    sf = (frame_x1 + 1.0, zif_y, st.pcb_top + 1.0)
    ef = (zif_x1 + 1.0, zif_y, kpt + 1.0)
    cpaths["cable_keys_ffc"] = (
        [sf, (ix1 - 0.5, zif_y, sf[2]), (ix1 - 0.5, zif_y, ef[2]), ef],
        0.6, 1.0, "ffc", ("plug_ffc_frame", "plug_ffc_knob"))
    # Touch: band connector (under the plate, right end) to the backplane's top-entry header.
    # The band stops short of the frame PCB's ZIF (they'd overlap in plan). Its header faces
    # right (+x), low on the band, so the plug stays out of slot 4's opening (D23) and in
    # front of the frame PCB's ZIF
    band_x1 = frame_x1 - P.ZIF_12P[1] - 0.5
    band_y = knob_y + P.MOTOR_D / 2 + P.TOUCH_BAR_MARGIN + P.SH_PLUG[0] / 2 + 0.4
    tb_c = (band_x1 - P.SH_HEADER_SIDE[1] / 2, band_y,
            st.plate_bot + P.TOUCH_BAR_RECESS - P.TOUCH_BAR_T - P.SH_HEADER_SIDE[2] / 2)
    st_ = (band_x1 + P.SH_PLUG[2], tb_c[1], tb_c[2])
    et_ = (tch[0], tch[1], kpt + P.SH_HEADER_TOP[2] + P.SH_PLUG[2])
    if P.TOUCH_BAR:
        cpaths["cable_touch"] = (
            [st_, (ix1 - 1.5, knob_y + P.SLOT_OPEN[2] - 1.0, st_[2] - 2.0),
             (ix1 - 1.5, tch[1] - 3.0, et_[2] + 2.0), (et_[0], et_[1], et_[2] + 2.5), et_],
            1.6, 1.5, "sh", ("plug_touch_band", "plug_knob_touch"))
    # Optional GPIO6 link (D5): knob board HY2.0 header -> back under the panel -> J8 on
    # the display board's right edge (plug inserted toward -x, cable trails +x)
    j8x, j8y, j8z = g["j8"]
    hp_len = P.HY_PLUG[2]
    sh_y = (hy_k[0], hy_k[1] + hp_len, kpt + P.HY_PLUG[1] / 2)
    eh_y = (j8x + hp_len, j8y, j8z)
    if P.HY_LINK:
        cpaths["cable_hy_link"] = (
            [sh_y, (sh_y[0], sh_y[1] + 2.5, sh_y[2] + 1.0), (j8x + 10.5, j8y - 4.5, j8z),
             (j8x + 10.5, j8y, j8z), eh_y],
            P.HY_CABLE_D, 2.0, "hy", ("plug_knob_hy", "plug_display_j8"))
    # Clips printed with the tray: (x, y, cable center z, cable d, cable runs along x?)
    clips = [(s7[0], -8.0, 9.6, P.USB_CABLE_D, False), (xu, -14.3, 10.8, P.USB_CABLE_D, False),
             (sg[0] - 2.25, -18.0, 4.7, P.GH_CABLE_D, False)]

    # --- Tray: floor, walls, and everything printed with it
    outer_sk = Pos(cx, cy) * RectangleRounded(ox1 - ox0, oy1 - oy0, P.CORNER_R)
    inner_sk = Pos((ix0 + ix1) / 2, (iy0 + iy1) / 2) * RectangleRounded(
        ix1 - ix0, iy1 - iy0, max(P.CORNER_R - P.WALL, 0.5))
    tray = extrude(outer_sk, amount=st.plate_bot)
    tray -= Pos(0, 0, P.FLOOR) * extrude(inner_sk, amount=st.plate_bot)
    for x, y in panel_posts:                                   # posts under the panel tabs
        tray += Pos(x, y, P.FLOOR - 0.01) * Cylinder(P.PANEL_POST_D / 2, panel_z0 - P.FLOOR + 0.01,
                                                     align=MIN)
    for x, y in kb_screws:                                     # backplane bosses
        tray += Pos(x, y, P.FLOOR - 0.01) * Cylinder(P.BP_BOSS_D / 2, st.bp_bot - P.FLOOR + 0.01, align=MIN)
    # Slot bosses (D23): up through the backplane to its top face; each takes an M2
    # heat-set insert for a module's (or blank's) retention screw
    ins2_d, ins2_l = P.INSERT_M2
    for _, _, x, y in slot_bosses:
        tray += Pos(x, y, P.FLOOR - 0.01) * Cylinder(P.BP_BOSS_D / 2, st.bp_top - P.FLOOR + 0.01, align=MIN)
        tray -= Pos(x, y, st.bp_top - ins2_l - 0.1) * Cylinder(ins2_d / 2, ins2_l + 1, align=MIN)
    for x in kxs:                                              # ribs under each slot connector
        x0_, x1_, y0_, y1_ = pogo_window()
        tray += Pos(x, knob_y + (P.POGO_ROW0 + y1_) / 2 - 0.3, P.FLOOR - 0.01) * Box(
            x1_ - x0_, y1_ - P.POGO_ROW0 + 1.0, st.bp_bot - P.FLOOR + 0.01, align=MIN)
    # Panel stops: the panel can't slide off its posts while the tray is tipped
    panel_stops = [(30.0, py1 + 1.2, 2.0, 2.0), (65.0, py1 + 1.2, 6.0, 2.0),
                   (px0 - 1.2, board_back_y + 4.0, 2.0, 6.0)]
    for x, y, w_, d_ in panel_stops:
        tray += Pos(x, y, P.FLOOR - 0.01) * Box(w_, d_, panel_back + 2.0 - P.FLOOR + 0.01,
                                                align=(Align.CENTER, Align.CENTER, Align.MIN))
    for x in (-40.0, 0.0, 40.0):                               # ribs under the backplane's back strip
        tray += Pos(x, board_back_y - 6, P.FLOOR - 0.01) * Box(
            12, 3, st.bp_bot - P.FLOOR + 0.01, align=MIN)
    if pocket > 0:
        tray -= Pos(hy_x - P.FLOOR_POCKET_MARGIN, hy_y, P.FLOOR - pocket) * Box(
            6 + 2 * P.FLOOR_POCKET_MARGIN, hy_len + 2 * P.FLOOR_POCKET_MARGIN, pocket + 1,
            align=(Align.MIN, Align.CENTER, Align.MIN))
    for x, y in ub_screws:                                     # USB board bosses
        tray += Pos(x, y, P.FLOOR - 0.01) * Cylinder(P.BP_BOSS_D / 2, ub_z0 - P.FLOOR + 0.01,
                                                     align=MIN)
        tray -= Pos(x, y, 0.6) * Cylinder(P.M2_PILOT / 2, 20, align=MIN)
    # Backstop behind the USB board's arm: pushing a plug in loads the case, not the solder joints
    tray += Pos(ext_x, arm_y0 - 0.75, P.FLOOR - 0.01) * Box(12.0, 1.5, ub_z1 - P.FLOOR + 0.01,
                                                            align=(Align.CENTER, Align.CENTER, Align.MIN))
    # External USB-C port: the socket face is flush with the inside of the back wall;
    # the plug's overmold seats in this opening, so a sideways yank bears on the wall
    tray -= Pos(ext_x, (iy1 + oy1) / 2 + 0.5, ext_z) * Box(P.USB_EXT_POCKET[0], P.WALL + 1.02,
                                                          P.USB_EXT_POCKET[1])
    for x, y, zc, d, along_x in clips:
        tray += cable_clip(x, y, zc, d / 2, along_x)
    pin_z = g["pin_z"]
    for name, off in P.DISPLAY_BUTTONS.items():                # paperclip holes, back wall
        tray -= Pos(dx0 + off, iy1 + P.WALL / 2, pin_z) * Rot(X=90) * Cylinder(
            P.PINHOLE_D / 2, P.WALL * 3)
    tray -= Pos(*boot_xy, -1) * Cylinder(P.PINHOLE_D / 2, P.FLOOR + 2, align=MIN)   # BOOTSEL, floor
    hd, hh = P.M3_HEAD
    cb = P.FLOOR - P.FLOOR_WEB_MIN                             # plate posts: counterbore depth from below
    if cb < hh:
        L.warnings.append(f"M3 head ({hh} mm) sticks out of its {cb:.1f} mm counterbore")
    # Panel screws: the longest standard screw whose head is still recessed, with the
    # counterbore set so the tip ends PANEL_SCREW_PAST beyond the tab face
    pan_len = max(n_ for n_ in STD_LENGTHS if panel_z0 + P.PANEL_SCREW_PAST - n_ >= hh + 0.2)
    cb_pan = panel_z0 + P.PANEL_SCREW_PAST - pan_len
    for x, y in panel_posts:
        tray -= Pos(x, y, -1) * Cylinder(P.M3_CLEAR / 2, panel_z0 + 2, align=MIN)
        tray -= Pos(x, y, -1) * Cylinder(hd / 2 + 0.2, cb_pan + 1, align=MIN)
    for x, y in plate_posts:
        tray -= Pos(x, y, -1) * Cylinder(P.M3_CLEAR / 2, P.FLOOR + 2, align=MIN)
        tray -= Pos(x, y, -1) * Cylinder(hd / 2 + 0.2, cb + 1, align=MIN)
    for x, y in kb_screws:
        tray -= Pos(x, y, 0.6) * Cylinder(P.M2_PILOT / 2, 20, align=MIN)
    magnets = [(sx * 40.0, oy0 + f * (oy1 - oy0)) for sx in (-1, 1) for f in P.MAGNET_ROWS]
    for x, y in magnets:
        tray -= Pos(x, y, -1) * Cylinder(P.MAGNET_TRAY[0] / 2 + 0.1, P.MAGNET_TRAY[1] + 1.1, align=MIN)
    items.append(Item(tray, "case_tray", C_CASE, 0))
    for i, (x, y) in enumerate(magnets):
        items.append(Item(Pos(x, y, 0.0) * Cylinder(P.MAGNET_TRAY[0] / 2, P.MAGNET_TRAY[1], align=MIN),
                          f"magnet_tray_{i}", C_MAGNET, -1))
    feet_front = [(sx * ((ox1 - ox0) / 2 - 25), oy0 + 7) for sx in (-1, 1)]
    for i, (x, y) in enumerate(feet_front):
        items.append(Item(Pos(x, y, -P.FOOT[1]) * Cylinder(P.FOOT[0] / 2, P.FOOT[1], align=MIN),
                          f"foot_front_{i}", C_FOOT, -1))

    # --- Display board (Waveshare), shown with its panel
    items += display_items(st, g, L.key_xy, L.win_xy, L.win_size)
    for i, (x, y) in enumerate(panel_posts):
        screws.append(Screw(f"screw_panel_{i}", "", x, y, cb_pan, True, pan_len, P.M3_HEAD,
                            "panel7_module", "display", engage=(1.5, P.PANEL_SCREW_MAX)))

    # --- Frame PCB + switches (hangs from the top plate)
    fsk = frame_pcb_sketch(rect, L.key_xy, L.cut_xy, L.cut_size, frame_holes, frame_pins)
    notch = None
    for x, y in plate_posts:                       # clear the top plate's posts
        c = Pos(x, y) * Circle(post_r + 0.6)
        notch = c if notch is None else notch + c
    fsk = fsk - notch
    frame = Pos(0, 0, st.pcb_bot) * extrude(fsk, amount=P.PCB_T)
    csd, csh = P.M2_CSK_HEAD
    for x, y in fs["csk"] + fs["csk_inner"]:       # countersinks (JLC option): heads flush underneath
        frame -= Pos(x, y, st.pcb_bot - 0.1) * Cylinder(csd / 2 + 0.1, csh + 0.1, align=MIN)
    items.append(Item(frame, "frame_pcb", C_PCB, 2))
    sw = switch(st)
    for i, (x, y) in enumerate(L.key_xy):
        items.append(Item(Pos(x, y + SW_DY, 0) * sw, f"switch_{i}", C_SWITCH, 2))
    for k, (x, y) in enumerate(fs["pan"]):
        screws.append(Screw(f"screw_frame_pan_{k}", "", x, y, st.pcb_bot, True,
                            std_length(P.PCB_T + 3.0), P.M2_HEAD, "top_plate", "top_plate_sub",
                            engage=(3.0, None), pilot=True))
    csk_nom = std_length(P.PCB_T + 3.0)
    for k, (x, y) in enumerate(fs["csk"] + fs["csk_inner"]):
        screws.append(Screw(f"screw_frame_csk_{k}", "", x, y, st.pcb_bot + csh, True, csk_nom - csh,
                            P.M2_CSK_HEAD, "top_plate", "top_plate_sub", engage=(3.0, None), pilot=True,
                            style="countersunk", nominal=csk_nom))

    # --- Caps
    cap = key_cap(st)
    for i, (x, y) in enumerate(L.key_xy):
        items.append(Item(Pos(x, y, 0) * cap, f"cap_{i}", C_CAP, 3))

    # --- Top plate, with its posts down to the floor and bosses for the frame PCB
    lw, lt = P.KNOB_WIN_LEDGE
    ow, of, ob = P.SLOT_OPEN
    openings = [(x, knob_y + (ob - of) / 2, 2 * ow + P.HOLE_COMP, of + ob + P.HOLE_COMP) for x in kxs]
    psk = plate_sketch(outer, P.CORNER_R, L.key_xy, L.cut_xy, L.cut_size, [], win_ledge=lw, openings=openings)
    plate = top_plate(psk, st, P.TOP_PLATE_T, L)
    plate += key_guides(st, L.key_xy)              # cap guide skirts (D8, B3)
    for x, y in L.cut_xy:                          # window pockets above the ledge
        plate -= Pos(x, y, st.plate_bot + lt) * extrude(
            RectangleRounded(L.cut_size[0] + P.HOLE_COMP, L.cut_size[1] + P.HOLE_COMP, 1.0), amount=P.TOP_PLATE_T)
    for x, y in frame_pins:
        plate += Pos(x, y, st.pcb_top) * Cylinder(P.FRAME_BOSS_D / 2, st.plate_bot - st.pcb_top + 0.01,
                                                         align=MIN)
        plate += Pos(x, y, st.pcb_bot + 0.2) * Cylinder(P.FRAME_PIN_D / 2, P.PCB_T - 0.19, align=MIN)
    # Locating tabs just inside the walls (register the plate on the tray; the front
    # wall has the slot openings, the dividers below register it there)
    for x, y, w_, d_ in [(ix0 + 0.3 + 0.6, -20.0, 1.2, 10.0), (ix1 - 0.3 - 0.6, -20.0, 1.2, 10.0),
                         (0.0, iy1 - 0.3 - 0.6, 10.0, 1.2)]:
        plate += Pos(x, y, st.plate_bot - 3.0) * Box(w_, d_, 3.01, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # Dividers between the slot openings (D23): walls down to just above the backplane.
    # They stiffen the plate's front strip around the openings and guide each module
    # straight down onto its pogo pins
    for a_, b_ in zip(kxs, kxs[1:]):
        dz0 = st.bp_top + P.SLOT_WALL_GAP
        plate += Pos((a_ + b_) / 2, knob_y + (ob - of) / 2, dz0) * Box(
            (b_ - a_) - 2 * ow - P.HOLE_COMP, of + ob, st.plate_bot - dz0 + 0.01, align=MIN)
    # Fence between slot 4 and the spare FFC / touch cable by the right wall
    fx = max(kxs) + ow + 1.2
    plate += Pos(fx, knob_y - 12.0, st.knob_pcb_top + 2.0) * Box(
        1.2, 14.0, st.plate_bot - st.knob_pcb_top - 2.0 + 0.01, align=MIN)
    ins_d, ins_l = P.INSERT_M3
    for x, y in plate_posts:                       # posts with an M3 heat-set insert in the bottom end
        plate += Pos(x, y, P.FLOOR) * Cylinder(post_r, st.plate_bot - P.FLOOR + 0.01, align=MIN)
        plate -= Pos(x, y, P.FLOOR - 0.1) * Cylinder(ins_d / 2, ins_l + 1.1, align=MIN)
    for (x, y), d in ([(p_, P.FRAME_BOSS_D) for p_ in fs["pan"] + fs["csk"]]
                      + [(p_, P.FRAME_INNER_BOSS_D) for p_ in fs["csk_inner"]]):
        plate += Pos(x, y, st.pcb_top) * Cylinder(d / 2, st.plate_bot - st.pcb_top + 0.01, align=MIN)
        plate -= Pos(x, y, st.pcb_top - 0.1) * Cylinder(P.M2_PILOT / 2, 4.5, align=MIN)
    items.append(Item(plate, "top_plate", C_PLATE, 4))
    for i, (x, y) in enumerate(plate_posts):
        items.append(Item(Pos(x, y, P.FLOOR) * Cylinder(ins_d / 2, ins_l, align=MIN),
                          f"top_plate_insert_{i}", C_BRASS, 4))
    items += knob_windows(st, L, ledge_t=lt)
    tb, tb_h = touch_bar(st, L, (-(P.AA_W - 2) / 2, band_x1), knob_y + P.MOTOR_D / 2,
                         recess=P.TOUCH_BAR_RECESS)
    items += tb
    if tb:                                          # flat pocket the band sits in (solid plate above it)
        bb = tb[0].part.bounding_box()
        plate -= Pos((bb.min.X + bb.max.X) / 2, (bb.min.Y + bb.max.Y) / 2, st.plate_bot - 1) * Box(
            bb.size.X + 0.6, bb.size.Y + 0.6, P.TOUCH_BAR_RECESS + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
        items[[it.label for it in items].index("top_plate")] = Item(plate, "top_plate", C_PLATE, 4)
    info_touch = tb[0].part.bounding_box() if tb else None
    for i, (x, y) in enumerate(plate_posts):
        screws.append(Screw(f"screw_plate_{i}", "", x, y, cb, True,
                            max(n_ for n_ in STD_LENGTHS if n_ - (P.FLOOR - cb) <= ins_l - 0.3),
                            P.M3_HEAD, f"top_plate_insert_{i}", "close", engage=(3.0, ins_l - 0.3)))

    # --- Backplane: on floor bosses and ribs, located by the slot bosses (D23)
    avoid = panel_posts + plate_posts
    kitems, ksk = backplane(st, L.knob_xy, slots, avoid_xy=avoid, screw_xy=kb_screws,
                            tabs=[(board_x1 - 5.0, board_x1, board_back_y, zif_y + P.ZIF_12P[0] / 2 + 0.2)],
                            mcu_xy=mcu_xy, holes_xy=[(*boot_xy, P.BOOTSEL_PLUNGER[0] + 0.4)])
    items += kitems
    bsw, bsh = P.BOOTSEL_SW[:2], P.BOOTSEL_SW[2]
    items.append(Item(Pos(*boot_xy, kpt) * Box(*bsw, bsh, align=MIN)
                      + Pos(*boot_xy, st.bp_bot - P.BOOTSEL_PLUNGER[1]) * Cylinder(
                          P.BOOTSEL_PLUNGER[0] / 2, P.BOOTSEL_PLUNGER[1] + P.PCB_T + 0.01, align=MIN),
                      "backplane_bootsel", C_CHIP, 0))
    for i, (x, y) in enumerate(kb_screws):
        screws.append(Screw(f"screw_backplane_{i}", "", x, y, st.bp_top, False,
                            std_length(P.PCB_T + P.BP_UNDER + 2.0), P.M2_HEAD,
                            "case_tray", "backplane", engage=(3.0, None), pilot=True))
    for n, k, x, y in slot_bosses:                  # the slots' M2 heat-set inserts
        items.append(Item(Pos(x, y, st.bp_top - ins2_l) * Cylinder(ins2_d / 2, ins2_l, align=MIN),
                          f"slot_insert_{n}_{k}", C_BRASS, 0))
    # --- Knob slots (D23): a haptic module, a lite module or a blank in each
    slot_plugs = []
    for n, (kx, kind) in enumerate(zip(kxs, slots)):
        si, sp_ = slot_items(st, kx, knob_y, n, kind, screws)
        items += si
        slot_plugs += sp_
    kb = next(it.part for it in kitems if it.label == "backplane_pcb").bounding_box()
    if board_back_y > dy1 - P.DISPLAY_PCB[1] - 1.0:
        L.warnings.append(f"backplane reaches y={kb.max.Y:.1f}, into the display board "
                          f"(front edge y={dy1 - P.DISPLAY_PCB[1]:.1f})")

    # --- USB board (hub, external USB-C, current sensing) and every connector + mated plug
    def bx(c, size):
        return Pos(*c) * Box(*size)

    gw, ghh, gd = P.GH_HEADER
    zl, zd, zh = P.ZIF_12P
    items.append(Item(Pos(0, 0, ub_z0) * extrude(usb_sketch, amount=P.PCB_T), "usb_board_pcb", C_PCB, 0))
    items += [
        Item(bx((ext_x, iy1 - sd_ / 2, ext_z), (sw_, sd_, sh_)), "usb_board_usb_ext", C_MOTOR, 0),
        Item(bx((j_disp_x, ub_front + sd_ / 2, ub_z1 + sh_ / 2), (sw_, sd_, sh_)),
             "usb_board_usb_display", C_MOTOR, 0),
        Item(bx((gh_usb[0], gh_usb[1] + gd / 2, ub_z1 + ghh / 2), (gw, gd, ghh)), "usb_board_gh", C_SWITCH, 0),
        # Hub next to the external socket (short high-speed run), ESD in line between them
        Item(bx((ext_x - 13.0, arm_y0 + 2.5, ub_z1 + 0.43), (4.0, 4.0, 0.85))   # hub
             + bx((ub_x0 + 9.5, 44.0, ub_z1 + 0.55), (3.0, 3.0, 1.1))          # power switch
             + bx((ext_x - 7.0, arm_y0 + 2.5, ub_z1 + 0.5), (2.9, 1.6, 1.0)),  # ESD
             "usb_board_chips", C_CHIP, 0),
        # Optional USB-PD sink (D9, CH224-class, not fitted by default) on the external port's CC lines
        Item(bx((ext_x + 8.0, arm_y0 + 2.5, ub_z1 + P.PD_SINK[2] / 2), P.PD_SINK), "usb_board_pd_sink",
             C_CHIP, 0),
        Item(bx((gh_k[0], gh_k[1] - gd / 2, kpt + ghh / 2), (gw, gd, ghh)), "backplane_conn_gh", C_SWITCH, 0),
        Item(bx((zif_x1 - zd / 2, zif_y, kpt + zh / 2), (zd, zl, zh)), "backplane_conn_zif", C_SWITCH, 0),
        # GPIO6 link header: footprint always on the board, fitted only with the optional lead
        Item(bx((hy_k[0], hy_k[1] - hyd / 2, kpt + hyh / 2), (hyw, hyd, hyh)), "backplane_conn_hy", C_SWITCH, 0),
        Item(bx((frame_x1 - zd / 2, zif_y, st.pcb_top + zh / 2), (zd, zl, zh)), "frame_pcb_zif", C_SWITCH, 2),
    ]
    if P.TOUCH_BAR:
        items += [
            Item(bx((tch[0], tch[1], kpt + P.SH_HEADER_TOP[2] / 2),
                    (P.SH_HEADER_TOP[1], P.SH_HEADER_TOP[0], P.SH_HEADER_TOP[2])),
                 "backplane_conn_touch", C_SWITCH, 0),
            Item(bx(tb_c, (P.SH_HEADER_SIDE[1], P.SH_HEADER_SIDE[0], P.SH_HEADER_SIDE[2])), "touch_bar_conn",
                 C_SWITCH, 3),
        ]
    for i, (x, y) in enumerate(ub_screws):
        screws.append(Screw(f"screw_usbboard_{i}", "", x, y, ub_z1, False,
                            std_length(P.PCB_T + P.USB_BOARD_Z + 1.5), P.M2_HEAD, "case_tray", "usb_board",
                            engage=(3.0, None), pilot=True))

    # Mated plugs: (label, body, insertion direction, kind, mating connector, step, length out of socket)
    C_PLUG = Color(0.20, 0.20, 0.22)
    plugs = [
        ("plug_usb_ext", bx((ext_x, iy1 + Ls_usb / 2, ext_z), (W_usb, Ls_usb, H_usb)), (0, -1, 0), "usb",
         "usb_board_usb_ext", "plug_in", Ls_usb),
        ("plug_display_usb", bx((dx0 - Lra_usb / 2, usb_y, usb_z), (Lra_usb, W_usb, H_usb)), (1, 0, 0), "usb",
         "display_board_usb_c", "display", Lra_usb),
        ("plug_usb_board_display", bx((j_disp_x, ub_front - Ls_usb / 2, ub_z1 + sh_ / 2), (W_usb, Ls_usb, H_usb)),
         (0, 1, 0), "usb", "usb_board_usb_display", "display", Ls_usb),
        ("plug_usb_board_gh", bx((gh_usb[0], gh_usb[1] - P.GH_PLUG[2] / 2, ub_z1 + P.GH_PLUG[1] / 2),
                                 (P.GH_PLUG[0], P.GH_PLUG[2], P.GH_PLUG[1])), (0, 1, 0), "gh",
         "usb_board_gh", "backplane", P.GH_PLUG[2]),
        ("plug_knob_gh", bx((gh_k[0], gh_k[1] + P.GH_PLUG[2] / 2, kpt + P.GH_PLUG[1] / 2),
                            (P.GH_PLUG[0], P.GH_PLUG[2], P.GH_PLUG[1])), (0, -1, 0), "gh",
         "backplane_conn_gh", "backplane", P.GH_PLUG[2]),
        ("plug_ffc_frame", bx((frame_x1 + 0.5, zif_y, st.pcb_top + 1.0), (1.0, 13.0, 0.3)), (-1, 0, 0), "ffc",
         "frame_pcb_zif", "top_plate_sub", 1.0),
        ("plug_ffc_knob", bx((zif_x1 + 0.5, zif_y, kpt + 1.0), (1.0, 13.0, 0.3)), (-1, 0, 0), "ffc",
         "backplane_conn_zif", "close", 1.0),
    ]
    if P.HY_LINK:
        plugs[3:3] = [
            ("plug_knob_hy", bx((hy_k[0], hy_k[1] + hp_len / 2, kpt + P.HY_PLUG[1] / 2),
                                (P.HY_PLUG[0], hp_len, P.HY_PLUG[1])), (0, -1, 0), "hy",
             "backplane_conn_hy", "display", hp_len),
            ("plug_display_j8", bx((j8x + hp_len / 2, j8y, j8z), (hp_len, P.HY_PLUG[0], P.HY_PLUG[1])),
             (-1, 0, 0), "hy", "display_board_connectors", "display", hp_len),
        ]
    if P.TOUCH_BAR:
        plugs.insert(len(plugs) - 1, (
            "plug_touch_band", bx((band_x1 + P.SH_PLUG[2] / 2, tb_c[1], tb_c[2]),
                                  (P.SH_PLUG[2], P.SH_PLUG[0], P.SH_HEADER_SIDE[2])), (-1, 0, 0), "sh",
            "touch_bar_conn", "top_plate_sub", P.SH_PLUG[2]))
        plugs.append(("plug_knob_touch", bx((tch[0], tch[1], kpt + P.SH_HEADER_TOP[2] + P.SH_PLUG[2] / 2),
                                            (P.SH_PLUG[1], P.SH_PLUG[0], P.SH_PLUG[2])), (0, 0, -1), "sh",
                      "backplane_conn_touch", "close", P.SH_PLUG[2]))
    plugs += slot_plugs                            # motor plugs on the haptic modules
    plug_len = {}
    for lb, part, d, kind, mate, step, ln in plugs:
        color = C_PLUG if kind == "usb" else (C_CABLE if kind == "ffc" else C_SWITCH)
        items.append(Item(part, lb, color, 0))
        plug_len[lb] = ln

    # --- Cables (bought, plugged in; lengths from these routes)
    std = {"usb": (100, 150, 200, 250, 300), "gh": (50, 100, 150, 200, 300),
           "sh": (50, 80, 100, 150, 200, 300), "ffc": (50, 60, 80, 100, 150, 200),
           "hy": (50, 100, 150, 200, 300)}
    cables = {}
    for name, (corners, d, r, kind, ends) in cpaths.items():
        pts = fillet_path(corners, r, name, warns)
        part, length = cable(pts, d)
        overall = length + sum(plug_len[e] for e in ends)
        lift = None
        if name in ("cable_keys_ffc", "cable_touch"):              # top-plate side end lifts off
            a, b = Vector(*corners[0]) + Vector(0, 0, P.LIFT_SERVICE), Vector(*corners[-1])
            lift = (a - b).length + 10.0 + sum(plug_len[e] for e in ends)
        need = max(overall, lift or 0.0)
        buy = next((n for n in std[kind] if n >= need - 0.5), None)
        if buy is None:
            warns.append(f"{name}: needs {need:.0f} mm, longer than any stock length")
        cables[name] = dict(kind=kind, length=overall, lift=lift, buy=buy, ends=ends, d=d)
        items.append(Item(part, name, C_CABLE, 2))
    ext_pts = [(ext_x, iy1 + Ls_usb, ext_z), (ext_x, iy1 + Ls_usb + 30.0, ext_z)]
    items.append(Item(cable(ext_pts, 4.0)[0], "cable_usb_ext", C_PLUG, 0))
    cables["cable_usb_ext"] = dict(kind="usb", length=None, lift=None, buy=None, ends=("plug_usb_ext",), d=4.0)

    # Motor leads (haptic modules): the spare lead coils flat in front of the bell
    leads = {n: dict(coil=P.LEAD_COIL, plug=f"knob{n}_motor_plug") for n, k in enumerate(slots) if k == "haptic"}

    for sc in screws:
        sc.kind = f"{'M3' if sc.head == P.M3_HEAD else 'M2'}x{sc.nominal or sc.length}"
        items.append(Item(screw_part(sc), sc.label, C_SCREW, 5))

    info = {
        "outer_mm": (round(ox1 - ox0, 1), round(oy1 - oy0, 1), round(st.plate_top, 1)),
        "stack": st, "frame_sketch": fsk, "plate_sketch": psk, "normal": (0.0, 0.0, 1.0),
        "display_gap": (dy1 - P.DISPLAY_PCB[1]) - board_back_y,
        "display_floor_gap": min(lowest, conn_bot + pocket) - P.FLOOR,
        "floor_pocket": pocket,
        "backplane_sketch": ksk, "touch_bar_h": tb_h,
        "screws": screws, "cables": cables, "outer": outer, "leads": leads,
        "plugs": [dict(label=lb, dir=d, kind=k, mate=m, step=sp, length=ln)
                  for lb, _, d, k, m, sp, ln in plugs],
        "clips": clips, "ext_port": (ext_x, oy1, ext_z), "usb_board_screws": ub_screws,
        "usb_board_sketch": usb_sketch,
        # Paperclip holes: (x, y, z, name, direction of the clip's push, button label, clip start)
        "pinholes": [(dx0 + off, iy1, pin_z, name, (0, -1, 0), "display_board_buttons", oy1 + 15.0)
                     for name, off in P.DISPLAY_BUTTONS.items()]
                    + [(boot_xy[0], boot_xy[1], 0.0, "BOOTSEL", (0, 0, 1), "backplane_bootsel", -15.0)],
        "magnets": magnets,
        "threaded": [(f"knob{n}_striker", f"knob{n}_spacer") for n, k in enumerate(slots) if k == "haptic"]
                    + [(f"top_plate_insert_{i}", "top_plate") for i in range(len(plate_posts))]
                    + [(f"slot_insert_{n}_{k}", "case_tray") for n, k, _, _ in slot_bosses],
        "press_fits": {(f"knob{n}_knob", f"knob{n}_{'hub' if k == 'haptic' else 'encoder'}"): 3.0
                       for n, k in enumerate(slots) if k != "blank"},
        "slots": slots, "knob_xy": L.knob_xy, "lite": lite_heights(st),
        "module_pcb_sketch": {k: module_pcb_sketch(k) for k in ("haptic", "lite")},
        "module_screw": module_screw_nominal(st),
        "touch_band_bbox": info_touch, "panel_screw": (pan_len, cb_pan),
        "usb_arm": (arm_y0, iy1), "usb_ext_socket_depth": sd_ + 0.3,
        "display_usb_z": usb_z, "board_back_y": board_back_y,
        "key_frame": dict(rect=rect, key_xy=L.key_xy, knob_wins=L.cut_xy,
                          knob_size=(L.cut_size[0] + 2 * P.PCB_WIN_EXTRA, L.cut_size[1] + 2 * P.PCB_WIN_EXTRA),
                          supports=frame_holes, loads=[(x, y + SW_DY) for x, y in L.key_xy]),
        "frame_supports": fs, "glass_rect": g["glass_rect"],
    }
    if tilt:
        info["flat_items"] = list(items)
        items, info2 = tilt_on_stand(items, outer, st, magnets, feet_front)
        info.update(info2)
    return items, L, info


def tilt_on_stand(items: list[Item], outer, st: Stack, magnets=(), front_feet=()) -> tuple[list[Item], dict]:
    """Rotate the slab back about its front-bottom edge and add a wedge stand.

    The stand runs under the whole slab: STAND_LIFT of material under the front
    edge and a lip up the front face that catches the slab, so the slab can't
    slide down the stand face (magnets only locate it). The tray's front feet
    (for flat use) sit in pockets in the stand. The stand is a shell, open
    underneath, with ribs; it stands on four rubber feet on solid corner blocks.
    """
    ox0, ox1, oy0, oy1 = outer
    th = math.radians(P.TILT_DEG)
    c, s_ = math.cos(th), math.sin(th)
    lift = P.STAND_LIFT
    T = Pos(0, oy0, lift) * Rot(X=P.TILT_DEG) * Pos(0, -oy0, 0)
    out = [Item(T * it.part, it.label, it.color, it.explode) for it in items]

    depth = oy1 - oy0
    lh, lt = P.STAND_LIP
    piv = (oy0, lift)
    a = (piv[0] - lh * s_, piv[1] + lh * c)                 # lip top, on the slab's front face
    b = (a[0] - lt * c, a[1] - lt * s_)                     # lip top, outside
    back_top = (oy0 + depth * c, lift + depth * s_)
    pts = [a, piv, back_top, (back_top[0], 0.0), (b[0], 0.0), b]
    width = (ox1 - ox0) - 2 * P.STAND_INSET
    prof = Plane.YZ * Polygon(*pts, align=None)
    stand = extrude(prof, amount=width)
    sb = stand.bounding_box()
    shift = -(sb.min.X + sb.max.X) / 2
    stand = Pos(shift, 0, 0) * stand
    try:
        stand = fillet(stand.edges().filter_by(Axis.X).filter_by(lambda e: e.center().Z < 0.01), 1.5)
    except Exception:
        pass
    # Shell: hollow it from below (walls STAND_SHELL), leaving ribs and solid corner blocks for the feet
    w = P.STAND_SHELL
    sbb = stand.bounding_box()
    y_in0 = oy0 + 20.0                                      # front of the hollow (solid nose ahead of it)
    # inner profile: below the top face by w, above the desk (open), between front/back walls
    yb = back_top[0] - w
    zt_front = lift + (y_in0 - oy0) * math.tan(th) - w / c
    zt_back = lift + (yb - oy0) * math.tan(th) - w / c
    inner_pts = [(y_in0, -1.0), (y_in0, zt_front), (yb, zt_back), (yb, -1.0)]
    inner = extrude(Plane.YZ * Polygon(*inner_pts, align=None), amount=width - 2 * w)
    ib = inner.bounding_box()
    inner = Pos(-(ib.min.X + ib.max.X) / 2, 0, 0) * inner
    blk = 16.0
    keep = None
    xs_rib = [-width / 4, 0.0, width / 4]
    for xr in xs_rib:                                       # ribs along y
        r_ = Pos(xr, 0, -2) * Box(2.0, 400, 400, align=(Align.CENTER, Align.CENTER, Align.MIN))
        keep = r_ if keep is None else keep + r_
    for sx in (-1, 1):                                      # corner blocks under the feet
        for yy in (y_in0, yb):
            keep += Pos(sx * (width / 2 - blk / 2), yy, -2) * Box(blk, 2 * blk, 400)
    for x, y in magnets:                                    # bosses behind the magnet pockets
        keep += T * (Pos(x, y, -12) * Cylinder(P.MAGNET_STAND[0] / 2 + 3, 12, align=MIN))
    stand -= inner - keep
    for i, (x, y) in enumerate(magnets):       # pockets below the tray's magnets, in slab coords
        stand -= T * (Pos(x, y, -P.MAGNET_STAND[1] - 0.2) * Cylinder(
            P.MAGNET_STAND[0] / 2 + 0.1 + P.HOLE_COMP / 2, P.MAGNET_STAND[1] + 0.25, align=MIN))
        out.append(Item(T * (Pos(x, y, -P.MAGNET_STAND[1] - 0.05) * Cylinder(
            P.MAGNET_STAND[0] / 2, P.MAGNET_STAND[1], align=MIN)), f"magnet_stand_{i}", C_MAGNET, -1))
    for x, y in front_feet:                    # the tray's flat-use feet sit in pockets
        stand -= T * (Pos(x, y, -P.FOOT[1] - 0.4) * Cylinder(P.FOOT[0] / 2 + 0.5, P.FOOT[1] + 0.45, align=MIN))
    feet = [(sx * (width / 2 - blk / 2), y) for sx in (-1, 1) for y in (y_in0, yb)]
    for i, (x, y) in enumerate(feet):
        out.append(Item(Pos(x, y, -P.FOOT[1]) * Cylinder(P.FOOT[0] / 2, P.FOOT[1], align=MIN),
                        f"foot_stand_{i}", C_FOOT, -1))
    out.insert(0, Item(stand, "stand", C_CASE, -1))

    top_z = lift + depth * s_ + st.plate_top * c
    info = {
        "normal": (0.0, -s_, c),
        "tilted_mm": (round(ox1 - ox0, 1),
                      round(depth * c + st.plate_top * s_, 1),
                      round(top_z, 1)),
        "desk_z": -P.FOOT[1], "stand_volume_cm3": stand.volume / 1000.0,
    }
    return out, info


def proto_frame(keys: list, g: dict) -> dict:
    """The prototype frame PCB: the full build's frame cut down to two keys at the
    panel's top-left corner, so its left and back edges hang off the glass (pan-head
    screws, solder pads) like the full frame's. Over the glass it's held by
    countersunk screws, which tests the full build's support method too. Each key
    gets a second switch footprint above its window (D8 force test)."""
    xs = sorted(x for x, _ in keys)
    ky = keys[0][1]
    strip = P.KEY_PITCH - PCB_WIN
    x0 = g["px0"] - 5.0
    x1 = xs[-1] + PCB_WIN / 2 + P.PROTO_FRAME_RIGHT
    y0 = ky - PCB_WIN / 2 - strip
    y1 = g["py1"] + 4.5
    right_x = xs[-1] + PCB_WIN / 2 + 3.0
    pan = [(g["px0"] - 2.5, y0 + 3.0), (g["px0"] - 2.5, y1 - 2.8),
           ((xs[0] + xs[1]) / 2, g["py1"] + 2.5), (right_x, g["py1"] + 2.5)]
    csk = [((xs[0] + xs[1]) / 2, y0 + strip / 2), (right_x, ky - 1.8)]
    pad_y = (g["glass_rect"][3] + y1) / 2 - 0.05
    sw_a = [(x, ky + SW_DY) for x in xs]
    sw_b = [(x, ky - SW_DY) for x in xs] if P.PROTO_SECOND_SWITCH else []
    pads = {"K1": (x0 + 7.0, pad_y), "GND": (x0 + 9.54, pad_y),
            "K1B": (xs[0] - 1.7, pad_y), "K2B": (xs[1] + 1.7, pad_y), "K2": (xs[1] + 7.0, pad_y)}
    return dict(rect=(x0, x1, y0, y1), pan=pan, csk=csk, switches=sw_a, switches_b=sw_b, pads=pads)


def knob_test_stand(x: float, y: float) -> tuple[list[Item], dict]:
    """Printed knob test stand (JLC3DP), standing on the desk at (x, y).

    A deck the 2204 screws onto (M2 from below, heads in counterbores), with the
    magnet in its center hole. A bought MT6701 breakout slides in on two rails under
    the deck, chip up, so the chip sits SENSOR_GAP below the magnet as on the knob
    board. The tunnel under it leaves room for the header wires. Hub and knob are the
    full build's, at the same height above the motor.
    """
    bw, bt = P.MT6701_BREAKOUT
    W, D = P.KTS_W, P.KTS_D
    deck_bot = P.KTS_TUNNEL_H + bt
    deck_t = P.MT6701[2] + P.SENSOR_GAP + P.MAGNET_H
    deck_top = deck_bot + deck_t
    guide = bw / 2 + 0.2                                  # wall inner face at the breakout
    rail = 1.0                                            # rail ledge under each edge
    body = Box(W, D, P.KTS_BASE_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for sx in (-1, 1):
        wall_w = W / 2 - guide
        body += Pos(sx * (guide + wall_w / 2), 0, 0) * Box(wall_w, D, deck_bot,
                                                          align=(Align.CENTER, Align.CENTER, Align.MIN))
        body += Pos(sx * (guide - rail / 2), 0, P.KTS_TUNNEL_H - 2.0) * Box(
            rail + 0.01, D, 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    body += Pos(0, 0, deck_bot - 0.01) * Box(W, D, deck_t + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN))
    body -= Pos(0, 0, deck_bot - 1) * Cylinder(P.MOTOR_SPACER_ID / 2, deck_t + 2, align=MIN)
    hd = P.M2_HEAD[0] + 0.4
    for sx, sy in motor_screw_xy(0, 0):
        body -= Pos(sx, sy, deck_bot - 1) * Cylinder(P.M2_CLEAR / 2, deck_t + 2, align=MIN)
        body -= Pos(sx, sy, deck_bot - 1) * Cylinder(hd / 2, P.KTS_CBORE + 1, align=MIN)
    stand = Pos(x, y, 0) * body
    brk = Pos(x, y, P.KTS_TUNNEL_H) * Box(bw, 20.0, bt, align=(Align.CENTER, Align.CENTER, Align.MIN))
    chip = Pos(x, y, deck_bot) * Box(P.MT6701[0], P.MT6701[1], P.MT6701[2], align=(Align.CENTER, Align.CENTER, Align.MIN))
    magnet = Pos(x, y, deck_top - P.MAGNET_H) * Cylinder(P.MAGNET_D / 2, P.MAGNET_H, align=MIN)
    items = [Item(stand, "test_stand", C_CASE, 0),
             Item(brk, "test_stand_mt6701_breakout", C_PCB, 0),
             Item(chip, "test_stand_mt6701", C_CHIP, 0),
             Item(magnet, "test_stand_magnet", C_MAGNET, 1),
             Item(motor_2204(x, y, deck_top), "test_stand_motor_2204", C_MOTOR, 2)]
    # Hub + knob cap: the full build's, at the same height above the motor
    st = make_stack(P.FLOOR, P.TOP_PLATE_T)
    for it in knob_parts(st, 0, 0, 0):
        items.append(Item(Pos(x, y, deck_top - st.motor_bot) * it.part,
                          "test_stand_" + it.label.removeprefix("knob0_"), it.color, it.explode))
    thru = deck_t - P.KTS_CBORE
    screw = max(n_ for n_ in STD_LENGTHS if n_ - thru <= P.MOTOR_THREAD_DEPTH - 0.5)
    return items, {"stand_part": body, "motor_screw": f"M2×{screw}", "size_mm": (W, D, round(deck_top, 1))}


def prototype() -> tuple[list[Item], Layout, dict]:
    """2 keys on the real Waveshare 7B between a printed top plate (it carries the
    cap guides) and a laser-cut acrylic base, plus the printed knob test stand
    beside it (D3, changed 2026-10-18).

    Uses the full build's geometry: the panel and display board at the same place,
    the two top-left keys and knob 0's display window. The knob runs on bought
    breakouts on its own stand; the knob board, hub and touch circuits are first
    tested on Rev A.
    """
    st = make_stack(P.PROTO_PLATE_T, P.PROTO_PLATE_T, modular=False)   # no backplane: the old height
    FL = full_layout()
    keys = [FL.key_xy[i] for i in P.PROTO_KEY_IDX]
    wins, win = [FL.win_xy[0]], FL.win_size
    cut_xy, cut_size = [FL.cut_xy[0]], FL.cut_size
    L = Layout(keys, wins, win, [], list(FL.warnings), cut_xy, cut_size)
    g = panel_geometry(st)
    base_t = P.PROTO_PLATE_T

    items: list[Item] = []
    # Plates: cover the panel
    mg = P.PROTO_PLATE_MARGIN
    x0, x1 = g["px0"] - mg, g["px1"] + mg
    y0, y1 = g["py0"] - mg, g["py1"] + mg
    outline = (x0, x1, y0, y1)
    ymid = (y0 + y1) / 2
    corner_holes = [(x0 + 4.5, y0 + 4.5), (x1 - 4.5, y0 + 4.5), (x0 + 4.5, y1 - 4.5), (x1 - 4.5, y1 - 4.5),
                    (x0 + 4.5, ymid), (x1 - 4.5, ymid)]

    with BuildSketch() as base_sk:
        with Locations(((x0 + x1) / 2, (y0 + y1) / 2)):
            RectangleRounded(x1 - x0, y1 - y0, 3.0)
        with Locations(*corner_holes, *g["panel_posts"]):
            Circle(1.6, mode=Mode.SUBTRACT)
    base = extrude(base_sk.sketch, amount=base_t)
    items.append(Item(base, "base_plate_acrylic", C_CASE, 0))
    for i, (x, y) in enumerate(corner_holes):
        items.append(Item(standoff(x, y, base_t, st.plate_bot, P.PROTO_STANDOFF_D),
                          f"standoff_m3_{i}", C_STANDOFF, 0))
    # The 7B on M3 standoffs under its four tabs
    for i, (x, y) in enumerate(g["panel_posts"]):
        items.append(Item(standoff(x, y, base_t, g["panel_z0"], P.PROTO_STANDOFF_D),
                          f"panel_standoff_m3_{i}", C_STANDOFF, 0))
    items += display_items(st, g, keys, wins, win)

    # Frame PCB (2 keys), hung from the top plate on M2 standoffs
    pf = proto_frame(keys, g)
    holes = pf["pan"] + pf["csk"]
    fsk = frame_pcb_sketch(pf["rect"], keys, [], (0, 0), holes)
    frame = Pos(0, 0, st.pcb_bot) * extrude(fsk, amount=P.PCB_T)
    csd, csh = P.M2_CSK_HEAD
    for x, y in pf["csk"]:
        frame -= Pos(x, y, st.pcb_bot - 0.1) * Cylinder(csd / 2 + 0.1, csh + 0.1, align=MIN)
    items.append(Item(frame, "frame_pcb", C_PCB, 2))
    sw = switch(st)
    for i, (x, y) in enumerate(pf["switches"] + pf["switches_b"]):
        items.append(Item(Pos(x, y, 0) * sw, f"switch_{i}", C_SWITCH, 2))
    cap = key_cap(st, nubs=2 if P.PROTO_SECOND_SWITCH else 1)
    for i, (x, y) in enumerate(keys):
        items.append(Item(Pos(x, y, 0) * cap, f"cap_{i}", C_CAP, 3))
    for i, (x, y) in enumerate(holes):
        items.append(Item(standoff(x, y, st.pcb_top, st.plate_bot, 3.2), f"frame_standoff_m2_{i}",
                          C_STANDOFF, 3))

    psk = plate_sketch(outline, 3.0, keys, cut_xy, cut_size, [], corner_holes,
                       small_holes_xy=holes)
    plate = Pos(0, 0, st.plate_bot) * extrude(psk, amount=P.PROTO_PLATE_T)
    plate += key_guides(st, keys, nubs=2 if P.PROTO_SECOND_SWITCH else 1)   # cap guides (D8): printed plate
    items.append(Item(plate, "top_plate_proto", C_PLATE, 4))
    items += knob_windows(st, L, P.PROTO_PLATE_T)

    # Knob test stand on the desk, right of the plates
    kts_items, kts = knob_test_stand(x1 + 12.0 + P.KTS_W / 2, (y0 + y1) / 2)
    items += kts_items

    # Standoff lengths a builder buys (rounded to stock and shimmed)
    standoffs = {
        "M3, plate to plate (corners)": st.plate_bot - base_t,
        "M3, base plate to the 7B's tabs": g["panel_z0"] - base_t,
        "M2, frame PCB to top plate": st.plate_bot - st.pcb_top,
    }
    info = {
        "outer_mm": (round(x1 - x0, 1), round(y1 - y0, 1), round(st.plate_top, 1)),
        "stack": st, "frame_sketch": fsk, "plate_sketch": psk, "base_sketch": base_sk.sketch,
        "standoffs": standoffs, "knob_test_stand": kts,
        "key_frame": dict(rect=pf["rect"], key_xy=keys, knob_wins=(), knob_size=None, supports=holes,
                          loads=pf["switches"] + pf["switches_b"]),
        "frame_pcb": {
            "outline": pf["rect"], "corner_r": 1.5,
            "key_windows": [[x, y, PCB_WIN, PCB_WIN] for x, y in keys],
            "other_windows": [],
            "window_corner_r": P.PCB_WIN_R, "glass_rect": list(g["glass_rect"]),
            "copper_edge": P.PROTO_COPPER_EDGE,
            "switches": pf["switches"], "switches_b": pf["switches_b"],
            "mount_holes_pan": pf["pan"], "mount_holes_csk": pf["csk"],
            "mount_hole_d": P.FRAME_MOUNT_HOLE_D, "csk_head": list(P.M2_CSK_HEAD),
            "pads": pf["pads"], "thickness": P.PCB_T,
        },
    }
    return items, L, info


def key_section(items: list[Item], key_xy: tuple[float, float], z0: float,
                slab: float = 28.0) -> list[Item]:
    """Cut through one key's center (YZ plane) for a side view of the key stack.

    Keeps x from (key center - slab) to key center, y from -26 to +12 around
    the key, z from z0 up, so the tab, nub and switch all show in profile.
    A thin slab gives a clean 2D profile; a thick one a 3D cutaway.
    """
    x, y = key_xy
    keep = Pos(x - slab / 2, y - 7, z0) * Box(slab, 38, 60, align=MIN)
    out = []
    for it in items:
        if it.label.startswith("cable_"):      # never in the key stack; a cable fuse can be an invalid
            continue                           # solid, whose boolean with the slab returns the whole slab
        try:
            cut = it.part & keep
        except Exception:
            continue
        if cut is None or not cut.solids() or cut.volume < 1e-3:
            continue
        color = it.color
        if tuple(color)[3] < 0.99 and slab < 5:
            color = Color(*tuple(color)[:3], 0.6)
        out.append(Item(cut, it.label, color, it.explode))
    return out
