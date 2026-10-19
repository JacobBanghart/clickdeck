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

## Build one from this repo: ~$475–710 (own 3D printer) or ~$530–825 (case ordered)

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
| All four PCBs, JLC-assembled, 2 of each: knob board (5× TMC6300 from DigiKey via JLC Global Sourcing, 5× MT6701, RP2350B, inverters, switches), frame PCB with 21 B3U switches, touch band with the AT42QT2120, USB board with the CH334F hub. Fabrication, fees and parts; split in "Where the money goes" | $205–300 |
| Internal cables, ready-made: 100 mm USB-C to USB-C (one 90° end), 100 mm JST-GH 8-pin, 80 mm 12-pin FFC, 80 mm JST-SH 6-pin (optional: HY2.0 3-pin link lead, ~$1) | $5–8 |
| 21 clear resin key caps + 5 knob-window covers (JLC3DP SLA, one standard clear finish) | $23–46 |
| 5 printed knobs, hubs and motor spacers (CNC aluminum knobs instead: +$50–100, plus 90% duty) | $3–10 |
| Case (tray, top plate, stand) in PETG: printed at home / ordered from JLC3DP | $9–15 / $45–90 |
| Screws, M3 heat-set inserts, magnets, rubber feet, cable ties, shims, transfer tape, epoxy, a USB-C to USB-C cable to the PC (1.5 A+ port for full haptics) | $20–27 |
| Shipping, 2 orders | $15–35 |
| **Import duty, US** (~35% of the goods, 40% on prints; more with a JLC3DP case) | $115–170 |

The four PCBs go in one panel so JLC charges one assembly setup fee. All
case parts fit a 256 mm print bed (checked by `cad/build.py`).

### Where the money goes (one build, own printer)

| Bucket | ~Cost | Share |
|---|---|---|
| **JLC boards** (all four, 2 of each) | **$205–300** | **43%** |
| – PCB fabrication: 5 panels, ~215 × 169 mm (`cad/build.py` estimate), 2-layer, ENIG (owner decision). JLC's fee for 4 designs in one panel, the countersink option, maybe its keyboard-PCB surcharge (~$24) for the frame PCB | $45–70 | 10% |
| – Setup, stencil, hand-solder labor: Economic $8.18 + $1.53 + $3.58; Standard $25.56 + $8.21 + $3.58 | $14–38 | 4% |
| – Extended-part fees: 19 types × $3.07 = ~$58 (Economic). Standard charges $1.53 on every unique part instead, basic ones too (~44) | $55–65 | 10% |
| – Parts for 2 board sets (one is the spare), at LCSC prices for that quantity; TMC6300 at DigiKey's $2.44; the inductor's pre-order minimum (32) | $85–110 | 17% |
| – Placement: ~1,800 SMD joints × $0.0016, plus the USB-C shell legs by hand | $3–6 | 1% |
| – Global Sourcing extras on the TMC6300 (China import duty of 3–30%, price differences) | $1–10 | 1% |
| Import duty, US | $115–170 | 24% |
| Motors + sensor magnets | $45–65 | 9% |
| Display board | $34 | 6% |
| SLA key caps + knob windows | $23–46 | 6% |
| Hardware + internal cables (incl. the cable to the PC) | $25–35 | 5% |
| Shipping, 2 orders | $15–35 | 4% |
| Case + knobs, printed at home | $12–25 | 3% |
| **Total** | **$475–710** | 100% |

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
- **Basic and preferred parts (applied 2026-10-17).** 5 fewer extended
  types (~$15, ~$21 with duty). The RP2350B's crystal is now the basic
  C9002 the USB board uses, with 33 pF load caps (the ABM8-272-T3 stays as
  the tested fallback). The USBLC6-2SC6 and the knob board's ESD arrays are
  now the preferred SRV05-4-P-T7 (C85364, no loading fee). One part, the
  TPS259470ARPWR (C3662799), covers the motor rail and both VBUS branches.
  The input polymer cap is now 2 × 22 µF basic ceramics (C45783); a
  polymer footprint stays in case the hot-plug test rings. The 3.3 V
  regulator is the basic AMS1117-3.3 (C6186).
