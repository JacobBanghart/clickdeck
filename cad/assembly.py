"""Assembly and service: steps, build checks, pictures, animation, and the guide.

    .venv/bin/python cad/assembly.py --check     # checks only (fast; CI)
    CLICKDECK_TOUCH_BAR=1 .venv/bin/python cad/assembly.py --check --default-only
                                                 # the touch band option (D24), default slots only (CI)
    .venv/bin/python cad/assembly.py --bom       # checks + docs/bom.md only
    .venv/bin/python cad/assembly.py             # checks + step pictures + guide
    .venv/bin/python cad/assembly.py --animate   # also the animation: GIF, plus MP4 if ffmpeg is installed (~15 min)

Writes cad/out/assembly/*.png, the animation, docs/assembly.md and docs/bom.md. The
pictures come from the same model the checks run on, so a step that can't be
built shows up as a failed check, not just a wrong picture.

Checks:
- interference: no two parts overlap in the finished device (except screws
  threading into their target part)
- tool access: every screw can be reached with a straight screwdriver at the
  step that installs it
- service: each knob module (or blank) lifts straight out of its slot with
  the case closed (D23); the top plate, display and backplane lift out in that
  order; a paperclip reaches the display board's BOOT/RESET through the back
  wall and the backplane's BOOTSEL through the floor
- knob slots (D23): every knob top matches the haptic knob's position, covers
  and blanks sit flush, the pogo pins are compressed inside their stroke and
  land on the module's pads; run on the default build and on CHECK_CONFIGS
- key stack (D8): every cap's down-stop lands on the frame PCB, every key has
  its guide skirt on all four sides, and the worst cap drop (guide tilt, switch
  bottomed, down-stop) plus the frame PCB's flex at a firm press stays short of
  the glass
- plug insertion: every plug has a straight path into its socket at the step
  that connects it (like the screwdriver check)
- cables: no cable runs through a part (motor bells included); the cables
  between the top plate and the tray are long enough to lift the plate
  LIFT_SERVICE mm with them still plugged in
"""

import math
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np  # noqa: E402
from build123d import Box, Circle, Cylinder, Pos, Rot  # noqa: E402

import model  # noqa: E402
import params as P  # noqa: E402

ROOT = Path(__file__).parent.parent
OUT = Path(__file__).parent / "out" / "assembly"
GUIDE = ROOT / "docs" / "assembly.md"

OVERLAYS = ("panel7_image", "panel7_knob_display", "panel7_active_area")


def starts(*prefixes):
    return lambda lb: lb.startswith(prefixes)


# --------------------------------------------------------------------------
# Steps. `parts` picks labels; `move` is where new parts come from (offset in
# mm, flat frame); screws come in along their own axis.
# --------------------------------------------------------------------------
@dataclass
class Step:
    key: str
    title: str
    text: str
    parts: object                      # label -> bool
    move: tuple = (0, 0, 45)
    bench: bool = False                # built on its own, not in the tray yet
    view: tuple = (-60, 32)            # (az, el) for placing parts
    screw_view: tuple = (-60, -32)     # (az, el) for the screws in this step
    tilted: bool = False
    fixed: tuple = ()                  # labels (prefixes) that are new but don't move


def slot_part(lb, n=None):
    """A knob slot's contents (D23): module parts, cover or blank, knob cap, motor plug,
    lead coil. n: only slot n."""
    if lb.startswith("cable_motor"):
        return n is None or lb.startswith(f"cable_motor{n}_")
    return lb.startswith("knob") and lb[4:5].isdigit() and (n is None or lb.startswith(f"knob{n}_"))


def module_sub(lb):
    """Built on the bench: a module's own parts, without its cover and knob cap."""
    return slot_part(lb) and not lb.endswith(("_knob", "_cover", "_blank"))


def modules(lb):
    """Dropped into the slots: modules (with their covers) and blanks."""
    return slot_part(lb) and not lb.endswith("_knob")


GH_LINK = starts("plug_usb_board_gh", "plug_knob_gh", "cable_usb_knob_gh")
DISPLAY_CABLE = starts("plug_display_usb", "plug_usb_board_display", "cable_usb_display",
                       "plug_display_j8", "plug_knob_hy", "cable_hy_link")
TOP_SUB = starts("top_plate", "cap_", "frame_pcb", "switch_", "touch_bar", "knob_window",
                 "cable_keys", "cable_touch", "plug_ffc", "plug_touch_band", "plug_knob_touch")
# Plugs that stay on the backplane when the top plate lifts (their cable comes with the plate)
KNOB_SIDE = ("plug_ffc_knob", "plug_knob_touch")

STEPS = [
    Step("tray", "Print the case; fit magnets, feet and inserts",
         "Print the tray, top plate and stand (all fit a 256 mm bed) in PETG, 4 walls, "
         "≥25% infill (" + ("100% over the touch band area of the top plate; " if P.TOUCH_BAR else "")
         + "no carbon- or metal-filled filament). PLA softens in the case's ~2.3 W of heat. Glue the four "
         "tray magnets into the pockets underneath. Stick the two rubber feet near the front "
         "edge (for flat use; on the stand they sit in pockets). With a soldering iron "
         "(insert tip, ~240 °C), press an M3 heat-set insert "
         f"({P.INSERT_M3[0]:g} mm hole, {P.INSERT_M3[1]:g} mm long) into the bottom end of "
         "each of the top plate's four posts, flush with the end: the case screws go into "
         "these, so they survive being undone for every service. Press an M2 insert "
         f"({P.INSERT_M2[0]:g} mm hole, {P.INSERT_M2[1]:g} mm long) into the top of each of the "
         "ten slot bosses along the front, flush: the knob modules' screws go into these.",
         starts("case_tray", "magnet_tray", "foot_front", "slot_insert"), move=(0, 0, -25), view=(-60, -30),
         fixed=("case_tray",)),
    Step("usb_board", "Screw in the USB board",
         "Lower the USB board into the back-left corner, external USB-C socket first: the "
         "socket's face sits flush behind the opening in the back wall, the board's arm "
         "rests against the printed backstop, and its edge touches the back wall. Drive the "
         "four M2 screws into the floor bosses (two of them either side of the socket). The "
         "hub chip sits on the arm next to the socket, so the high-speed upstream run is short.",
         starts("usb_board"), move=(0, 0, 40), view=(-60, 40), screw_view=(-60, 45)),
    Step("backplane", "Screw in the backplane; plug in the USB link",
         "With the PC unplugged: lower the backplane in over the ten slot bosses (they come up "
         "through its holes and locate it), with its back strip on the floor ribs, and screw it "
         "down at both ends and along the back strip (thread-forming, don't overtighten). Before "
         "the first power-up, check the JST-GH cable pin 1 to pin 1 with a meter. Plug it into "
         "the backplane's back-left corner and into the USB board (both click), and press it "
         "into its floor clip. The BOOTSEL button on the backplane's left end sits over the "
         "small hole in the floor (for recovery).",
         lambda lb: lb.startswith("backplane") or GH_LINK(lb), move=(0, 0, 40), view=(-60, 40),
         screw_view=(-60, 45)),
    Step("display", "Mount the display; plug in its USB cable",
         "Stand the tray upright on two blocks (~50 mm high) under its left and right walls, "
         "so screws can go in from below without turning it over. Lay the panel face up on its "
         "four posts, against the three printed stops behind and beside it, and drive the four "
         "M3 screws up from underneath into the panel's tabs (the tip ends ~2 mm past the tab "
         "face, short of the LCD's back sheet: don't substitute longer screws). Plug the right-angle "
         "end of the USB-C cable into the display board's USB port (the one nearer the back; "
         "the cable points forward), loop it round in the bay and plug the straight end into "
         "the USB board. Press the cable into its two floor clips, clear of the backplane. "
         "Optional GPIO6 link: before laying the panel down, plug the HY2.0 3-pin lead into the "
         "3-pin header on the backplane's back edge, then into J8 on the display board's right "
         "edge (check the silkscreen: J8 is the GPIO6 port).",
         lambda lb: lb.startswith(("display_board", "panel7")) or DISPLAY_CABLE(lb),
         move=(0, 0, 45), view=(-60, 35), screw_view=(-60, -35)),
    Step("top_plate_sub", "Build the top plate (on the bench)",
         "With the top plate face up, drop the five clear knob-window covers into their "
         "pockets (they rest on a ledge) and fix each with a little clear UV glue or clear "
         "tape on the ledge. Lay the plate face down. Drop the clear caps into their holes, "
         "tabs toward the front edge; each should slide freely in its guide. Plug the key cable (FFC) into the frame PCB's ZIF "
         "connector (flip the latch up, slide the cable in, latch down), then fit the frame "
         "PCB over the plate's two locating pins (switches facing the caps) and screw it to "
         "the bosses: pan-head screws along the back and left edges (off the glass), "
         "countersunk ones everywhere else (flush underneath, so nothing touches the glass). "
         "Every key should click and none read pressed at rest: if one does, add a 0.1 mm "
         "shim washer between the nearest bosses and the PCB."
         + (" Stick the touch band into its pocket under the plate, below the knob "
            "display windows, with full-coverage 3M 467MP/468MP transfer tape (no air "
            "gaps), and plug the touch cable into it." if P.TOUCH_BAR else ""),
         TOP_SUB, move=(0, 0, -35), bench=True, view=(-60, -40), screw_view=(-60, -40)),
    Step("close", "Close the case",
         "With the PC unplugged: shake out any loose screws or debris. Rest the top plate on "
         "the two printed props (`print_plate_prop.stl`) on the tray's walls, which hold it "
         "~40 mm up with " + ("its cables" if P.TOUCH_BAR else "the key cable") + " plugged in. Plug "
         "the key cable into the backplane's ZIF connector at its right end"
         + (" and the touch cable into the header beside it; the spare cable folds"
            if P.TOUCH_BAR else "; the spare cable folds") + " into the gap by the right wall, "
         "outside the fence next to slot 4. Take "
         "the props out and lower the top plate (its tabs and the dividers between the slot "
         "openings register it). With the tray still on its blocks, drive the four M3 screws up "
         "from underneath into the inserts in its posts. The slots are still empty: the knob "
         "modules go in from the top, with the case closed.",
         TOP_SUB, move=(0, 0, 50), view=(-60, 35), screw_view=(-60, -35)),
    Step("module_sub", "Build the knob modules (on the bench)",
         "Each slot takes a haptic module, a lite module or a blank (D23). **Haptic module:** lay "
         "the module PCB in its printed base (the pads underneath face down through the base's "
         "window). Glue a diametric magnet to the bottom end of the motor shaft. Set a printed "
         "spacer ring on the tongue (its two pins drop into the holes beside the MT6701 and center "
         "the motor, so the magnet sits within 0.3 mm of the sensor axis), put the motor on it with "
         "its lead pointing forward, and drive four M2×8 screws up from under the tongue into the "
         "motor base. Never use longer screws: a tip past the base's thread can short a winding. "
         "The spacer's arm reaches forward over the slot to above the press switch on the front "
         "border: thread an M2×3 set screw (the striker) down through the arm's tip. Screw a "
         "printed hub onto the bell with four M2×3 countersunk screws (its spigot centers it). "
         "Plug the motor's 3-pin plug onto the upright header on the front border (any way round: "
         "the firmware finds the phase order) and coil the spare lead flat in the space right of "
         "it, in front of the bell, clear of the bell. Calibrate: turn the striker until the knob "
         "clicks after a light press on the hub, then back it off a quarter turn. **Lite module:** "
         "the encoder comes soldered to the module PCB; lay the PCB in its base. **Blank:** "
         "nothing to build.",
         module_sub, move=(0, 0, 35), bench=True, view=(120, 40)),
    Step("modules", "Drop in the knob modules and blanks; screw them down",
         "With the PC unplugged (no hot-plugging): drop each module, base first, straight down "
         "through its opening in the top plate. The dividers either side guide it, and the two "
         "key pins under the base only fit the backplane's holes one way round, so a module "
         "turned back to front won't seat. Its pads land on the slot's pogo pins as it goes down. "
         "Set the printed cover on it (the bezel sits flush in the opening, around the hub) and "
         "drive the two countersunk M2 screws through the bezel's corners into the inserts in the "
         "slot bosses, until the bezel is flush with the plate. A blank is one printed part: drop "
         "it in and screw it down the same way. Swapping later is the same in reverse: pull the "
         "knob cap, undo the two screws, lift the module out by its cover.",
         modules, move=(0, 0, 45), view=(-60, 40), screw_view=(-60, 45)),
    Step("knobs", "Press on the knob caps",
         "Press each knob cap onto its hub (haptic) or encoder shaft (lite). They pull straight "
         "off for service.",
         lambda lb: lb.startswith("knob") and lb.endswith("_knob"), move=(0, 0, 30),
         view=(-60, 35)),
    Step("stand", "Put it on the stand",
         "To get the polarity right, stack each stand magnet on its mating tray magnet (so "
         "they attract), mark the stand magnet's exposed face, and glue it into the stand "
         "with that marked face down (away from the tray). Stick the four feet on the stand's "
         "corner blocks. Set the slab on the stand: its front edge drops behind the stand's "
         "lip, which carries it, and the magnets locate it.",
         starts("stand", "magnet_stand", "foot_stand"), move=(0, 40, -40), view=(-62, 20),
         tilted=True),
    Step("plug_in", "Plug it in",
         "Plug a USB-C cable from the computer into the port in the back wall. A C-to-C "
         "cable lets the device see how much current the port offers; an A-to-C cable "
         "works too, with weaker haptics (500 mA budget). With only lite modules and blanks, "
         "any port and cable will do.",
         starts("plug_usb_ext", "cable_usb_ext"), move=(0, 30, 27), view=(115, 28), tilted=True),
]


