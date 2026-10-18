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
FAQ gives 35–92.5% depending on the goods: PCBs and assembly 35%, stencils
90%, resin and PETG prints 40%, CNC aluminum 90% (rates from 2026-03-17,
FAQ updated 2026-09-09). 35% is used below, 40% on prints. AliExpress also
collects duty at checkout. Outside the US, replace the duty lines with
your own VAT/duty.

## Build one from this repo: ~$475–735 (own 3D printer) or ~$530–850 (case ordered)

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
| All four PCBs, JLC-assembled, 2 of each: knob board (5× TMC6300 from DigiKey via JLC Global Sourcing, 5× MT6701, RP2350B, inverters, switches), frame PCB with 21 B3U switches, touch band with the AT42QT2120, USB board with the CH334F hub. Fabrication, fees and parts; split in "Where the money goes" | $205–320 |
| Internal cables, ready-made: 100 mm USB-C to USB-C (one 90° end), 100 mm JST-GH 8-pin, 80 mm 12-pin FFC, 80 mm JST-SH 6-pin (optional: HY2.0 3-pin link lead, ~$1) | $5–8 |
| 21 clear resin key caps + 5 knob-window covers (JLC3DP SLA, one standard clear finish) | $23–46 |
| 5 printed knobs, hubs and motor spacers (CNC aluminum knobs instead: +$50–100, plus 90% duty) | $3–10 |
| Case (tray, top plate, stand) in PETG: printed at home / ordered from JLC3DP | $9–15 / $45–90 |
| Screws, M3 heat-set inserts, magnets, rubber feet, cable ties, shims, transfer tape, epoxy, a USB-C to USB-C cable to the PC (1.5 A+ port for full haptics) | $20–27 |
| Shipping, 2 orders | $15–35 |
| **Import duty, US** (~35% of the goods, 40% on prints; more with a JLC3DP case) | $115–175 |

The four PCBs go in one panel so JLC charges one assembly setup fee. All
case parts fit a 256 mm print bed (checked by `cad/build.py`).

### Where the money goes (one build, own printer)

| Bucket | ~Cost | Share |
|---|---|---|
| **JLC boards** (all four, 2 of each) | **$205–320** | **43%** |
| – PCB fabrication: 5 panels, ~180 × 160 mm, 2-layer. HASL to ENIG, JLC's fee for 4 designs in one panel, the countersink option, maybe its keyboard-PCB surcharge (~$24) for the frame PCB | $30–70 | 8% |
| – Setup, stencil, hand-solder labor: Economic $8.18 + $1.53 + $3.58; Standard $25.56 + $8.21 + $3.58 | $14–38 | 4% |
| – Extended-part fees: 24 types × $3.07 (Economic). Standard charges $1.53 on every unique part instead, basic ones too (~44) | $65–80 | 12% |
| – Parts for 2 board sets (one is the spare), at LCSC prices for that quantity; TMC6300 at DigiKey's $2.44; pre-order minimums for two short parts | $90–115 | 17% |
| – Placement: ~1,800 SMD joints × $0.0016, plus the USB-C shell legs by hand | $3–6 | 1% |
| – Global Sourcing extras on the TMC6300 (China import duty of 3–30%, price differences) | $1–10 | 1% |
| Import duty, US | $115–175 | 24% |
| Motors + sensor magnets | $45–65 | 9% |
| Display board | $34 | 6% |
| SLA key caps + knob windows | $23–46 | 6% |
| Hardware + internal cables (incl. the cable to the PC) | $25–35 | 5% |
| Shipping, 2 orders | $15–35 | 4% |
| Case + knobs, printed at home | $12–25 | 3% |
| **Total** | **$475–735** | 100% |

Shares are of the midpoints. JLC's boards and the duty on them are about
two thirds of the build. Fees are from JLC's pricing pages (2026-09-09) and
its PCBA blog (2026-10-14); fabrication is an estimate, so the instant
quote decides it.

Levers that don't cut features:

- **Economic PCBA.** Every board is top-side only, 2-layer 1.6 mm, in one
  mouse-bite panel under 250 × 250 mm. The finest pitch is the RP2350B's
  0.4 mm, right at Economic's limit. That saves ~$24 of setup and stencil
  over Standard, and preferred extended parts load free. Keep the BOOTSEL
  switch on top: a bottom-side part forces Standard double-side ($51.12 +
  $16.42). Don't use V-cuts in the panel.
- **Basic and preferred parts.** About 5 fewer extended types (~$15, ~$20
  with duty): the RP2350B's crystal → the basic 12 MHz C9002 the USB board
  uses (check the load caps); USBLC6-2SC6 and the knob board's ESD arrays →
  one preferred SRV05-4-P-T7 (C85364, same SOT-23-6 pinout); one switch part
  for the motor rail and both VBUS branches (set by Rset); basic 22 µF
  ceramics (C45783) instead of the input polymer cap, if the hot-plug test
  passes; a basic 3.3 V regulator (AMS1117-3.3 C6186 or XC6206P332MR C5446).