- **In-stock parts (applied 2026-10-17).** The GH header is now HCTL's
  HC-GH-8PWT (C3011950, 1,726 in stock), a JST GH clone. That drops the
  SM08B-GHS-TB's minimum of 19 (~$9). The AOTA inductor stays (3 in stock,
  minimum 32, ~$8 extra): no stocked 3.3 µH part has the polarity mark
  Raspberry Pi requires.
- **TMC6300 from DigiKey** (already in the numbers): $2.44 against LCSC's
  ~$5.07, ~$26 per build.
- **Group buy** (not planned until a device works). 5 builds share
  ~$110–200 of fixed JLC cost and skip the spare set (below).

### Extended part types: 19

Counted from [bom.md](bom.md), JLC's library checked 2026-10-17. A part
used on two boards is one type. Was 24 before the swaps in the levers.

Chosen parts (15): RP2350B (C42415655), AOTA-B201610S3R3 inductor
(C42411119), TMC6300 (Global Sourcing), MT6701 (C3003196), SN74LVC3G04
(C139324), B3U-1000P (C231329, keys and knobs), HC-GH-8PWT GH header
(C3011950, both GH ends), 12-pin ZIF (C19269355, both ends), BM06B-SRSS-TB
(C160392), AT42QT2120 (C614938), SM06B-SRSS-TB (C160405), CH334F
(C5187527), mid-mount USB-C (C2894902), TYPE-C-31-M-12 (C165948),
TPS259470ARPWR (C3662799, motor rail and both VBUS branches).

Not chosen yet, no basic part found (4): SMD right-angle 1×3 motor
header, reverse-mount BOOTSEL switch, VBUS TVS, ~470 µF bulk cap.

Preferred extended, no fee: SRV05-4-P-T7 (C85364, all ESD arrays).

Basic: the 12 MHz crystal C9002 (both boards), the W25Q128JVSIQ flash,
1N4148W, the AMS1117-3.3 (C6186), the 22 µF input ceramics (C45783), the
passives and ferrite. So the RP2354B (on-chip flash) saves no fee. Add one
type each for the optional HY2.0 header, the PD sink if fitted, the input
polymer cap if the hot-plug test needs it, or the ABM8-272-T3 if the C9002
fails its start-up test.

None of the 19 has a basic or preferred alternative that fits: the
RP2350B, TMC6300, MT6701, inverter, B3U, connectors, CH334F, AT42QT2120,
the eFuse and the inductor.

Global Sourcing has no listed handling fee, and shipping to JLC is free.
Some sourced parts pay 3–30% Chinese import duty, prices can differ a
little from DigiKey's, and switches and connectors pay a $20 inspection
fee per kind (not the TMC6300). The quote shows it.

One small extra to check on the quote: JLC's countersink option for the
frame PCB's countersunk M2 holes, and whether it keeps the order Economic.

**Large-size fee, not in the totals.** JLC adds $57.46 when "PCB area >
650 cm²" and doesn't say what area it counts. `cad/build.py` estimates the
panel at ~362 cm² (2 mm gaps, 5 mm rails). Two assembled panels are
~724 cm². If JLC counts the assembled area, a single build pays the fee
(~$78 with duty). The quote decides. Splitting the panel avoids it, but
costs a second setup.

## 5 builds ordered together: ~$275–520 each

No group buy is planned until a working device exists.

PCB minimums, assembly setup fees, extended-part fees and shipping get
shared, and nobody pays for a spare board. The internal hub adds ~$10–15
per device here (parts, cables, a share of the fees). Parts don't get
cheaper: the five TMC6300 drivers are ~$12 per device from DigiKey. Duty
(~35%) is included.

## Development cost (the designer's, not a builder's): ~$700–1,300

Plan changed 2026-10-18 (D3): final parts bought early, a throwaway test
kit with bought breakouts, then the full build ("Rev A") as the first
build of our own boards, with one revision of whichever board fails.