def step_of(lb, flat_labels):
    for s in STEPS:
        if not s.tilted and s.parts(lb) and not lb.startswith("screw_"):
            if s.bench:
                continue                      # bench steps; installed in "close" and "modules"
            return s.key
    return None


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------
def vol(a, b, _retry=True):
    try:
        r = a & b
        v = r.volume if r is not None else 0.0
    except Exception:
        return 0.0
    if v > 1e-6 and _retry and (v > min(a.volume, b.volume) * 1.001 + 1e-6
                                or any(sa.volume <= 0 for sa in a.solids())):
        # OCC boolean glitch on a multi-solid part (seen on moved cables, and on the
        # inverted slivers a cable fuse can leave at tight bends): retry solid by
        # solid, skipping slivers with no positive volume
        return sum(vol(sa, b, False) for sa in a.solids() if sa.volume > 1e-6)
    if v > 1e-6 and not (a.is_valid and b.is_valid):
        # Booleans on an invalid solid (a cable fuse can make one) can report volume for
        # parts that don't even touch; confirm with the minimum distance. (Only for invalid
        # shapes: for a solid nested inside another, distance_to measures between surfaces.)
        try:
            if a.distance_to(b) > 1e-3:
                return 0.0
        except Exception:
            pass
    return v


def bbox_overlap(b1, b2, eps=0.01):
    return (b1.min.X < b2.max.X - eps and b2.min.X < b1.max.X - eps and
            b1.min.Y < b2.max.Y - eps and b2.min.Y < b1.max.Y - eps and
            b1.min.Z < b2.max.Z - eps and b2.min.Z < b1.max.Z - eps)


def check_interference(items, screws, info=None, only=None):
    """No two parts overlap. Screws may overlap only their target (how deep is
    check_screws' job), set screws their threaded hole, and press fits up to their
    designed interference volume. only: restrict to pairs involving these labels."""
    info = info or {}
    allowed = {(sc.label, sc.target) for sc in screws} | set(info.get("threaded", []))
    press = info.get("press_fits", {})
    parts = [it for it in items if not it.label.startswith(OVERLAYS + ("cable_",))]
    bbs = [it.part.bounding_box() for it in parts]
    problems = []
    for i in range(len(parts)):
        for j in range(i + 1, len(parts)):
            a, b = parts[i], parts[j]
            if only is not None and not (only(a.label) or only(b.label)):
                continue
            if (a.label, b.label) in allowed or (b.label, a.label) in allowed:
                continue
            if not bbox_overlap(bbs[i], bbs[j]):
                continue
            v = vol(a.part, b.part)
            lim = press.get((a.label, b.label), press.get((b.label, a.label), 0.01))
            if v > lim:
                problems.append(f"{a.label} overlaps {b.label} ({v:.2f} mm³)")
    return problems


def check_screws(items, screws):
    """Thread engagement in the target within (min, max); the tip ends inside the
    target (not in a part behind it); printed pilot holes run past the tip."""
    by = {it.label: it for it in items}
    probs, rows = [], []
    for sc in screws:
        d = 3.0 if sc.kind.startswith("M3") else 2.0
        tgt = by[sc.target].part
        z0, z1 = (sc.z, sc.z + sc.length) if sc.up else (sc.z - sc.length, sc.z)
        thread = Pos(sc.x, sc.y, z0) * Cylinder(d / 2, z1 - z0, align=model.MIN)
        engage = 0.0
        try:
            inter = thread & tgt
            if inter is not None and inter.volume > 1e-4:
                engage = inter.bounding_box().size.Z
        except Exception:
            pass
        lo, hi = sc.engage
        tip = z1 if sc.up else z0
        rows.append((sc, engage))
        if engage < lo - 0.01:
            probs.append(f"{sc.label} ({sc.kind}): only {engage:.2f} mm of thread in {sc.target} (min {lo:g})")
        if hi is not None and engage > hi + 0.01:
            probs.append(f"{sc.label} ({sc.kind}): {engage:.2f} mm into {sc.target}, max {hi:g} "
                         "(tip reaches what's behind the thread)")
        disc = Pos(sc.x, sc.y, tip - 0.3 if sc.up else tip) * Cylinder(d / 2, 0.3, align=model.MIN)
        if vol(disc, tgt) <= 1e-4:
            probs.append(f"{sc.label}: tip pokes out of {sc.target}")
        if sc.pilot:
            core = Pos(sc.x, sc.y, z0) * Cylinder(0.4, z1 - z0, align=model.MIN)
            if vol(core, tgt) > 1e-3:
                probs.append(f"{sc.label}: bottoms out, the pilot hole in {sc.target} is shorter than the screw")
    return probs, rows


TILT_GROUP = starts("stand", "magnet_stand", "foot_stand")


def check_tilted(tilted, info, screws):
    """On the stand: nothing hits the stand group; every foot is on the desk and
    nothing else reaches below it."""
    probs = check_interference(tilted, screws, info, only=TILT_GROUP)
    desk = info["desk_z"]
    for it in tilted:
        if it.label.startswith(OVERLAYS + ("cable_",)):
            continue
        z = it.part.bounding_box().min.Z
        if z < desk - 0.01:
            probs.append(f"on the stand: {it.label} reaches {desk - z:.2f} mm below the desk")
        if it.label.startswith("foot_stand") and z > desk + 0.01:
            probs.append(f"on the stand: {it.label} is {z - desk:.2f} mm above the desk")
    return probs


# Minimum gaps between mating parts that must not touch (prefixes, min mm, note)
SLOTS = range(P.KNOBS)
KNOB_CAPS = tuple(f"knob{n}_knob" for n in SLOTS)
ENCODERS = tuple(f"knob{n}_encoder" for n in SLOTS)
MOTORS = tuple(f"knob{n}_motor_2204" for n in SLOTS)
COVERS = tuple(f"knob{n}_cover" for n in SLOTS) + tuple(f"knob{n}_blank" for n in SLOTS)
MODULE_BODIES = COVERS + tuple(f"knob{n}_{p}" for n in SLOTS for p in ("pcb", "base"))
GAPS = [
    (MOTORS, COVERS, P.MOTOR_TO_PLATE - 0.05, "motor bells ↔ module covers (bezel above)"),
    (MOTORS, ("top_plate",), 0.5, "motor bells ↔ top plate (slot dividers beside them)"),
    (tuple(f"knob{n}_hub" for n in SLOTS), ("top_plate",) + COVERS, 0.4,
     "knob hubs (flange, column) ↔ covers"),
    (KNOB_CAPS, ("top_plate", "knob_window") + COVERS, 0.5, "knob caps ↔ top plate and covers"),
    (tuple(f"knob{n}_press" for n in SLOTS), tuple(f"knob{n}_striker" for n in SLOTS),
     P.KNOB_PRESS_GAP - 0.05, "knob press switches ↔ strikers (set at calibration)"),
    (MODULE_BODIES, ("top_plate",), P.BEZEL_GAP - 0.05, "modules and blanks ↔ top plate (openings, dividers)"),
    (tuple(f"backplane_pogo{n}" for n in SLOTS), tuple(f"knob{n}_base" for n in SLOTS) + COVERS, 0.3,
     "pogo pins ↔ module bases and blanks (D23)"),
    (ENCODERS, ("top_plate",) + COVERS, 0.5, "encoder shafts ↔ covers"),
    (ENCODERS, ("backplane_pcb",), 0.3, "encoder pins (trimmed) ↔ backplane"),
    (("frame_pcb",), ("panel7_module",), P.GLASS_GAP - 0.01, "frame PCB ↔ glass (D8)"),
    (("cap_",), ("panel7_module",), P.GLASS_GAP - 0.01, "key caps ↔ glass, at rest (D8)"),
    (("screw_frame_csk",), ("panel7_module",), P.GLASS_GAP - 0.01, "countersunk frame screws ↔ glass"),
    (("screw_frame_pan",), ("panel7_module",), 0.5, "pan-head frame screws ↔ panel edge (off the glass)"),
    *([(("touch_bar_pcb",), ("frame_pcb_zif", "frame_pcb"), 0.3, "touch band ↔ frame PCB and its ZIF"),
       (("touch_bar_pcb",), MOTORS, 0.5, "touch band ↔ motor bells"),
       (("touch_bar_pcb",), COVERS, 0.3, "touch band ↔ module covers (D11)"),
       (("touch_bar_pcb",), ENCODERS + KNOB_CAPS, 0.5, "touch band ↔ encoders and knob stems")]
      if P.TOUCH_BAR else []),
    (("display_board",), ("usb_board",), 0.5, "display board ↔ USB board"),
    (("display_board",), ("backplane",), 0.5, "display board ↔ backplane"),
]
# The slot-only gaps, for the other module configurations (assembly checks on the rest once)
GAPS_SLOTS = [g for g in GAPS if g[0][0].startswith(("knob", "backplane_pogo"))
              or g[1][0].startswith("knob") or "D11" in g[3] or "motor bells" in g[3]
              or "encoders and knob" in g[3]]


def check_gaps(items, gaps=None):
    from build123d import Vector  # noqa: F401
    rows, probs = [], []
    for pa, pb, need, name in (GAPS if gaps is None else gaps):
        A = [it for it in items if it.label.startswith(pa)]
        B = [it for it in items if it.label.startswith(pb) and not it.label.startswith(OVERLAYS)]
        best = None
        for a in A:
            ab = a.part.bounding_box()
            for b in B:
                if a.label == b.label:
                    continue
                bb = b.part.bounding_box()
                if not bbox_overlap(ab, bb, eps=-(need + 3.0)):
                    continue
                try:
                    dd = a.part.distance_to(b.part)
                except Exception:
                    continue
                if best is None or dd < best[0]:
                    best = (dd, a.label, b.label)
        if best is None:
            rows.append((name, None, need))
            continue
        rows.append((name, best[0], need))
        if best[0] < need - 1e-3:
            probs.append(f"gap {name}: {best[0]:.2f} mm ({best[1]} ↔ {best[2]}), min {need:.2f}")
    return probs, rows


def check_floating(items, tol=0.15):
    """Every part touches (or is glued/threaded to, within tol) a chain of parts down to the tray."""
    parts = [it for it in items if not it.label.startswith(OVERLAYS + ("cable_",))]
    bbs = {it.label: it.part.bounding_box() for it in parts}
    by = {it.label: it for it in parts}
    reached, todo = {"case_tray"}, ["case_tray"]
    while todo:
        cur = todo.pop()
        for it in parts:
            lb = it.label
            if lb in reached or not bbox_overlap(bbs[cur], bbs[lb], eps=-tol):
                continue
            try:
                dd = by[cur].part.distance_to(it.part)
            except Exception:
                continue
            if dd <= tol:
                reached.add(lb)
                todo.append(lb)
    return [f"{lb} floats: touches nothing that leads to the tray" for lb in sorted(set(by) - reached)]


def present_at(step_key, items):
    """Labels physically present when `step_key`'s screws go in."""
    labels = {it.label for it in items}
    if step_key == "top_plate_sub":
        return {lb for lb in labels if TOP_SUB(lb) and not lb.startswith("cable_")}
    if step_key == "module_sub":
        return {lb for lb in labels if module_sub(lb) and not lb.startswith("cable_")}
    if step_key == "plug_in":
        step_key = "knobs"
    order = [s.key for s in STEPS if not s.bench and not s.tilted]
    upto = order[: order.index(step_key) + 1]
    out = set()
    for lb in labels:
        if lb.startswith(OVERLAYS + ("cable_",)):
            continue
        k = step_of(lb, labels)
        if k in upto:
            out.add(lb)
    return out


def check_access(items, screws):
    by = {it.label: it for it in items}
    problems, ok = [], 0
    for sc in screws:
        here = present_at(sc.step, items)
        here |= {s.label for s in screws if s.label in by and present_at(s.step, items) <= here}
        tool = model.tool_part(sc)
        tb = tool.bounding_box()
        blockers = []
        for lb in here:
            if lb == sc.label:
                continue
            part = by[lb].part
            if bbox_overlap(tb, part.bounding_box()) and vol(tool, part) > 0.01:
                blockers.append(lb)
        if blockers:
            problems.append(f"{sc.label} ({sc.kind}, step '{sc.step}'): screwdriver blocked by "
                            + ", ".join(sorted(blockers)))
        else:
            ok += 1
    return problems, ok


def check_lift(items, moving, staying, name, dz=(0.5, 2, 5, 10, 20, 40)):
    by = {it.label: it for it in items}
    probs = []
    for d in dz:
        for m in moving:
            mp = Pos(0, 0, d) * by[m].part
            mb = mp.bounding_box()
            for s in staying:
                if bbox_overlap(mb, by[s].part.bounding_box()) and vol(mp, by[s].part) > 0.01:
                    probs.append(f"{name}: {m} hits {s} when lifted {d} mm")
        if probs:
            break
    return probs


def check_pinholes(items, info):
    """A 1 mm paperclip, straight in from outside the case, reaches each button
    without touching anything else (back wall: BOOT/RESET; floor: BOOTSEL)."""
    by = {it.label: it for it in items}
    probs = []
    for x, y, z, name, d, target, start in info["pinholes"]:
        tb = by[target].part.bounding_box()
        if d == (0, -1, 0):
            end = tb.max.Y
            clip = Pos(x, (start + end) / 2, z) * Rot(X=90) * Cylinder(0.5, start - end)
        else:
            end = tb.min.Z
            clip = Pos(x, y, (start + end) / 2) * Cylinder(0.5, end - start)
        hits = [lb for lb, it in by.items()
                if not lb.startswith(OVERLAYS + ("cable_",)) and lb != target
                and bbox_overlap(clip.bounding_box(), it.part.bounding_box())
                and vol(clip, it.part) > 0.001]
        if hits:
            probs.append(f"paperclip to {name} blocked by {', '.join(hits)}")
        if vol(Pos(*d) * clip, by[target].part) <= 0:
            probs.append(f"paperclip through the {name} hole doesn't reach the button")
    return probs


