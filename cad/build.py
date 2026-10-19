"""Build every model and export it.

    .venv/bin/python cad/build.py            # STEP + DXF + STL + previews
    .venv/bin/python cad/build.py --no-render
    .venv/bin/python cad/build.py --no-render --strict   # fail on fit warnings (CI)

Outputs go to cad/out/:
  *.step      full assemblies with colors; open in FreeCAD or Fusion 360
  *.dxf       2D outlines: frame PCB (import into KiCad as Edge.Cuts) and
              laser-cut plates (SendCutSend/Ponoko accept DXF)
  *.stl       single parts for JLC3DP (clear resin caps)
  *.png       quick preview renders
"""

import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from build123d import (Align, BoundBox, Box, Compound, Cylinder, ExportDXF, Pos, Rectangle, Rot, Unit,  # noqa: E402
                       export_step, export_stl)

import model  # noqa: E402
import params as P  # noqa: E402

OUT = Path(__file__).parent / "out"


def to_compound(items, label):
    parts = []
    for it in items:
        p = it.part
        p.label = it.label
        p.color = it.color
        parts.append(p)
    return Compound(children=parts, label=label)


def exploded_offsets(items, normal=(0.0, 0.0, 1.0)):
    """Move parts apart along the slab normal (straight up when flat)."""
    return {it.label: tuple(it.explode * P.EXPLODE * c for c in normal) for it in items}


def export_dxf(sketch, path):
    exp = ExportDXF(unit=Unit.MM)
    exp.add_shape(sketch)
    exp.write(path)


