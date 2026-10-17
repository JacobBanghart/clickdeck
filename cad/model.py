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
    knob_pcb_bot: float
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


def make_stack(floor_t: float, plate_t: float) -> Stack:
    knob_pcb_bot = floor_t + P.SW_H + P.KNOB_PRESS_GAP  # press switch hangs below
    knob_pcb_top = knob_pcb_bot + P.PCB_T
    motor_bot = knob_pcb_top + P.MT6701[2] + P.SENSOR_GAP + P.MAGNET_H
    motor_top = motor_bot + P.MOTOR_H
    adapter_h = P.ADAPTER_H if P.KNOB_STYLE == "shaft_adapter" else 0.0
    plate_bot = motor_top + adapter_h + P.MOTOR_TO_PLATE
    plate_top = plate_bot + plate_t
    flange_top = plate_bot - P.CAP_TO_PLATE
    flange_bot = flange_top - P.FLANGE_T
    sw_top = flange_bot - P.NUB_H
    pcb_top = sw_top - P.SW_H
    pcb_bot = pcb_top - P.PCB_T
    glass = pcb_bot - P.GLASS_GAP
    return Stack(floor_t, knob_pcb_bot, knob_pcb_top, motor_bot, motor_top,
                 plate_bot, plate_top, flange_top, flange_bot, sw_top,
                 pcb_top, pcb_bot, glass, plate_top + P.CAP_PROTRUDE)


# Switch position relative to its key center (it sits on the PCB strip
# below the key's window).
SW_DY = -(P.CAP_SIZE / 2 + P.CAP_CLEAR + P.SW_EDGE_MARGIN + P.SW_W / 2)
TAB_REACH = (-SW_DY - P.CAP_SIZE / 2) + P.NUB_D / 2 + 0.25


def check_key_fit(pitch: float, below_gap_edge: float | None = None) -> list[str]:
    """Return warnings if the switch or tab doesn't fit between keys."""
    warnings = []
    window = P.CAP_SIZE + 2 * P.CAP_CLEAR
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
def key_cap(st: Stack) -> Part:
    cap_bot = st.pcb_bot
    body = Box(P.CAP_SIZE, P.CAP_SIZE, st.cap_top - cap_bot, align=MIN)
    body = fillet(body.edges().group_by(Axis.Z)[-1], P.CAP_TOP_FILLET)
    body = Pos(0, 0, cap_bot) * body
    tab = Pos(0, -P.CAP_SIZE / 2 - TAB_REACH / 2 + 0.25, st.flange_bot) * Box(
        P.TAB_W, TAB_REACH + 0.5, P.FLANGE_T, align=MIN)
    nub = Pos(0, SW_DY, st.flange_bot - P.NUB_H) * Cylinder(
        P.NUB_D / 2, P.NUB_H + 0.01, align=MIN)
    lips = [
        Pos(sx * (P.CAP_SIZE / 2 + P.LIP_W / 2 - 0.25), 0, st.flange_bot)
        * Box(P.LIP_W + 0.5, P.LIP_LEN, P.FLANGE_T, align=MIN)
        for sx in (-1, 1)
    ]
    return body + tab + nub + lips[0] + lips[1]


def switch(st: Stack) -> Part:
    base = Box(P.SW_L, P.SW_W, P.SW_H - 0.35, align=MIN)
    stem = Pos(0, 0, P.SW_H - 0.35) * Cylinder(0.6, 0.35, align=MIN)
    return Pos(0, 0, st.pcb_top) * (base + stem)


def frame_pcb_sketch(rect: tuple[float, float, float, float],
                     key_xy: list[tuple[float, float]],
                     win_xy: list[tuple[float, float]],
                     win_size: tuple[float, float],
                     holes_xy: list[tuple[float, float]] = ()) -> Sketch:
    """2D outline of the frame PCB: outer rectangle minus all windows and mount holes.

    rect = (xmin, xmax, ymin, ymax). Also exported as DXF for KiCad.
    """
    x0, x1, y0, y1 = rect
    w = P.CAP_SIZE + 2 * P.CAP_CLEAR
    with BuildSketch() as sk:
        with Locations(((x0 + x1) / 2, (y0 + y1) / 2)):
            RectangleRounded(x1 - x0, y1 - y0, 1.5)
        with Locations(*key_xy):
            Rectangle(w, w, mode=Mode.SUBTRACT)
        with Locations(*win_xy):
            Rectangle(*win_size, mode=Mode.SUBTRACT)
        if holes_xy:
            with Locations(*holes_xy):
                Circle(P.FRAME_MOUNT_HOLE_D / 2, mode=Mode.SUBTRACT)
    return sk.sketch


def plate_sketch(outline: tuple[float, float, float, float], radius: float,
                 key_xy, win_xy, win_size, knob_xy,
                 holes_xy=(), hole_d: float = 3.2, small_holes_xy=(),
                 small_hole_d: float = P.FRAME_MOUNT_HOLE_D) -> Sketch:
    x0, x1, y0, y1 = outline
    w = P.CAP_SIZE + 2 * P.CAP_CLEAR
    with BuildSketch() as sk:
        with Locations(((x0 + x1) / 2, (y0 + y1) / 2)):
            RectangleRounded(x1 - x0, y1 - y0, radius)
        with Locations(*key_xy):
            Rectangle(w, w, mode=Mode.SUBTRACT)
        with Locations(*win_xy):
            RectangleRounded(*win_size, 1.0, mode=Mode.SUBTRACT)
        with Locations(*knob_xy):
            Circle(knob_hole_d() / 2, mode=Mode.SUBTRACT)
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
    return P.KNOB_HUB_D + P.KNOB_HUB_HOLE_CLEAR


def tapered_knob() -> Part:
    """Knob body, bottom at z=0: tapered, wider at the top."""
    knob = Cone(P.KNOB_BOT_D / 2, P.KNOB_TOP_D / 2, P.KNOB_H, align=MIN)
    knob = fillet(knob.edges().group_by(Axis.Z)[-1], 0.8)
    return knob - Pos(0, P.KNOB_TOP_D / 2 - 2.5, P.KNOB_H - 0.5) * Cylinder(0.8, 2, align=MIN)