def check_keystack(items, info, nubs=1):
    """D8: the cap's down-stop lands on the frame PCB after the switch trips, and no
    press (any point, any tilt the plate allows) brings a cap within KEY_GLASS_MARGIN
    of the glass, counting the frame PCB's flex at KEY_PRESS_DESIGN_N (grillage).
    B3: every key has its guide skirt on all four sides. The worst drop counts the
    guide's tilt (slop, not a feature), the switch bottomed and the down-stop; the
    down-stop is what keeps the cap off the glass."""
    import keystack
    from build123d import Rectangle
    by = {it.label: it for it in items}
    st, kf = info["stack"], info["key_frame"]
    g = model.key_stop_geometry(nubs)
    probs = []
    # Cap guide (D8, B3): straight-line travel; its tilt is slop. The worst drop counts
    # that tilt, the switch bottomed and the down-stop landing on the frame PCB
    g_len = model.key_guide_length(st)
    tilt = keystack.guide_tilt(P.KEY_GUIDE_CLEAR, g_len)
    tilt_deg = math.degrees(tilt)
    drop = keystack.cap_max_drop(g, tilt)
    defl = keystack.frame_deflection(kf["rect"], kf["key_xy"], model.PCB_WIN, kf["supports"], kf["loads"],
                                     kf["knob_wins"], kf["knob_size"])
    n_keys = len(kf["key_xy"])
    per_key = [max(defl[i::n_keys]) for i in range(n_keys)]       # a key's worst switch (2-switch proto)
    cap0, (kx0, ky0) = by["cap_0"].part, kf["key_xy"][0]
    glass_gap = cap0.bounding_box().min.Z - st.glass
    plate = next(it.part for it in items if it.label.startswith("top_plate"))
    probe_z = st.pcb_top + P.KEY_GUIDE_GAP + 0.05
    r = P.CAP_SIZE / 2 + P.KEY_GUIDE_CLEAR + P.KEY_GUIDE_WALL / 2      # mid-wall of the skirt
    probes = [(-r, 6.7), (r, -6.7), (4.2, r), (-4.2, -r)]               # one point on each side
    for i, (kx, ky) in enumerate(kf["key_xy"]):
        for dx, dy in probes:
            hit = plate & (Pos(kx + dx, ky + dy, probe_z) * Box(0.2, 0.2, 0.05))
            if hit is None or hit.volume < 1e-4:
                probs.append(f"key {i}: cap guide skirt missing at ({dx:.1f}, {dy:.1f}) from its center")
    if drop > glass_gap - P.KEY_GLASS_MARGIN + 1e-6:
        probs.append(f"worst cap drop {drop:.2f} mm (guide tilt {tilt_deg:.2f}°, switch bottomed, down-stop) "
                     f"leaves {glass_gap - drop:.2f} mm to the glass, need {P.KEY_GLASS_MARGIN} mm")
    sk = info["frame_sketch"]
    gaps = []
    for x0, x1, y0, y1 in g["feet_boxes"]:
        col = Pos(kx0 + (x0 + x1) / 2, ky0 + (y0 + y1) / 2, st.pcb_top) * Box(
            x1 - x0 - 0.02, y1 - y0 - 0.02, st.flange_bot - st.pcb_top, align=model.MIN)
        c = cap0 & col
        gaps.append(c.bounding_box().min.Z - st.pcb_top if c is not None and c.volume > 1e-4 else None)
        for i, (kx, ky) in enumerate(kf["key_xy"]):
            foot = Pos(kx + (x0 + x1) / 2, ky + (y0 + y1) / 2) * Rectangle(x1 - x0, y1 - y0)
            over = foot & sk
            if over is None or over.area < 0.99 * (x1 - x0) * (y1 - y0):
                probs.append(f"key {i}: a down-stop foot isn't fully over the frame PCB")
                break
    if any(gp is None or abs(gp - P.KEY_STOP_GAP) > 0.02 for gp in gaps):
        probs.append(f"cap down-stop gap in the model is {gaps}, expected {P.KEY_STOP_GAP}")
    if P.KEY_STOP_GAP < P.SW_TRAVEL_MAX + 0.1:
        probs.append(f"down-stop gap {P.KEY_STOP_GAP} mm may stop the cap before the switch trips "
                     f"(travel up to {P.SW_TRAVEL_MAX} mm)")
    F = P.KEY_PRESS_DESIGN_N
    worst = max(range(n_keys), key=lambda i: per_key[i])
    need = drop + per_key[worst] * F
    if need > glass_gap - P.KEY_GLASS_MARGIN + 1e-6:
        probs.append(f"key {worst}: cap can drop {drop:.2f} mm + frame flex {per_key[worst] * F:.2f} mm "
                     f"at {F:g} N = {need:.2f} mm, glass is {glass_gap:.2f} mm below "
                     f"(margin {P.KEY_GLASS_MARGIN} mm)")
    rows = dict(guide_len=g_len, tilt_deg=tilt_deg, drop=drop, margin=glass_gap - drop, glass_gap=glass_gap, stop_gap=min(g_ for g_ in gaps if g_ is not None),
                defl_max=per_key[worst], worst_key=worst, force=F, need=need,
                clearance=glass_gap - need, defl_5n=drop + per_key[worst] * 5.0)
    return probs, rows


def swept(part, d, dist):
    """Box covering a box-shaped plug body and its path `dist` back along -d."""
    b = part.bounding_box()
    lo = [b.min.X, b.min.Y, b.min.Z]
    hi = [b.max.X, b.max.Y, b.max.Z]
    for i in range(3):
        if d[i] > 0:
            lo[i] -= dist
        elif d[i] < 0:
            hi[i] += dist
    # Shrink 0.05 mm across the axis so a plug touching a neighbour face-to-face isn't a hit
    for i in range(3):
        if d[i] == 0:
            lo[i] += 0.05
            hi[i] -= 0.05
    return Pos((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, (lo[2] + hi[2]) / 2) * Box(
        hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2])


def check_insertion(items, info, only=None):
    """Each plug slides straight in along its socket's axis at the step that connects it.
    only: check just the plugs whose labels pass."""
    by = {it.label: it for it in items}
    plugs = [pl for pl in info["plugs"] if only is None or only(pl["label"])]
    order = {pl["label"]: i for i, pl in enumerate(plugs)}
    problems, ok = [], 0
    for pl in plugs:
        lb = pl["label"]
        here = present_at(pl["step"], items)
        pstep = {p["label"]: p["step"] for p in plugs}
        # same-step plugs count only if they went in earlier (list order = guide order)
        here = {h for h in here if h not in order or pstep[h] != pl["step"] or order[h] < order[lb]}
        here -= {lb, pl["mate"]}
        if pl["step"] == "close":                 # plugged in while the plate is held above
            here = {h for h in here if not TOP_SUB(h) or h in KNOB_SIDE}
        vol_ = swept(by[lb].part, pl["dir"], P.PLUG_APPROACH[pl["kind"]])
        vb = vol_.bounding_box()
        hits = [h for h in sorted(here) if h in by and bbox_overlap(vb, by[h].part.bounding_box())
                and vol(vol_, by[h].part) > 0.01]
        if hits:
            problems.append(f"{lb} (step '{pl['step']}'): way in blocked by {', '.join(hits)}")
        else:
            ok += 1
    return problems, ok


def check_cables(items, info):
    """Cables don't run through parts; plate cables reach with the plate lifted."""
    by = {it.label: it for it in items}
    solid = [it for it in items if not it.label.startswith(OVERLAYS + ("cable_", "case_tray"))]
    probs = []
    ends = {name: set(c["ends"]) for name, c in info["cables"].items()}
    for n in info["leads"]:
        ends[f"cable_motor{n}_coil"] = {f"knob{n}_motor_plug", f"knob{n}_header"}
    for it in items:
        if not it.label.startswith("cable_") or it.label not in ends:
            continue
        cb = it.part.bounding_box()
        for o in solid:
            if o.label in ends[it.label] or not bbox_overlap(cb, o.part.bounding_box()):
                continue
            v = vol(it.part, o.part)
            if v > 0.05:
                probs.append(f"{it.label} runs through {o.label} ({v:.1f} mm³)")
    for name, c in info["cables"].items():
        if c["buy"] is None:
            continue
        if c["length"] > c["buy"] + 0.5:
            probs.append(f"{name}: route needs {c['length']:.0f} mm, cable is {c['buy']} mm")
        if c["lift"] and c["lift"] > c["buy"] + 0.5:
            probs.append(f"{name}: lifting the plate {P.LIFT_SERVICE:.0f} mm needs {c['lift']:.0f} mm")
    return probs


def check_slots(items, info):
    """Knob slots (D23), every configuration: each knob's top sits where the haptic knob's
    does (same XY, KNOB_GAP + KNOB_H above the plate); each cover and blank is flush with
    the plate; the pogo pins' compression is inside their stroke and every pin lands
    fully on a pad of the module PCB (not on a slot or hole); the key pins only fit one
    way round. Lite modules: the shaft fills the knob's bore past its flat, and a full
    press keeps the knob off the cover and the stem off the bushing."""
    st, slots = info["stack"], info["slots"]
    by = {it.label: it for it in items}
    probs, rows = [], dict(top_diff=0.0, flush=0.0, pads=0, pressed_gap=None)
    ref_z = st.plate_top + P.KNOB_GAP + P.KNOB_H
    for n, ((kx, ky), kind) in enumerate(zip(info["knob_xy"], slots)):
        if kind == "blank":
            top = by[f"knob{n}_blank"].part.bounding_box().max.Z
            rows["flush"] = max(rows["flush"], abs(top - st.plate_top))
            if abs(top - st.plate_top) > P.KNOB_TOP_TOL:
                probs.append(f"slot {n}: blank top is {top - st.plate_top:+.2f} mm off the plate (flush)")
            continue
        top = by[f"knob{n}_cover"].part.bounding_box().max.Z
        rows["flush"] = max(rows["flush"], abs(top - st.plate_top))
        if abs(top - st.plate_top) > P.KNOB_TOP_TOL:
            probs.append(f"slot {n}: cover top is {top - st.plate_top:+.2f} mm off the plate (flush)")
        b = by[f"knob{n}_knob"].part.bounding_box()
        d = max(abs(b.max.Z - ref_z), abs((b.min.X + b.max.X) / 2 - kx), abs((b.min.Y + b.max.Y) / 2 - ky))
        rows["top_diff"] = max(rows["top_diff"], d)
        if d > P.KNOB_TOP_TOL:
            probs.append(f"slot {n} ({kind}): knob top is {d:.2f} mm off the haptic knob's (max {P.KNOB_TOP_TOL:g})")
        sk = info["module_pcb_sketch"][kind]
        for px, py in model.pogo_xy(0.0, 0.0):
            pad = Pos(px, py) * Circle(P.POGO_PAD_D / 2)
            over = pad & sk
            if over is None or over.area < 0.999 * pad.area:
                probs.append(f"slot {n} ({kind}): pogo pin at ({px:.1f}, {py:.1f}) isn't fully on the module PCB")
            else:
                rows["pads"] += 1
    gap = st.knob_pcb_bot - st.bp_top
    comp = P.POGO[1] - gap
    rows["compress"] = comp
    if not P.POGO_COMPRESS[0] - 1e-6 <= comp <= P.POGO_COMPRESS[1] + 1e-6:
        probs.append(f"pogo pins compressed {comp:.2f} mm, outside {P.POGO_COMPRESS} (stroke {P.POGO[2]:g})")
    big, small = max(P.KEY_PIN_D), min(P.KEY_PIN_D)
    if big <= small + 0.1 + 0.2:
        probs.append(f"key pins {P.KEY_PIN_D}: the big one fits the small one's hole, a module turned round seats")
    # Lite modules (D22): shaft engagement and the pressed knob
    if "lite" in slots:
        h, travel = info["lite"], P.ENC_PRESS_TRAVEL
        engage = h["shaft_top"] - h["stem_bot"]
        stem_gap = h["stem_bot"] - travel - h["bushing_top"]
        rows.update(engage=engage, stem_gap=stem_gap)
        if engage < P.ENC_SHAFT_FLAT[0]:
            probs.append(f"encoder shaft only {engage:.1f} mm into the knob, less than its {P.ENC_SHAFT_FLAT[0]:g} mm flat")
        if stem_gap < 0.3 - 1e-6:
            probs.append(f"pressed knob stem is {stem_gap:.2f} mm above the encoder bushing (min 0.3)")
        near = [it for it in items if it.label.startswith(("top_plate", "knob_window", "touch_bar_pcb") + COVERS)]
        for n, kind in enumerate(slots):
            if kind != "lite":
                continue
            pressed = Pos(0, 0, -travel) * by[f"knob{n}_knob"].part
            pb = pressed.bounding_box()
            for it in near:
                if not bbox_overlap(pb, it.part.bounding_box(), eps=-1.0):
                    continue
                dd = pressed.distance_to(it.part)
                g_ = rows["pressed_gap"]
                rows["pressed_gap"] = dd if g_ is None else min(g_, dd)
                if dd < 0.2:
                    probs.append(f"knob{n} pressed {travel:g} mm: {dd:.2f} mm from {it.label} (min 0.2)")
    return probs, rows


