# Cost

Rough estimates from 2026-10-16. Nothing here is a live quote; JLC/LCSC
prices depend on board size, quantity and part stock. Get real quotes from
the generated files before ordering.

## Build one from this repo: ~$275–415 (own 3D printer) or ~$305–490 (case ordered)

What someone pays to build the finished design. No prototype, no PCB
revisions, no tools beyond basic soldering. PCB lines include JLC's
5-board minimum, and JLC assembles at least 2 of each, so the builder
pays for parts on 2 boards and ends up with a spare.

Two orders: **JLC** (all three PCBs in one panel, assembly, 3D prints) and
**AliExpress/Waveshare** (display board, motors, magnets).

| Item | ~Cost |
|---|---|
| ESP32-S3 + 7" 1024×600 display board (Waveshare ESP32-S3-LCD-7B, non-touch, SKU 31727; $33.99 from Waveshare) | ~$34 |
| 5× 2204 gimbal motors | $40–60 |
| 5× diametric magnets | ~$5 |
| Knob board, JLC-assembled, 2 boards minimum (per board: 5× TMC6300 at ~$5.12 = ~$26, 5× MT6701, RP2350B, inverters, switches, passives ≈ $36–41; plus extended-part and setup fees) | $105–130 |
| Frame PCB with 21 B3U switches, JLC-assembled | $30–50 |
| Touch band PCB + touch controller, JLC-assembled | $5–10 |
| 21 clear resin key caps (JLC3DP) | $20–40 |
| 5 printed knobs (CNC aluminum instead: +$50–100) | $5–15 |
| Case (tray, top plate, stand): printed at home / ordered from JLC3DP | $10–15 / $40–90 |
| Screws, standoffs, USB-C cable, rubber feet | $10–20 |
| Shipping, 2 orders | $15–35 |

The three PCBs go in one panel so JLC charges one assembly setup fee. All
case parts fit a 256 mm print bed (checked by `cad/build.py`).

## 5 builds ordered together: ~$185–355 each

PCB minimums, assembly setup fees, extended-part fees and shipping get
shared, and nobody pays for a spare board. Parts don't get cheaper: the five
TMC6300 drivers alone are ~$26 per device.

## Development cost (the designer's, not a builder's): ~$420–660

| | ~Cost |
|---|---|
| Prototype (2 keys + 1 knob, see below) | $115–185 |
| Full device | $275–415 |
| One PCB redo | $30–60 |

## Prototype (2 keys + 1 knob): ~$115–185

| Item | ~Cost |
|---|---|
| AliExpress order: ESP32-S3 board, 2.4" screen, 2× 2204 motors, magnets, switches, touch test kit, breadboard, test tools (calipers, USB power meter, scale) | $55–80 |
| JLC knob module, 2 assembled (MT6701 + TMC6300 at ~$5.93 + press switch) | $30–45 |
| Laser-cut acrylic plates, frame PCB, clear caps (stage 4) | $30–60 |

Details: [parts.md](parts.md).

## Comparison

A Stream Deck + XL is about $350 (US reseller listing, 2026-10-16). With
current TMC6300 pricing, a single clickdeck build costs about the same or
more. The biggest lever is the motor driver: a cheaper low-voltage
3-phase driver would save ~$15–20 per device (see
[open-questions.md](open-questions.md)).
