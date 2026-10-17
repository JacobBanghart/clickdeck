# clickdeck

A custom Stream Deck–style USB controller: per-key images, real clicky micro
switches, and motor-driven knobs that switch between clicky and smooth in
software.

![Full device](cad/out/freecad_three_quarter.png)

## Why not just buy a Stream Deck + XL?

What this adds:
- **Programmable knobs.** Each knob switches per function between clicky,
  smooth, a set number of clicks, or hard end stops, and can push back
  (a tick at a preset, a nudge for attention). Stream Deck dials have one
  fixed feel.
- **Clicky keys.** Micro switches instead of soft rubber pads.
- **Open and Linux-first.** Open hardware, open USB protocol, your own
  firmware. No vendor app or account.

What the + XL does better: it's polished and ready today, has a huge plugin
library, 36 keys plus a touch strip, and costs about the same (see below). Build this for the knobs and the switch feel; if those don't matter,
buy the + XL.

## Cost (rough estimates)

| | ~Cost |
|---|---|
| **Build one from this repo** | **$260–470** |
| Per unit, 5 people ordering together | $200–370 |
| Stream Deck + XL, for comparison | ~$350 |

Building one covers parts, PCBs (JLC's 5-board minimum included), prints and
shipping. Most of the range is the case ($50–120) and shipping. Breakdown:
[docs/cost.md](docs/cost.md).

## Design

| Exploded | Key profile (cap, tab, switch) |
|---|---|
| ![Exploded](cad/out/full_exploded.png) | ![Key section](cad/out/key_section.png) |

Prototype (2 keys + 1 knob, laser-cut acrylic):

![Prototype](cad/out/proto_exploded.png)

- [docs/plan.md](docs/plan.md): goals, architecture, and the staged build plan
- [docs/parts.md](docs/parts.md): prototype parts list with links
- [docs/cost.md](docs/cost.md): cost breakdown
- [docs/pcb.md](docs/pcb.md): how the PCBs get designed and ordered
- [cad/](cad/): parametric CAD (build123d). STEP files for FreeCAD/Fusion 360 in `cad/out/`

Status (2026-10-16): planning and CAD. Next step is reviewing the models,
then ordering the prototype parts.

## License

- Software (Python, scripts, firmware, host code): [MIT](LICENSE)
- Hardware designs (CAD models and exports in `cad/`, PCB designs, and the
  design docs in `docs/`): [CERN-OHL-P-2.0](LICENSE-HARDWARE)