def check_slot_lift(items, screws, slots, dz=(0.5, 2, 5, 10, 20, 30, 40)):
    """Swap from the top (D23): with the top plate on, each slot's module (or blank) lifts
    straight out of its opening once its knob cap and two screws are off. The parts that
    stay are cropped to the module's column first, so the big plate and tray booleans
    stay small."""
    from build123d import Compound
    by = {it.label: it for it in items}
    probs = []
    for n in range(len(slots)):
        moving = [lb for lb in by if (slot_part(lb, n) and not lb.endswith("_knob"))
                  or lb.startswith((f"screw_motor{n}_", f"screw_hub{n}_"))]
        staying = [lb for lb in by if lb not in moving and not lb.startswith(OVERLAYS + ("cable_",))
                   and not lb.endswith("_knob") and not lb.startswith(f"screw_slot{n}_")]
        parts = [by[m].part for m in moving]
        mb = Compound(children=parts).bounding_box()
        col = Pos((mb.min.X + mb.max.X) / 2, (mb.min.Y + mb.max.Y) / 2, mb.min.Z) * Box(
            mb.size.X + 1.0, mb.size.Y + 1.0, mb.size.Z + max(dz) + 1.0, align=model.MIN)
        cb = col.bounding_box()
        near = {}
        for s in staying:
            if not bbox_overlap(cb, by[s].part.bounding_box()):
                continue
            try:
                c = by[s].part & col
            except Exception:
                c = by[s].part
            if c is not None and c.volume > 1e-4:
                near[s] = c
        hits = []
        for d in dz:
            for m, mp0 in zip(moving, parts):
                mp = Pos(0, 0, d) * mp0
                bb = mp.bounding_box()
                for s, c in near.items():
                    if bbox_overlap(bb, c.bounding_box()) and vol(mp, c) > 0.01:
                        hits.append(f"slot {n} ({slots[n]}) lift-out: {m} hits {s} when lifted {d} mm")
            if hits:
                break
        probs += hits
    return probs


def run_checks_slots(items, info):
    """Another slot configuration (D23): only the slots' contents differ, so check the
    parts in and around the slots; the rest is checked once on the default build."""
    screws = info["screws"]
    slotish = lambda lb: slot_part(lb) or lb.startswith(("backplane_pogo", "screw_slot", "screw_motor",  # noqa: E731
                                                          "screw_hub", "slot_insert"))
    t = time.time()
    # Crop the big printed parts and boards to the band the slots sit in (one boolean
    # each): every check here only looks at parts in and around the slots
    ky = info["knob_xy"][0][1]
    band = Pos(0, ky + (P.SLOT_OPEN[2] - P.SLOT_OPEN[1]) / 2, -50) * Box(
        1000, P.SLOT_OPEN[1] + P.SLOT_OPEN[2] + 12.0, 300, align=(model.Align.CENTER, model.Align.CENTER,
                                                                  model.Align.MIN))
    big = ("top_plate", "case_tray", "backplane_pcb", "touch_bar_pcb", "panel7_module")
    items = [model.Item(it.part & band, it.label, it.color, it.explode) if it.label in big else it
             for it in items]
    res = {}
    res["interference"] = check_interference(items, screws, info, only=slotish)
    sl_screws = [sc for sc in screws if sc.step in ("module_sub", "modules")]
    res["screws"], _ = check_screws(items, sl_screws)
    res["gaps"], res["gap_rows"] = check_gaps(items, GAPS_SLOTS)
    res["floating"] = [m for m in check_floating([it for it in items if slotish(it.label)
                                                  or it.label in big + ("case_tray",)])
                       if m.startswith(("knob", "backplane_pogo"))]
    res["access"], res["access_ok"] = check_access(items, sl_screws)
    res["insertion"], _ = check_insertion(items, info, only=lambda lb: lb.startswith("knob"))
    res["cables"] = [m for m in check_cables(items, info) if "motor" in m]
    res["service"] = check_slot_lift(items, screws, info["slots"])
    res["slots"], res["slot_rows"] = check_slots(items, info)
    keys = ("interference", "screws", "gaps", "floating", "access", "insertion", "cables", "service", "slots")
    name = "+".join(sorted(set(info["slots"])))
    res["problems"] = [f"{name}: {m}" for k in keys for m in res[k]]
    res["seconds"] = time.time() - t
    return res


def run_checks(items, info, tilted=None, tinfo=None, proto=None):
    screws = info["screws"]
    labels = {it.label for it in items}
    t = time.time()
    res = {}
    res["interference"] = check_interference(items, screws, info)
    res["screws"], res["screw_rows"] = check_screws(items, screws)
    res["gaps"], res["gap_rows"] = check_gaps(items)
    res["floating"] = check_floating(items)
    res["tilted"] = check_tilted(tilted, tinfo, screws) if tilted is not None else []
    res["access"], res["access_ok"] = check_access(items, screws)
    res["insertion"], res["insertion_ok"] = check_insertion(items, info)
    res["cables"] = check_cables(items, info)
    plate = [lb for lb in labels if TOP_SUB(lb) and not lb.startswith("cable_") and lb not in KNOB_SIDE]
    plate += [s.label for s in screws if s.step == "top_plate_sub"]
    caps = [lb for lb in labels if lb.startswith("knob") and lb.endswith("_knob")]
    rest = [lb for lb in labels if lb not in plate and lb not in caps
            and not lb.startswith(OVERLAYS + ("cable_", "screw_plate", "plug_usb_ext"))]
    res["service"] = check_lift(items, plate, rest, "top plate lift-off")
    res["service"] += check_slot_lift(items, screws, info["slots"])
    rest = [lb for lb in rest if not lb.startswith("plug_")]     # unplugged before lifting more out
    display = [lb for lb in labels if lb.startswith(("display_board", "panel7_module"))]
    rest2 = [lb for lb in rest if lb not in display and not lb.startswith("screw_panel")]
    res["service"] += check_lift(items, display, rest2, "display lift-out")
    bp = [lb for lb in labels if lb.startswith("backplane")]
    rest3 = [lb for lb in rest2 if lb not in bp and not slot_part(lb)
             and not lb.startswith(("screw_backplane", "screw_slot", "screw_motor", "screw_hub"))]
    res["service"] += check_lift(items, bp, rest3, "backplane lift-out (modules out)")
    res["pinholes"] = check_pinholes(items, info)
    res["keystack"], res["keystack_rows"] = check_keystack(items, info)
    res["slots"], res["slot_rows"] = check_slots(items, info)
    if proto is not None:
        p_items, p_info = proto
        pk, res["keystack_proto"] = check_keystack(p_items, p_info, nubs=2 if P.PROTO_SECOND_SWITCH else 1)
        res["keystack"] += [f"prototype: {m}" for m in pk]
    res["problems"] = (res["interference"] + res["screws"] + res["gaps"] + res["floating"] + res["tilted"]
                       + res["access"] + res["insertion"] + res["cables"] + res["service"] + res["pinholes"]
                       + res["keystack"] + res["slots"])
    res["seconds"] = time.time() - t
    return res


# --------------------------------------------------------------------------
# Pictures
# --------------------------------------------------------------------------
def step_pictures(scene, items, info, tilted_scene=None, size=(1400, 900)):
    import render
    OUT.mkdir(parents=True, exist_ok=True)
    labels = scene.labels()
    screws = info["screws"]
    done: set = set()
    shots = []
    for n, s in enumerate(STEPS, 1):
        if s.tilted:
            new = [lb for lb in tilted_scene.labels() if s.parts(lb)]
            later = [t for t in STEPS[n:] if t.tilted]
            others = [lb for lb in tilted_scene.labels() if lb not in new
                      and not lb.startswith(("cable_",)) and not any(t.parts(lb) for t in later)]
            tf = {lb: s.move for lb in new}
            img = tilted_scene.draw(new + others, az=s.view[0], el=s.view[1], size=size,
                                    transforms=tf, fit_labels=new + others, margin=0.08)
            path = OUT / f"step{n}_{s.key}.png"
            img.save(path)
            shots.append((s, [path.name]))
            continue
        new = [lb for lb in labels if s.parts(lb) and not lb.startswith("screw_")]
        step_screws = [sc for sc in screws if sc.step == s.key]
        base = [] if s.bench else [lb for lb in done if not lb.startswith(OVERLAYS)]
        names = []
        tf = {lb: s.move for lb in new if not lb.startswith(s.fixed or ("\0",))}
        img = scene.draw(base + new, az=s.view[0], el=s.view[1], size=size, transforms=tf,
                         dim=set(base), fit_labels=base + new, margin=0.08)
        path = OUT / f"step{n}_{s.key}.png"
        img.save(path)
        names.append(path.name)
        if step_screws:
            tf2 = {sc.label: (0, 0, -25 if sc.up else 25) for sc in step_screws}
            shown = base + new + [sc.label for sc in step_screws]
            img = scene.draw(shown, az=s.screw_view[0], el=s.screw_view[1], size=size,
                             transforms=tf2, dim=set(base), fit_labels=shown, margin=0.08)
            path = OUT / f"step{n}_{s.key}_screws.png"
            img.save(path)
            names.append(path.name)
        if not s.bench:
            done |= set(new) | {sc.label for sc in step_screws}
        shots.append((s, names))
    return shots


def service_pictures(scene, items, info, size=(1400, 900)):
    labels = scene.labels()
    screws = info["screws"]
    plate = [lb for lb in labels if TOP_SUB(lb)] + [s.label for s in screws if s.step == "top_plate_sub"]
    caps = [lb for lb in labels if lb.startswith("knob") and lb.endswith("_knob")]
    rest = [lb for lb in labels if lb not in plate and lb not in caps
            and not lb.startswith(("screw_plate",))]
    pics = {}
    tf = {lb: (0, 0, 45) for lb in plate}
    tf.update({lb: (0, 0, 75) for lb in caps})
    scene.draw(rest + plate + caps, az=-60, el=32, size=size, transforms=tf,
               fit_labels=rest + plate + caps, margin=0.08).save(OUT / "service_open.png")
    pics["open"] = "service_open.png"
    # Back wall pinholes, seen from behind
    scene.draw([lb for lb in labels if not lb.startswith(OVERLAYS)], az=90, el=12, size=size,
               fit_labels=["case_tray"], margin=0.04).save(OUT / "service_pinholes.png")
    pics["pinholes"] = "service_pinholes.png"
    # BOOTSEL hole in the floor, seen from below
    scene.draw([lb for lb in labels if not lb.startswith(OVERLAYS)], az=-120, el=-55, size=size,
               fit_labels=["case_tray"], margin=0.04).save(OUT / "service_bootsel.png")
    pics["bootsel"] = "service_bootsel.png"
    return pics


def animate(scene, tilted_scene, info, path_gif, size=(960, 630), frames_move=10, frames_hold=3,
            gif_width=720):
    """Assembly animation: parts fly in step by step, then the slab tilts onto the stand.

    Writes an MP4 next to the GIF when ffmpeg is installed (sharper, smaller);
    the GIF is downscaled so it plays inline on GitHub.
    """
    import render
    from PIL import Image
    labels = scene.labels()
    screws = info["screws"]
    oy0 = info["outer"][2]
    done: list = []
    frames = []

    def ease(t):
        return 0.5 - 0.5 * math.cos(math.pi * t)

    cam = (-60.0, 32.0)

    def shot(visible, tf, az_el, fit, ftf=None):
        return scene.draw(visible, az=az_el[0], el=az_el[1], size=size, transforms=tf, ss=1,
                          fit_labels=fit, fit_transforms=ftf or {}, margin=0.12)

    everything = [lb for lb in labels if not lb.startswith(OVERLAYS)]
    for s in STEPS:
        if s.tilted or s.bench:
            continue
        new = [lb for lb in labels if s.parts(lb) and not lb.startswith("screw_")]
        if s.key == "close":
            new = [lb for lb in labels if TOP_SUB(lb)]
        phases = [(new, s.move, s.view)]
        st_screws = [sc for sc in screws if sc.step == s.key
                     or (s.key == "close" and sc.step == "top_plate_sub")]
        if st_screws:
            phases.append(([sc.label for sc in st_screws], None, s.screw_view))
        for parts, move, view in phases:
            for f in range(frames_move + frames_hold):
                t = ease(min(1.0, f / frames_move))
                c = (cam[0] + (view[0] - cam[0]) * min(1, f / 5), cam[1] + (view[1] - cam[1]) * min(1, f / 5))
                tf = {}
                for lb in parts:
                    if move is not None:
                        if not lb.startswith(s.fixed or ("\0",)):
                            tf[lb] = tuple((1 - t) * m for m in move)
                    else:
                        sc = next(x for x in st_screws if x.label == lb)
                        tf[lb] = (0, 0, (1 - t) * (-25 if sc.up else 25))
                frames.append(shot(done + parts, tf, c, everything))
            cam = view
            done = done + parts
    # Tilt onto the stand
    stand_new = [lb for lb in tilted_scene.labels() if starts("stand", "magnet_stand", "foot_stand")(lb)]
    for f in range(frames_move * 2 + frames_hold * 2):
        t = ease(min(1.0, f / (frames_move * 2)))
        m = render.rot_x(P.TILT_DEG * t, pivot=(0, oy0, 0))
        c = (cam[0] + (-62 - cam[0]) * t, cam[1] + (20 - cam[1]) * t)
        tf = {lb: m for lb in done}
        img_flat = scene.draw(done, az=c[0], el=c[1], size=size, transforms=tf, ss=1,
                              fit_labels=everything, fit_transforms={lb: render.rot_x(P.TILT_DEG, (0, oy0, 0))
                                                                      for lb in everything},
                              margin=0.12)
        frames.append(img_flat)
    final = tilted_scene.draw([lb for lb in tilted_scene.labels() if not lb.startswith("cable_")],
                              az=-62, el=20, size=size, ss=1, margin=0.12)
    frames += [final] * 12
    gh = round(size[1] * gif_width / size[0])
    small = [f.resize((gif_width, gh), Image.LANCZOS) for f in frames]
    small[0].save(path_gif, save_all=True, append_images=small[1:], duration=90, loop=0,
                  optimize=True)
    import shutil
    import subprocess
    if shutil.which("ffmpeg"):
        mp4 = Path(path_gif).with_suffix(".mp4")
        proc = subprocess.Popen(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
             "-s", f"{size[0]}x{size[1]}", "-r", "11", "-i", "-", "-c:v", "libx264",
             "-pix_fmt", "yuv420p", "-crf", "20", "-movflags", "+faststart", str(mp4)],
            stdin=subprocess.PIPE)
        for f in frames:
            proc.stdin.write(f.convert("RGB").tobytes())
        proc.stdin.close()
        proc.wait()
    return len(frames)