def knob_parts(st: Stack, x: float, y: float, n: int) -> list[Item]:
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
    # Integrated: a hub bonded to the bell reaches up through the plate; the knob
    # cap presses onto it, so caps pull straight off and the plate lifts over the hubs.
    hub_top = knob_z + P.KNOB_HUB_ENGAGE
    hub = Pos(x, y, st.motor_top) * Cylinder(P.KNOB_HUB_D / 2, hub_top - st.motor_top, align=MIN)
    cap = tapered_knob() - Cylinder(P.KNOB_HUB_D / 2 + 0.1, P.KNOB_HUB_ENGAGE, align=MIN)
    return [Item(hub, f"knob{n}_hub", C_STANDOFF, 3),
            Item(Pos(x, y, knob_z) * cap, f"knob{n}_knob", C_KNOB, 6)]


def knob_stack(st: Stack, x: float, y: float, n: int) -> list[Item]:
    """Per-knob parts: MT6701, TMC6300, press switch, magnet, 2204 motor, knob."""
    sensor = Pos(x, y, st.knob_pcb_top) * Box(*P.MT6701, align=MIN)
    driver = Pos(x + 9, y - 9, st.knob_pcb_top) * Box(*P.TMC6300, align=MIN)
    # Press switch on the underside of the tongue's front tip, stem down
    py = y - P.TONGUE / 2 + P.SW_W / 2 + 1.0
    body = Pos(x, py, st.knob_pcb_bot - (P.SW_H - 0.35)) * Box(P.SW_L, P.SW_W, P.SW_H - 0.35,
                                                              align=MIN)
    stem = Pos(x, py, st.knob_pcb_bot - P.SW_H) * Cylinder(0.6, 0.35, align=MIN)
    magnet = Pos(x, y, st.motor_bot - P.MAGNET_H) * Cylinder(
        P.MAGNET_D / 2, P.MAGNET_H, align=MIN)
    base = Pos(x, y, st.motor_bot) * Cylinder(
        P.MOTOR_BASE_D / 2, P.MOTOR_BASE_H, align=MIN)
    bell = Cylinder(P.MOTOR_D / 2, P.MOTOR_H - P.MOTOR_BASE_H + 0.5, align=MIN)
    bell = bell - Cylinder(P.SHAFT_BORE / 2, 50, align=MIN)
    bell = Pos(x, y, st.motor_bot + P.MOTOR_BASE_H - 0.5) * bell
    return [
        Item(sensor, f"knob{n}_mt6701", C_CHIP, 0),
        Item(driver, f"knob{n}_tmc6300", C_CHIP, 0),
        Item(body + stem, f"knob{n}_press_switch", C_SWITCH, 0),
        Item(magnet, f"knob{n}_magnet", C_MAGNET, 1),
        Item(base + bell, f"knob{n}_motor_2204", C_MOTOR, 2),
    ] + knob_parts(st, x, y, n)


def tongue_slots(x: float, y: float) -> list[tuple[float, float, float, float]]:
    """Slot rectangles (cx, cy, w, h) that free a tongue around (x, y), hinged at the back."""
    t, sl, hw = P.TONGUE, P.TONGUE_SLOT, P.TONGUE_HINGE_W
    outer = t / 2 + sl
    side_w = (outer - hw / 2)
    return [
        (x - t / 2 - sl / 2, y, sl, t + 2 * sl),           # left
        (x + t / 2 + sl / 2, y, sl, t + 2 * sl),           # right
        (x, y - t / 2 - sl / 2, t + 2 * sl, sl),           # front
        (x - hw / 2 - side_w / 2, y + t / 2 + sl / 2, side_w, sl),  # back, left of hinge
        (x + hw / 2 + side_w / 2, y + t / 2 + sl / 2, side_w, sl),  # back, right of hinge
    ]


