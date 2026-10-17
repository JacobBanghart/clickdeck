# Cost

Rough estimates from 2026-10-16. Nothing here is a live quote; JLC/LCSC
prices depend on board size, quantity and part stock. Get real quotes from
the generated files before ordering.

## Build one from this repo: ~$260–470

What someone pays to build the finished design. No prototype, no PCB
revisions, no tools beyond basic soldering. PCB lines include JLC's
5-board minimum, so the builder ends up with spare boards.

| Item | ~Cost |
|---|---|
| ESP32-S3 + 7" 800×480 display board (Waveshare ESP32-S3-LCD-7, $32–37 from Waveshare) | $32–37 |
| 5× 2204 gimbal motors | $40–60 |
| 5× diametric magnets | ~$5 |
| 5× knob module PCBs, JLC-assembled (MT6701 + TMC6300) | $30–50 |
| Knob controller (RP2040 + parts) | $5–15 |
| Frame PCB with 21 B3U switches, JLC-assembled | $30–50 |
| 21 clear resin key caps (JLC3DP) | $20–40 |
| 5 printed knobs (CNC aluminum instead: +$50–100) | $5–15 |
| Case: tray, top plate, stand (printed; top plate could be laser-cut) | $50–120 |
| Screws, standoffs, USB-C cable, spacer tape | $10–20 |
| Shipping across 3–4 orders | $30–60 |

## 5 builds ordered together: ~$200–370 each

PCB minimums, assembly setup fees and shipping get shared: the frame PCB
and knob modules drop to roughly half per unit, and one shipment covers
everyone. The display board, motors, caps and case stay about the same per
unit.

## Development cost (the designer's, not a builder's): ~$380–675

| | ~Cost |
|---|---|
| Prototype (2 keys + 1 knob, see below) | $90–145 |
| Full device | $260–470 |
| One PCB redo | $30–60 |

## Prototype (2 keys + 1 knob): ~$90–145

| Item | ~Cost |
|---|---|
| AliExpress order: ESP32-S3 board, 2.4" screen, 2× 2204 motors, magnets, switches, breadboard, calipers | $40–55 |
| JLC knob module (MT6701 + TMC6300, assembled) | $20–30 |
| Laser-cut acrylic plates, frame PCB, clear caps (stage 4) | $30–60 |

Details: [parts.md](parts.md).

## Comparison

A Stream Deck + XL is about $350 (US reseller listing, 2026-10-16).