# --------------------------------------------------------------------------
# Guide
# --------------------------------------------------------------------------
CABLES = {   # name: (type, connects)
    "cable_usb_display": ("USB-C to USB-C, USB 2.0 (3 A), one 90° side-exit end + one straight end",
                          "display board USB port ↔ USB board"),
    "cable_usb_knob_gh": ("JST-GH 1.25 mm 8-pin, plugs both ends, pin 1 to pin 1 (\"same direction\"), 26 AWG",
                          "USB board ↔ backplane"),
    "cable_keys_ffc": ("FFC, 12-pin, 1.0 mm pitch, contacts on opposite sides (type B)",
                       "frame PCB ↔ backplane"),
    "cable_touch": ("JST-SH 1.0 mm 6-pin, plugs both ends, pin 1 to pin 1",
                    "touch band ↔ backplane"),
    "cable_hy_link": ("HY2.0 (2.0 mm) 3-pin, plugs both ends, pin 1 to pin 1 (optional)",
                      "backplane ↔ display board J8 (GPIO6 link)"),
}
STEP_OF_CABLE = {"cable_usb_display": "display", "cable_usb_knob_gh": "backplane",
                 "cable_keys_ffc": "top_plate_sub", "cable_touch": "top_plate_sub",
                 "cable_hy_link": "display"}


def screw_name(sc):
    plastic = sc.target in ("case_tray", "top_plate")
    return sc.kind + (f" {sc.style}" if sc.style else "") + (" thread-forming" if plastic else " machine")


def screw_table(rows):
    seen, out = set(), []
    for sc, e in rows:
        into = "motor (base)" if sc.label.startswith("screw_motor") else (
            "motor (bell)" if sc.label.startswith("screw_hub") else
            "heat-set insert (top plate post)" if sc.target.startswith("top_plate_insert") else
            "heat-set insert (slot boss)" if sc.target.startswith("slot_insert") else
            {"panel7_module": "panel tab (metal)", "case_tray": "tray boss", "top_plate": "top plate boss"
             }.get(sc.target, sc.target))
        lim = f"{sc.engage[0]:g}–{sc.engage[1]:g} mm" if sc.engage[1] is not None else f"≥ {sc.engage[0]:g} mm"
        row = f"| {screw_name(sc)} | {into} | {e:.1f} mm | {lim} |"
        if row not in seen:
            seen.add(row)
            out.append(row)
    return out


def keystack_lines(checks):
    k, kp = checks["keystack_rows"], checks.get("keystack_proto")
    out = [
        "Key stack (D8), from `cad/keystack.py`:",
        "",
        "| | Full build | Prototype |",
        "|---|---|---|",
    ]

    def col(f):
        return f"| {f(k)} | {f(kp) if kp else '—'} |"
    out += [
        f"| Cap guide: clearance per side, engagement " + col(
            lambda r: f"{P.KEY_GUIDE_CLEAR:g} mm, {r['guide_len']:.1f} mm"),
        "| Max cap tilt in the guide (slop, not a feature) " + col(lambda r: f"{r['tilt_deg']:.2f}°"),
        "| Cap bottom ↔ glass at rest " + col(lambda r: f"{r['glass_gap']:.2f} mm"),
        "| Down-stop gap (cap feet ↔ frame PCB) " + col(lambda r: f"{r['stop_gap']:.2f} mm"),
        "| Worst cap-edge drop, any press, PCB rigid (guide tilt + switch bottomed + down-stop) "
        + col(lambda r: f"{r['drop']:.2f} mm"),
        f"| Glass margin after that drop (need {P.KEY_GLASS_MARGIN:g} mm) " + col(lambda r: f"{r['margin']:.2f} mm"),
        "| Frame PCB flex at the worst switch (grillage) " + col(lambda r: f"{r['defl_max']:.3f} mm/N"),
        f"| Cap drop + flex at {P.KEY_PRESS_DESIGN_N:g} N " + col(lambda r: f"{r['need']:.2f} mm"),
        "| Same at a hard 5 N press " + col(lambda r: f"{r['defl_5n']:.2f} mm"),
    ]
    return out


def write_guide(info, checks, shots, service):
    screws = info["screws"]
    n_hap = info["slots"].count("haptic")
    n_frame = sum(1 for sc in screws if sc.label.startswith("screw_frame"))
    counts = {}
    for sc in screws:
        kind = screw_name(sc)
        counts.setdefault((kind, sc.step), 0)
        counts[(kind, sc.step)] += 1
    num = {s.key: f"{i}. {s.title}" for i, s in enumerate(STEPS, 1)}
    num["close"] = num["close"]
    order = {s.key: i for i, s in enumerate(STEPS)}
    hw_rows = "\n".join(f"| {k} | {n} | {num[step]} |"
                        for (k, step), n in sorted(counts.items(), key=lambda kv: order[kv[0][1]]))
    cable_rows = "\n".join(
        f"| {CABLES[name][0]} | {CABLES[name][1]} | **{c['buy']} mm** | {c['length']:.0f} mm"
        + (f"; {c['lift']:.0f} mm with the plate lifted {P.LIFT_SERVICE:.0f} mm" if c["lift"] else "")
        + f" | {num[STEP_OF_CABLE[name]]} |"
        for name, c in info["cables"].items() if c["buy"])

    def status(lst, ok_text):
        return "✅ " + ok_text if not lst else "❌ " + "<br>".join(lst)

    lines = [
        "# Assembly and service guide",
        "",
        "> [!CAUTION]",
        "> **Generated from the CAD model; nothing here has been built.** The pictures and",
        "> checks come from `cad/assembly.py`, so they show the design as modeled, not a",
        "> verified build. Expect the first real assembly to find problems the model can't.",
        "",
        "![Assembly animation](../cad/out/assembly/assembly.gif)",
        "",
        "Sharper version: [assembly.mp4](../cad/out/assembly/assembly.mp4).",
        "",
        "## Model checks",
        "",
        "Run on every build of this guide (`.venv/bin/python cad/assembly.py --check`). They",
        "check the CAD model only: real parts, print tolerances and hands aren't in it, so a",
        "pass here means \"the model is consistent\", not \"it will build\".",
        "",
        "| Check | Result |",
        "|---|---|",
        f"| Parts don't overlap in the finished device (screws only into their target; knob caps on "
        f"their hubs only by the crush ribs' interference) | {status(checks['interference'], 'no overlaps')} |",
        f"| Screws: thread engagement within limits, tips stay inside their target, pilot holes "
        f"run past the tips | {status(checks['screws'], str(len(screws)) + ' screws OK')} |",
        f"| Minimum gaps between mating parts (table below) | {status(checks['gaps'], 'all met')} |",
        f"| Nothing floats: every part touches a chain of parts down to the tray | "
        f"{status(checks['floating'], 'all supported')} |",
        f"| On the stand: nothing hits the stand, every foot is on the desk | "
        f"{status(checks['tilted'], 'clear')} |",
        f"| Every screw reachable with a straight screwdriver at its step | "
        f"{status(checks['access'], str(checks['access_ok']) + ' of ' + str(len(screws)) + ' screws reachable')} |",
        f"| Every plug slides straight into its socket at its step (plug bodies modeled at "
        f"full size: USB-C overmold {P.USB_PLUG_STRAIGHT[0]:g}×{P.USB_PLUG_STRAIGHT[1]:g} mm) | "
        f"{status(checks['insertion'], str(checks['insertion_ok']) + ' of ' + str(len(info['plugs'])) + ' plugs')} |",
        f"| Cables clear every part (motor bells included); bends ≥ {P.USB_BEND_R:g} mm on the "
        f"USB-C cable; plate cables reach with the plate lifted {P.LIFT_SERVICE:g} mm | "
        f"{status(checks['cables'], 'all clear')} |",
        f"| Service: each slot's module or blank lifts straight out with the case closed (D23); top "
        f"plate, then display, then backplane lift straight out | "
        f"{status(checks['service'], 'all lift out')} |",
        f"| Knob slots (D23): knob tops within {P.KNOB_TOP_TOL:g} mm of the haptic knob's position, covers "
        f"and blanks flush with the plate, pogo pins compressed {checks['slot_rows']['compress']:.2f} mm "
        f"(stroke {P.POGO[2]:g} mm) and each on a pad; also checked with every slot haptic and every slot "
        f"lite | {status(checks['slots'], 'all match')} |",
        f"| A paperclip reaches BOOT and RESET through the back wall, and BOOTSEL through the floor | "
        f"{status(checks['pinholes'], 'all three reachable')} |",
        f"| Key stack (D8): every cap's down-stop lands on the frame PCB, and the worst cap drop plus "
        f"the frame's flex at a {P.KEY_PRESS_DESIGN_N:g} N press stays {P.KEY_GLASS_MARGIN:g} mm off the glass. "
        f"Cap guide (B3): every key has its guide skirt on all four sides; the worst drop counts the "
        f"guide's tilt, and the down-stop keeps the cap {P.KEY_GLASS_MARGIN:g} mm off the glass | "
        f"{status(checks['keystack'], 'clear of the glass (full build and prototype)')} |",
        "",
        *keystack_lines(checks),
        "",
        "Minimum gaps (nominal, from the model):",
        "",
        "| Between | Gap | Min |",
        "|---|---|---|",
        *[f"| {n} | {('> 3 mm' if g is None else f'{g:.2f} mm')} | {need:.2f} mm |"
          for n, g, need in checks["gap_rows"]],
        "",
        "Screw engagement (thread length in the part it screws into):",
        "",
        "| Screw | Into | Engaged | Allowed |",
        "|---|---|---|---|",
        *screw_table(checks["screw_rows"]),
        "",
        "## Hardware",
        "",
        "| Part | Qty | Used in step |",
        "|---|---|---|",
        hw_rows,
        f"| Magnets {P.MAGNET_TRAY[0]:g}×{P.MAGNET_TRAY[1]:g} mm (tray) | 4 | {num['tray']} |",
        f"| Magnets {P.MAGNET_STAND[0]:g}×{P.MAGNET_STAND[1]:g} mm (stand) | 4 | {num['stand']} |",
        f"| Rubber feet {P.FOOT[0]:g}×{P.FOOT[1]:g} mm | 6 | {num['tray']}, {num['stand']} |",
        f"| M2×{P.STRIKER_LEN:g} set screws (press strikers, in the spacer arms) | {n_hap} | {num['module_sub']} |",
        f"| M3 heat-set inserts, {P.INSERT_M3[0]:g} mm hole × {P.INSERT_M3[1]:g} mm long | 4 | {num['tray']} |",
        f"| M2 heat-set inserts, {P.INSERT_M2[0]:g} mm hole × {P.INSERT_M2[1]:g} mm long (slot bosses) | "
        f"{2 * P.KNOBS} | {num['tray']} |",
        f"| M2 shim washers 0.1 / 0.2 mm (tune the key stack at the frame bosses) | a few | {num['top_plate_sub']} |",
        f"| Epoxy | — | magnets |",
        "",
        "Thread-forming screws go into printed plastic (PT/WN 1411-style K30, K20, or ST2.9/ST2.2",
        "DIN 7981 pan heads): drive them slowly and stop when snug. The four case screws and the",
        "modules' screws go into brass heat-set inserts, so they can be undone for every service",
        "and every module swap.",
        "Panel screws thread into the display's metal tabs (check the thread on the real",
        "board; the drawing says M3).",
        "",
        "### Cables",
        "",
        "All bought ready-made and plugged in: nothing to solder or crimp. The length to buy",
        "is the shortest common stock length that covers the modeled route (plug tip to plug",
        "tip, plugs included) and, for the two cables to the top plate, the reach with the",
        "plate lifted. The display cable's loop is sized for 100 mm; 95-110 mm cables fit.",
        "",
        "| Cable | Connects | Buy | Route in the model | Step |",
        "|---|---|---|---|---|",
        cable_rows,
        f"| Motor leads (on the motors) | motor ↔ its module's header | {P.MOTOR_LEAD_LEN:.0f} mm assumed | "
        f"the spare coils flat in front of the bell, in a {P.LEAD_COIL[0]:g} × {P.LEAD_COIL[1]:g} × "
        f"{P.LEAD_COIL[2]:g} mm space | {num['module_sub']} |",
        "",
        "Pinouts and the strain-relief measures: [wiring.md](wiring.md). Every part with",
        "sources: [bom.md](bom.md).",
        "",
        "The HY2.0 lead is optional (the GPIO6 link: page and wake signals to the display board",
        "without a host). Its header footprint is always on the backplane.",
        "",
        "## Assembly",
        "",
    ]
    for n, (s, names) in enumerate(shots, 1):
        lines += [f"### {n}. {s.title}", "", s.text, ""]
        for nm in names:
            lines += [f"![{s.title}](../cad/out/assembly/{nm})", ""]
    lines += [
        "## Service",
        "",
        "### Open the case",
        "",
        "1. Pull the slab off the stand (magnets).",
        "2. Pull the knob caps straight up.",
        "3. Undo the four M3 screws under the tray (the top plate's posts).",
        *(["4. Lift the top plate straight up, with the caps, frame PCB and touch band on it. The",
           "   modules and blanks stay in their slots; the plate's openings lift over them.",
           f"   Its two cables reach {P.LIFT_SERVICE:.0f} mm; at that height unplug them at the",
           "   backplane's right end (flip the ZIF latch up to free the key cable; pull the touch",
           "   plug straight up)."] if P.TOUCH_BAR else
          ["4. Lift the top plate straight up, with the caps and frame PCB on it. The modules",
           "   and blanks stay in their slots; the plate's openings lift over them. The key",
           f"   cable reaches {P.LIFT_SERVICE:.0f} mm; at that height flip the ZIF latch up at the",
           "   backplane's right end to free it."]),
        "",
        f"![Top plate lifted off](../cad/out/assembly/{service['open']})",
        "",
        "### Swap a knob module (case closed)",
        "",
        "No hot-plugging: unplug USB first. Pull the knob cap, undo the two countersunk M2 screws",
        "in the cover's corners, and lift the module (or blank) straight up by its cover. Drop",
        "the new one in the same way round (the key pins only fit one way), set its cover on, and",
        "drive the two screws until the bezel is flush. Plug USB back in: the device reads which",
        "module is in each slot at power-up. Checked in the model for every slot of the default",
        "build, all-haptic and all-lite: each module lifts straight out with the plate on.",
        "",
        "### Swap a key cap or switch",
        "",
        f"With the top plate off and face down, undo the frame PCB's {n_frame} screws, lift the PCB",
        "and replace the cap or switch. Keep any shim washers with their bosses.",
        "",
        "### Recovery (factory reset)",
        "",
        "Full steps: [recovery.md](recovery.md). Nothing needs the case opened:",
        "",
        "1. **Always first: unplug for 10 s.** The 7B's I/O expander isn't reset by an ESP32",
        "   reset, so a stuck USB/CAN switch (EXIO5) only clears on power-off.",
        "2. **Settings reset** (firmware kept): hold the top-left key while plugging in.",
        "3. **Factory firmware:** the web configurator's \"Restore factory firmware\" flashes the",
        "   pinned release builds to both chips through their ROM bootloaders.",
        "4. **If a chip doesn't answer,** start its bootloader by hand with a paperclip: BOOT (and",
        "   RESET) for the display board through the two holes in the back wall; BOOTSEL for the",
        "   backplane through the hole in the floor under its left end (pull the slab off the",
        "   stand first). Hold the button while plugging in. Checked in the model: a straight",
        "   1 mm clip reaches each button and touches nothing else.",
        "5. **Never burn ESP32 eFuses or RP2350 OTP** (secure boot, flash encryption, disabling",
        "   download mode or BOOTSEL). That is the only brick a pinhole can't undo.",
        "",
        "Don't fit a battery to the 7B's J3, and unplug the back cable before using the",
        "7B's UART port: either one would feed 5 V back into the hub and the PC.",
        "",
        f"![Back wall pinholes](../cad/out/assembly/{service['pinholes']})",
        "",
        f"![BOOTSEL pinhole in the floor](../cad/out/assembly/{service['bootsel']})",
        "",
        "### Replace a motor",
        "",
        "Lift its module out (above), take the cover off and unplug the motor from the upright",
        "header on the module's front border. Undo the four screws under the tongue.",
        "",
        "### Replace the backplane",
        "",
        "Take every module and blank out, then open the case (PC unplugged). Unplug the USB-C",
        "cable at the display board, remove the display (four M3 screws from underneath), unplug",
        "the JST-GH cable at the backplane (press the latch), undo the backplane's screws at both",
        "ends and along its back strip, and lift it off the slot bosses. Its back strip sits",
        "under the display, which is why the display comes out first.",
        "",
    ]
    GUIDE.write_text("\n".join(lines) + "\n")


