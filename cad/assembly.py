"""Assembly and service: steps, build checks, pictures, animation, and the guide.

    .venv/bin/python cad/assembly.py --check     # checks only (fast; CI)
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
- service: the top plate, display and knob board lift out in that order;
  a paperclip reaches the display board's BOOT/RESET through the back wall
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
from build123d import Box, Cylinder, Pos, Rot  # noqa: E402

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


KNOB_SUB = starts("knob_board_pcb", "knob_board_rp2040", "knob_board_conn", "cable_motor")


def knob_sub(lb):
    return KNOB_SUB(lb) or (lb.startswith("knob") and lb[4:5].isdigit()
                            and not lb.endswith("_knob"))


GH_LINK = starts("plug_usb_board_gh", "plug_knob_gh", "cable_usb_knob_gh")
DISPLAY_CABLE = starts("plug_display_usb", "plug_usb_board_display", "cable_usb_display")
TOP_SUB = starts("top_plate", "cap_", "frame_pcb", "switch_", "touch_bar", "knob_window",
                 "cable_keys", "cable_touch", "plug_ffc", "plug_touch_band", "plug_knob_touch")
# Plugs that stay on the knob board when the top plate lifts (their cable comes with the plate)
KNOB_SIDE = ("plug_ffc_knob", "plug_knob_touch")

STEPS = [
    Step("tray", "Print the case; fit magnets and front feet",
         "Print the tray, top plate and stand (all fit a 256 mm bed). Glue the four "
         "tray magnets into the pockets underneath (check polarity against the stand's "
         "magnets first) and stick the two rubber feet near the front edge.",
         starts("case_tray", "magnet_tray", "foot_front"), move=(0, 0, -25), view=(-60, -30),
         fixed=("case_tray",)),
    Step("usb_board", "Screw in the USB board",
         "Lower the USB board into the back-left corner, external USB-C socket first: the "
         "socket's face sits flush behind the opening in the back wall, the board's arm "
         "rests against the printed backstop, and its edge touches the back wall. Drive the "
         "four M2 screws into the floor bosses (two of them either side of the socket).",
         starts("usb_board"), move=(0, 0, 40), view=(-60, 40), screw_view=(-60, 45)),
    Step("knob_sub", "Build the knob board (on the bench)",
         "Glue a diametric magnet to the bottom end of each motor shaft. Screw each "
         "motor's base to its tongue on the knob board, centered over the MT6701, with its "
         "lead pointing back. Bond a printed hub to the top of each motor bell (epoxy, or M2 "
         "screws if the bell has holes). Plug each motor's 3-pin plug onto the header behind "
         "its tongue (any way round: the firmware finds the phase order), coil the spare "
         "lead flat on the back strip and strap it through the two slots with a hook-and-loop "
         "tie. Keep the lead clear of the bell. Calibrate each knob now, before it's buried "
         "in the case.",
         knob_sub, move=(0, 0, 35), bench=True, view=(120, 40)),
    Step("knob_board", "Screw the knob board into the tray; plug in the USB link",
         "Lower the knob board in with its back strip resting on the floor ribs, and "
         "screw it down along its front edge into the floor bosses (self-tapping, don't "
         "overtighten). Plug the JST-GH cable into the knob board's back-left corner and "
         "into the USB board (both click), and press it into its floor clip.",
         lambda lb: knob_sub(lb) or GH_LINK(lb), move=(0, 0, 40), view=(-60, 40),
         screw_view=(-60, 45)),
    Step("display", "Mount the display; plug in its USB cable",
         "Lay the panel face up on its four posts, then turn the tray on its side and drive "
         "the four M3 screws up from underneath into the panel's tabs. Plug the right-angle "
         "end of the USB-C cable into the display board's USB port (the one nearer the back; "
         "the cable points forward), loop it round in the bay and plug the straight end into "
         "the USB board. Press the cable into its two floor clips, clear of the knob board.",
         lambda lb: lb.startswith(("display_board", "panel7")) or DISPLAY_CABLE(lb),
         move=(0, 0, 45), view=(-60, 35), screw_view=(-60, -35)),
    Step("top_plate_sub", "Build the top plate (on the bench)",
         "Lay the top plate face down. Drop the clear caps into their holes, tabs toward "
         "the front edge. Plug the key cable (FFC) into the frame PCB's ZIF connector "
         "(flip the latch up, slide the cable in, latch down) before screwing the frame PCB "
         "onto the plate's bosses (switches facing the caps). Stick the touch band under the "
         "plate below the knob display windows and plug the touch cable into it.",
         TOP_SUB, move=(0, 0, -35), bench=True, view=(-60, -40), screw_view=(-60, -40)),
    Step("close", "Close the case",
         "Hold the top plate above the tray (its cables reach with the plate ~40 mm up). "
         "Plug the key cable into the knob board's ZIF connector at its right end and the "
         "touch cable into the header beside it; the spare cable folds into the gap by the "
         "right wall. Lower the top plate over the knob hubs, then drive the four M3 screws "
         "up from underneath into its posts.",
         TOP_SUB, move=(0, 0, 50), view=(-60, 35), screw_view=(-60, -35)),
    Step("knobs", "Press on the knob caps",
         "Press each knob cap onto its hub. They pull straight off for service.",
         lambda lb: lb.startswith("knob") and lb.endswith("_knob"), move=(0, 0, 30),
         view=(-60, 35)),
    Step("stand", "Put it on the stand",
         "Glue the stand's magnets in (opposite polarity to the tray's) and stick its four "
         "feet on. The slab snaps onto the stand with the magnets.",
         starts("stand", "magnet_stand", "foot_stand"), move=(0, 40, -40), view=(-62, 20),
         tilted=True),
    Step("plug_in", "Plug it in",
         "Plug a USB-C cable from the computer into the port in the back wall. A C-to-C "
         "cable lets the device see how much current the port offers; an A-to-C cable "
         "works too, with weaker haptics (500 mA budget).",
         starts("plug_usb_ext", "cable_usb_ext"), move=(0, 30, 27), view=(115, 28), tilted=True),
]


def step_of(lb, flat_labels):
    for s in STEPS:
        if not s.tilted and s.parts(lb) and not lb.startswith("screw_"):
            if s.key == "knob_sub":
                continue                      # bench step; installed in "knob_board"
            if s.key == "top_plate_sub":
                continue                      # bench step; installed in "close"
            return s.key
    return None


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------
def vol(a, b):
    try:
        r = a & b
        return r.volume if r is not None else 0.0
    except Exception:
        return 0.0


def bbox_overlap(b1, b2, eps=0.01):
    return (b1.min.X < b2.max.X - eps and b2.min.X < b1.max.X - eps and
            b1.min.Y < b2.max.Y - eps and b2.min.Y < b1.max.Y - eps and
            b1.min.Z < b2.max.Z - eps and b2.min.Z < b1.max.Z - eps)


def check_interference(items, screws):
    allowed = {(sc.label, sc.target) for sc in screws}
    parts = [it for it in items if not it.label.startswith(OVERLAYS + ("cable_",))]
    bbs = [it.part.bounding_box() for it in parts]
    problems = []
    for i in range(len(parts)):
        for j in range(i + 1, len(parts)):
            a, b = parts[i], parts[j]
            if (a.label, b.label) in allowed or (b.label, a.label) in allowed:
                continue
            if not bbox_overlap(bbs[i], bbs[j]):
                continue
            v = vol(a.part, b.part)
            if v > 0.01:
                problems.append(f"{a.label} overlaps {b.label} ({v:.2f} mm³)")
    return problems


def present_at(step_key, items):
    """Labels physically present when `step_key`'s screws go in."""
    labels = {it.label for it in items}
    if step_key == "top_plate_sub":
        return {lb for lb in labels if TOP_SUB(lb) and not lb.startswith("cable_")}
    if step_key == "knob_sub":
        return {lb for lb in labels if knob_sub(lb) and not lb.startswith("cable_")}
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
    by = {it.label: it for it in items}
    probs = []
    for x, wall_y, z, name in info["pinholes"]:
        oy1 = info["outer"][3]
        reach = by["display_board_buttons"].part.bounding_box().max.Y - 0.5
        clip = Pos(x, (oy1 + 15 + reach) / 2, z) * Rot(X=90) * Cylinder(0.5, oy1 + 15 - reach)
        hits = [lb for lb, it in by.items()
                if not lb.startswith(OVERLAYS + ("cable_",)) and lb != "display_board_buttons"
                and bbox_overlap(clip.bounding_box(), it.part.bounding_box())
                and vol(clip, it.part) > 0.001]
        if hits:
            probs.append(f"paperclip to {name} blocked by {', '.join(hits)}")
        if vol(Pos(0, -1.0, 0) * clip, by["display_board_buttons"].part) <= 0:
            probs.append(f"paperclip through the {name} hole doesn't reach the button")
    return probs


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


