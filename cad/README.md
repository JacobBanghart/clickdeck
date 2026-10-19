# CAD

Parametric models written in Python with [build123d](https://build123d.readthedocs.io).
Every dimension is in [`params.py`](params.py); change a value and rebuild.

```sh
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python build123d pillow numpy
.venv/bin/python cad/build.py            # ~45 s with previews
.venv/bin/python cad/build.py --no-render  # ~5 s, exports only
```

`build.py` prints a summary (size, z-stack, fit warnings) and writes it to
`out/summary.md`. Fit checks warn when a change breaks something, e.g. the
switch no longer fits between key rows or the knobs are closer together than
the motor diameter.

## Outputs (`cad/out/`)

| File | Use |
|---|---|
| `clickdeck_full.step` | Full device, every part named and colored. Open in FreeCAD or Fusion 360 |
| `clickdeck_proto.step` | 2-key prototype on the real 7B, with the knob test stand beside it |
| `key_cutaway.step` | One key cut in half, to inspect the cap/tab/switch stack |
| `*_frame_pcb_outline.dxf` | Board outline with key windows. KiCad: File → Import → Graphics, layer Edge.Cuts |
| `full_knob_board_outline.dxf` | Knob board outline with the tongue slots |
| `full_usb_board_outline.dxf` | USB board (hub) outline |
| `full_touch_band_outline.dxf` | Touch band outline (stops short of the frame PCB's ZIF) |
| `cabling.png` | Top view of the internal cabling, display and top plate removed |
| `print_case_tray.stl`, `print_top_plate.stl`, `print_stand.stl` | Case parts for a home printer (fit a 256 mm bed) or JLC3DP, in print orientation (plate face-down). PETG; M3 heat-set inserts in the plate's posts |
| `print_plate_prop.stl` | Tool: two of these hold the top plate 40 mm up while its cables are plugged in |
| `print_knob_test_stand.stl` | Prototype knob test stand (JLC3DP): the 2204 on a deck, an MT6701 breakout on rails under it (`MT6701_BREAKOUT`, EST) |
| `print_fit_coupon.stl` | Print first: cap guide hole, magnet pocket and hub bore at -0.1/0/+0.1 mm; set `HOLE_COMP` from it |
| `print_proto_top_plate.stl` | Prototype top plate (3 mm, face-down), with the cap guide skirts (D8) |
| `proto_base_plate_3mm_acrylic.dxf` | Laser-cut base plate for the prototype (SendCutSend/Ponoko) |
| `full_top_plate.dxf` | Top plate outline for the full device |
| `key_cap_clear_resin.stl`, `knob_window.stl` | Clear resin (SLA) parts: key caps (one nub; rails and lugs underneath are the down-stop), knob-window covers (JLC3DP) |
| `key_cap_two_nub_clear_resin.stl` | Prototype cap with a nub at both ends, for the two-switch test (D8) |
| `knob.stl`, `knob_hub.stl`, `motor_spacer.stl` | Knob cap, hub (screws to the bell), motor spacer ring (its arm carries the press striker) |
| `full_side.png`, `full_face.png` | Side profile and straight-on view of the angled device |
| `*.png` | Quick previews from a small CPU renderer (`render.py`) |

## Files

- `params.py`: all dimensions. Values marked (EST) are from listings/datasheets; measure the real parts.
- `model.py`: parts and assemblies. The vertical stack is derived from the knob motor height,
  and the key stack hangs from the top plate (`make_stack`).
- `build.py`: exports and previews.
- `keystack.py`: key stack checks (D8): the cap's tilt in its guide (clearance over
  engagement), the worst cap drop for any press (a small linear program over the cap's
  tilt) and the frame PCB's flex at each switch (a grillage model).
- `render.py`: preview renderer (no GPU needed).

## Coordinates

x right, y toward the back (the user sits at -y), z up. Origin is the center
of the display's active area, at the case floor.

## FreeCAD screenshots (headless)

FreeCAD 1.1.4 AppImage is extracted at `~/Applications/freecad/squashfs-root`.
To capture real FreeCAD views of a STEP file without a display:

```sh
xvfb-run -a -s "-screen 0 1920x1080x24" \
  env CLICKDECK_STEP=cad/out/clickdeck_full.step CLICKDECK_OUT=cad/out/freecad \
  ~/Applications/freecad/squashfs-root/AppRun cad/freecad_screenshot.py
```

Writes `freecad_three_quarter.png`, `freecad_front.png`, `freecad_side.png`.
To open the model interactively: `~/Applications/freecad/squashfs-root/AppRun cad/out/clickdeck_full.step`.

## Assembly and service

`cad/assembly.py` defines the assembly steps and checks that the design can
actually be built and serviced: no overlapping parts (screws may enter only
their target, and only as deep as its thread allows; pilot holes run past the
tips), minimum gaps between mating parts, nothing floating, nothing hitting the
stand or below the desk in the tilted model, every screw reachable
with a straight screwdriver at its step, the top plate, display and knob
board lift out in order, a paperclip reaches the display board's
BOOT/RESET through the back wall and the knob board's BOOTSEL through the
floor, every cap's down-stop lands on the frame PCB and no press (plus the
frame's flex at 3 N) brings a cap within 0.1 mm of the glass, every plug (modeled at full size,
overmolds included) slides straight into its socket at the step that
connects it, cables don't run through parts, and the top plate's cables
reach with the plate lifted 40 mm. Cable bends below the minimum radius are
fit warnings in `build.py`. It also renders the step pictures, the
animation, [docs/assembly.md](../docs/assembly.md) and
[docs/bom.md](../docs/bom.md).

```sh
.venv/bin/python cad/assembly.py --check     # checks only (~30 s)
.venv/bin/python cad/assembly.py --bom       # checks + docs/bom.md
.venv/bin/python cad/assembly.py             # + pictures and the guide (~2 min)
.venv/bin/python cad/assembly.py --animate   # + the animation (~15 min)
```

## Checks

GitHub Actions ([`.github/workflows/cad.yml`](../.github/workflows/cad.yml))
rebuilds the models on every change to `cad/` with the pinned toolchain in
`requirements.txt`, and fails if:
- any fit check warns (`--strict`), or a case part doesn't fit the print bed
- any assembly check fails (`assembly.py --check`)
- `out/summary.md` doesn't match the committed one (outputs weren't rebuilt
  and committed after a parameter change)
