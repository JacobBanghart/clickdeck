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
    Cone,
    Cylinder,
    Locations,
    Mode,
    Part,
    Plane,
    Polygon,
    Rot,
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
    adapter_h = P.ADAPTER_H if P.KNOB_STYLE == "keebio_adapter" else 0.0
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
                     win_size: tuple[float, float]) -> Sketch:
    """2D outline of the frame PCB: outer rectangle minus all windows.

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
    return sk.sketch


def plate_sketch(outline: tuple[float, float, float, float], radius: float,
                 key_xy, win_xy, win_size, knob_xy,
                 holes_xy=(), hole_d: float = 3.2) -> Sketch:
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
    return sk.sketch


def knob_hole_d() -> float:
    if P.KNOB_STYLE == "keebio_adapter":
        return P.PLATE_SHAFT_HOLE_D
    return P.KNOB_STEM_D + 1.0


def tapered_knob() -> Part:
    """Keebio-style knob body, bottom at z=0: tapered, wider at the top."""
    knob = Cone(P.KNOB_BOT_D / 2, P.KNOB_TOP_D / 2, P.KNOB_H, align=MIN)
    knob = fillet(knob.edges().group_by(Axis.Z)[-1], 0.8)
    return knob - Pos(0, P.KNOB_TOP_D / 2 - 2.5, P.KNOB_H - 0.5) * Cylinder(0.8, 2, align=MIN)


def knob_parts(st: Stack, x: float, y: float, n: int) -> list[Item]:
    """What sits on top of the motor bell, for the chosen KNOB_STYLE."""
    knob_z = st.plate_top + P.KNOB_GAP
    if P.KNOB_STYLE == "keebio_adapter":
        shaft_top = knob_z + P.KNOB_BORE_DEPTH
        disc = Cylinder(P.ADAPTER_D / 2, P.ADAPTER_H, align=MIN)
        shaft = Pos(0, 0, P.ADAPTER_H) * Cylinder(
            P.KNOB_BORE_D / 2, shaft_top - st.motor_top - P.ADAPTER_H, align=MIN)
        flat = Pos(P.SHAFT_FLAT - P.KNOB_BORE_D / 2 + 5, 0, P.ADAPTER_H + 4) * Box(
            10, 10, 50, align=MIN)
        adapter = Pos(x, y, st.motor_top) * (disc + shaft - flat)
        knob = tapered_knob() - Cylinder(P.KNOB_BORE_D / 2, P.KNOB_BORE_DEPTH, align=MIN)
        return [Item(adapter, f"knob{n}_shaft_adapter", C_STANDOFF, 3),
                Item(Pos(x, y, knob_z) * knob, f"knob{n}_keebio_knob", C_KNOB, 6)]
    # Integrated: stem from the bell top up through the plate, knob body on top
    stem = Cylinder(P.KNOB_STEM_D / 2, knob_z - st.motor_top + 0.5, align=MIN)
    knob = Pos(0, 0, knob_z - st.motor_top) * tapered_knob() + stem
    return [Item(Pos(x, y, st.motor_top) * knob, f"knob{n}_knob", C_KNOB, 6)]


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
               avoid_xy: list = ()) -> tuple[list[Item], Sketch]:
    """One PCB carrying every knob. Returns parts and the 2D outline (for KiCad)."""
    xs = [x for x, _ in knob_xy]
    ky = knob_xy[0][1]
    reach = P.TONGUE / 2 + P.TONGUE_SLOT + P.KNOB_BOARD_EDGE
    x0, x1 = min(xs) - reach, max(xs) + reach
    y0, y1 = ky - reach, ky + P.TONGUE / 2 + P.TONGUE_SLOT + P.KNOB_BOARD_BACK
    slots = [r for x, y in knob_xy for r in tongue_slots(x, y)]
    bosses = [(x0 + 3, y1 - 3), (x1 - 3, y1 - 3), (x0 + 3, y0 + 3), (x1 - 3, y0 + 3)]
    bosses += [((a + b) / 2, y1 - 3) for a, b in zip(xs, xs[1:])]
    with BuildSketch() as sk:
        with Locations(((x0 + x1) / 2, (y0 + y1) / 2)):
            RectangleRounded(x1 - x0, y1 - y0, 2.0)
        for cx, cy, w, h in slots:
            with Locations((cx, cy)):
                Rectangle(w, h, mode=Mode.SUBTRACT)
        with Locations(*bosses):
            Circle(1.1, mode=Mode.SUBTRACT)
        holes = [(x, y) for x, y in avoid_xy if x0 - 3 < x < x1 + 3 and y0 - 3 < y < y1 + 3]
        if holes:
            with Locations(*holes):
                Circle(3.25, mode=Mode.SUBTRACT)
    board = Pos(0, 0, st.knob_pcb_bot) * extrude(sk.sketch, amount=P.PCB_T)
    boss = None
    for bx, by in bosses:
        b = Pos(bx, by, st.floor_top) * Cylinder(2.0, st.knob_pcb_bot - st.floor_top, align=MIN)
        boss = b if boss is None else boss + b
    items = [Item(boss, f"{label}_bosses", C_STANDOFF, 0),
             Item(board, f"{label}_pcb", C_PCB, 0)]
    if with_mcu:
        mcu = Pos(xs[len(xs) // 2], y1 - P.KNOB_BOARD_BACK / 2, st.knob_pcb_top) * Box(
            *P.RP2040, align=MIN)
        items.append(Item(mcu, f"{label}_rp2040", C_CHIP, 0))
    for n, (x, y) in enumerate(knob_xy):
        items += knob_stack(st, x, y, n)
    return items, sk.sketch


def screen(st: Stack, glass_w: float, glass_h: float, glass_t: float,
           aa: tuple[float, float], center_y: float,
           key_xy, win_xy, win_size, label: str,
           back_pcb: tuple[float, float, float] | None = None) -> list[Item]:
    """Display module with colored placeholders for the key images."""
    items = []
    body = Pos(0, center_y, st.glass - glass_t) * Box(glass_w, glass_h, glass_t, align=MIN)
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
    win = (min(P.KNOB_WIN[0], P.AA_W / P.KNOBS - 3), min(P.KNOB_WIN[1], strip_h - 4))
    knob_pitch = P.AA_W / P.KNOBS
    win_y = (strip_top + strip_bot) / 2
    wins = [((k - (P.KNOBS - 1) / 2) * knob_pitch, win_y) for k in range(P.KNOBS)]
    panel_bot = -P.AA_H / 2 - P.PANEL_BORDER_BOTTOM
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
    return [Item(Pos(x, y, st.plate_bot) * Box(L.cut_size[0] - 0.2, L.cut_size[1] - 0.2, t,
                                                 align=MIN),
                 f"knob_window_{i}", C_CAP, 4) for i, (x, y) in enumerate(L.cut_xy)]


def touch_bar(st: Stack, L: Layout, x_span: float, motor_edge_y: float) -> tuple[list[Item], float]:
    """Capacitive touch band under the top plate, between the windows and the motors.

    Returns the parts and the band height (0 if it doesn't fit).
    """
    if not P.TOUCH_BAR:
        return [], 0.0
    top = L.cut_xy[0][1] - L.cut_size[1] / 2 - P.TOUCH_BAR_MARGIN
    bot = motor_edge_y + P.TOUCH_BAR_MARGIN
    h = top - bot
    if h < P.TOUCH_BAR_MIN_H:
        L.warnings.append(f"touch band is only {h:.1f} mm tall (min {P.TOUCH_BAR_MIN_H})")
        return [], h
    bar = Pos(0, (top + bot) / 2, st.plate_bot - P.TOUCH_BAR_T) * Box(
        x_span, h, P.TOUCH_BAR_T, align=MIN)
    return [Item(bar, "touch_bar_pcb", C_PCB, 3)], h


def full_device(tilt: bool = True) -> tuple[list[Item], Layout, dict]:
    """Full device. With tilt=True the slab is angled toward the user on a stand."""
    st = make_stack(P.FLOOR, P.TOP_PLATE_T)
    L = full_layout()
    items: list[Item] = []

    panel_bot_y = -P.AA_H / 2 - P.PANEL_BORDER_BOTTOM
    panel_cy = panel_bot_y + P.PANEL_H / 2
    knob_y = L.knob_xy[0][1]

    # Case outline
    ix0 = -P.PANEL_W / 2 - P.INNER_CLEAR
    ix1 = P.PANEL_W / 2 + P.INNER_CLEAR
    iy1 = panel_bot_y + P.PANEL_H + P.INNER_CLEAR
    iy0 = knob_y - P.MOTOR_D / 2 - P.INNER_CLEAR - 1.0
    ox0, ox1, oy0, oy1 = ix0 - P.WALL, ix1 + P.WALL, iy0 - P.WALL, iy1 + P.WALL
    outer = (ox0, ox1, oy0, oy1)
    cx, cy = (ox0 + ox1) / 2, (oy0 + oy1) / 2

    outer_sk = Pos(cx, cy) * RectangleRounded(ox1 - ox0, oy1 - oy0, P.CORNER_R)
    inner_sk = Pos((ix0 + ix1) / 2, (iy0 + iy1) / 2) * RectangleRounded(
        ix1 - ix0, iy1 - iy0, max(P.CORNER_R - P.WALL, 0.5))
    tray = extrude(outer_sk, amount=st.plate_bot)
    tray -= Pos(0, 0, P.FLOOR) * extrude(inner_sk, amount=st.plate_bot)
    # USB-C cutout in the back wall
    tray -= Pos(0, oy1 - P.WALL / 2, P.FLOOR + 3.0) * Box(
        P.USB_CUTOUT[0], P.WALL * 3, P.USB_CUTOUT[1])
    items.append(Item(tray, "case_tray", C_CASE, 0))

    # Main PCB (ESP32-S3) under the panel
    main = Pos(0, iy1 - P.MAIN_PCB[1] / 2 - 2, P.FLOOR + 1.0) * Box(*P.MAIN_PCB, P.PCB_T, align=MIN)
    module = Pos(0, iy1 - 12, P.FLOOR + 1.0 + P.PCB_T) * Box(18, 25.5, 3.1, align=MIN)
    usb = Pos(0, iy1 - 3.5, P.FLOOR + 1.0 + P.PCB_T) * Box(9.0, 7.3, 3.2, align=MIN)
    items += [Item(main, "main_pcb", C_PCB, 0), Item(module, "esp32s3_module", C_MOTOR, 0),
              Item(usb, "usb_c", C_MOTOR, 0)]

    # Panel on standoffs
    panel_z0 = st.glass - P.PANEL_T
    for i, (sx, sy) in enumerate([(-1, -1), (1, -1), (-1, 1), (1, 1)]):
        x = sx * (P.PANEL_W / 2 - 6)
        y = panel_cy + sy * (P.PANEL_H / 2 - 6)
        items.append(Item(standoff(x, y, P.FLOOR, panel_z0), f"panel_standoff{i}", C_STANDOFF, 0))
    items += screen(st, P.PANEL_W, P.PANEL_H, P.PANEL_T, (P.AA_W, P.AA_H), panel_cy,
                    L.key_xy, L.win_xy, L.win_size, "panel7")

    # Frame PCB + switches
    m = P.FRAME_PCB_MARGIN
    rect = (-P.AA_W / 2 - m, P.AA_W / 2 + m, -P.AA_H / 2 - min(m, P.PANEL_BORDER_BOTTOM),
            P.AA_H / 2 + m)
    fsk = frame_pcb_sketch(rect, L.key_xy, L.cut_xy, L.cut_size)
    frame = Pos(0, 0, st.pcb_bot) * extrude(fsk, amount=P.PCB_T)
    items.append(Item(frame, "frame_pcb", C_PCB, 2))
    sw = switch(st)
    for i, (x, y) in enumerate(L.key_xy):
        items.append(Item(Pos(x, y + SW_DY, 0) * sw, f"switch_{i}", C_SWITCH, 2))

    # Caps
    cap = key_cap(st)
    for i, (x, y) in enumerate(L.key_xy):
        items.append(Item(Pos(x, y, 0) * cap, f"cap_{i}", C_CAP, 3))

    # Top plate
    psk = plate_sketch(outer, P.CORNER_R, L.key_xy, L.cut_xy, L.cut_size, L.knob_xy)
    plate = top_plate(psk, st, P.TOP_PLATE_T, L)
    items.append(Item(plate, "top_plate", C_PLATE, 4))
    items += knob_windows(st, L)
    tb, tb_h = touch_bar(st, L, P.KNOBS * (P.AA_W / P.KNOBS) - 2,
                         knob_y + P.MOTOR_D / 2)
    items += tb

    # Knobs: one board for all of them
    standoffs = [(sx * (P.PANEL_W / 2 - 6), panel_cy + sy * (P.PANEL_H / 2 - 6))
                 for sx in (-1, 1) for sy in (-1, 1)]
    kitems, ksk = knob_board(st, L.knob_xy, "knob_board", with_mcu=True, avoid_xy=standoffs)
    items += kitems

    info = {
        "outer_mm": (round(ox1 - ox0, 1), round(oy1 - oy0, 1), round(st.plate_top, 1)),
        "stack": st, "frame_sketch": fsk, "plate_sketch": psk, "normal": (0.0, 0.0, 1.0),
        "knob_board_sketch": ksk, "touch_bar_h": tb_h,
    }
    if tilt:
        items, info2 = tilt_on_stand(items, outer, st)
        info.update(info2)
    return items, L, info


def tilt_on_stand(items: list[Item], outer, st: Stack) -> tuple[list[Item], dict]:
    """Rotate the slab back about its front-bottom edge and add a wedge stand."""
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
    win = (P.KNOB_WIN[0], min(P.KNOB_WIN[1], strip_h - 3.7))
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
    fsk = frame_pcb_sketch(rect, keys, cut_xy, cut_size)
    frame = Pos(0, 0, st.pcb_bot) * extrude(fsk, amount=P.PCB_T)
    items.append(Item(frame, "frame_pcb", C_PCB, 2))
    sw = switch(st)
    cap = key_cap(st)
    for i, (x, y) in enumerate(keys):
        items.append(Item(Pos(x, y + SW_DY, 0) * sw, f"switch_{i}", C_SWITCH, 2))
        items.append(Item(Pos(x, y, 0) * cap, f"cap_{i}", C_CAP, 3))

    psk = plate_sketch(outline, 3.0, keys, cut_xy, cut_size, knobs, corner_holes)
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
