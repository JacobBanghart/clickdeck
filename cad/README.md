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
| `clickdeck_full.step` | Full device (the default slots: 2 haptic modules + 3 blanks), every part named and colored. Open in FreeCAD or Fusion 360 |
| `knob_modules.step` | The three slot types side by side (D23): haptic module, lite module, blank, each with its pogo pins |
| `clickdeck_proto.step` | 2-key prototype on the real 7B, with the knob test stand beside it |
| `key_cutaway.step` | One key cut in half, to inspect the cap/tab/switch stack |
| `*_frame_pcb_outline.dxf` | Board outline with key windows. KiCad: File → Import → Graphics, layer Edge.Cuts |
| `full_backplane_outline.dxf` | Backplane outline: slot-boss and key-pin holes (the pogo pins go under each slot's front) |
| `module_haptic_pcb_outline.dxf`, `module_lite_pcb_outline.dxf` | Module PCB outlines (haptic: the tongue on two torsion necks; lite: solid) |
| `full_usb_board_outline.dxf` | USB board (hub) outline |
| `full_touch_band_outline.dxf` | Touch band outline (stops short of the frame PCB's ZIF). The band is an optional add-on, off by default (D24); this file is only rewritten by a build with the band (`CLICKDECK_TOUCH_BAR=1`), and its geometry doesn't depend on the flag |
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
| `knob_lite.stl` | Lite knob: the same cap with a stem down to the encoder's 6 mm flatted shaft |
| `module_base.stl`, `module_cover.stl`, `blank_cover.stl` | Module carrier (D23): base under the module PCB (sets the pogo height, key pins underneath), cover with the flush bezel (print bezel-down), and the blank. PETG |
| `full_side.png`, `full_face.png` | Side profile and straight-on view of the angled device |
| `*.png` | Quick previews from a small CPU renderer (`render.py`) |

## Knob slots (D23)

`KNOB_SLOTS` in `params.py` says what's in each of the five slots, left to
right: `"haptic"`, `"lite"` or `"blank"`. The default is the owner's first
build, `("haptic", "haptic", "blank", "blank", "blank")`; it's what
`model.full_device()` builds (and the assembly guide's pictures).
`build.py --strict` and `assembly.py --check` also build `CHECK_CONFIGS`:
every slot haptic and every slot lite. The default build gets every check;
the other two get the checks on and around the slots (interference,
screws, gaps, floating parts, screwdriver access, the motor plug, the lead
coil, each module lifting out, knob heights). The slot checks: every knob
top sits where the haptic knob's does (`KNOB_TOP_TOL`), covers and blanks
are flush with the plate, the pogo pins are compressed inside their stroke
(`POGO_COMPRESS`) and each lands fully on a module pad, the key pins only
fit one way, and every module lifts straight out with the plate on. Lite
modules: the shaft fills the knob's bore past its flat, and a full press
clears the cover and the encoder's bushing. Module and slot dimensions are
`MODULE_*`, `SLOT_*`, `POGO*`; the encoder's are `ENC_*` (from the Bourns
drawing; measure the real part).

## Touch band (D24)

`TOUCH_BAR = False` in `params.py`: the band is an optional add-on, off by
default. The model then has no band, no touch cable and no SH header on the
backplane (its footprint stays on the real board), and the plate has no
band pocket. The knobs sit in the same place either way. Set
`CLICKDECK_TOUCH_BAR=1` in the environment (or `TOUCH_BAR = True`) to build
the band; CI runs `assembly.py --check --default-only` that way in a second
job.

## Files

- `params.py`: all dimensions. Values marked (EST) are from listings/datasheets; measure the real parts.
- `model.py`: parts and assemblies. The vertical stack is derived from the knob motor height
  (backplane, pogo pins, module PCB, motor), and the key stack hangs from the top plate
  (`make_stack`). Slots: `slot_items`, `backplane`, `module_cover`, `module_base`.
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
with a straight screwdriver at its step, every knob module and blank lifts
out of its slot with the case closed, the top plate, display and backplane
lift out in order, a paperclip reaches the display board's BOOT/RESET
through the back wall and the backplane's BOOTSEL through the floor, the
slot checks above, every cap's down-stop lands on the frame PCB and no press (plus the
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
- any assembly check fails (`assembly.py --check`), for the default slots, all haptic or all lite,
  or for the default slots with the touch band fitted (`CLICKDECK_TOUCH_BAR=1`, second job)
- `out/summary.md` doesn't match the committed one (outputs weren't rebuilt
  and committed after a parameter change)