def check_insertion(items, info):
    """Each plug slides straight in along its socket's axis at the step that connects it."""
    by = {it.label: it for it in items}
    plugs = info["plugs"]
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
        ends[f"cable_motor{n}"] = {f"knob{n}_motor_2204", f"knob{n}_motor_plug", f"knob{n}_header"}
        ends[f"cable_motor{n}_coil"] = set()
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


def run_checks(items, info):
    screws = info["screws"]
    labels = {it.label for it in items}
    t = time.time()
    res = {}
    res["interference"] = check_interference(items, screws)
    res["access"], res["access_ok"] = check_access(items, screws)
    res["insertion"], res["insertion_ok"] = check_insertion(items, info)
    res["cables"] = check_cables(items, info)
    plate = [lb for lb in labels if TOP_SUB(lb) and not lb.startswith("cable_") and lb not in KNOB_SIDE]
    plate += [s.label for s in screws if s.step == "top_plate_sub"]
    caps = [lb for lb in labels if lb.startswith("knob") and lb.endswith("_knob")]
    rest = [lb for lb in labels if lb not in plate and lb not in caps
            and not lb.startswith(OVERLAYS + ("cable_", "screw_plate", "plug_usb_ext"))]
    res["service"] = check_lift(items, plate, rest, "top plate lift-off")
    rest = [lb for lb in rest if not lb.startswith("plug_")]     # unplugged before lifting more out
    display = [lb for lb in labels if lb.startswith(("display_board", "panel7_module"))]
    rest2 = [lb for lb in rest if lb not in display and not lb.startswith("screw_panel")]
    res["service"] += check_lift(items, display, rest2, "display lift-out")
    knobs = [lb for lb in labels if knob_sub(lb)]
    rest3 = [lb for lb in rest2 if lb not in knobs and not lb.startswith("screw_knobboard")]
    res["service"] += check_lift(items, knobs, rest3, "knob board lift-out")
    res["pinholes"] = check_pinholes(items, info)
    res["problems"] = (res["interference"] + res["access"] + res["insertion"] + res["cables"]
                       + res["service"] + res["pinholes"])
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
        if s.tilted or s.key in ("knob_sub", "top_plate_sub"):
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
    "cable_usb_knob_gh": ("JST-GH 1.25 mm 8-pin, plugs both ends, pin 1 to pin 1 (\"same direction\")",
                          "USB board ↔ knob board"),
    "cable_keys_ffc": ("FFC, 12-pin, 1.0 mm pitch, contacts on opposite sides (type B)",
                       "frame PCB ↔ knob board"),
    "cable_touch": ("JST-SH 1.0 mm 6-pin, plugs both ends, pin 1 to pin 1",
                    "touch band ↔ knob board"),
}
STEP_OF_CABLE = {"cable_usb_display": "display", "cable_usb_knob_gh": "knob_board",
                 "cable_keys_ffc": "top_plate_sub", "cable_touch": "top_plate_sub"}