# --------------------------------------------------------------------------
# Bill of materials (docs/bom.md). Parts and sources are listed here; screw
# counts, cable types and lengths come from the model, so they stay in sync.
# ~Price is per device, rough, USD; "(V)" = unverified, check before ordering.
# --------------------------------------------------------------------------
BOM_PATH = ROOT / "docs" / "bom.md"
LC = "https://www.lcsc.com/product-detail/{}.html"


def lcsc(c):
    return f"[{c}]({LC.format(c)})"


# Touch band (D12, D24): an optional add-on, off by default. Its board, chip and cable
# leave the default BOM; the backplane keeps the SH header's footprint, not fitted.
TB = P.TOUCH_BAR
BASE_EXT_TYPES = 13 + (3 if TB else 0)       # extended part types on the base panel (cost.md)
BOM_JLC_BOARDS = [
    # qty, part, spec, source, ~price, used in
    ("1 panel", "PCBs: backplane, frame PCB, " + ("touch band, " if TB else "") + "USB board, panelized",
     "2-layer FR-4 1.6 mm, ENIG (owner decision: flat pads for the 0.4 mm QFNs and the pogo contacts); "
     "outlines from `cad/out/*.dxf`. Every part on one side of "
     "each board (D6), so JLC's Economic (single-side) assembly can take them. The frame PCB has "
     "countersunk M2 holes (JLC countersink option, V: fee) so its screws sit flush over the glass. "
     "JLC makes 5 panels and assembles at least 2", "JLCPCB",
     f"$45–70 for 5 panels (ENIG, {4 if TB else 3}-design fee); fees in cost.md",
     "all boards"),
]
BOM_JLC_PARTS = [
    # Backplane
    ("1", "RP2350B, stepping A4 (erratum E9 fixed)", "QFN-80 microcontroller, 48 GPIO, native USB",
     lcsc("C42415655") + " (stepping A4 per LCSC; 4,720 in stock, 2026-10-17) (V: A4 marking)", "~$1.3",
     "backplane"),
    ("1", "RP2350B support parts", "16 MB QSPI flash W25Q128JVSIQ " + lcsc("C97521") + "; 12 MHz crystal "
     "X322512MSB4SI " + lcsc("C9002") + " (basic, 20 pF load, 80 Ω ESR) with 2 × 33 pF C0G "
     + lcsc("C1562") + " and the 1 kΩ series resistor. Raspberry Pi's reference is the ABM8-272-T3 "
     + lcsc("C20625731") + " (10 pF, 50 Ω) with 2 × 15 pF; same 3225 footprint, so it's the fallback "
     "if Rev A's crystal start-up test fails. 3.3 µH SMPS inductor AOTA-B201610S3R3-101-T "
     + lcsc("C42411119") + " (3 in JLC stock, pre-order minimum 32, 2026-10-17). No stocked substitute: "
     "Raspberry Pi requires a polarity-marked, shielded 3.3 µH ±20%, DCR ≤ 250 mΩ, Isat ≥ 1.5 A, and "
     "only this part is marked. 3.3 V regulator AMS1117-3.3 " + lcsc("C6186") + " (basic, 1 A) with "
     "22 µF on its output. Flash, crystal, caps and regulator are basic parts",
     "JLC (V: inductor stock on order day)", "$3–4", "backplane"),
    ("1", "GH 8-pin header, HCTL HC-GH-8PWT", "1.25 mm GH, side entry, latching (USB link). Clone of "
     "JST SM08B-GHS-TB: 13.25 mm wide with solder tabs, 4.25 mm tall, mates with JST GH plugs",
     lcsc("C3011950") + " (1,726 in JLC stock, $0.18, 2026-10-17; the JST part " + lcsc("C265111")
     + " has 0) (V: pad drawing on layout day)", "~$0.2", "backplane"),
    ("1", "FFC/FPC connector, 12-pin 1.0 mm, flip-lock ZIF, right angle",
     "e.g. XUNPU FPC-1.0FX-12PWCR-H20 (V: contact side, height)", lcsc("C19269355"), "~$0.2", "backplane"),
    ("1" if TB else "— (footprint, DNP)", "JST BM06B-SRSS-TB", "6-pin SH header, top entry (touch cable). "
     + ("Fitted with the touch band" if TB else "Not fitted by default (D24): the footprint stays so a "
        "touch band can be added later (fit the header, or order the backplane with it)"),
     lcsc("C160392"), "~$0.4" if TB else "—", "backplane"),
    ("1 (optional)", "HY2.0 3-pin header, 2.0 mm, SMD side entry", "GPIO6 link to the 7B's J8 (D5); the "
     "footprint is always on the board, fit it if you use the link", "LCSC (V: part not chosen)", "~$0.1",
     "backplane"),
    ("1", "BOOTSEL button", "reverse-mount SMD tact switch (plunger through the board, pressed through the "
     "floor pinhole). If none is found: a plain SMD tact switch on the bottom side, the board's only "
     "bottom-side part", "LCSC (V: part not chosen)", "~$0.1", "backplane"),
    ("4" if TB else "3", "SRV05-4-P-T7 ESD arrays", "4 lines each, SOT-23-6, pin 5 to 3V3. Three on the 10 "
     "key-matrix lines at the ZIF, one on SDA/SCL at the SH header (DNP with the header); series resistors "
     "on every line",
     lcsc("C85364") + " (preferred extended: no loading fee; 36,942 in JLC stock, 2026-10-17)",
     "~$0.8" if TB else "~$0.6",
     "backplane"),
    ("90", "Pogo pin, SMD, BAT WIRELESS BWCD-L3W2.0H1.0", "slot connectors (D23): 18 per slot, upright on "
     f"the top side (D6), {P.POGO[1]:g} mm tall, {P.POGO[0]:g} mm barrel, {P.POGO[2]:g} mm stroke, ~1 N, 1.5 A, "
     "10,000 cycles, gold-plated brass. They press the ENIG pads under each module; pinout in wiring.md",
     lcsc("C2988082") + " (32,763 in JLC stock, $0.0596 at 50–149, 2026-10-19; extended) (V: drawing, "
     "force at 0.5 mm)", "~$5.4", "backplane"),
    ("1 set", "Backplane passives", "~470 µF bulk on the motor rail; decoupling; 1 kΩ BOOTSEL resistor at "
     "the MCU end; pull-downs on the five SSI data lines and the two ID rows; one 10 kΩ pull-up on the "
     "shared nFAULT line (the slots' contact C6, D24); CC sense filters; I²C pull-ups for the touch band "
     "(the drivers' pull-downs sit on the haptic modules)",
     "JLC basic parts", "$2–4", "backplane"),
    ("1", "TPS259470ARPWR eFuse (motor rail)", "soft-start switch for the motor rail only (to the slots' "
     "VMOT pins), enabled by firmware after reading CC and only with a haptic module fitted. Same part as the USB board's two VBUS switches: true reverse blocking, "
     "current limit set by RILM (0.5–6 A), slew rate set by a dVdt cap", lcsc("C3662799")
     + " (4,468 in JLC stock, $1.29, 2026-10-17)", "~$1.3", "backplane"),
    # Frame PCB
    ("21", "B3U-1000P", "key switches (buy spares and sort by feel)", lcsc("C231329"), "~$3", "frame PCB"),
    ("21", "1N4148W", "SOD-123 matrix diodes (each module adds 2: press and ID)", "JLC basic part", "~$0.5",
     "frame PCB"),
    ("1", "FFC/FPC connector, 12-pin 1.0 mm, flip-lock ZIF", "same as on the backplane",
     lcsc("C19269355"), "~$0.2", "frame PCB"),
    # Touch band (optional add-on, D24: only with TOUCH_BAR = True)
    *([("1", "Touch controller: AT42QT2120", "capacitive slider controller, I²C, on the band's "
        "parts side. Optional (D12, D24): off by default", lcsc("C614938") + " (V: stock; 69 on 2026-10-17)",
        "~$1.9", "touch band"),
       ("1", "JST SM06B-SRSS-TB", "6-pin SH header, side entry", lcsc("C160405"), "~$0.9", "touch band"),
       ("1 set", "Touch band passives", "1–10 kΩ in series with each electrode; ferrite bead + 10 µF on 3V3",
        "JLC basic parts", "~$0.2", "touch band")] if TB else []),
    # USB board
    ("1", "WCH CH334F", "4-port USB 2.0 hub, QFN-24; PSELF strapped low (bus-powered), 0 Ω option to flip",
     lcsc("C5187527") + " (8,489 in stock, $0.63, 2026-10-17)", "~$0.6", "USB board"),
    ("1", "12 MHz crystal, 3225", "CH334F XI/XO (its load caps are built in); plus a 0 Ω link footprint "
     "that can ground XI for crystal-free mode. Same part as the RP2350B's crystal",
     lcsc("C9002") + " (basic)", "~$0.1", "USB board"),
    ("1", "USB-C receptacle, 16-pin, mid-mount (sinks 1.6 mm into the board)",
     "external port; HCTL HC-TYPE-C-16P-CB1.6 (V: get the drawing; slot and pad depth in the outline are "
     "from the model, shell legs unverified)",
     lcsc("C2894902") + "; fallback top-mount TYPE-C-31-M-12 " + lcsc("C165948"), "~$0.2", "USB board"),
    ("1", "USB-C receptacle, 16-pin, TYPE-C-31-M-12", "internal port to the display board; SMD signals, "
     "4 through-hole shell legs", lcsc("C165948"), "~$0.2", "USB board"),
    ("1", "GH 8-pin header, HCTL HC-GH-8PWT", "USB link to the backplane; same as on the backplane",
     lcsc("C3011950"), "~$0.2", "USB board"),
    ("2", "TPS259470ARPWR eFuses (VBUS)", "one per downstream VBUS branch: display port (RILM 3.32 kΩ, "
     "~1 A) and backplane (RILM ~1.87 kΩ, ~1.8 A). Back-to-back FETs block reverse current while on, "
     "so the 7B can't back-feed the PC. Enable delayed by an RC. QFN-10 2 × 2 mm, 0.45 mm pitch",
     lcsc("C3662799") + " (one type for all three switches)", "~$2.6", "USB board"),
    ("1", "SRV05-4-P-T7", "USB ESD, external port, at the socket: D+, D−, CC1, CC2 on its four lines, "
     "pin 5 to VBUS. 3.5 pF typ (5 pF max) per line; the datasheet lists USB 2.0, so it suits the "
     "480 Mbit/s pair. Same SOT-23-6 footprint as the USBLC6-2SC6 " + lcsc("C7519") + ", but its four "
     "lines are separate pins (no flow-through), so route each line to its own pad",
     lcsc("C85364") + " (preferred extended: no loading fee)", "~$0.2", "USB board"),
    ("1 (optional, not fitted)", "USB-PD sink, CH224-class (e.g. CH224K)", "D9: footprint beside the external "
     "port on its CC lines, to ask a PD charger for 5 V / 3 A. Not fitted by default; the policy is a "
     "1.5 A+ C-to-C port", "LCSC (V: part and stock)", "~$0.5 + extended fee", "USB board"),
    ("1", "VBUS TVS", "5–5.5 V standoff, clamping below 6 V (the CH334F sits straight on VBUS; check "
     "its absolute max)",
     "LCSC (V: not chosen)", "~$0.1", "USB board"),
    ("1 set", "USB board passives", "5.1 kΩ CC pull-downs ×2, 56 kΩ CC pull-ups ×2 (display port), "
     "10 kΩ CC sense resistors ×2 (+ 10–22 kΩ at the knob end), 2 × 22 µF 25 V X5R at the input "
     "(CL21A226MAQNNNE C45783, basic; keep a 22–47 µF polymer footprint, fitted only if the hot-plug "
     "test rings), RC delay on the switch enables, RILM and dVdt parts, 22 µF on the CH334F's VDD33, "
     "decoupling",
     "JLC basic parts", "~$1", "USB board"),
]
BOM_PRINTS = [
    ("21", "Clear key caps", "`cad/out/key_cap_clear_resin.stl`, clear resin (SLA), one standard clear "
     "finish (D15; revisit after seeing it). The rails and lugs underneath are the down-stop", "JLC3DP",
     "$20–40", "Build the top plate"),
    ("5", "Knob-window covers", "`cad/out/knob_window.stl`, clear resin (SLA), same order as the caps; "
     "sit on a ledge in the top plate", "JLC3DP", "$3–6", "Build the top plate"),
    ("1", "Case tray", "`cad/out/print_case_tray.stl`; the cable clips are part of it. PETG, "
     "4 walls, ≥25% infill", "home printer or JLC3DP", "$4–6 / $20–40", "Print the case"),
    ("1", "Top plate", "`cad/out/print_top_plate.stl` (exported face-down); PETG, 100% infill over "
     "the touch band, no CF/metal-filled filament; M3 heat-set inserts in its four posts",
     "home printer or JLC3DP", "$3–5 / $15–30", "Print the case"),
    ("1", "Stand", "`cad/out/print_stand.stl` (a shell, open underneath, with ribs); PETG",
     "home printer or JLC3DP (get a quote)", "$2–4 / $10–25", "Put it on the stand"),
    ("2", "Plate props (tool)", "`cad/out/print_plate_prop.stl`: hold the top plate 40 mm up while you "
     "plug its cables in", "home printer", "<$1", "Close the case"),
    ("1", "Fit coupon (optional)", "`cad/out/print_fit_coupon.stl`: cap holes, magnet pocket and hub fit "
     "at three sizes; print it first and set `HOLE_COMP` in params.py", "home printer", "<$1",
     "Print the case"),
]
BOM_ALI = [
    ("1", "Waveshare ESP32-S3-LCD-7B (non-touch, SKU 31727)", "7\" 1024×600 display board. No battery on "
     "J3", "Waveshare", "$34", "Mount the display"),
]
# Knob slots (D23): what one module or blank adds. Screws come from the model.
MODULE_JLC = {
    "haptic": [
        ("1", "Module PCB, haptic", f"{P.MODULE_W:g} × {P.MODULE_FRONT + P.MODULE_BACK:g} mm, 2-layer 1.6 mm, ENIG; "
         "`cad/out/module_haptic_pcb_outline.dxf`. The motor's tongue hangs on two torsion necks (the hinge, "
         "D10); 18 ENIG pads underneath meet the slot's pogo pins (pads aren't parts, so every part is on "
         "top, D6). Its own JLC design: 5 made, at least 2 assembled (cost.md)", "JLCPCB",
         "$4–8 of a $20–40 order", "Build the knob modules"),
        ("1", "DRV8311HRRWR (TI)", "3-phase motor driver, 3–20 V, 5 A peak, hardware variant, WQFN-24 3 × 3 mm "
         "0.4 mm, on the fixed front border (D16). 3x PWM (MODE to AVDD); nSLEEP and INLA/B/C on NSTDBY (D24). "
         "Fallback: TMC6300-LA-T " + lcsc("C5274455") + " (other footprint: a module respin)",
         lcsc("C5218862") + " (7,399 in JLC stock, $0.95 at 500, 2026-10-19; extended)", "~$1.0–1.4",
         "Build the knob modules"),
        ("1", "MT6701CT-STD", "magnetic angle sensor, SSI, SOP-8 (not the QT: that's a 3×3 QFN-16), on the "
         "tongue under the magnet", lcsc("C3003196") + " (V: JLC stock)", "~$1.6", "Build the knob modules"),
        ("1", "B3U-1000P", "knob press switch on the front border (the spacer's arm presses it)",
         lcsc("C231329"), "~$0.2", "Build the knob modules"),
        ("2", "1N4148W", "press switch and module-ID diodes (key matrix; wiring.md)", "JLC basic part",
         "~$0.02", "Build the knob modules"),
        ("1", "Pin header 1×3, 2.54 mm, vertical SMD (HX PZ2.54-1x3P TP-YQ)", "motor plug, upright on the "
         "front border; staggered SMD pins (D6)", lcsc("C41417360") + " (47,856 in JLC stock, $0.039, "
         "2026-10-19) (V: fits the motor's plug)", "~$0.04", "Build the knob modules"),
        ("1 set", "Module passives", "2 × 22 µF 0805 25 V (C45783) and 100 nF on VM/VIN_AVDD; 100 nF CP to VM; "
         "1 µF on AVDD; 100 nF on CSAREF (tied to AVDD); 10 kΩ pull-downs on NSTDBY and the three PWM nets "
         "(RP2350 erratum E9: they live with the driver, so a lite module's lines stay free); 10 kΩ CSN "
         "pull-up; decoupling. MODE and SLEW tied to AVDD, GAIN to GND, the current-sense outputs open",
         "JLC basic parts", "~$0.3", "Build the knob modules"),
    ],
    "lite": [
        ("1", "Module PCB, lite", f"{P.MODULE_W:g} × {P.MODULE_FRONT + P.MODULE_BACK:g} mm, 2-layer 1.6 mm, ENIG; "
         "`cad/out/module_lite_pcb_outline.dxf`: the haptic outline, pads and holes, no tongue. Its own JLC "
         "design: 5 made, at least 2 assembled", "JLCPCB", "$3–6 of a $15–30 order", "Build the knob modules"),
        ("1", "Push encoder, Bourns PEC11R, vertical, 15 mm flatted 6 mm shaft, push switch",
         "Pick one when ordering (D22): **detented** PEC11R-4215F-S0024 (24 detents, 24 pulses) or **smooth** "
         "PEC11R-4015F-S0024 (no detents, 24 pulses). Same body, shaft and footprint; the push switch is the "
         "knob press. Through-hole: JLC hand-solders it under Economic assembly (7 joints, ~$0.0173 per "
         f"joint; V: on the quote). Leads trimmed to ≤ {P.ENC_PIN_STUB:g} mm (the backplane is "
         f"{P.POGO_WORK:g} mm below). SMD option for the detented build only: Alps EC11J1525402 "
         + lcsc("C209762") + " (30 detents, 1,666 in JLC stock, $2.59 at 10, 2026-10-19; other footprint)",
         lcsc("C143790") + " detented (5,249 in stock, $2.00 at 10) / " + lcsc("C143789")
         + " smooth (3,748, $2.73 at 1), 2026-10-19 (V: body height, shaft length)", "~$2–3",
         "Build the knob modules"),
        ("2", "1N4148W", "push switch and module-ID diodes (key matrix)", "JLC basic part", "~$0.02",
         "Build the knob modules"),
        ("1 set", "Module passives (lite)", "10 kΩ pull-ups to 3V3 on A and B, then 10 kΩ in series (it also "
         "limits the current if a misread slot drives these lines as PWM) and 10 nF to GND (Bourns' filter)",
         "JLC basic parts", "~$0.1", "Build the knob modules"),
    ],
    "blank": [],
}
MODULE_PRINTS = {
    "haptic": [
        ("1", "Module base", "`cad/out/module_base.stl`: under the PCB, sets the pogo pins' "
         f"{P.POGO_WORK:g} mm working height; two key pins ({P.KEY_PIN_D[0]:g} and {P.KEY_PIN_D[1]:g} mm) "
         "underneath. PETG", "home printer or JLC3DP", "<$1", "Build the knob modules"),
        ("1", "Module cover", "`cad/out/module_cover.stl`: bezel flush with the plate, four posts, front "
         "wall. PETG, black like the plate", "home printer or JLC3DP", "<$1", "Drop in the knob modules"),
        ("1", "Motor spacer ring", "`cad/out/motor_spacer.stl`: sets the sensor gap, centers the magnet; "
         "the arm carries the press striker. PETG", "home printer or JLC3DP", "<$1", "Build the knob modules"),
        ("1", "Knob hub", "`cad/out/knob_hub.stl`: D-flat column, flange screwed to the bell; PETG",
         "home printer or JLC3DP", "<$1", "Build the knob modules"),
        ("1", "Knob cap", "`cad/out/knob.stl` (D-bore with crush ribs); PETG", "home printer or JLC3DP",
         "<$1", "Press on the knob caps"),
    ],
    "lite": [
        ("1", "Module base", "`cad/out/module_base.stl`, the same as the haptic module's", "home printer or JLC3DP",
         "<$1", "Build the knob modules"),
        ("1", "Module cover", "`cad/out/module_cover.stl`, the same as the haptic module's",
         "home printer or JLC3DP", "<$1", "Drop in the knob modules"),
        ("1", "Knob cap (lite)", "`cad/out/knob_lite.stl`: the same cap with a stem through the cover's hub "
         "hole; D-bore with crush ribs that seats on the encoder's shaft tip; PETG", "home printer or JLC3DP",
         "<$1", "Press on the knob caps"),
    ],
    "blank": [
        ("1", "Blank cover", "`cad/out/blank_cover.stl`: bezel flush with the plate, four posts down to the "
         "backplane, front wall. PETG", "home printer or JLC3DP", "<$1", "Drop in the knob modules"),
    ],
}
MODULE_BOUGHT = {
    "haptic": [
        ("1", "2204 gimbal motor (Mitoot 2204 260KV or similar)", "~28 × 13 mm, hollow shaft; lead ~30 cm with a "
         "3-pin 2.54 mm servo-style (Futaba/JR) plug per one listing (V: check plug and lead on arrival; "
         "measure base/bell hole patterns and thread depths against params.py)",
         "AliExpress (two sellers); for a 100-unit run, factory-direct after samples (cost.md)",
         "$8–12 ($5–9 landed at 100)", "Build the knob modules"),
        ("1", "Diametric magnet 6 × 2.5 mm", "for the MT6701", "AliExpress", "~$1", "Build the knob modules"),
        ("1", f"M2×{P.STRIKER_LEN:g} set screw", "press striker, in the spacer's arm", "hardware kit", "~$0.1",
         "Build the knob modules"),
        ("—", "Epoxy", "the magnet", "any", "—", "Build the knob modules"),
    ],
    "lite": [],
    "blank": [],
}
MODULE_TITLES = {"haptic": "Haptic module", "lite": "Lite module", "blank": "Blank cover"}
BOM_EXTERNAL = [
    ("1", "USB-C to USB-C cable (to the computer)", "USB 2.0 is enough; a C-to-C cable lets the device read "
     "the port's 1.5 A / 3 A offer. An A-to-C cable works, with weaker haptics (500 mA). Plug overmold "
     f"≤ {P.USB_EXT_POCKET[0] - 0.5:g} × {P.USB_EXT_POCKET[1] - 0.5:g} mm to seat in the back-wall opening",
     "any", "$3–8", "Plug it in"),
]