def knob_board(st: Stack, knob_xy: list, label: str, with_mcu: bool,
               avoid_xy: list = (), screw_xy: list | None = None,
               tabs: list = (), slots_xy: list = (),
               mcu_xy: tuple | None = None) -> tuple[list[Item], Sketch]:
    """One PCB carrying every knob. Returns parts and the 2D outline (for KiCad).

    screw_xy: if given, the board's screw holes (bosses are printed in the tray
    elsewhere); otherwise the board gets its own bosses (prototype).
    tabs: extra rectangles (x0, x1, y0, y1) added to the outline.
    slots_xy: tie-down slots for straps (cable ties) around the motor lead coils.
    """
    xs = [x for x, _ in knob_xy]
    ky = knob_xy[0][1]
    reach = P.TONGUE / 2 + P.TONGUE_SLOT + P.KNOB_BOARD_EDGE
    x0, x1 = min(xs) - reach, max(xs) + reach
    y0, y1 = ky - reach, ky + P.TONGUE / 2 + P.TONGUE_SLOT + P.KNOB_BOARD_BACK
    slots = [r for x, y in knob_xy for r in tongue_slots(x, y)]
    if screw_xy is not None:
        bosses = list(screw_xy)
    else:
        bosses = [(x0 + 3, y1 - 3), (x1 - 3, y1 - 3), (x0 + 3, y0 + 3), (x1 - 3, y0 + 3)]
        bosses += [((a + b) / 2, y1 - 3) for a, b in zip(xs, xs[1:])]
    with BuildSketch() as sk:
        with Locations(((x0 + x1) / 2, (y0 + y1) / 2)):
            RectangleRounded(x1 - x0, y1 - y0, 2.0)
        for tx0, tx1, ty0, ty1 in tabs:
            with Locations(((tx0 + tx1) / 2, (ty0 + ty1) / 2 - 0.5)):
                Rectangle(tx1 - tx0, ty1 - ty0 + 1.0)
        for sx, sy in slots_xy:
            with Locations((sx, sy)):
                RectangleRounded(1.4, 3.2, 0.6, mode=Mode.SUBTRACT)
        for cx, cy, w, h in slots:
            with Locations((cx, cy)):
                Rectangle(w, h, mode=Mode.SUBTRACT)
        with Locations(*bosses):
            Circle(P.M2_CLEAR / 2, mode=Mode.SUBTRACT)
        r_avoid = max(P.PANEL_POST_D, P.PLATE_POST_D) / 2 + 0.6
        holes = [(x, y) for x, y in avoid_xy
                 if x0 - r_avoid < x < x1 + r_avoid and y0 - r_avoid < y < y1 + r_avoid]
        if holes:
            with Locations(*holes):
                Circle(r_avoid, mode=Mode.SUBTRACT)
    board = Pos(0, 0, st.knob_pcb_bot) * extrude(sk.sketch, amount=P.PCB_T)
    items = [Item(board, f"{label}_pcb", C_PCB, 0)]
    if screw_xy is None:
        boss = None
        for bx, by in bosses:
            b = Pos(bx, by, st.floor_top) * Cylinder(2.0, st.knob_pcb_bot - st.floor_top, align=MIN)
            boss = b if boss is None else boss + b
        items.insert(0, Item(boss, f"{label}_bosses", C_STANDOFF, 0))
    if with_mcu:
        mx, my = mcu_xy or (xs[len(xs) // 2], y1 - P.KNOB_BOARD_BACK / 2)
        mcu = Pos(mx, my, st.knob_pcb_top) * Box(*P.RP2040, align=MIN)
        items.append(Item(mcu, f"{label}_rp2040", C_CHIP, 0))
    for n, (x, y) in enumerate(knob_xy):
        items += knob_stack(st, x, y, n)
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


def knob_windows(st: Stack, L: Layout, t: float = P.TOP_PLATE_T) -> list[Item]:
    """Clear covers over the knob displays, flush with the top plate."""
    w, h = L.cut_size[0] - 0.2, L.cut_size[1] - 0.2
    return [Item(Pos(x, y, st.plate_bot) * extrude(RectangleRounded(w, h, 0.9), amount=t),
                 f"knob_window_{i}", C_CAP, 4) for i, (x, y) in enumerate(L.cut_xy)]


def touch_bar(st: Stack, L: Layout, x_span, motor_edge_y: float) -> tuple[list[Item], float]:
    """Capacitive touch band under the top plate, between the windows and the motors.

    x_span: width (centered) or (x0, x1). Returns the parts and the band height
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
    bar = Pos((x0 + x1) / 2, (top + bot) / 2, st.plate_bot - P.TOUCH_BAR_T) * Box(
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


def full_device(tilt: bool = True) -> tuple[list[Item], Layout, dict]:
    """Full device. With tilt=True the slab is angled toward the user on a stand.

    Everything is built in the flat (untilted) frame first; assembly steps and
    checks use that frame (see cad/assembly.py).
    """
    st = make_stack(P.FLOOR, P.TOP_PLATE_T)
    L = full_layout()
    items: list[Item] = []
    screws: list[Screw] = []

    # --- Panel frame, positioned so the active area is centered at the origin
    px0 = -P.AA_W / 2 - P.PANEL_BORDER_LEFT
    px1 = px0 + P.PANEL_W
    py0 = -P.AA_H / 2 - P.PANEL_BORDER_FRONT
    py1 = py0 + P.PANEL_H
    pcx, pcy = (px0 + px1) / 2, (py0 + py1) / 2
    panel_z0 = st.glass - P.PANEL_T
    knob_y = L.knob_xy[0][1]
    kxs = [x for x, _ in L.knob_xy]
    board_front = P.TONGUE / 2 + P.TONGUE_SLOT + P.KNOB_BOARD_EDGE
    board_back_y = knob_y + P.TONGUE / 2 + P.TONGUE_SLOT + P.KNOB_BOARD_BACK
    board_x1 = max(kxs) + board_front

    # --- Case outline: symmetric about the key grid
    half_w = max(-px0, px1) + P.INNER_CLEAR
    ix0, ix1 = -half_w, half_w
    iy1 = py1 + P.INNER_CLEAR_BACK
    iy0 = knob_y - max(P.MOTOR_D / 2 + P.INNER_CLEAR + 1.0, board_front + P.INNER_CLEAR)
    ox0, ox1, oy0, oy1 = ix0 - P.WALL, ix1 + P.WALL, iy0 - P.WALL, iy1 + P.WALL
    outer = (ox0, ox1, oy0, oy1)
    cx, cy = (ox0 + ox1) / 2, (oy0 + oy1) / 2

    # --- Waveshare's ESP32-S3 board behind the panel (parts facing down)
    dx0 = px0 + P.DISPLAY_PCB_LEFT
    dy1 = py1 - P.DISPLAY_PCB_BACK
    dpcb_top = panel_z0 - P.DISPLAY_STANDOFF_H
    dpcb_bot = dpcb_top - P.PCB_T
    usb_y = dy1 - P.USB_FROM_PCB_BACK
    uart_y = dy1 - P.UART_USB_FROM_PCB_BACK
    usb_z = dpcb_bot - P.USB_BELOW_PCB
    lowest = dpcb_bot - P.DISPLAY_PARTS_H
    conn_bot = dpcb_bot - P.DISPLAY_CONNECTOR_H
    pocket = math.ceil(max(0.0, (P.FLOOR + 1.0) - conn_bot) * 2) / 2   # 1 mm clearance, 0.5 mm steps
    if pocket > P.FLOOR - 0.6:
        L.warnings.append(f"display board connectors need a {pocket:.1f} mm floor pocket; "
                          f"floor is only {P.FLOOR} mm")
    if lowest < P.FLOOR + 0.5:
        L.warnings.append(f"display board parts reach {lowest:.1f} mm, below the floor + 0.5 mm")
    hy_x, hy_y, hy_len = dx0 + P.DISPLAY_PCB[0] - 6, dy1 - 40, 44.0

    # --- Positions of posts, bosses and screws
    post_r = P.PLATE_POST_D / 2
    plate_posts = [(sx * (half_w - P.PLATE_POST_INSET), y) for sx in (-1, 1)
                   for y in ((py1 + iy1) / 2, iy0 + P.PLATE_POST_INSET)]
    panel_posts = [(pcx + sx * P.PANEL_M3_DX / 2, y)
                   for sx in (-1, 1)
                   for y in (py0 + P.PANEL_M3_FROM_FRONT, py1 - P.PANEL_M3_FROM_BACK)]
    kb_front_y = knob_y - P.TONGUE / 2 - P.TONGUE_SLOT - P.KNOB_BOARD_EDGE / 2
    kb_screws = [((a + b) / 2, kb_front_y) for a, b in zip(kxs, kxs[1:])]
    kb_screws += [(sx * (board_x1 - P.KNOB_BOARD_EDGE / 2), knob_y) for sx in (-1, 1)]
    # Frame PCB screws: only where there's no glass under the head (back edge, left side)
    frame_y1 = py1 + 4.5
    frame_x0 = px0 - 5.0
    frame_holes = [(x, py1 + 2.5) for x in (-50.0, 0.0, 50.0)]
    frame_holes += [(px0 - 2.5, y) for y in (0.0, 25.0)]

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
    arm_y0 = dy1 + 0.4                            # arm sits behind the display board
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

    # Knob board connectors: JST-GH (USB link) at the back-left corner; keys FFC
    # (ZIF) and touch (JST-SH, top entry) at the right end. Motor headers behind
    # each tongue, plugs pointing left; excess motor lead coiled on the back strip.
    kpt = st.knob_pcb_top
    gh_k = (-board_x1 + 9.3, board_back_y)       # header mouth on the back edge
    zif_y = board_back_y - 2.4                    # ZIF center (also the frame PCB's ZIF)
    zif_x1 = board_x1                             # mouth at the board's right edge
    tch = (board_x1 - P.KNOB_BOARD_EDGE / 2, knob_y + 7.24)
    mh_y = knob_y + P.TONGUE / 2 + P.TONGUE_SLOT + 0.4 + P.HEADER_3P[1] / 2
    coil_y0, coil_y1 = mh_y + P.HEADER_3P[1] / 2 + 0.4, board_back_y - P.GH_HEADER[2] - 0.2
    coil_l = 24.0
    slots = [(x + sx * (coil_l / 2 - 1.5), (coil_y0 + coil_y1) / 2) for x in kxs for sx in (-1, 1)]
    mcu_xy = (2.0, mh_y)                         # centre
    frame_x1 = ix1 - 2.2                          # frame PCB reaches past the panel on the right

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
    # Touch: band connector (under the plate, right end) to the knob board's top-entry header
    tb_c = (frame_x1 - P.SH_HEADER_SIDE[0] / 2, knob_y + P.MOTOR_D / 2 + P.TOUCH_BAR_MARGIN + 0.12
            + P.SH_HEADER_SIDE[1] / 2, st.plate_bot - P.TOUCH_BAR_T - P.SH_HEADER_SIDE[2] / 2)
    st_ = (tb_c[0], tb_c[1] - P.SH_HEADER_SIDE[1] / 2 - P.SH_PLUG[2], tb_c[2])
    et_ = (tch[0], tch[1], kpt + P.SH_HEADER_TOP[2] + P.SH_PLUG[2])
    cpaths["cable_touch"] = (
        [st_, (st_[0], st_[1] - 3.0, st_[2]), (ix1 - 1.5, tch[1] - 3.0, st_[2] - 3.0),
         (ix1 - 1.5, tch[1] - 3.0, et_[2] + 2.0), (et_[0], et_[1], et_[2] + 2.5), et_],
        1.6, 1.5, "sh", ("plug_touch_band", "plug_knob_touch"))
    # Motor leads: motor -> coil on the back strip (strapped through two slots) -> plug
    lead_pts = {}
    for n, kx in enumerate(kxs):
        p0 = (kx, knob_y + P.MOTOR_BASE_D / 2, st.motor_bot + 1.0)
        pts = [p0, (kx + 1.0, mh_y - 1.0, 10.6), (kx + coil_l / 2, (coil_y0 + coil_y1) / 2, 9.0)]
        tail = [(kx - coil_l / 2, (coil_y0 + coil_y1) / 2, 9.0), (kx - coil_l / 2 - 1.0, mh_y + 2.0, 10.6),
                (kx - 21.0, mh_y + 2.0, 10.6), (kx - 21.0, mh_y, kpt + 1.8),
                (kx - 4.5 - P.MOTOR_PLUG[2], mh_y, kpt + 1.8)]
        lead_pts[n] = (pts, tail)
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
    for x, y in kb_screws:                                     # knob board front bosses
        tray += Pos(x, y, P.FLOOR - 0.01) * Cylinder(P.KNOB_BOARD_BOSS_D / 2,
                                                     st.knob_pcb_bot - P.FLOOR + 0.01, align=MIN)
    for x in (-40.0, 0.0, 40.0):                               # ribs under the knob board's back strip
        tray += Pos(x, board_back_y - 6, P.FLOOR - 0.01) * Box(
            12, 3, st.knob_pcb_bot - P.FLOOR + 0.01, align=MIN)
    if pocket > 0:
        tray -= Pos(hy_x - P.FLOOR_POCKET_MARGIN, hy_y, P.FLOOR - pocket) * Box(
            6 + 2 * P.FLOOR_POCKET_MARGIN, hy_len + 2 * P.FLOOR_POCKET_MARGIN, pocket + 1,
            align=(Align.MIN, Align.CENTER, Align.MIN))
    for x, y in ub_screws:                                     # USB board bosses
        tray += Pos(x, y, P.FLOOR - 0.01) * Cylinder(P.KNOB_BOARD_BOSS_D / 2, ub_z0 - P.FLOOR + 0.01,
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
    pin_z = dpcb_bot - 1.0
    for name, off in P.DISPLAY_BUTTONS.items():                # paperclip holes, back wall
        tray -= Pos(dx0 + off, iy1 + P.WALL / 2, pin_z) * Rot(X=90) * Cylinder(
            P.PINHOLE_D / 2, P.WALL * 3)
    hd, hh = P.M3_HEAD
    cb = hh + 0.3                                              # counterbore depth from below
    for x, y in panel_posts:
        tray -= Pos(x, y, -1) * Cylinder(P.M3_CLEAR / 2, panel_z0 + 2, align=MIN)
        tray -= Pos(x, y, -1) * Cylinder(hd / 2 + 0.2, cb + 1, align=MIN)
    for x, y in plate_posts:
        tray -= Pos(x, y, -1) * Cylinder(P.M3_CLEAR / 2, P.FLOOR + 2, align=MIN)
        tray -= Pos(x, y, -1) * Cylinder(hd / 2 + 0.2, cb + 1, align=MIN)
    for x, y in kb_screws:
        tray -= Pos(x, y, 0.6) * Cylinder(P.M2_PILOT / 2, 20, align=MIN)
    magnets = [(sx * 40.0, oy0 + f * (oy1 - oy0)) for sx in (-1, 1) for f in (0.3, 0.8)]
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
    dpcb = Pos(dx0, dy1, dpcb_bot) * Box(*P.DISPLAY_PCB, P.PCB_T,
                                        align=(Align.MIN, Align.MAX, Align.MIN))
    module = Pos(dx0 + 8.0, dy1 - 1, dpcb_bot - 3.1) * Box(
        18, 25.5, 3.1, align=(Align.MIN, Align.MAX, Align.MIN))
    usb = None
    for y in (usb_y, uart_y):                                  # native USB + USB-to-UART ports
        u = Pos(dx0, y, usb_z) * Box(7.6, sw_, 4.06, align=(Align.MIN, Align.CENTER, Align.CENTER))
        usb = u if usb is None else usb + u
    hy = Pos(hy_x, hy_y, conn_bot) * Box(
        6, hy_len, P.DISPLAY_CONNECTOR_H, align=(Align.MIN, Align.CENTER, Align.MIN))
    buttons = None
    for name, off in P.DISPLAY_BUTTONS.items():
        b = Pos(dx0 + off, dy1 - 2.0, dpcb_bot - 2.0) * Box(3.5, 4.0, 2.0, align=MIN)
        buttons = b if buttons is None else buttons + b
    items += [Item(dpcb, "display_board_pcb", C_PCB, 1),
              Item(module, "display_board_esp32s3", C_MOTOR, 1),
              Item(usb, "display_board_usb_c", C_MOTOR, 1),
              Item(hy, "display_board_connectors", C_SWITCH, 1),
              Item(buttons, "display_board_buttons", C_CHIP, 1)]
    items += screen(st, P.PANEL_W, P.PANEL_H, P.PANEL_T, (P.AA_W, P.AA_H), pcy,
                    L.key_xy, L.win_xy, L.win_size, "panel7", center_x=pcx)
    for i, (x, y) in enumerate(panel_posts):
        screws.append(Screw(f"screw_panel_{i}", "", x, y, cb, True,
                            std_length(panel_z0 + 2.5 - cb), P.M3_HEAD, "panel7_module",
                            "display"))

    # --- Frame PCB + switches (hangs from the top plate)
    m = P.FRAME_PCB_MARGIN
    rect = (frame_x0, frame_x1, -P.AA_H / 2 - min(m, P.PANEL_BORDER_FRONT), frame_y1)
    fsk = frame_pcb_sketch(rect, L.key_xy, L.cut_xy, L.cut_size, frame_holes)
    notch = None
    for x, y in plate_posts:                       # clear the top plate's posts
        c = Pos(x, y) * Circle(post_r + 0.6)
        notch = c if notch is None else notch + c
    fsk = fsk - notch
    frame = Pos(0, 0, st.pcb_bot) * extrude(fsk, amount=P.PCB_T)
    items.append(Item(frame, "frame_pcb", C_PCB, 2))
    sw = switch(st)
    for i, (x, y) in enumerate(L.key_xy):
        items.append(Item(Pos(x, y + SW_DY, 0) * sw, f"switch_{i}", C_SWITCH, 2))
    for i, (x, y) in enumerate(frame_holes):
        screws.append(Screw(f"screw_frame_{i}", "", x, y, st.pcb_bot, True,
                            std_length(P.PCB_T + 3.0), P.M2_HEAD, "top_plate", "top_plate_sub"))

    # --- Caps
    cap = key_cap(st)
    for i, (x, y) in enumerate(L.key_xy):
        items.append(Item(Pos(x, y, 0) * cap, f"cap_{i}", C_CAP, 3))

    # --- Top plate, with its posts down to the floor and bosses for the frame PCB
    psk = plate_sketch(outer, P.CORNER_R, L.key_xy, L.cut_xy, L.cut_size, L.knob_xy)
    plate = top_plate(psk, st, P.TOP_PLATE_T, L)
    for x, y in plate_posts:
        plate += Pos(x, y, P.FLOOR) * Cylinder(post_r, st.plate_bot - P.FLOOR + 0.01, align=MIN)
        plate -= Pos(x, y, P.FLOOR - 0.1) * Cylinder(P.M3_PILOT / 2, 10.0, align=MIN)
    for x, y in frame_holes:
        plate += Pos(x, y, st.pcb_top) * Cylinder(P.FRAME_BOSS_D / 2, st.plate_bot - st.pcb_top + 0.01,
                                                  align=MIN)
        plate -= Pos(x, y, st.pcb_top - 0.1) * Cylinder(P.M2_PILOT / 2, 4.5, align=MIN)
    items.append(Item(plate, "top_plate", C_PLATE, 4))
    items += knob_windows(st, L)
    tb, tb_h = touch_bar(st, L, (-(P.AA_W - 2) / 2, frame_x1), knob_y + P.MOTOR_D / 2)
    items += tb
    for i, (x, y) in enumerate(plate_posts):
        screws.append(Screw(f"screw_plate_{i}", "", x, y, cb, True,
                            std_length(P.FLOOR - cb + 8.0), P.M3_HEAD, "top_plate", "close"))

    # --- Knob board: screwed to the tray along its front edge, back strip on ribs
    avoid = panel_posts + plate_posts
    kitems, ksk = knob_board(st, L.knob_xy, "knob_board", with_mcu=True,
                             avoid_xy=avoid, screw_xy=kb_screws,
                             tabs=[(board_x1 - P.KNOB_BOARD_EDGE, board_x1, board_back_y,
                                    zif_y + P.ZIF_12P[0] / 2 + 0.2)],
                             slots_xy=slots, mcu_xy=mcu_xy)
    items += kitems
    for i, (x, y) in enumerate(kb_screws):
        screws.append(Screw(f"screw_knobboard_{i}", "", x, y, st.knob_pcb_top, False,
                            std_length(P.PCB_T + (st.knob_pcb_bot - P.FLOOR) + 2.0), P.M2_HEAD,
                            "case_tray", "knob_board"))
    kb = next(it.part for it in kitems if it.label == "knob_board_pcb").bounding_box()
    if board_back_y > dy1 - P.DISPLAY_PCB[1] - 1.0:
        L.warnings.append(f"knob board reaches y={kb.max.Y:.1f}, into the display board "
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
        Item(bx((ub_x1 - 8.0, 44.5, ub_z1 + 0.43), (4.0, 4.0, 0.85))           # hub
             + bx((ub_x0 + 9.5, 44.0, ub_z1 + 0.55), (3.0, 3.0, 1.1))          # power switch
             + bx((ext_x - 12.0, 49.5, ub_z1 + 0.5), (2.9, 1.6, 1.0)),         # ESD
             "usb_board_chips", C_CHIP, 0),
        Item(bx((gh_k[0], gh_k[1] - gd / 2, kpt + ghh / 2), (gw, gd, ghh)), "knob_board_conn_gh", C_SWITCH, 0),
        Item(bx((zif_x1 - zd / 2, zif_y, kpt + zh / 2), (zd, zl, zh)), "knob_board_conn_zif", C_SWITCH, 0),
        Item(bx((tch[0], tch[1], kpt + P.SH_HEADER_TOP[2] / 2),
                (P.SH_HEADER_TOP[1], P.SH_HEADER_TOP[0], P.SH_HEADER_TOP[2])),
             "knob_board_conn_touch", C_SWITCH, 0),
        Item(bx((frame_x1 - zd / 2, zif_y, st.pcb_top + zh / 2), (zd, zl, zh)), "frame_pcb_zif", C_SWITCH, 2),
        Item(bx(tb_c, P.SH_HEADER_SIDE), "touch_bar_conn", C_SWITCH, 3),
    ]
    for i, (x, y) in enumerate(ub_screws):
        screws.append(Screw(f"screw_usbboard_{i}", "", x, y, ub_z1, False,
                            std_length(P.PCB_T + P.USB_BOARD_Z + 1.5), P.M2_HEAD, "case_tray", "usb_board"))
    mp = P.MOTOR_PLUG
    for n, kx in enumerate(kxs):
        items.append(Item(bx((kx - 2.0 - P.HEADER_3P[0] / 2, mh_y, kpt + P.HEADER_3P[2] / 2), P.HEADER_3P),
                          f"knob{n}_header", C_CHIP, 0))

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
         "usb_board_gh", "knob_board", P.GH_PLUG[2]),
        ("plug_knob_gh", bx((gh_k[0], gh_k[1] + P.GH_PLUG[2] / 2, kpt + P.GH_PLUG[1] / 2),
                            (P.GH_PLUG[0], P.GH_PLUG[2], P.GH_PLUG[1])), (0, -1, 0), "gh",
         "knob_board_conn_gh", "knob_board", P.GH_PLUG[2]),
        ("plug_ffc_frame", bx((frame_x1 + 0.5, zif_y, st.pcb_top + 1.0), (1.0, 13.0, 0.3)), (-1, 0, 0), "ffc",
         "frame_pcb_zif", "top_plate_sub", 1.0),
        ("plug_touch_band", bx((tb_c[0], tb_c[1] - P.SH_HEADER_SIDE[1] / 2 - P.SH_PLUG[2] / 2, tb_c[2]),
                               (P.SH_PLUG[0], P.SH_PLUG[2], P.SH_HEADER_SIDE[2])), (0, 1, 0), "sh",
         "touch_bar_conn", "top_plate_sub", P.SH_PLUG[2]),
        ("plug_ffc_knob", bx((zif_x1 + 0.5, zif_y, kpt + 1.0), (1.0, 13.0, 0.3)), (-1, 0, 0), "ffc",
         "knob_board_conn_zif", "close", 1.0),
        ("plug_knob_touch", bx((tch[0], tch[1], kpt + P.SH_HEADER_TOP[2] + P.SH_PLUG[2] / 2),
                               (P.SH_PLUG[1], P.SH_PLUG[0], P.SH_PLUG[2])), (0, 0, -1), "sh",
         "knob_board_conn_touch", "close", P.SH_PLUG[2]),
    ]
    for n, kx in enumerate(kxs):
        plugs.append((f"knob{n}_motor_plug", bx((kx - 4.5 - mp[2] / 2, mh_y, kpt + 0.5 + mp[1] / 2),
                                                (mp[2], mp[0], mp[1])), (1, 0, 0), "motor",
                      f"knob{n}_header", "knob_sub", mp[2]))
    plug_len = {}
    for lb, part, d, kind, mate, step, ln in plugs:
        color = C_PLUG if kind == "usb" else (C_CABLE if kind == "ffc" else C_SWITCH)
        items.append(Item(part, lb, color, 0))
        plug_len[lb] = ln

    # --- Cables (bought, plugged in; lengths from these routes)
    std = {"usb": (100, 150, 200, 250, 300), "gh": (50, 100, 150, 200, 300),
           "sh": (50, 100, 150, 200, 300), "ffc": (50, 60, 80, 100, 150, 200)}
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

    # Motor leads: whatever doesn't fit the route is coiled on the back strip and strapped
    leads = {}
    cw = coil_y1 - coil_y0
    for n, kx in enumerate(kxs):
        head, tail = lead_pts[n]
        hp = fillet_path(head, 3.0, f"cable_motor{n}", warns)
        tp = fillet_path(tail, 2.0, f"cable_motor{n}", warns)
        part = Compound(children=[cable(hp, P.MOTOR_LEAD_D)[0], cable(tp, P.MOTOR_LEAD_D)[0]])
        routed = path_length(hp) + path_length(tp)
        excess = max(0.0, P.MOTOR_LEAD_LEN - routed)
        per_turn = 2 * (coil_l - cw) + math.pi * cw
        across = max(1, int(cw // P.MOTOR_LEAD_D))
        layers = max(1, math.ceil(excess / per_turn / across))
        coil_h = layers * P.MOTOR_LEAD_D
        room = panel_z0 - 0.3 - (kpt + 0.1)
        if coil_h > room:
            fit = routed + int(room // P.MOTOR_LEAD_D) * across * per_turn
            warns.append(f"motor {n}: {P.MOTOR_LEAD_LEN:.0f} mm lead needs a {coil_h:.1f} mm coil, "
                         f"only {room:.1f} mm under the panel (leads up to ~{fit:.0f} mm fit)")
        coil = Pos(kx, (coil_y0 + coil_y1) / 2, kpt + 0.1) * Box(coil_l, cw, min(coil_h, room),
                                                                align=MIN)
        items.append(Item(part, f"cable_motor{n}", C_CABLE, 0))
        items.append(Item(coil, f"cable_motor{n}_coil", C_CABLE, 0))
        leads[n] = dict(routed=routed, excess=excess, coil_h=coil_h, room=room)

    for sc in screws:
        sc.kind = f"{'M3' if sc.head == P.M3_HEAD else 'M2'}x{sc.length}"
        items.append(Item(screw_part(sc), sc.label, C_SCREW, 5))

    info = {
        "outer_mm": (round(ox1 - ox0, 1), round(oy1 - oy0, 1), round(st.plate_top, 1)),
        "stack": st, "frame_sketch": fsk, "plate_sketch": psk, "normal": (0.0, 0.0, 1.0),
        "display_gap": (dy1 - P.DISPLAY_PCB[1]) - board_back_y,
        "display_floor_gap": min(lowest, conn_bot + pocket) - P.FLOOR,
        "floor_pocket": pocket,
        "knob_board_sketch": ksk, "touch_bar_h": tb_h,
        "screws": screws, "cables": cables, "outer": outer, "leads": leads,
        "plugs": [dict(label=lb, dir=d, kind=k, mate=m, step=sp, length=ln)
                  for lb, _, d, k, m, sp, ln in plugs],
        "clips": clips, "ext_port": (ext_x, oy1, ext_z), "usb_board_screws": ub_screws,
        "usb_board_sketch": usb_sketch,
        "pinholes": [(dx0 + off, iy1, pin_z, name) for name, off in P.DISPLAY_BUTTONS.items()],
        "magnets": magnets,
    }
    if tilt:
        items, info2 = tilt_on_stand(items, outer, st, magnets)
        info.update(info2)
    return items, L, info


def tilt_on_stand(items: list[Item], outer, st: Stack, magnets=()) -> tuple[list[Item], dict]:
    """Rotate the slab back about its front-bottom edge and add a wedge stand.

    The stand holds the slab with magnets (pockets match the tray's) and sits
    on rubber feet, like the tray's front edge.
    """
    ox0, ox1, oy0, oy1 = outer
    th = math.radians(P.TILT_DEG)
    T = Pos(0, oy0, 0) * Rot(X=P.TILT_DEG) * Pos(0, -oy0, 0)
    out = [Item(T * it.part, it.label, it.color, it.explode) for it in items]

    depth = oy1 - oy0
    s0 = P.STAND_FRONT_SETBACK
    pts = [
        (oy0 + s0 * math.cos(th), s0 * math.sin(th)),
        (oy0 + depth * math.cos(th), depth * math.sin(th)),
        (oy0 + depth * math.cos(th), 0.0),
        (oy0 + s0 * math.cos(th), 0.0),
    ]
    width = (ox1 - ox0) - 2 * P.STAND_INSET
    stand = extrude(Plane.YZ * Polygon(*pts, align=None), amount=width)
    sb = stand.bounding_box()
    stand = Pos(-(sb.min.X + sb.max.X) / 2, 0, 0) * stand
    stand = fillet(stand.edges().filter_by(Axis.X), 1.5)
    for i, (x, y) in enumerate(magnets):       # pockets below the tray's magnets, in slab coords
        stand -= T * (Pos(x, y, -P.MAGNET_STAND[1] - 0.2) * Cylinder(
            P.MAGNET_STAND[0] / 2 + 0.1, P.MAGNET_STAND[1] + 0.25, align=MIN))
        out.append(Item(T * (Pos(x, y, -P.MAGNET_STAND[1] - 0.05) * Cylinder(
            P.MAGNET_STAND[0] / 2, P.MAGNET_STAND[1], align=MIN)), f"magnet_stand_{i}", C_MAGNET, -1))
    sbb = stand.bounding_box()
    feet = [(sx * (sbb.size.X / 2 - 10), y) for sx in (-1, 1) for y in (sbb.min.Y + 8, sbb.max.Y - 8)]
    for i, (x, y) in enumerate(feet):
        out.append(Item(Pos(x, y, -P.FOOT[1]) * Cylinder(P.FOOT[0] / 2, P.FOOT[1], align=MIN),
                        f"foot_stand_{i}", C_FOOT, -1))
    out.insert(0, Item(stand, "stand", C_CASE, -1))

    top_z = depth * math.sin(th) + st.plate_top * math.cos(th)
    info = {
        "normal": (0.0, -math.sin(th), math.cos(th)),
        "tilted_mm": (round(ox1 - ox0, 1),
                      round(depth * math.cos(th) + st.plate_top * math.sin(th), 1),
                      round(top_z, 1)),
    }
    return out, info


def prototype() -> tuple[list[Item], Layout, dict]:
    """2 keys + 1 knob on a 2.4" screen. Two laser-cut acrylic plates on standoffs."""
    st = make_stack(P.PROTO_PLATE_T, P.PROTO_PLATE_T)
    gw, gh, gt = P.P24_GLASS
    aw, ah = P.P24_AA
    keys = key_grid(P.PROTO_KEYS, 1, P.KEY_PITCH, ah / 2)
    strip_top = ah / 2 - P.KEY_PITCH
    strip_bot = -ah / 2
    strip_h = strip_top - strip_bot
    win = (P.KNOB_WIN[0], max(min(P.KNOB_WIN[1], strip_h - 3.7), 4.0))
    wins = [(0.0, (strip_top + strip_bot) / 2)]
    knob_y = min(-gh / 2 - P.INNER_CLEAR, touch_bar_floor(wins[0][1], win[1])) - P.MOTOR_D / 2
    knobs = [(0.0, knob_y)]
    warns = check_key_fit(P.KEY_PITCH)
    if P.PROTO_KEYS * P.KEY_PITCH > aw + 0.5:
        warns.append("prototype keys are wider than the 2.4\" active area")
    cut_xy, cut_size = strip_cut(wins, win, win[0])
    L = Layout(keys, wins, win, knobs, warns, cut_xy, cut_size)

    items: list[Item] = []
    # Plate outline covers the display module PCB and the knob
    x0 = -gw / 2 - 6
    x1 = P.P24_PCB_OFFSET_X + P.P24_PCB[0] / 2 + 6
    y0 = knob_y - P.MOTOR_D / 2 - 7
    y1 = gh / 2 + 8
    outline = (x0, x1, y0, y1)
    corner_holes = [(x0 + 4.5, y0 + 4.5), (x1 - 4.5, y0 + 4.5),
                    (x0 + 4.5, y1 - 4.5), (x1 - 4.5, y1 - 4.5)]

    with BuildSketch() as base_sk:
        with Locations(((x0 + x1) / 2, (y0 + y1) / 2)):
            RectangleRounded(x1 - x0, y1 - y0, 3.0)
        with Locations(*corner_holes):
            Circle(1.6, mode=Mode.SUBTRACT)
    base = extrude(base_sk.sketch, amount=P.PROTO_PLATE_T)
    items.append(Item(base, "base_plate_acrylic", C_CASE, 0))

    for i, (x, y) in enumerate(corner_holes):
        items.append(Item(standoff(x, y, P.PROTO_PLATE_T, st.plate_bot, P.PROTO_STANDOFF_D),
                          f"standoff_m3_{i}", C_STANDOFF, 0))

    # Display module on short standoffs
    mod_bot = st.glass - gt - P.PCB_T
    for i, (sx, sy) in enumerate([(-1, -1), (1, -1), (-1, 1), (1, 1)]):
        x = P.P24_PCB_OFFSET_X + sx * (P.P24_PCB[0] / 2 - 3)
        y = sy * (P.P24_PCB[1] / 2 - 3)
        items.append(Item(standoff(x, y, P.PROTO_PLATE_T, mod_bot, 4.0), f"display_standoff{i}",
                          C_STANDOFF, 0))
    items += screen(st, gw, gh, gt, (aw, ah), 0.0, keys, wins, win, "lcd24",
                    back_pcb=(P.P24_PCB[0], P.P24_PCB[1], P.P24_PCB_OFFSET_X))

    rect = (-aw / 2 - 2.5, aw / 2 + 2.5, -ah / 2 - 2.5, ah / 2 + 2.5)
    mx = rect[1] - P.FRAME_MOUNT_INSET
    frame_holes = [(sx * mx, y) for sx in (-1, 1) for y in P.FRAME_MOUNT_Y]
    fsk = frame_pcb_sketch(rect, keys, cut_xy, cut_size, frame_holes)
    frame = Pos(0, 0, st.pcb_bot) * extrude(fsk, amount=P.PCB_T)
    items.append(Item(frame, "frame_pcb", C_PCB, 2))
    sw = switch(st)
    cap = key_cap(st)
    for i, (x, y) in enumerate(keys):
        items.append(Item(Pos(x, y + SW_DY, 0) * sw, f"switch_{i}", C_SWITCH, 2))
        items.append(Item(Pos(x, y, 0) * cap, f"cap_{i}", C_CAP, 3))

    for i, (x, y) in enumerate(frame_holes):
        items.append(Item(standoff(x, y, st.pcb_top, st.plate_bot, 3.2), f"frame_standoff_m2_{i}",
                          C_STANDOFF, 3))
    psk = plate_sketch(outline, 3.0, keys, cut_xy, cut_size, knobs, corner_holes,
                       small_holes_xy=frame_holes)
    plate = Pos(0, 0, st.plate_bot) * extrude(psk, amount=P.PROTO_PLATE_T)
    items.append(Item(plate, "top_plate_acrylic", C_PLATE, 4))
    items += knob_windows(st, L, P.PROTO_PLATE_T)
    tb, tb_h = touch_bar(st, L, win[0], knob_y + P.MOTOR_D / 2)
    items += tb

    # Knob module: the same tongue/press design as the full knob board, one knob
    kitems, ksk = knob_board(st, knobs, "knob_module", with_mcu=False)
    items += kitems
    info = {
        "knob_board_sketch": ksk, "touch_bar_h": tb_h,
        "outer_mm": (round(x1 - x0, 1), round(y1 - y0, 1), round(st.plate_top, 1)),
        "stack": st, "frame_sketch": fsk, "plate_sketch": psk, "base_sketch": base_sk.sketch,
        "frame_pcb": {
            "outline": rect, "corner_r": 1.5,
            "key_windows": [[x, y, P.CAP_SIZE + 2 * P.CAP_CLEAR, P.CAP_SIZE + 2 * P.CAP_CLEAR]
                            for x, y in keys],
            "other_windows": [[x, y, *cut_size] for x, y in cut_xy],
            "switches": [[x, y + SW_DY] for x, y in keys],
            "mount_holes": frame_holes, "mount_hole_d": P.FRAME_MOUNT_HOLE_D,
            "thickness": P.PCB_T,
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