def write_guide(info, checks, shots, service):
    screws = info["screws"]
    counts = {}
    for sc in screws:
        kind = sc.kind + (" self-tapping" if sc.target in ("case_tray", "top_plate") else " machine")
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
        "## Build checks",
        "",
        "Run on every build of this guide (`.venv/bin/python cad/assembly.py --check`).",
        "",
        "| Check | Result |",
        "|---|---|",
        f"| Parts don't overlap in the finished device | {status(checks['interference'], 'no overlaps')} |",
        f"| Every screw reachable with a straight screwdriver at its step | "
        f"{status(checks['access'], str(checks['access_ok']) + ' of ' + str(len(screws)) + ' screws reachable')} |",
        f"| Every plug slides straight into its socket at its step (plug bodies modeled at "
        f"full size: USB-C overmold {P.USB_PLUG_STRAIGHT[0]:g}×{P.USB_PLUG_STRAIGHT[1]:g} mm) | "
        f"{status(checks['insertion'], str(checks['insertion_ok']) + ' of ' + str(len(info['plugs'])) + ' plugs')} |",
        f"| Cables clear every part (motor bells included); bends ≥ {P.USB_BEND_R:g} mm on the "
        f"USB-C cable; plate cables reach with the plate lifted {P.LIFT_SERVICE:g} mm | "
        f"{status(checks['cables'], 'all clear')} |",
        f"| Service: top plate, then display, then knob board lift straight out | "
        f"{status(checks['service'], 'all three lift out')} |",
        f"| A paperclip reaches BOOT and RESET through the back wall | "
        f"{status(checks['pinholes'], 'both reachable')} |",
        "",
        "## Hardware",
        "",
        "| Part | Qty | Used in step |",
        "|---|---|---|",
        hw_rows,
        f"| Motor mounting screws (usually supplied with the 2204; check length vs the 1.6 mm board) | 5 sets | {num['knob_sub']} |",
        f"| Hook-and-loop cable ties, ~10 mm wide (strap each motor lead coil through its two slots) | 5 | {num['knob_sub']} |",
        f"| Magnets {P.MAGNET_TRAY[0]:g}×{P.MAGNET_TRAY[1]:g} mm (tray) | 4 | {num['tray']} |",
        f"| Magnets {P.MAGNET_STAND[0]:g}×{P.MAGNET_STAND[1]:g} mm (stand) | 4 | {num['stand']} |",
        f"| Rubber feet {P.FOOT[0]:g}×{P.FOOT[1]:g} mm | 6 | {num['tray']}, {num['stand']} |",
        f"| Epoxy | — | knob hubs, magnets |",
        "",
        "Self-tapping screws go into printed plastic: drive them slowly and stop when snug.",
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
        f"| Motor leads (on the motors) | motor ↔ knob board header | {P.MOTOR_LEAD_LEN:.0f} mm assumed | "
        f"~{max(v['routed'] for v in info['leads'].values()):.0f} mm routed; the rest coils on the back strip "
        f"({max(v['coil_h'] for v in info['leads'].values()):.1f} mm high, "
        f"{min(v['room'] for v in info['leads'].values()):.1f} mm room) | {num['knob_sub']} |",
        "",
        "Pinouts and the strain-relief measures: [wiring.md](wiring.md). Every part with",
        "sources: [bom.md](bom.md).",
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
        "2. Pull the five knob caps straight up.",
        "3. Undo the four M3 screws under the tray (the top plate's posts).",
        "4. Lift the top plate straight up, with the caps, frame PCB and touch band on it.",
        f"   Its two cables reach {P.LIFT_SERVICE:.0f} mm; at that height unplug them at the knob",
        "   board's right end (flip the ZIF latch up to free the key cable; pull the touch",
        "   plug straight up).",
        "",
        f"![Top plate lifted off](../cad/out/assembly/{service['open']})",
        "",
        "### Swap a key cap or switch",
        "",
        "With the top plate off and face down, undo the frame PCB's screws, lift the PCB",
        "and replace the cap or switch.",
        "",
        "### Recover the display board's firmware",
        "",
        "No need to open the case: press BOOT (hold) and RESET through the two small holes",
        "in the back wall with a paperclip, then flash over USB.",
        "",
        f"![Back wall pinholes](../cad/out/assembly/{service['pinholes']})",
        "",
        "### Recover the knob board's firmware",
        "",
        "The knob board has its own USB connection through the hub, so the host app reboots",
        "it into the RP2350B's built-in bootloader and copies a UF2 file. If the firmware is",
        "too broken for that, open the case, hold the BOOTSEL button on the knob board and",
        "unplug/replug the USB cable at the back: it shows up as a USB drive.",
        "",
        "### Replace a motor or the knob board",
        "",
        "Open the case. Unplug the USB-C cable at the display board, remove the display",
        "(four M3 screws from underneath), unplug the JST-GH cable at the knob board (press",
        "the latch), then undo the knob board's screws along its front edge and lift it out.",
        "Its back strip sits under the display, which is why the display comes out first.",
        "A motor unplugs from its header; cut its hook-and-loop tie free.",
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