| | ~Cost |
|---|---|
| Throwaway test kit (below) | $100–170 |
| Bench tools (below; skip what you have) | $70–140 |
| Spare 2204 motor (the 6th; the other 5 are in Rev A) | $10–15 |
| Rev A, the full device (includes the 7B, motors, magnets and cable bought early) | $475–710 |
| One single-board revision (only the board that fails; table below) | $45–250 |
| **Total, likely through a working device** | **$700–1,285** |

Without the tools (already owned): ~$630–1,145. Not included: a second
7B (~$46 with duty), JLC's large-size fee if the quote shows it, and a
second failed board.

### Single-board revision, per board

JLC: 5 PCBs, 2 assembled, Economic, the setup and extended-part fees for
that board alone, parts for 2 boards, shipping and 35% duty. A board
ordered alone can't share the panel's setup fee, but it's still much
less than redoing the whole panel ($285–430).

| Board | Extended part types | ~Cost |
|---|---|---|
| Knob board (RP2350B, 5 × TMC6300, 5 × MT6701, inverters, switches, eFuse; the inductor's minimum of 32) | ~13 | $180–250 |
| Frame PCB (21–42 B3U, ZIF; countersinks, maybe the keyboard-PCB surcharge) | 2 | $75–145 |
| USB board (CH334F, two USB-C, two eFuses, GH header, TVS) | ~6 | $80–105 |
| Touch band (AT42QT2120, SH header) | 2 | $45–65 |

The knob board is the likeliest to fail (hinge, motor fit, RP2350B and
drivers all meet there first) and the most expensive to redo.

## Prototype (2 keys on the 7B + a knob test stand): ~$290–485 up front

Of that, ~$120–175 are final parts that go into Rev A, so the prototype
itself costs ~$170–310 (throwaway kit plus tools). Details:
[parts.md](parts.md).

**Final parts, bought early (reused in Rev A; counted in the full build):**

| Item | ~Cost |
|---|---|
| Waveshare ESP32-S3-LCD-7B | $34 |
| 6 × 2204 motors from two sellers (5 + 1 spare) | $45–75 |
| Diametric magnets, 10 cm right-angle USB-C display cable | $5–10 |
| Shipping (Waveshare) | $5–15 |
| **Import duty, US** (~35%) | $29–42 |
| **Subtotal** | **$120–175** |

**Throwaway test kit:**

| Item | ~Cost |
|---|---|
| SparkFun TMC6300 breakout ROB-21867, with US shipping (no China duty) | $23–27 |
| WeAct RP2350B core board, CH334F hub module, MT6701 breakout, breadboard and jumpers (AliExpress), with ~35% duty. The core board and hub stay as the firmware dev bench | $18–31 |
| JLC order: rev C prototype frame PCB (5 made, 2 assembled with 4 B3U each), 2 + 2 clear caps, the knob test stand, knob and hub (JLC3DP), shipping, 35–40% duty | $45–80 |
| Laser-cut acrylic plates (US, shipping included) | $15–30 |
| **Subtotal** | **$100–170** |

An earlier estimate (~$50–65) counted only the kit's sticker prices.
Shipping, duty on the JLC and AliExpress parts, and the plates add the
rest.

**Bench tools (kept):** calipers, USB-C power meter, 0.1 g scale, logic
analyzer, current-limited 5 V supply, soldering iron (the breakouts'
headers; Rev A's heat-set inserts), M2/M3 screws, standoffs and shims:
$50–105, ~$70–140 with duty.

## Comparison

A Stream Deck + XL (36 keys, 6 dials) is about $350 (US reseller listing,
2026-10-16). clickdeck has 21 keys and 5 haptic knobs and costs more:
about $475–710 for a single build. That's accepted: it's for the knob feel
and the switch feel, which the + XL can't give. The biggest costs are
JLC's boards (fees and parts), import duty, the motors and the display
board. Sourcing the TMC6300 through Global Sourcing/DigiKey (~$2.44
instead of LCSC's ~$5.07) saves about $26 per build (10 chips), less any
sourcing duty. The internal hub (2026-10-17) adds ~$25 to a single build,
mostly JLC's per-part-type fees; it buys plug-in cabling, USB updates for
both chips and reading the port's current.
