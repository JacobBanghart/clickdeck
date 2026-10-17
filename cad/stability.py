"""Rough tipping check for the angled device.

Estimates mass and center of mass from the CAD volumes with rough densities,
then the force on a top-row key (pressing straight into the face) that
would tip the device backward over the stand's rear edge. All densities are
guesses; printed parts depend on infill. Treat the result as a sanity check.
"""

import math

import params as P

# g/cm^3 by label prefix (first match wins). Printed parts ~ 25% infill + walls.
DENSITY = [
    ("panel7_module", 1.9),        # glass + backlight + steel frame, ~180 g
    ("display_board", 1.9),
    ("knob", 0.0),                 # handled below (motors) / small
    ("cap_", 1.2),                 # clear resin
    ("frame_pcb", 1.85), ("touch_bar", 1.85),
    ("case_tray", 0.75), ("top_plate", 1.0),
    ("stand", 0.9),                # shelled stand: its CAD volume is mostly walls and ribs (PETG ~1.27 solid)
    ("panel_post", 1.24), ("display_standoff", 7.8),
]
MOTOR_G = 24.0                     # Mitoot 2204 listing
CABLE_PULL_N = 4.0                 # a horizontal tug on the USB cable, backward
KEY_PRESS_N = 3.0                  # a firm press


def density(label: str) -> float:
    for prefix, d in DENSITY:
        if label.startswith(prefix):
            return d
    return 0.0


def check(items, layout, info) -> dict:
    mass = 0.0
    my = mz = 0.0
    for it in items:
        if "_motor_2204" in it.label:
            m = MOTOR_G
        else:
            d = density(it.label)
            if d == 0:
                continue
            m = it.part.volume / 1000.0 * d
        c = it.part.center()
        mass += m
        my += m * c.Y
        mz += m * c.Z
    yc, zc = my / mass, mz / mass

    # Tipping edge: the rear stand feet's contact patches (back edge of the rubber)
    y_rear = max(it.part.bounding_box().max.Y for it in items if it.label.startswith("foot_stand"))
    th = math.radians(P.TILT_DEG)

    # Top-row key center, in the tilted frame: find the cap with the largest z
    caps = [it.part.center() for it in items if it.label.startswith("cap_")]
    top = max(caps, key=lambda c: c.Z)
    # Press force F along -normal: horizontal F*sin(th) backward at height z,
    # vertical F*cos(th) downward at y.
    w = mass / 1000.0 * 9.81
    resist = w * (y_rear - yc)
    lever = math.sin(th) * top.Z - math.cos(th) * (y_rear - top.Y)
    tip_force = resist / lever if lever > 0 else float("inf")
    # Horizontal backward pull on the USB plug (back wall, tilted) about the same edge
    plug = next((it.part.center() for it in items if it.label == "plug_usb_ext"), None)
    pull_n = resist / plug.Z if plug is not None and plug.Z > 0 else float("inf")
    stand_g = next(it.part.volume for it in items if it.label == "stand") / 1000.0 * density("stand")
    return {"mass_g": mass, "tip_force_n": tip_force, "press_n": KEY_PRESS_N,
            "cable_pull_n": pull_n, "stand_g": stand_g}