BOM_JLC_BOARDS = [
    # qty, part, spec, source, ~price, used in
    ("1 panel", "PCBs: knob board, frame PCB, touch band, USB board, panelized",
     "2-layer FR-4 1.6 mm, ENIG or HASL; outlines from `cad/out/*.dxf`. JLC makes 5 panels "
     "and assembles at least 2", "JLCPCB", "in the board lines of cost.md", "all boards"),
]
BOM_JLC_PARTS = [
    # Knob board
    ("1", "RP2350B", "QFN-80 microcontroller, 48 GPIO, native USB; + 16 MB QSPI flash, 12 MHz crystal",
     "LCSC (look up in JLC's library) (V)", "$2–3", "knob board"),
    ("5", "TMC6300-LA-T", "3-phase motor driver, 2–11 V", lcsc("C5274455") + " (200 in stock, 2026-10-17)",
     "~$26", "knob board"),
    ("5", "MT6701QT-STD", "magnetic angle sensor, SSI", lcsc("C2913974"), "~$5", "knob board"),
    ("5", "SN74LVC3G04DCTR", "triple inverter (3-PWM drive)", lcsc("C139324"), "~$1", "knob board"),
    ("5", "B3U-1000P", "knob press switch (underside of each tongue)", lcsc("C231329"), "~$2", "knob board"),
    ("5", "1×3 right-angle pin header, 2.54 mm", "motor plug sockets (must match the motor's plug)",
     lcsc("C2886703") + " (V: confirm male pins)", "~$0.5", "knob board"),
    ("1", "JST SM08B-GHS-TB", "8-pin GH header, side entry, latching (USB link)", lcsc("C265111"), "~$0.5",
     "knob board"),
    ("1", "FFC/FPC connector, 12-pin 1.0 mm, flip-lock ZIF, right angle",
     "e.g. XUNPU FPC-1.0FX-12PWCR-H20 (V: contact side, height)", lcsc("C19269355"), "~$0.2", "knob board"),
    ("1", "JST BM06B-SRSS-TB", "6-pin SH header, top entry (touch cable)", lcsc("C160392"), "~$0.2",
     "knob board"),
    ("1 set", "Knob board passives", "load switch (soft start), ~470 µF bulk, decoupling, 3.3 V regulator,"
     " BOOTSEL button, CC sense filters", "JLC basic parts", "$3–5", "knob board"),
    # Frame PCB
    ("21", "B3U-1000P", "key switches", lcsc("C231329"), "~$8", "frame PCB"),
    ("21", "1N4148W", "SOD-123 matrix diodes", "JLC basic part", "~$0.5", "frame PCB"),
    ("1", "FFC/FPC connector, 12-pin 1.0 mm, flip-lock ZIF", "same as on the knob board",
     lcsc("C19269355"), "~$0.2", "frame PCB"),
    # Touch band
    ("1", "Touch controller", "capacitive slider controller, I²C (part not chosen yet)", "LCSC (V)",
     "$0.5–2", "touch band"),
    ("1", "JST SM06B-SRSS-TB", "6-pin SH header, side entry", "JLC C160405", "~$0.2", "touch band"),
    # USB board
    ("1", "WCH CH334F", "4-port USB 2.0 hub, QFN-24, no crystal needed",
     lcsc("C5187527") + " (8,489 in stock, $0.63, 2026-10-17)", "~$0.6", "USB board"),
    ("1", "USB-C receptacle, 16-pin, mid-mount (sinks 1.6 mm into the board)",
     "external port; HCTL HC-TYPE-C-16P-CB1.6 (V: through-hole shell legs, protrusion)",
     lcsc("C2894902") + "; fallback top-mount TYPE-C-31-M-12 " + lcsc("C165948"), "~$0.2", "USB board"),
    ("1", "USB-C receptacle, 16-pin, TYPE-C-31-M-12", "internal port to the display board; SMD signals, "
     "4 through-hole shell legs", lcsc("C165948"), "~$0.2", "USB board"),
    ("1", "JST SM08B-GHS-TB", "8-pin GH header (USB link to the knob board)", lcsc("C265111"), "~$0.5",
     "USB board"),
    ("1", "SY6280AAC", "current-limited power switch for the display board's port", lcsc("C55136") + " (V: limit)",
     "~$0.1", "USB board"),
    ("1", "USBLC6-2SC6", "USB ESD protection, external port", lcsc("C7519"), "~$0.1", "USB board"),
    ("1 set", "USB board passives", "5.1 kΩ CC pull-downs ×2, 56 kΩ CC pull-ups ×2 (display port), "
     "10 kΩ CC sense resistors ×2, TVS, decoupling", "JLC basic parts", "~$0.5", "USB board"),
]
BOM_PRINTS = [
    ("21", "Clear key caps", "`cad/out/key_cap_clear_resin.stl`, clear resin (SLA)", "JLC3DP", "$20–40",
     "Build the top plate"),
    ("1", "Case tray", "`cad/out/print_case_tray.stl`; the cable clips are part of it", "home printer or JLC3DP",
     "$4–6 / $20–40", "Print the case"),
    ("1", "Top plate", "`cad/out/print_top_plate.stl`", "home printer or JLC3DP", "$3–5 / $15–30",
     "Print the case"),
    ("1", "Stand", "`cad/out/print_stand.stl`", "home printer or JLC3DP", "$3–5 / $10–25", "Put it on the stand"),
    ("5", "Knob caps", "`cad/out/knob.stl`", "home printer or JLC3DP", "$1–5", "Press on the knob caps"),
    ("5", "Knob hubs", f"{P.KNOB_HUB_D:g} mm hubs bonded to the motor bells (model: `knobN_hub`)",
     "home printer or JLC3DP", "<$1", "Build the knob board"),
]
BOM_ALI = [
    ("1", "Waveshare ESP32-S3-LCD-7B (non-touch, SKU 31727)", "7\" 1024×600 display board", "Waveshare",
     "$34", "Mount the display"),
    ("5", "2204 gimbal motor (Mitoot 2204 260KV or similar)", "~28 × 13 mm, hollow shaft; lead ~30 cm with a "
     "3-pin 2.54 mm servo-style (Futaba/JR) plug per one listing (V: check plug and lead on arrival)",
     "AliExpress", "$40–60", "Build the knob board"),
    ("5", "Diametric magnets 6 × 2.5 mm", "for the MT6701 sensors", "AliExpress", "~$5", "Build the knob board"),
]
BOM_EXTERNAL = [
    ("1", "USB-C to USB-C cable (to the computer)", "USB 2.0 is enough; a C-to-C cable lets the device read "
     "the port's 1.5 A / 3 A offer. An A-to-C cable works, with weaker haptics (500 mA). Plug overmold "
     f"≤ {P.USB_EXT_POCKET[0] - 0.5:g} × {P.USB_EXT_POCKET[1] - 0.5:g} mm to seat in the back-wall opening",
     "any", "$3–8", "Plug it in"),
]


