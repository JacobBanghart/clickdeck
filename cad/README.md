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
| `clickdeck_full.step` | Full device, 120 named and colored parts. Open in FreeCAD or Fusion 360 |
| `clickdeck_proto.step` | 2-key + 1-knob prototype |
| `key_cutaway.step` | One key cut in half, to inspect the cap/tab/switch stack |
| `*_frame_pcb_outline.dxf` | Board outline with key windows. KiCad: File → Import → Graphics, layer Edge.Cuts |
| `proto_*_plate_3mm_acrylic.dxf` | Laser-cut plates for the prototype (SendCutSend/Ponoko) |
| `full_top_plate.dxf` | Top plate outline for the full device |
| `key_cap_clear_resin.stl`, `knob_cap.stl` | 3D-print files (JLC3DP) |
| `*.png` | Quick previews from a small CPU renderer (`render.py`) |

## Files

- `params.py`: all dimensions. Values marked (EST) are from listings/datasheets; measure the real parts.
- `model.py`: parts and assemblies. The vertical stack is derived from the knob motor height,
  and the key stack hangs from the top plate (`make_stack`).
- `build.py`: exports and previews.
- `render.py`: preview renderer (no GPU needed).

## Coordinates

x right, y toward the back (the user sits at -y), z up. Origin is the center
of the display's active area, at the case floor.
