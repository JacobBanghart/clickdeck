# Cost

Rough estimates from 2026-10-16. Nothing here is a live quote; JLC/LCSC
prices depend on board size, quantity and part stock. Get real quotes from
the generated files before ordering.

## Build one from this repo: ~$300–450 (own 3D printer) or ~$330–525 (case ordered)

What someone pays to build the finished design. No prototype, no PCB
revisions, no soldering: JLC fits every part and connector, and the internal
cables are bought ready-made. Every part with sources:
[bom.md](bom.md) (generated from the CAD model, so it matches the assembly
guide). PCB lines include JLC's
5-board minimum, and JLC assembles at least 2 of each, so the builder
pays for parts on 2 boards and ends up with a spare.

Two orders: **JLC** (all four PCBs in one panel, assembly, 3D prints) and
**AliExpress/Waveshare** (display board, motors, magnets, cables, hardware).

| Item | ~Cost |
|---|---|
| ESP32-S3 + 7" 1024×600 display board (Waveshare ESP32-S3-LCD-7B, non-touch, SKU 31727; $33.99 from Waveshare) | ~$34 |
| 5× 2204 gimbal motors | $40–60 |
| 5× diametric magnets | ~$5 |
| Knob board, JLC-assembled, 2 boards minimum (per board: 5× TMC6300 at ~$5.12 = ~$26, 5× MT6701, RP2350B, inverters, switches, passives ≈ $36–41; plus extended-part and setup fees) | $105–130 |
| Frame PCB with 21 B3U switches, JLC-assembled | $30–50 |
| Touch band PCB + touch controller, JLC-assembled | $5–10 |
| USB board (CH334F hub, 2 USB-C sockets, JST-GH, power switch, ESD), JLC-assembled, 2 boards minimum. Most of it is JLC's fee for ~5 new "extended" part types ($3 each) | $20–25 |
| Internal cables, ready-made: 100 mm USB-C to USB-C (one 90° end), 100 mm JST-GH 8-pin, 80 mm 12-pin FFC, 100 mm JST-SH 6-pin | $5–8 |
| 21 clear resin key caps (JLC3DP) | $20–40 |
| 5 printed knobs (CNC aluminum instead: +$50–100) | $5–15 |
| Case (tray, top plate, stand): printed at home / ordered from JLC3DP | $10–15 / $40–90 |
| Screws, magnets, rubber feet, cable ties, epoxy, a USB-C cable to the PC | $10–20 |
| Shipping, 2 orders | $15–35 |

The four PCBs go in one panel so JLC charges one assembly setup fee. All
case parts fit a 256 mm print bed (checked by `cad/build.py`).

## 5 builds ordered together: ~$195–370 each

PCB minimums, assembly setup fees, extended-part fees and shipping get
shared, and nobody pays for a spare board. The internal hub adds ~$10–15
per device here (parts, cables, a share of the fees). Parts don't get cheaper: the five
TMC6300 drivers alone are ~$26 per device.

## Development cost (the designer's, not a builder's): ~$450–710

| | ~Cost |
|---|---|
| Prototype (2 keys + 1 knob, see below) | $120–200 |
| Full device | $300–450 |
| One PCB redo | $30–60 |

## Prototype (2 keys + 1 knob): ~$120–200

| Item | ~Cost |
|---|---|
| AliExpress order: ESP32-S3 board, RP2350B board, USB hub, 10 cm right-angle USB-C cable, 2.4" screen, 2× 2204 motors, magnets, switches, touch test kit, breadboard, test tools (calipers, USB power meter, scale) | $60–95 |
| JLC knob module, 2 assembled (MT6701 + TMC6300 at ~$5.93 + press switch) | $30–45 |
| Laser-cut acrylic plates, frame PCB, clear caps (stage 4) | $30–60 |

Details: [parts.md](parts.md).

## Comparison

A Stream Deck + XL is about $350 (US reseller listing, 2026-10-16). With
current TMC6300 pricing, a single clickdeck build costs about the same or
more. The internal hub (2026-10-17) added ~$25 to a single build, mostly
JLC's per-part-type fees; it buys plug-in cabling, USB updates for both
chips and reading the port's current. The biggest lever is the motor driver: a cheaper low-voltage
3-phase driver would save ~$15–20 per device (see
[open-questions.md](open-questions.md)).
