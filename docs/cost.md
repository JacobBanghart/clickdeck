# Cost

Rough estimates, updated 2026-10-17. Nothing here is a live quote; JLC/LCSC
prices depend on board size, quantity and part stock. **Before ordering,
get a real JLC cart quote** from the generated files, with a US shipping
address so it shows the duty.

**Cost isn't a design driver** (owner decision D1 in
[design-review.md](design-review.md)). clickdeck is built for the knob feel
and the switch feel, and features aren't cut to save money. But the numbers
here should be honest: **a single build costs more than a Stream Deck + XL**
(~$350, 36 keys, 6 dials).

**Import duty (US).** The US de minimis exemption is gone, so every order
from China pays duty. JLC ships DDP (duty paid at checkout); its US tariff
FAQ gives 35–92.5% depending on the goods, about 35% typical, and that's
the figure used below. AliExpress also collects duty at checkout. Outside
the US, replace the duty lines with your own VAT/duty.

## Build one from this repo: ~$375–575 (own 3D printer) or ~$410–650 (case ordered)

What someone pays to build the finished design. No prototype, no PCB
revisions: JLC fits every part and connector, and the internal cables are
bought ready-made. Every part is on the top side of each board (D6;
[pcb.md](pcb.md)). All parts with sources: [bom.md](bom.md) (generated
from the CAD model, so it matches the assembly guide). PCB lines include JLC's 5-board minimum, and JLC
assembles at least 2 of each, so the builder pays for parts on 2 boards and
ends up with a spare.

Two orders: **JLC** (all four PCBs in one panel, assembly, 3D prints) and
**AliExpress/Waveshare** (display board, motors, magnets, cables, hardware).

| Item | ~Cost |
|---|---|
| ESP32-S3 + 7" 1024×600 display board (Waveshare ESP32-S3-LCD-7B, non-touch, SKU 31727; $33.99 from Waveshare) | ~$34 |
| 5× 2204 gimbal motors | $40–60 |
| 5× diametric magnets | ~$5 |
| Knob board, JLC-assembled, 2 boards minimum (per board: 5× TMC6300 via JLC Global Sourcing or consigned from DigiKey at ~$2.44 = ~$12, 5× MT6701, RP2350B, inverters, switches, passives ≈ $22–27; plus extended-part, sourcing and setup fees) | $85–115 |
| Frame PCB with 21 B3U switches, JLC-assembled | $30–50 |
| Touch band PCB + AT42QT2120 touch controller (~$1.89), JLC-assembled | $5–10 |
| USB board (CH334F hub, 2 USB-C sockets, JST-GH, power switches, ESD), JLC-assembled, 2 boards minimum. Much of it is JLC's extended-part fees ($3 per part type) | $20–25 |
| Internal cables, ready-made: 100 mm USB-C to USB-C (one 90° end), 100 mm JST-GH 8-pin, 80 mm 12-pin FFC, 80 mm JST-SH 6-pin (optional: HY2.0 3-pin link lead, ~$1) | $5–8 |
| 21 clear resin key caps (JLC3DP, one standard clear finish) | $20–40 |
| 5 printed knobs (CNC aluminum instead: +$50–100) | $5–15 |
| Case (tray, top plate, stand) in PETG: printed at home / ordered from JLC3DP | $10–15 / $40–90 |
| Screws, M3 heat-set inserts, magnets, rubber feet, cable ties, epoxy, a USB-C to USB-C cable to the PC (1.5 A+ port for full haptics) | $13–23 |
| Shipping, 2 orders | $15–35 |
| **Import duty, US** (~35% of the goods; more with a JLC3DP case) | $80–140 |

The four PCBs go in one panel so JLC charges one assembly setup fee. All
case parts fit a 256 mm print bed (checked by `cad/build.py`).

Extended-part fees: count them from the BOM, not by guess. The whole panel
has roughly 17–19 extended part types (RP2350B, its flash and crystal,
TMC6300, MT6701, inverter, B3U, connectors, hub, switches…), not the ~5
first assumed, so the low ends of the board rows above are optimistic. The
RP2354B (on-chip flash) would drop one of them. JLC Global Sourcing adds
its own handling fee for the TMC6300; the quote shows it.

Assembly route: every board is top-side only (D6; the knob board's press
switches moved to the top of its front border), so JLC's cheaper
single-side assembly covers them and no two-sided assembly fee is needed.
One small extra to check on the quote: JLC's countersink option for the
frame PCB's countersunk M2 holes.

## 5 builds ordered together: ~$250–475 each

PCB minimums, assembly setup fees, extended-part fees and shipping get
shared, and nobody pays for a spare board. The internal hub adds ~$10–15
per device here (parts, cables, a share of the fees). Parts don't get
cheaper: the five TMC6300 drivers are ~$12 per device from DigiKey. Duty
(~35%) is included.

## Development cost (the designer's, not a builder's): ~$850–1,400

| | ~Cost |
|---|---|
| Prototype (2 keys + 1 knob on the 7B, Rev 0.5 board; see below) | $270–460 |
| Full device | $375–600 |
| One PCB redo (the whole 4-board panel: setup, extended-part fees, parts for 2 more boards, shipping, duty) | $200–335 |

## Prototype (2 keys + 1 knob on the 7B): ~$270–460

Wider than first planned (D3): the real display board instead of a small
screen, and one JLC order with the knob module, the Rev 0.5 test board, the
prototype frame PCB and the caps. It costs more up front, but it tests
what would otherwise first meet on a $200–335 four-board panel.

| Item | ~Cost |
|---|---|
| Order 1, AliExpress + Waveshare: Waveshare 7B, RP2350B core board, USB hub, 10 cm right-angle USB-C cable, 4× 2204 motors from two sellers, magnets, switches, copper tape, breadboard, test tools (calipers, USB power meter, scale, logic analyzer), current-limited 5 V supply, soldering iron, M2/M3 screws, standoffs and shims | $120–195 |
| Order 2, JLC: one panel with the Rev 0 knob module, the Rev 0.5 test board (RP2350B, CH334F, AT42QT2120, connectors) and the rev C prototype frame PCB, 2 of each assembled; clear caps and knobs (JLC3DP) | $75–125 |
| Order 3: laser-cut acrylic plates (shipping included in each order's range) | $15–30 |
| **Import duty, US** (~35% on orders 1 and 2) | $60–110 |

Details: [parts.md](parts.md).

## Comparison

A Stream Deck + XL (36 keys, 6 dials) is about $350 (US reseller listing,
2026-10-16). clickdeck has 21 keys and 5 haptic knobs and costs more:
about $375–600 for a single build. That's accepted: it's for the knob feel
and the switch feel, which the + XL can't give. The biggest costs are the
display board, the motors, JLC's fees and import duty. Sourcing the
TMC6300 through Global Sourcing/DigiKey (~$2.44 instead of LCSC's $5.93)
saves about $35 per build (10 chips) before the sourcing fee. The internal hub (2026-10-17) adds
~$25 to a single build, mostly JLC's per-part-type fees; it buys plug-in
cabling, USB updates for both chips and reading the port's current.