def write_bom(info):
    screws = info["screws"]
    num = {s.key: s.title for s in STEPS}
    counts = {}
    for sc in screws:
        kind = sc.kind + (" self-tapping (for plastic)" if sc.target in ("case_tray", "top_plate")
                          else " machine")
        counts.setdefault(kind, {})
        counts[kind][sc.step] = counts[kind].get(sc.step, 0) + 1
    price = {"cable_usb_display": "$2–4", "cable_usb_knob_gh": "$1–2", "cable_keys_ffc": "$0.5–1",
             "cable_touch": "$0.5–1"}

    def table(rows):
        out = ["| Qty | Part | Spec | Source / LCSC # | ~Price | Used in |", "|---|---|---|---|---|---|"]
        out += [f"| {q} | {p} | {sp} | {src} | {pr} | {u} |" for q, p, sp, src, pr, u in rows]
        return out

    cable_rows = [("1", CABLES[n][0].split(",")[0], CABLES[n][0].split(",", 1)[1].strip()
                   + f"; **{c['buy']} mm** (model route {c['length']:.0f} mm"
                   + (f", {c['lift']:.0f} mm with the plate lifted" if c["lift"] else "") + ")",
                   "AliExpress (search the spec)", price[n], num[STEP_OF_CABLE[n]])
                  for n, c in info["cables"].items() if c["buy"]]
    hw_rows = [(str(sum(st.values())), f"{kind.split()[0]} screw", " ".join(kind.split()[1:]),
                "hardware kit", "", ", ".join(num[k] for k in st)) for kind, st in counts.items()]
    hw_rows += [
        ("4", f"Magnets {P.MAGNET_TRAY[0]:g} × {P.MAGNET_TRAY[1]:g} mm", "tray", "AliExpress", "~$1",
         num["tray"]),
        ("4", f"Magnets {P.MAGNET_STAND[0]:g} × {P.MAGNET_STAND[1]:g} mm", "stand", "AliExpress", "~$1",
         num["stand"]),
        ("6", f"Rubber feet {P.FOOT[0]:g} × {P.FOOT[1]:g} mm", "self-adhesive", "AliExpress", "~$1",
         f"{num['tray']}, {num['stand']}"),
        ("5", "Hook-and-loop cable ties", "~10 mm wide, reusable; strap the motor lead coils",
         "AliExpress", "~$1", num["knob_sub"]),
        ("5 sets", "Motor mounting screws", "usually supplied with the motors (check length)", "with the motors",
         "", num["knob_sub"]),
        ("—", "Epoxy", "knob hubs, magnets", "any", "~$3", f"{num['knob_sub']}, {num['tray']}"),
    ]
    lines = [
        "# Bill of materials (full build)",
        "",
        "> [!CAUTION]",
        "> Generated by `cad/assembly.py` from the CAD model; nothing has been built or",
        "> ordered. **(V)** marks parts to verify before ordering. LCSC numbers were looked up",
        "> on 2026-10-17; stock moves, so check each one in JLC's parts library when ordering.",
        "",
        "Everything a builder buys for one device, grouped by order. The builder solders and",
        "crimps nothing: JLC fits every board-mounted part, and every cable is bought ready-made.",
        "Screws, cable types and lengths come from the model, so they match",
        "[assembly.md](assembly.md). Totals: [cost.md](cost.md).",
        "",
        "## Order 1: JLC (PCBs, assembly, prints)",
        "",
        "### PCBs",
        "",
        *table(BOM_JLC_BOARDS),
        "",
        "### Parts JLC fits (per device)",
        "",
        *table(BOM_JLC_PARTS),
        "",
        "JLC's assembly minimum is 2 boards, so you pay for the parts on a spare set too",
        "(see [cost.md](cost.md)). JLC charges a setup fee once for the panel, plus a fee per",
        "\"extended\" part type.",
        "",
        "### 3D prints",
        "",
        *table(BOM_PRINTS),
        "",
        "## Order 2: AliExpress / Waveshare",
        "",
        "### Bought parts",
        "",
        *table(BOM_ALI),
        "",
        "### Internal cables (ready-made, plug-in)",
        "",
        *table(cable_rows),
        "",
        "Search terms that find them: \"USB C to USB C 90 degree 10cm\" (pick a side-angle "
        "(left/right) plug for the display end, not up/down); \"JST GH 1.25 8 pin double head "
        "cable 10cm\" (same direction); \"FFC 12 pin 1.0mm 80mm\" (reverse/opposite side); "
        "\"JST SH 1.0 6 pin double head 10cm\".",
        "",
        "### Hardware",
        "",
        *table(hw_rows),
        "",
        "## Not in the kit",
        "",
        *table(BOM_EXTERNAL),
        "",
        "## Totals",
        "",
        "One device: **~$300–450** with your own 3D printer, ~$330–525 with the case from",
        "JLC3DP, ~$195–370 each when 5 people order together. Prices above are per-part",
        "guides; the totals in [cost.md](cost.md) also include JLC's PCB, setup and",
        "extended-part fees, the spare assembled board set, and shipping.",
        "",
    ]
    BOM_PATH.write_text("\n".join(lines) + "\n")