def proto_bom_lines(pinfo):
    """Prototype (D3, changed 2026-10-18) parts that come from the model; the full list
    is docs/parts.md."""
    if pinfo is None:
        return []
    fp = pinfo["frame_pcb"]
    x0, x1, y0, y1 = fp["outline"]
    n_sw = len(fp["switches"]) + len(fp["switches_b"])
    kts = pinfo["knob_test_stand"]
    w_, d_, h_ = kts["size_mm"]
    so = "; ".join(f"{k}: **{v:.1f} mm**" for k, v in pinfo["standoffs"].items())
    rows = [
        ("1", "Prototype frame PCB, rev C", f"{x1 - x0:.1f} × {y1 - y0:.1f} mm, the full build's two top-left "
         f"keys on the 7B; {n_sw} B3U footprints (a second switch above each key for the D8 force test), "
         f"{len(fp['mount_holes_pan'])} M2 holes off the glass, {len(fp['mount_holes_csk'])} countersunk over it, "
         "solder pads off the glass. `hardware/proto-frame/`. The only custom PCB before Rev A",
         "JLCPCB (assembled)", "$35–55 with shipping and duty (cost.md)", "prototype"),
        ("2 + 2", "Key caps: one nub and two nubs", "`cad/out/key_cap_clear_resin.stl` (one switch) and "
         "`cad/out/key_cap_two_nub_clear_resin.stl` (two switches), clear resin, one standard finish",
         "JLC3DP", "$4–8", "prototype"),
        ("1", "Knob test stand", f"`cad/out/print_knob_test_stand.stl`, {w_:g} × {d_:g} mm, "
         f"{h_:g} mm to the motor seat. The 2204 screws on with 4 × {kts['motor_screw']} from below; an "
         f"MT6701 breakout ({P.MT6701_BREAKOUT[0]:g} mm wide, EST: measure it) slides in on rails under "
         "the deck. With `knob.stl` and `knob_hub.stl`", "JLC3DP (PETG or resin)", "$3–8", "prototype"),
        ("1", "Prototype top plate", "`cad/out/print_proto_top_plate.stl`, 3 mm, with the cap guide skirts "
         f"({P.KEY_GUIDE_CLEAR:g} mm per side, D8). Tune the fit with the coupon via `HOLE_COMP` first",
         "JLC3DP or home printer (PETG or resin)", "$5–10", "prototype"),
        ("1 set", "Standoffs (model lengths; round to stock, shim the rest)", so, "hardware kit", "~$5",
         "prototype"),
    ]
    out = ["## Prototype parts from the model (D3)", "",
           "The rest of the prototype list is in [parts.md](parts.md).", ""]
    out += ["| Qty | Part | Spec | Source / LCSC # | ~Price | Used in |", "|---|---|---|---|---|---|"]
    out += [f"| {q} | {p_} | {sp} | {src} | {pr} | {u} |" for q, p_, sp, src, pr, u in rows]
    return out


