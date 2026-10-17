# Cost

Rough estimates from 2026-10-16. Nothing here is a live quote; JLC/LCSC
prices depend on board size, quantity and part stock. Get real quotes from
the generated files before ordering.

## Build one from this repo: ~$205–340 (own 3D printer) or ~$235–420 (case ordered)

What someone pays to build the finished design. No prototype, no PCB
revisions, no tools beyond basic soldering. PCB lines include JLC's
5-board minimum, so the builder ends up with spare boards.

Two orders: **JLC** (all three PCBs in one panel, assembly, 3D prints) and
**AliExpress/Waveshare** (display board, motors, magnets).

| Item | ~Cost |
|---|---|
| ESP32-S3 + 7" 800×480 display board (Waveshare ESP32-S3-LCD-7, non-touch; $32–37 from Waveshare) | $32–37 |
| 5× 2204 gimbal motors | $40–60 |
| 5× diametric magnets | ~$5 |
| Knob board, JLC-assembled (RP2350B, 5× MT6701, 5× motor drivers, 5× press switches) | $35–55 |
| Frame PCB with 21 B3U switches, JLC-assembled | $30–50 |
| Touch band PCB + touch controller, JLC-assembled | $5–10 |
| 21 clear resin key caps (JLC3DP) | $20–40 |
| 5 printed knobs (CNC aluminum instead: +$50–100) | $5–15 |
| Case (tray, top plate, stand): printed at home / ordered from JLC3DP | $10–15 / $40–90 |
| Screws, standoffs, USB-C cable, rubber feet | $10–20 |
| Shipping, 2 orders | $15–35 |

The three PCBs go in one panel so JLC charges one assembly setup fee. All
case parts fit a 256 mm print bed (checked by `cad/build.py`).

## 5 builds ordered together: ~$160–330 each

PCB minimums, assembly setup fees and shipping get shared: the PCBs drop to
roughly half per unit, and one shipment covers everyone. The display board,
motors, caps and case stay about the same per unit.

## Development cost (the designer's, not a builder's): ~$330–550

| | ~Cost |
|---|---|
| Prototype (2 keys + 1 knob, see below) | $95–150 |
| Full device | $205–340 |
| One PCB redo | $30–60 |

## Prototype (2 keys + 1 knob): ~$95–150

| Item | ~Cost |
|---|---|
| AliExpress order: ESP32-S3 board, 2.4" screen, 2× 2204 motors, magnets, switches, touch test kit, breadboard, calipers | $45–60 |
| JLC knob module (MT6701 + TMC6300 + press switch, assembled) | $20–30 |
| Laser-cut acrylic plates, frame PCB, clear caps (stage 4) | $30–60 |

Details: [parts.md](parts.md).

## Comparison

A Stream Deck + XL is about $350 (US reseller listing, 2026-10-16).