def plate_prop():
    """Holds the top plate LIFT_SERVICE mm above the tray walls (two needed): a block
    with a slot that sits over the wall."""
    h = P.LIFT_SERVICE
    body = Box(14.0, 12.0, h + 6.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    slot = Pos(0, 0, -0.1) * Box(14.2, P.WALL + 0.4, 6.1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return body - slot


def fit_coupon():
    """Hole-fit test: key cap guide hole, magnet pocket and hub D-bore at -0.1 / 0 / +0.1 mm."""
    plate = Box(84.0, 64.0, P.TOP_PLATE_T + 1.0, align=(Align.MIN, Align.MIN, Align.MIN))
    w = P.CAP_SIZE + 2 * P.KEY_GUIDE_CLEAR
    for i, d in enumerate((-0.1, 0.0, 0.1)):
        x = 14.0 + i * 28.0
        plate -= Pos(x, 16.0, -1) * Box(w + d, w + d, 10)
        plate -= Pos(x, 40.0, -0.01) * Cylinder(P.MAGNET_TRAY[0] / 2 + 0.1 + d / 2, P.MAGNET_TRAY[1] + 0.1,
                                                align=(Align.CENTER, Align.CENTER, Align.MIN))
        bore = model.d_shape(P.KNOB_HUB_D / 2 + 0.1 + d / 2, P.KNOB_HUB_FLAT - P.KNOB_HUB_D / 2 + 0.1 + d / 2, 10)
        plate -= Pos(x, 54.0, -1) * bore
    return plate


# JLC panel estimate. The four boards go in one mouse-bite panel. JLC charges a
# large-size fee (~$57) when "PCB area > 650 cm²" and doesn't say whether that's one
# panel or the order. Conservative reading: the area JLC assembles for one build,
# i.e. ASSEMBLED_PANELS panels (its minimum is 2). Five are made, but only two assembled.
PANEL_GAP = 2.0           # mm between boards (mouse-bite tabs)
PANEL_RAIL = 5.0          # mm assembly rail on two opposite edges
JLC_LARGE_CM2 = 650.0
ASSEMBLED_PANELS = 2
PANEL_FEE_ACCEPTED = True  # pending a real JLC quote (it decides whether the >650 cm² fee applies); True keeps the warning but stops --strict failing on it


def panel_estimate(boards):
    """Smallest rectangle (mm) for the boards' bounding boxes: each board goes in a
    main column (as drawn) or a side column (turned 90°); rails on either pair of edges."""
    best = None
    names = list(boards)
    for mask in range(1 << len(names)):
        cols = ([boards[n] for i, n in enumerate(names) if not mask >> i & 1],
                [boards[n][::-1] for i, n in enumerate(names) if mask >> i & 1])
        cols = [c for c in cols if c]
        w = sum(max(b[0] for b in c) for c in cols) + PANEL_GAP * (len(cols) - 1)
        h = max(sum(b[1] for b in c) + PANEL_GAP * (len(c) - 1) for c in cols)
        for size in ((w, h + 2 * PANEL_RAIL), (w + 2 * PANEL_RAIL, h)):
            if best is None or size[0] * size[1] < best[0] * best[1]:
                best = size
    return best


def panel_lines(info):
    """Summary lines and problems for the JLC panel area check."""
    def size(sk):
        bb = sk if isinstance(sk, BoundBox) else sk.bounding_box()
        return (bb.size.X, bb.size.Y)
    boards = {"frame PCB": size(info["frame_sketch"]), "knob board": size(info["knob_board_sketch"]),
              "USB board": size(info["usb_board_sketch"])}
    if info.get("touch_band_bbox") is not None:
        boards["touch band"] = size(info["touch_band_bbox"])
    w, h = panel_estimate(boards)
    board_cm2 = sum(a * b for a, b in boards.values()) / 100
    panel_cm2 = w * h / 100
    order_cm2 = ASSEMBLED_PANELS * panel_cm2
    lines = [
        "## JLC panel (estimate)",
        "- Boards: " + ", ".join(f"{n} {a:.1f} x {b:.1f}" for n, (a, b) in boards.items())
        + f" mm; {board_cm2:.0f} cm² of bounding boxes",
        f"- Panel: ~{w:.0f} x {h:.0f} mm = {panel_cm2:.0f} cm² ({PANEL_GAP:g} mm gaps, "
        f"{PANEL_RAIL:g} mm rails on two edges)",
        f"- Assumption: JLC's large-size fee counts the assembled area, {ASSEMBLED_PANELS} panels for "
        f"one build = {order_cm2:.0f} cm² against {JLC_LARGE_CM2:.0f} cm² (5 assembled for a group buy "
        f"= {5 * panel_cm2:.0f} cm²)",
    ]
    problems = []
    if order_cm2 > JLC_LARGE_CM2:
        msg = (f"JLC panel area {order_cm2:.0f} cm² for one build is over the {JLC_LARGE_CM2:.0f} cm² "
               f"large-size threshold (~$57 fee)")
        lines.append(f"- WARNING: {msg}" + (" (accepted)" if PANEL_FEE_ACCEPTED else ""))
        if not PANEL_FEE_ACCEPTED:
            problems.append(msg)
    else:
        lines.append(f"- Under the large-size threshold by {JLC_LARGE_CM2 - order_cm2:.0f} cm²")
    return lines, problems


def main():
    render_on = "--no-render" not in sys.argv
    OUT.mkdir(exist_ok=True)
    t0 = time.time()

    full, L, info = model.full_device()
    flat, _, _ = model.full_device(tilt=False)
    proto, PL, pinfo = model.prototype()
    st, pst = info["stack"], pinfo["stack"]
    section = model.key_section(flat, L.key_xy[P.KEY_COLS * (P.KEY_ROWS // 2) + P.KEY_COLS // 2],
                                z0=st.glass - P.PANEL_T - 0.5, slab=0.4)
    proto_section = model.key_section(proto, PL.key_xy[0],
                                      z0=pst.glass - P.PANEL_T - 0.5, slab=0.4)

    export_step(to_compound(full, "clickdeck_full"), str(OUT / "clickdeck_full.step"))
    export_step(to_compound(proto, "clickdeck_proto"), str(OUT / "clickdeck_proto.step"))
    cutaway = model.key_section(flat, L.key_xy[P.KEY_COLS * (P.KEY_ROWS // 2) + P.KEY_COLS // 2],
                                z0=st.glass - P.PANEL_T - 0.5, slab=28.0)
    export_step(to_compound(cutaway, "key_cutaway"), str(OUT / "key_cutaway.step"))

    export_dxf(info["frame_sketch"], str(OUT / "full_frame_pcb_outline.dxf"))
    export_dxf(info["plate_sketch"], str(OUT / "full_top_plate.dxf"))
    export_dxf(pinfo["frame_sketch"], str(OUT / "proto_frame_pcb_outline.dxf"))
    export_dxf(pinfo["base_sketch"], str(OUT / "proto_base_plate_3mm_acrylic.dxf"))
    export_dxf(info["knob_board_sketch"], str(OUT / "full_knob_board_outline.dxf"))
    export_dxf(info["usb_board_sketch"], str(OUT / "full_usb_board_outline.dxf"))
    tb = info.get("touch_band_bbox")
    if tb is not None:                                     # touch band outline (with the ZIF clearance)
        export_dxf(Pos((tb.min.X + tb.max.X) / 2, (tb.min.Y + tb.max.Y) / 2) * Rectangle(tb.size.X, tb.size.Y),
                   str(OUT / "full_touch_band_outline.dxf"))
    # PCB geometry for the KiCad generators in hardware/ (mm, CAD coordinates, y up)
    import json
    (OUT / "proto_frame_pcb.json").write_text(json.dumps(pinfo["frame_pcb"], indent=1) + "\n")

    # Case parts as printable STLs, in print orientation: tray floor-down, top plate
    # face-down (flipped), stand on its bottom
    print_lines = []
    for label, src in (("case_tray", flat), ("top_plate", flat), ("stand", full)):
        part = next(it.part for it in src if it.label == label)
        if label == "top_plate":
            part = Rot(X=180) * part
            part = Pos(0, 0, -part.bounding_box().min.Z) * part
        export_stl(part, str(OUT / f"print_{label}.stl"))
        bb = part.bounding_box()
        dims = sorted((bb.size.X, bb.size.Y, bb.size.Z))
        fits = all(d <= b for d, b in zip(dims, sorted(P.PRINT_BED)))
        print_lines.append(
            f"- {label}: {bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.0f} mm, "
            + ("fits" if fits else "DOES NOT FIT")
            + f" a {P.PRINT_BED[0]:.0f} mm bed")

    # Prototype top plate: printed (it carries the cap guides, D8), face-down
    pplate = Rot(X=180) * next(it.part for it in proto if it.label == "top_plate_proto")
    export_stl(Pos(0, 0, -pplate.bounding_box().min.Z) * pplate, str(OUT / "print_proto_top_plate.stl"))

    def at_origin(part):
        bb = part.bounding_box()
        return Pos(-(bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, -bb.min.Z) * part

    for src, name in ((flat, "key_cap_clear_resin.stl"), (proto, "key_cap_two_nub_clear_resin.stl")):
        cap = next(it for it in src if it.label == "cap_0")
        x, y = (L.key_xy[0] if src is flat else PL.key_xy[0])
        export_stl(Pos(-x, -y, 0) * cap.part, str(OUT / name))
    knob_part = next(it for it in flat if it.label.startswith("knob0_")
                     and it.label.endswith(("_knob", "_shaft_adapter")))
    export_stl(at_origin(knob_part.part), str(OUT / f"{knob_part.label.removeprefix('knob0_')}.stl"))
    export_stl(pinfo["knob_test_stand"]["stand_part"], str(OUT / "print_knob_test_stand.stl"))

    for label, name, flip in (("knob0_hub", "knob_hub", True), ("knob0_spacer", "motor_spacer", True),
                              ("knob_window_0", "knob_window", False)):
        it = next((i for i in flat if i.label == label), None)
        if it is not None:
            part = Rot(X=180) * it.part if flip else it.part
            export_stl(at_origin(part), str(OUT / f"{name}.stl"))
    export_stl(plate_prop(), str(OUT / "print_plate_prop.stl"))
    export_stl(fit_coupon(), str(OUT / "print_fit_coupon.stl"))

    import keystack
    lines = ["# Model summary (generated by cad/build.py)", ""]
    for name, inf, lay in (("Full device", info, L), ("Prototype", pinfo, PL)):
        kf = inf["key_frame"]
        defl = keystack.frame_deflection(kf["rect"], kf["key_xy"], model.PCB_WIN, kf["supports"], kf["loads"],
                                         kf["knob_wins"], kf["knob_size"])
        nubs = 2 if (name == "Prototype" and P.PROTO_SECOND_SWITCH) else 1
        st = inf["stack"]
        g = model.key_stop_geometry(nubs)
        g_len = model.key_guide_length(st)
        tilt = keystack.guide_tilt(P.KEY_GUIDE_CLEAR, g_len)
        drop = keystack.cap_max_drop(g, tilt)
        w, d, h = inf["outer_mm"]
        tilted = inf.get("tilted_mm")
        lines += [
            f"## {name}",
            *([f"- Angled {P.TILT_DEG}° on the stand: {tilted[0]} wide x {tilted[1]} deep x "
               f"{tilted[2]} mm tall (top plate at the back)"] if tilted else []),
            f"- Size: {w} x {d} mm footprint, {h} mm to the top plate "
            f"(caps +{P.CAP_PROTRUDE}" + (f", knobs +{P.KNOB_GAP + P.KNOB_H})" if lay.knob_xy else ")"),
            f"- Keys: {len(lay.key_xy)} at {P.KEY_PITCH} mm pitch, cap {P.CAP_SIZE} mm",
            f"- Knob display window: {lay.win_size[0]:.1f} x {lay.win_size[1]:.1f} mm",
            f"- Z stack: glass {st.glass:.2f}, frame PCB {st.pcb_bot:.2f}-{st.pcb_top:.2f}, "
            f"switch top {st.sw_top:.2f}, top plate {st.plate_bot:.2f}-{st.plate_top:.2f}, "
            f"motor {st.motor_bot:.2f}-{st.motor_top:.2f}",
            f"- Key stack (D8): caps and frame PCB {P.GLASS_GAP:.2f} mm above the glass, down-stop "
            f"{P.KEY_STOP_GAP:.2f} mm; worst cap drop {drop:.2f} mm (guide tilt + switch bottomed + "
            f"down-stop), glass margin {st.pcb_bot - st.glass - drop:.2f} mm; frame flex {max(defl):.3f} mm/N "
            f"({max(defl) * P.KEY_PRESS_DESIGN_N:.2f} mm at {P.KEY_PRESS_DESIGN_N:g} N)",
            f"- Cap guide (D8, B3): straight-line travel in the plate's key hole and skirt, "
            f"{P.KEY_GUIDE_CLEAR:g} mm per side over {g_len:.1f} mm; max tilt {math.degrees(tilt):.2f}° "
            f"(guide slop, not a feature; the down-stop keeps the cap off the glass)",
        ]
        if "knob_test_stand" in inf:
            kts = inf["knob_test_stand"]
            w_, d_, h_ = kts["size_mm"]
            lines.append(f"- Knob test stand (print): {w_:g} x {d_:g} x {h_:g} mm to the motor seat; "
                         f"MT6701 breakout {P.MT6701_BREAKOUT[0]:g} mm wide (EST) on rails under the deck; "
                         f"motor screws {kts['motor_screw']} from below")
        if "standoffs" in inf:
            lines.append("- Standoffs: " + ", ".join(f"{k} {v:.1f} mm" for k, v in inf["standoffs"].items()))
        if "frame_supports" in inf:
            fs = inf["frame_supports"]
            lines.append(f"- Frame PCB screws: {len(fs['pan'])} pan-head off the glass, "
                         f"{len(fs['csk']) + len(fs['csk_inner'])} countersunk (flush) over it")
        if "display_gap" in inf:
            lines.append(f"- Display board: {inf['display_gap']:.1f} mm behind the knob board, "
                         f"{inf['display_floor_gap']:.1f} mm above the floor"
                         + (f" (connector row sits in a {inf['floor_pocket']:.1f} mm floor pocket)"
                            if inf['floor_pocket'] > 0 else "") + " (Waveshare STEP depths)")
        if "cables" in inf:
            cab = ", ".join(f"{n.removeprefix('cable_')} {c['buy']} mm"
                            for n, c in inf["cables"].items() if c["buy"])
            lead = max(inf["leads"].values(), key=lambda v: v["coil_h"])
            lines.append(f"- Internal cables (bought, plug-in): {cab}; "
                         f"{P.MOTOR_LEAD_LEN:.0f} mm motor leads coil {lead['coil_h']:.1f} mm "
                         f"high ({lead['room']:.1f} mm room under the panel)")
        if P.TOUCH_BAR and inf.get("touch_bar_h", 0) >= P.TOUCH_BAR_MIN_H:
            plate_t = P.TOP_PLATE_T if name == "Full device" else P.PROTO_PLATE_T
            if name == "Full device":
                plate_t -= P.TOUCH_BAR_RECESS
            lines.append(f"- Touch band: {inf['touch_bar_h']:.1f} mm tall under the knob "
                         f"displays, sensing through {plate_t:g} mm of plate")
        lines += [f"- WARNING: {w_}" for w_ in lay.warnings] or ["- Fit checks: OK"]
        lines.append("")
    import stability
    stab = stability.check(full, L, info)
    stab_line = (f"- Estimated mass {stab['mass_g']:.0f} g (stand {stab['stand_g']:.0f} g, shelled); tips "
                 f"backward at {stab['tip_force_n']:.1f} N on a top-row key (a firm press is "
                 f"~{stab['press_n']:.0f} N), or {stab['cable_pull_n']:.1f} N pulling the USB cable "
                 f"straight back. Rough densities, see cad/stability.py")
    lines += ["## Stability (estimate)", stab_line]
    if stab["tip_force_n"] < 2 * stab["press_n"]:
        msg = "less than 2x margin against tipping when pressing the top row"
        L.warnings.append(msg)
        lines.append(f"- WARNING: {msg}")
    lines.append("")
    lines += ["## Printing (case parts)", *print_lines, ""]
    p_lines, panel_problems = panel_lines(info)
    lines += [*p_lines, ""]
    (OUT / "summary.md").write_text("\n".join(lines))
    print("\n".join(lines))
    problems = [w for lay in (L, PL) for w in lay.warnings]
    problems += [p for p in print_lines if "DOES NOT FIT" in p]
    problems += panel_problems
    if problems and "--strict" in sys.argv:
        print(f"\n--strict: {len(problems)} problem(s), failing", file=sys.stderr)
        sys.exit(1)
    print(f"exports done in {time.time() - t0:.1f}s")

    if render_on:
        import render

        jobs = [
            ("full_iso.png", full, dict(az=-62, el=20)),
            ("full_exploded.png", full, dict(az=-62, el=22,
                                             offsets=exploded_offsets(full, info["normal"]),
                                             size=(1500, 1300))),
            ("full_face.png", full, dict(az=-90, el=90 - P.TILT_DEG)),
            ("full_side.png", full, dict(az=0, el=0, size=(1500, 900))),
            ("key_section.png", section, dict(az=0, el=0.5, size=(1500, 700), tol=0.02)),
            ("proto_iso.png", proto, dict(az=-55, el=34)),
            ("proto_exploded.png", proto, dict(az=-55, el=24, offsets=exploded_offsets(proto),
                                               size=(1300, 1200))),
            ("inside_layout.png",
             [it for it in flat
              if not it.label.startswith(("top_plate", "cap_", "knob_window", "switch_",
                                          "frame_pcb", "panel7", "touch_bar"))
              and not it.label.endswith("_knob")],
             dict(az=-115, el=55, size=(1500, 1000))),
            ("cabling.png",                    # top-down, display and top plate removed
             [it for it in flat
              if not it.label.startswith(("top_plate", "cap_", "knob_window", "switch_",
                                          "frame_pcb", "panel7", "touch_bar", "display_board_pcb",
                                          "display_board_esp32s3", "screw_", "plug_ffc_frame",
                                          "plug_touch_band"))
              and not it.label.endswith(("_knob", "_hub"))],
             dict(az=-90, el=89.9, size=(1500, 1250))),
            ("knob_board_detail.png",
             [it for it in flat if it.label.startswith(("knob_board", "knob0_", "knob1_",
                                                         "touch_bar"))
              and not it.label.endswith("_knob")],
             dict(az=-70, el=38, size=(1500, 900), tol=0.08,
                  offsets={f"knob{i}_{p}": (0, 0, 18) for i in (0, 1)
                           for p in ("motor_2204", "magnet")})),
            ("proto_key_section.png", proto_section, dict(az=0, el=0.5, size=(1500, 700), tol=0.02)),
        ]
        for name, items, kw in jobs:
            t1 = time.time()
            render.render(items, str(OUT / name), **kw)
            print(f"rendered {name} in {time.time() - t1:.1f}s")


if __name__ == "__main__":
    main()