def write_bom(info, proto_info=None, infos=None):
    """docs/bom.md: the base device, then what each knob module and blank adds (D23).
    infos: model infos with every slot "haptic" and every slot "lite" (their screws)."""
    infos = infos or {}
    screws = info["screws"]
    num = {s.key: s.title for s in STEPS}
    slot_steps = ("module_sub", "modules")

    def screw_rows(scs):
        counts = {}
        for sc in scs:
            kind = screw_name(sc)
            counts.setdefault(kind, {})
            counts[kind][sc.step] = counts[kind].get(sc.step, 0) + 1
        return [(str(sum(st.values())), f"{kind.split()[0]} screw", " ".join(kind.split()[1:]),
                 "hardware kit", "~$1 (pack of 50)" if "M2x30" not in kind else "~$2 (pack of 20)",
                 ", ".join(num[k] for k in st)) for kind, st in counts.items()]

    def slot_screws(inf, n):
        return [sc for sc in inf["screws"] if sc.label.startswith((f"screw_motor{n}_", f"screw_hub{n}_",
                                                                    f"screw_slot{n}_"))]
    price = {"cable_usb_display": "$2–4", "cable_usb_knob_gh": "$1–2 (26 AWG)",
             "cable_keys_ffc": "$0.06 (LCSC " + lcsc("C80646") + ", reverse) to $1",
             "cable_touch": "$0.5–1", "cable_hy_link": "~$0.5 (optional)"}

    def table(rows):
        out = ["| Qty | Part | Spec | Source / LCSC # | ~Price | Used in |", "|---|---|---|---|---|---|"]
        out += [f"| {q} | {p} | {sp} | {src} | {pr} | {u} |" for q, p, sp, src, pr, u in rows]
        return out

    cable_rows = [("1", CABLES[n][0].split(",")[0], CABLES[n][0].split(",", 1)[1].strip()
                   + f"; **{c['buy']} mm** (model route {c['length']:.0f} mm"
                   + (f", {c['lift']:.0f} mm with the plate lifted" if c["lift"] else "") + ")",
                   "AliExpress (search the spec)", price[n], num[STEP_OF_CABLE[n]])
                  for n, c in info["cables"].items() if c["buy"]]
    hw_rows = screw_rows([sc for sc in screws if sc.step not in slot_steps])
    hw_rows += [
        ("4", f"Magnets {P.MAGNET_TRAY[0]:g} × {P.MAGNET_TRAY[1]:g} mm", "tray", "AliExpress", "~$1",
         num["tray"]),
        ("4", f"Magnets {P.MAGNET_STAND[0]:g} × {P.MAGNET_STAND[1]:g} mm", "stand", "AliExpress", "~$1",
         num["stand"]),
        ("6", f"Rubber feet {P.FOOT[0]:g} × {P.FOOT[1]:g} mm", "self-adhesive", "AliExpress", "~$1",
         f"{num['tray']}, {num['stand']}"),
        ("4", f"M3 heat-set inserts, {P.INSERT_M3[0]:g} mm hole × {P.INSERT_M3[1]:g} mm", "top plate posts "
         "(e.g. Ruthex RX-M3x5.7 or CNC Kitchen M3 short)", "AliExpress / Amazon", "~$1", num["tray"]),
        (str(2 * P.KNOBS), f"M2 heat-set inserts, {P.INSERT_M2[0]:g} mm hole × {P.INSERT_M2[1]:g} mm",
         "slot bosses: the modules' and blanks' screws go into these (D23; V: an M2 × 4 mm insert, ~3.5 mm "
         "outside)", "AliExpress", "~$1", num["tray"]),
        ("1 set", "M2 shim washers, 0.1 and 0.2 mm", "between the frame PCB and its bosses, to tune the key "
         "stack", "AliExpress", "~$1", num["top_plate_sub"]),
        *([("1", "3M 467MP or 468MP transfer tape", "full coverage under the touch band (no air gaps)",
            "AliExpress / DigiKey", "~$3", num["top_plate_sub"])] if TB else []),
        ("—", "Epoxy", "magnets", "any", "~$3", num["tray"]),
        ("— (optional)", "Thin foam or silicone ring", "on each key cap's flange, against rattle", "any", "~$1",
         num["top_plate_sub"]),
    ]
    first = {k: (inf, inf["slots"].index(k)) for k, inf in [("haptic", infos.get("haptic", info)),
                                                           ("lite", infos.get("lite", info)),
                                                           ("blank", info)] if k in inf["slots"]}

    def module_lines(kind):
        rows = list(MODULE_JLC[kind]) + list(MODULE_PRINTS[kind]) + list(MODULE_BOUGHT[kind])
        if kind in first:
            inf, n = first[kind]
            rows += screw_rows(slot_screws(inf, n))
        return [f"### {MODULE_TITLES[kind]}", "", *table(rows), ""]

    cfg = ", ".join(info["slots"])
    lines = [
        "# Bill of materials",
        "",
        "> [!CAUTION]",
        "> Generated by `cad/assembly.py` from the CAD model; nothing has been built or",
        "> ordered. **(V)** marks parts to verify before ordering. LCSC numbers were looked up",
        "> on 2026-10-17 (encoders, pogo pins and the module header 2026-10-19); stock moves, so",
        "> check each one in JLC's parts library when ordering.",
        "",
        "Knobs are modules in slots (D23). This list has two parts: the **base device** (display,",
        "keys, case, backplane, USB board, cables: no knobs) and what **each knob module or",
        "blank** adds. Every slot takes a haptic module, a lite module or a blank. The touch band",
        "is " + ("fitted in this build (`TOUCH_BAR = True`)." if TB else "an optional add-on, off by "
                 "default (D24): its board, chip and cable aren't in this list (`TOUCH_BAR = True` in "
                 "params.py adds them; the backplane keeps the SH header's footprint)."),
        f"The model's default build is the owner's first: {cfg}.",
        "",
        "The builder solders and crimps nothing: JLC fits every board-mounted part, and every",
        "cable is bought ready-made. Screws, cable types and lengths come from the model, so they",
        "match [assembly.md](assembly.md). Totals: [cost.md](cost.md).",
        "",
        "## Base device",
        "",
        "### Order 1: JLC (PCBs, assembly, prints)",
        "",
        "#### PCBs",
        "",
        *table(BOM_JLC_BOARDS),
        "",
        "#### Parts JLC fits (per device)",
        "",
        *table(BOM_JLC_PARTS),
        "",
        "JLC's assembly minimum is 2 boards, so you pay for the parts on a spare set too",
        "(see [cost.md](cost.md)). JLC charges a setup fee once for the panel, plus a fee per",
        f"\"extended\" part type: {BASE_EXT_TYPES} types with the parts above (list and fees in cost.md).",
        "Prices are LCSC's at the quantity for 2 boards, 2026-10-17.",
        "",
        "#### 3D prints",
        "",
        *table(BOM_PRINTS),
        "",
        "### Order 2: AliExpress / Waveshare",
        "",
        "#### Bought parts",
        "",
        *table(BOM_ALI),
        "",
        "#### Internal cables (ready-made, plug-in)",
        "",
        *table(cable_rows),
        "",
        "Search terms that find them: \"USB C to USB C 90 degree 10cm\" (pick a side-angle "
        "(left/right) plug for the display end, not up/down); \"JST GH 1.25 8 pin double head "
        "cable 10cm\" (same direction, 26 AWG); the FFC is LCSC C80646 (12-pin 1.0 mm, 100 mm, "
        "reverse/opposite side), or \"FFC 12 pin 1.0mm 100mm\" type B; "
        + ("\"JST SH 1.0 6 pin double head 8cm\"; " if TB else "")
        + "optional: \"HY2.0 3 pin double head 5cm\" (GPIO6 link).",
        "",
        "#### Hardware",
        "",
        *table(hw_rows),
        "",
        "### Not in the kit",
        "",
        *table(BOM_EXTERNAL),
        "",
        "## Knob modules and blanks (per slot)",
        "",
        "One of these per slot. Each module type is its own small JLC design (5 PCBs made, at",
        "least 2 assembled), ordered with the base or later; the motors, magnets and screws come",
        "with order 2. Modules have no MCU: the backplane runs every slot (D23).",
        "",
        *module_lines("haptic"),
        *module_lines("lite"),
        *module_lines("blank"),
        *proto_bom_lines(proto_info),
        "",
        "## Totals",
        "",
        "Base device **~$320–505** with your own 3D printer, plus per module (US import duty",
        "included; one build, module boards ordered with the base): haptic ~$42–57 each for two",
        "(~$28–38 each for five), lite ~$26–33 each for two, blank ~$1. The owner's first build",
        "(2 haptic + 3 blank) comes to **~$405–620**" + (" (the touch band adds ~$30)" if TB else "")
        + ". Prices above are per part; the totals also",
        "include JLC's PCB, setup and extended-part fees, the parts on the spare boards, shipping and",
        "duty. Breakdown and the 5, 25 and 100 unit figures: [cost.md](cost.md).",
        "",
    ]
    BOM_PATH.write_text("\n".join(lines) + "\n")


def slot_line(name, r):
    """One summary line for a slot configuration's checks."""
    out = (f"  slots {name}: knob tops within {r['top_diff']:.2f} mm of the haptic knob's (max "
           f"{P.KNOB_TOP_TOL:g}), covers/blanks flush within {r['flush']:.2f} mm, pogo pins "
           f"{r['compress']:.2f} mm in (stroke {P.POGO[2]:g}), {r['pads']} pins on pads")
    if "engage" in r:
        pg = "n/a" if r["pressed_gap"] is None else f"{r['pressed_gap']:.2f} mm"
        out += (f"; lite: shaft {r['engage']:.1f} mm into the knob, pressed {P.ENC_PRESS_TRAVEL:g} mm: "
                f"{pg} to the cover, stem {r['stem_gap']:.2f} mm above the bushing")
    return out


def main():
    check_only = "--check" in sys.argv
    t0 = time.time()
    tilted, L, info = model.full_device(tilt=True)
    flat = info["flat_items"]
    tinfo = info
    proto, _, pinfo = model.prototype()
    checks = run_checks(flat, info, tilted, tinfo, proto=(proto, pinfo))
    checks["problems"] += [f"fit: {w}" for w in L.warnings]   # build.py's fit warnings for this build
    others = {}
    # --default-only: skip the other slot configurations (the touch band run, D24)
    for cfg in (() if "--default-only" in sys.argv else P.CHECK_CONFIGS):   # other slot configurations (D23)
        o_flat, _, o_info = model.full_device(tilt=False, slots=cfg)
        others[cfg] = (o_info, run_checks_slots(o_flat, o_info))
    problems = checks["problems"] + [m for _, r in others.values() for m in r["problems"]]
    secs = "".join(f" + {r['seconds']:.0f}s" for _, r in others.values())
    print(f"checks ({checks['seconds']:.0f}s{secs}, touch band {'on' if P.TOUCH_BAR else 'off'}): "
          f"{len(problems)} problem(s)")
    for p in problems:
        print("  -", p)
    print(f"  screws reachable: {checks['access_ok']}/{len(info['screws'])}, "
          f"plugs insertable: {checks['insertion_ok']}/{len(info['plugs'])}")
    for name, c in info["cables"].items():
        if c["buy"]:
            print(f"  {name}: route {c['length']:.0f} mm"
                  + (f", lift needs {c['lift']:.0f} mm" if c["lift"] else "") + f" -> {c['buy']} mm")
    k = checks["keystack_rows"]
    for name, r in (("full", k), ("proto", checks.get("keystack_proto"))):
        if r:
            print(f"  cap guide ({name}): {P.KEY_GUIDE_CLEAR:g} mm per side over {r['guide_len']:.1f} mm -> "
                  f"max tilt {r['tilt_deg']:.2f}°, worst drop {r['drop']:.2f} mm (tilt + switch bottomed + "
                  f"down-stop), glass margin {r['margin']:.2f} mm of {r['glass_gap']:.2f} mm")
    print(f"  key stack: cap drop {k['drop']:.2f} + frame {k['defl_max']:.3f} mm/N x {k['force']:g} N = "
          f"{k['need']:.2f} mm of {k['glass_gap']:.2f} mm to the glass")
    print(slot_line(",".join(info["slots"]), checks["slot_rows"]))
    for cfg, (_, r) in others.items():
        print(slot_line(",".join(cfg), r["slot_rows"]) + f"; {r['access_ok']} slot screws reachable")
    infos = {cfg[0]: oi for cfg, (oi, _) in others.items()}
    if check_only:
        sys.exit(1 if problems else 0)
    if "--bom" in sys.argv:
        write_bom(info, pinfo, infos)
        sys.exit(0)

    import render
    OUT.mkdir(parents=True, exist_ok=True)
    scene = render.Scene(flat, tol=0.25)
    tscene = render.Scene(tilted, tol=0.25)
    shots = step_pictures(scene, flat, info, tscene)
    service = service_pictures(scene, flat, info)
    write_guide(info, checks, shots, service)
    write_bom(info, pinfo, infos)
    print(f"pictures + guide in {time.time() - t0:.0f}s")
    if "--animate" in sys.argv:
        t1 = time.time()
        n = animate(scene, tscene, info, OUT / "assembly.gif")
        print(f"animation: {n} frames in {time.time() - t1:.0f}s")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