def main():
    check_only = "--check" in sys.argv
    t0 = time.time()
    flat, L, info = model.full_device(tilt=False)
    checks = run_checks(flat, info)
    problems = checks["problems"]
    print(f"checks ({checks['seconds']:.0f}s): {len(problems)} problem(s)")
    for p in problems:
        print("  -", p)
    print(f"  screws reachable: {checks['access_ok']}/{len(info['screws'])}, "
          f"plugs insertable: {checks['insertion_ok']}/{len(info['plugs'])}")
    for name, c in info["cables"].items():
        if c["buy"]:
            print(f"  {name}: route {c['length']:.0f} mm"
                  + (f", lift needs {c['lift']:.0f} mm" if c["lift"] else "") + f" -> {c['buy']} mm")
    if check_only:
        sys.exit(1 if problems else 0)
    if "--bom" in sys.argv:
        write_bom(info)
        sys.exit(0)

    import render
    OUT.mkdir(parents=True, exist_ok=True)
    scene = render.Scene(flat, tol=0.25)
    tilted, _, _ = model.full_device(tilt=True)
    tscene = render.Scene(tilted, tol=0.25)
    shots = step_pictures(scene, flat, info, tscene)
    service = service_pictures(scene, flat, info)
    write_guide(info, checks, shots, service)
    write_bom(info)
    print(f"pictures + guide in {time.time() - t0:.0f}s")
    if "--animate" in sys.argv:
        t1 = time.time()
        n = animate(scene, tscene, info, OUT / "assembly.gif")
        print(f"animation: {n} frames in {time.time() - t1:.0f}s")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
