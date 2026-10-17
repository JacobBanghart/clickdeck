"""Assembly and service: steps, build checks, pictures, animation, and the guide.

    .venv/bin/python cad/assembly.py --check     # checks only (fast; CI)
    .venv/bin/python cad/assembly.py             # checks + step pictures + guide
    .venv/bin/python cad/assembly.py --animate   # also the animation (slow, ~15 min)

Writes cad/out/assembly/*.png, the animation, and docs/assembly.md. The
pictures come from the same model the checks run on, so a step that can't be
built shows up as a failed check, not just a wrong picture.

Checks:
- interference: no two parts overlap in the finished device (except screws
  threading into their target part)
- tool access: every screw can be reached with a straight screwdriver at the
  step that installs it
- service: the top plate, display and knob board lift out in that order;
  a paperclip reaches the display board's BOOT/RESET through the back wall
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


KNOB_SUB = starts("knob_board_pcb", "knob_board_rp2040", "knob_board_connectors")


def knob_sub(lb):
    return KNOB_SUB(lb) or (lb.startswith("knob") and lb[4:5].isdigit()
                            and not lb.endswith("_knob"))


TOP_SUB = starts("top_plate", "cap_", "frame_pcb", "switch_", "touch_bar", "knob_window",
                 "cable_keys", "cable_touch")

STEPS = [
    Step("tray", "Print the case; fit magnets and front feet",
         "Print the tray, top plate and stand (all fit a 256 mm bed). Glue the four "
         "tray magnets into the pockets underneath (check polarity against the stand's "
         "magnets first) and stick the two rubber feet near the front edge.",
         starts("case_tray", "magnet_tray", "foot_front"), move=(0, 0, -25), view=(-60, -30),
         fixed=("case_tray",)),
    Step("knob_sub", "Build the knob board (on the bench)",
         "Glue a diametric magnet to the bottom end of each motor shaft. Screw each "
         "motor's base to its tongue on the knob board, centered over the MT6701. Bond a "
         "printed hub to the top of each motor bell (epoxy, or M2 screws if the bell has "
         "holes). Calibrate each knob now, before it's buried in the case.",
         knob_sub, move=(0, 0, 35), bench=True, view=(-60, 35)),
    Step("knob_board", "Screw the knob board into the tray",
         "Lower the knob board in with its back strip resting on the floor ribs, and "
         "screw it down along its front edge into the floor bosses (self-tapping, don't "
         "overtighten). Plug the link, reset and power cable into the knob board.",
         knob_sub, move=(0, 0, 40), view=(-60, 40), screw_view=(-60, 45)),
    Step("display", "Mount the display",
         "On Waveshare's board, set the UART2/UART1 slide switch to UART2 and plug in the "
         "link, reset and power cable (UART2, GPIO and POWER connectors). Lay the panel "
         "face up on its four posts, then turn the tray on its side and drive the four M3 "
         "screws up from underneath into the panel's tabs.",
         starts("display_board", "panel7", "cable_link"), move=(0, 0, 45),
         view=(-60, 35), screw_view=(-60, -35)),
    Step("top_plate_sub", "Build the top plate (on the bench)",
         "Lay the top plate face down. Drop the clear caps into their holes, tabs toward "
         "the front edge. Screw the frame PCB onto the plate's bosses (switches facing the "
         "caps). Stick the touch band under the plate below the knob display windows and "
         "plug its cable and the key cable (FFC) into it and the frame PCB.",
         TOP_SUB, move=(0, 0, -35), bench=True, view=(-60, -40), screw_view=(-60, -40)),
    Step("close", "Close the case",
         "Plug the key cable and the touch cable into the knob board. Lower the top plate "
         "over the knob hubs, then drive the four M3 screws up from underneath into its "
         "posts.",
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
        return {lb for lb in labels if TOP_SUB(lb)}
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


def run_checks(items, info):
    screws = info["screws"]
    labels = {it.label for it in items}
    t = time.time()
    res = {}
    res["interference"] = check_interference(items, screws)
    res["access"], res["access_ok"] = check_access(items, screws)
    plate = [lb for lb in labels if TOP_SUB(lb) and not lb.startswith("cable_")]
    plate += [s.label for s in screws if s.step == "top_plate_sub"]
    caps = [lb for lb in labels if lb.startswith("knob") and lb.endswith("_knob")]
    rest = [lb for lb in labels if lb not in plate and lb not in caps
            and not lb.startswith(OVERLAYS + ("cable_", "screw_plate"))]
    res["service"] = check_lift(items, plate, rest, "top plate lift-off")
    display = [lb for lb in labels if lb.startswith(("display_board", "panel7_module"))]
    rest2 = [lb for lb in rest if lb not in display and not lb.startswith("screw_panel")]
    res["service"] += check_lift(items, display, rest2, "display lift-out")
    knobs = [lb for lb in labels if knob_sub(lb)]
    rest3 = [lb for lb in rest2 if lb not in knobs and not lb.startswith("screw_knobboard")]
    res["service"] += check_lift(items, knobs, rest3, "knob board lift-out")
    res["pinholes"] = check_pinholes(items, info)
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
            others = [lb for lb in tilted_scene.labels() if lb not in new
                      and not lb.startswith(("cable_",))]
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


def animate(scene, tilted_scene, info, path_gif, size=(720, 470), frames_move=10, frames_hold=3):
    """Assembly animation: parts fly in step by step, then the slab tilts onto the stand."""
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
    frames[0].save(path_gif, save_all=True, append_images=frames[1:], duration=90, loop=0,
                   optimize=True)
    return len(frames)


# --------------------------------------------------------------------------
# Guide
# --------------------------------------------------------------------------
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
    cab = info["cables"]
    cable_rows = "\n".join(
        f"| {name} | ~{math.ceil((length + 30) / 10) * 10} mm |" for name, length in cab.items())

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
        "## Build checks",
        "",
        "Run on every build of this guide (`.venv/bin/python cad/assembly.py --check`).",
        "",
        "| Check | Result |",
        "|---|---|",
        f"| Parts don't overlap in the finished device | {status(checks['interference'], 'no overlaps')} |",
        f"| Every screw reachable with a straight screwdriver at its step | "
        f"{status(checks['access'], str(checks['access_ok']) + ' of ' + str(len(screws)) + ' screws reachable')} |",
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
        "Lengths from the model's routing plus ~30 mm slack, rounded up.",
        "",
        "| Cable | Length |",
        "|---|---|",
        cable_rows,
        "",
        "`cable_link` is three HY2.0 leads (UART2 4-pin, GPIO 3-pin, POWER 2-pin) bundled;",
        "`cable_keys_ffc` is a 12-pin 1.0 mm FFC; `cable_touch` is a 6-pin JST-SH lead.",
        "Pinouts: [wiring.md](wiring.md).",
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
        "4. Lift the top plate straight up, with the caps, frame PCB and touch band on it,",
        "   and unplug the key and touch cables from the knob board.",
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
        "Normally the display board updates it over the link cable. If that fails, open",
        "the case: the knob board's recovery USB pads and BOOTSEL button are at its left",
        "end.",
        "",
        "### Replace a motor or the knob board",
        "",
        "Open the case, remove the display (four M3 screws from underneath, unplug the",
        "link cable), then undo the knob board's screws along its front edge and lift it",
        "out. Its back strip sits under the display, which is why the display comes out",
        "first.",
        "",
    ]
    GUIDE.write_text("\n".join(lines) + "\n")


def main():
    check_only = "--check" in sys.argv
    t0 = time.time()
    flat, L, info = model.full_device(tilt=False)
    checks = run_checks(flat, info)
    problems = checks["interference"] + checks["access"] + checks["service"] + checks["pinholes"]
    print(f"checks ({checks['seconds']:.0f}s): {len(problems)} problem(s)")
    for p in problems:
        print("  -", p)
    print(f"  screws reachable: {checks['access_ok']}/{len(info['screws'])}")
    if check_only:
        sys.exit(1 if problems else 0)

    import render
    OUT.mkdir(parents=True, exist_ok=True)
    scene = render.Scene(flat, tol=0.25)
    tilted, _, _ = model.full_device(tilt=True)
    tscene = render.Scene(tilted, tol=0.25)
    shots = step_pictures(scene, flat, info, tscene)
    service = service_pictures(scene, flat, info)
    write_guide(info, checks, shots, service)
    print(f"pictures + guide in {time.time() - t0:.0f}s")
    if "--animate" in sys.argv:
        t1 = time.time()
        n = animate(scene, tscene, info, OUT / "assembly.gif")
        print(f"animation: {n} frames in {time.time() - t1:.0f}s")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