- **In-stock parts.** Swap the two short parts (SM08B-GHS-TB: 0 in JLC
  stock, pre-order minimum 19; AOTA inductor: 3 in stock, minimum 32) for
  stocked equivalents. Saves ~$15 of minimum buys.
- **TMC6300 from DigiKey** (already in the numbers): $2.44 against LCSC's
  ~$5.07, ~$26 per build.
- **HASL instead of ENIG** saves ~$10–25. ENIG is flatter for the 0.4 mm
  QFN-80, so it's a yield trade-off.
- **Group buy.** 5 builds share ~$110–200 of fixed JLC cost and skip the
  spare set (below).

### Extended part types: 24

Counted from [bom.md](bom.md), JLC's library checked 2026-10-17. A part
used on two boards is one type.

Chosen parts (16): RP2350B (C42415655), ABM8-272-T3 crystal (C20625731),
AOTA-B201610S3R3 inductor (C42411119), TMC6300 (Global Sourcing), MT6701
(C3003196), SN74LVC3G04 (C139324), B3U-1000P (C231329, keys and knobs),
SM08B-GHS-TB (C265111, both GH ends), 12-pin ZIF (C19269355, both ends),
BM06B-SRSS-TB (C160392), AT42QT2120 (C614938), SM06B-SRSS-TB (C160405),
CH334F (C5187527), mid-mount USB-C (C2894902), TYPE-C-31-M-12 (C165948),
USBLC6-2SC6 (C7519).

Not chosen yet, no basic part found (8): SMD right-angle 1×3 motor
header, reverse-mount BOOTSEL switch, ESD arrays for the matrix and touch
lines, motor-rail load switch (listed with the passives, but not a basic
part), reverse-blocking VBUS switches (one type if both use the same part),
VBUS TVS, ~470 µF bulk cap, 22–47 µF input polymer cap.

Basic already: the W25Q128JVSIQ flash, 1N4148W, the USB board's 12 MHz
crystal, the passives and ferrite, the 3.3 V regulator if a basic one is
picked. So the RP2354B (on-chip flash) saves no fee. Add one type each for
the optional HY2.0 header, the PD sink if fitted, or two different VBUS
switch parts.

Basic or preferred alternatives exist for 4 of the 24 (the crystal,
USBLC6-2SC6, the ESD arrays, the polymer cap); one shared switch part saves
a fifth (see the levers). None for the RP2350B, TMC6300, MT6701, inverter, B3U,
connectors, CH334F, AT42QT2120 or inductor.

Global Sourcing has no listed handling fee, and shipping to JLC is free.
Some sourced parts pay 3–30% Chinese import duty, prices can differ a
little from DigiKey's, and switches and connectors pay a $20 inspection
fee per kind (not the TMC6300). The quote shows it.

One small extra to check on the quote: JLC's countersink option for the
frame PCB's countersunk M2 holes, and whether it keeps the order Economic.

## 5 builds ordered together: ~$275–520 each

PCB minimums, assembly setup fees, extended-part fees and shipping get
shared, and nobody pays for a spare board. The internal hub adds ~$10–15
per device here (parts, cables, a share of the fees). Parts don't get
cheaper: the five TMC6300 drivers are ~$12 per device from DigiKey. Duty
(~35%) is included.

## Development cost (the designer's, not a builder's): ~$1,000–1,650

| | ~Cost |
|---|---|
| Prototype (2 keys + 1 knob on the 7B, Rev 0.5 board; see below) | $270–460 |
| Full device | $475–735 |
| One PCB redo (the whole 4-board panel: fabrication, setup, extended-part fees, parts for 2 more boards, shipping, duty) | $290–455 |

## Prototype (2 keys + 1 knob on the 7B): ~$270–460

Wider than first planned (D3): the real display board instead of a small
screen, and one JLC order with the knob module, the Rev 0.5 test board, the
prototype frame PCB and the caps. It costs more up front, but it tests
what would otherwise first meet on a $290–455 four-board panel.

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
about $475–735 for a single build. That's accepted: it's for the knob feel
and the switch feel, which the + XL can't give. The biggest costs are
JLC's boards (fees and parts), import duty, the motors and the display
board. Sourcing the TMC6300 through Global Sourcing/DigiKey (~$2.44
instead of LCSC's ~$5.07) saves about $26 per build (10 chips), less any
sourcing duty. The internal hub (2026-10-17) adds ~$25 to a single build,
mostly JLC's per-part-type fees; it buys plug-in cabling, USB updates for
both chips and reading the port's current.
