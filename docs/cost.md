# Cost

Rough estimates, updated 2026-10-19. Nothing here is a live quote; JLC/LCSC
prices depend on board size, quantity and part stock. **Before ordering,
get a real JLC cart quote** from the generated files, with a US shipping
address so it shows the duty.

**Cost isn't a design driver** (owner decision D1 in
[design-review.md](design-review.md)). clickdeck is built for the knob feel
and the switch feel, and features aren't cut to save money. But the numbers
here should be honest: **a single build costs more than a Stream Deck + XL**
(~$350, 36 keys, 6 dials).

**Knobs are modules (D23).** A device is the **base** (display, keys, case,
backplane, USB board, touch band, cables: no knobs) plus one item per knob
slot: a **haptic module** (motor, software clicky/smooth), a **lite
module** (push encoder, detented or smooth as ordered, D22) or a **blank**.
The owner's first build is 2 haptic + 3 blanks; knobs can be added later.

**Import duty (US).** The US de minimis exemption is gone, so every order
from China pays duty. JLC ships DDP (duty paid at checkout); its US tariff
FAQ gives 35–92.5% depending on the goods: PCBs and assembly 35%, stencils
90%, resin and PETG prints 40%, CNC aluminum 90% (rates from 2026-03-17,
FAQ updated 2026-09-09). 35% is used below, 40% on prints. AliExpress also
collects duty at checkout. Outside the US, replace the duty lines with
your own VAT/duty.

## Summary: base + per module

Per device, US duty included, case, carriers and knobs printed at home.
"1" is a single build with the module boards ordered in the same JLC order
as the base (each module type is its own small JLC design: 5 PCBs made, at
least 2 assembled). 5, 25 and 100 are devices ordered together (none
planned until a device works); they are estimates from the BOM and JLC's
published fees, not quotes.

| Per device | 1 | 5 | 25 | 100 |
|---|---|---|---|---|
| **Base device** (no knobs; 5 slot connectors included) | $345–540 | $175–260 | $140–195 | $125–180 |
| + **haptic module**, each | $20–27, plus $51–77 once per order for the module design | $24–33 | $20–26 | $16–21 |
| + **lite module**, each | $6–8, plus $39–50 once per order | $7–10 | $5–7 | $4–5 |
| + **blank**, each | ~$1 | ~$1 | ~$1 | ~$1 |

A module design's fixed cost (PCB fabrication, assembly setup, its
extended-part fees, Global Sourcing extras, duty) is paid once per order,
however many of that module are assembled, and JLC assembles at least 2.
So one haptic module costs ~$71–104, two ~$91–131 ($46–66 each), five
~$151–212 ($30–42 each).

**Common configurations:**

| Configuration | 1 | 5 | 25 | 100 |
|---|---|---|---|---|
| 0 knobs (5 blanks) | $350–545 | $180–265 | $145–200 | $130–185 |
| **2 haptic + 3 blank** (the owner's first build) | **$440–675** | $225–330 | $180–250 | $160–225 |
| 5 haptic (the full version) | $495–750 | $295–425 | $240–325 | $205–285 |
| 5 lite | $415–630 | $210–310 | $165–230 | $145–205 |
| 3 haptic + 2 lite (mixed) | $505–765 | $260–380 | $210–290 | $180–255 |

Before D23 the whole device was quoted as one: 5 haptic $475–710 for one
build and ~$200–270 at 100; lite ~$355–555 and ~$140–190. The modular
version costs a little more with every slot full (the slot connectors,
the module boards' own setup and fees, the carriers), and less for a first
build with fewer knobs.

**Owner target (2026-10-19): the full version at ~$250 retail at 100
units.** The cost estimate for 5 haptic at 100 is $205–285 before any
margin, so it doesn't reach that retail price yet. The modules add ~$9–12
of it (below); most of the rest is the display board ($34), the base boards,
the motors and the duty (~$45–60).

**Adding modules later.** A later small order pays its own JLC setup and
fees for the module design ($51–77 haptic, $39–50 lite), its own shipping
and duty (~$12–27 more), and needs at least 2 assembled. Going from the
first build's 2 haptic to 5 later is ~$123–185 for 3 haptic modules (vs
~$60–80 more had all 5 been in the first order). The first order's spare
module PCBs come bare: JLC only fits parts on the ones it assembles.

## Module overhead per slot (vs the old single knob board)

What the slots cost on top of the old design, where all five knob channels
sat on one knob board. The knob channel itself (driver, sensor, inverter,
switch, header, motor, magnet, spacer, hub, cap) costs the same either way.

| Per slot | 1 build | 100 units |
|---|---|---|
| Slot connector: 18 pogo pins on the backplane (C2988082; $0.0596 at 50+, $0.0378 at 4,500+, 2026-10-19). On every slot, filled or blank, so it's in the base | $1.07 (×2 for the spare backplane JLC assembles) | $0.68 |
| Module-ID diode (and pads, which cost nothing) | ~$0.01 | ~$0.01 |
| Module PCB, 28.4 × 30.5 mm 2-layer ENIG, its own design | in the design's fixed $51–77 | $0.30–0.50, plus ~$0.05 of setup and fees |
| Carrier: printed base and cover | $0.20–0.40 | $0.15–0.30 |
| Retention: two M2×30 countersunk screws, two M2 heat-set inserts | ~$0.20 | ~$0.15 |
| US duty on the above (~35%) | | $0.40–0.60 |
| **Total per slot** | **~$1.5–2.5, plus each module design's fixed cost per order** | **~$1.7–2.3** |

At 100 units that's ~$9–12 per device with all five slots full. The
connector plus the extra parts (the ID diode) is **~$0.69 per slot at 100
units and ~$1.08 for one build**, inside the ~$1–1.5 target; with the
module PCB and the printed carrier it's ~$1.3–1.7 before duty.

**Why pogo pins and not a header pair.** A keyed 2.54 mm pair is cheaper: an
18-pin SMD male header (C88175, $0.054 at 50) and an 18-pin SMD female
(HC-PM254-8.5H-2x9PS, C22373949, $0.20–0.28) come to ~$0.25–0.34 per slot,
~$0.4 less. But one half has to sit on the module's underside, a
bottom-side part: that breaks D6 (Standard double-sided assembly, ~$67 more
per order, or hand soldering). The female is 8.5 mm tall, so the case would
grow ~6 mm more. And 18 header pins need ±0.1 mm alignment and ~20–35 N to
mate, more than printed carriers and two M2 screws give. Pogo pins on the
backplane press flat pads under the module: top-side only, 3 mm of height,
±0.4 mm of alignment tolerance, ~18 N, rated 10,000 cycles.

## Build one, the owner's first build (2 haptic + 3 blank): ~$440–675

What someone pays to build the finished design. No prototype, no PCB
revisions: JLC fits every part and connector, and the internal cables are
bought ready-made. Every part is on the top side of each board (D6;
[pcb.md](pcb.md)). All parts with sources: [bom.md](bom.md) (generated
from the CAD model, so it matches the assembly guide). PCB lines include
JLC's 5-board minimum, and JLC assembles at least 2 of each design, so the
builder pays for parts on 2 and ends up with a spare backplane, frame PCB,
touch band and USB board. Two haptic modules is exactly the module
design's assembly minimum.

Two orders: **JLC** (the base panel, the haptic module design, 3D prints)
and **AliExpress/Waveshare** (display board, motors, magnets, cables,
hardware).

| Item | ~Cost |
|---|---|
| ESP32-S3 + 7" 1024×600 display board (Waveshare ESP32-S3-LCD-7B, non-touch, SKU 31727; $33.99 from Waveshare) | ~$34 |
| Base panel, JLC-assembled, 2 of each: backplane (RP2350B, 90 pogo pins, connectors, motor-rail eFuse), frame PCB with 21 B3U switches, touch band with the AT42QT2120, USB board with the CH334F hub. Fabrication, fees and parts | $160–245 |
| Haptic module design, 2 assembled (5 PCBs): TMC6300 from DigiKey via Global Sourcing, MT6701, inverter, B3U, header; fabrication, setup, 5 extended types | $45–65 |
| 2× 2204 gimbal motors + magnets | $18–26 |
| Internal cables, ready-made: 100 mm USB-C to USB-C (one 90° end), 100 mm JST-GH 8-pin, 80 mm 12-pin FFC, 80 mm JST-SH 6-pin (optional: HY2.0 3-pin link lead, ~$1) | $5–8 |
| 21 clear resin key caps + 5 knob-window covers (JLC3DP SLA, one standard clear finish) | $23–46 |
| Case (tray, top plate, stand), 2 module carriers, 2 knobs and hubs, 3 blanks, in PETG at home (case from JLC3DP: +$35–75) | $12–20 |
| Screws, M3 and M2 heat-set inserts, magnets, rubber feet, shims, transfer tape, epoxy, a USB-C to USB-C cable to the PC (1.5 A+ port for full haptics) | $20–27 |
| Shipping, 2 orders | $15–35 |
| **Import duty, US** (~35% of the goods, 40% on prints) | $100–155 |

The four base boards go in one panel so JLC charges one assembly setup
fee; the module design is a second item in the same order, so it shares the
shipping and the duty line. All case parts fit a 256 mm print bed (checked
by `cad/build.py`).

### Where the money goes (first build, own printer)

| Bucket | ~Cost | Share |
|---|---|---|
| **JLC base boards** (all four, 2 of each) | **$160–245** | **37%** |
| – PCB fabrication: 5 panels, ~215 × 169 mm (`cad/build.py` estimate), 2-layer, ENIG (owner decision). JLC's fee for 4 designs in one panel, the countersink option, maybe its keyboard-PCB surcharge (~$24) for the frame PCB | $45–70 | 10% |
| – Setup, stencil, hand-solder labor: Economic $8.18 + $1.53 + $3.58; Standard $25.56 + $8.21 + $3.58 | $14–38 | 5% |
| – Extended-part fees: 16 types × $3.07 = ~$49 (Economic) | $45–55 | 9% |
| – Parts for 2 board sets (one is the spare), at LCSC prices for that quantity, 180 pogo pins ($10.7) and the inductor's pre-order minimum (32) included | $55–75 | 12% |
| – Placement: ~1,600 SMD joints × $0.0016, plus the USB-C shell legs by hand | $3–6 | 1% |
| **Haptic module design** (2 assembled): 5 PCBs ($15–25 ENIG), setup ~$10, 5 extended types ($15), parts for 2 (~$10), Global Sourcing extras ($1–10) | $45–65 | 10% |
| Import duty, US | $100–155 | 23% |
| Display board | $34 | 6% |
| SLA key caps + knob windows | $23–46 | 6% |
| Hardware + internal cables (incl. the cable to the PC) | $25–35 | 5% |
| Motors + sensor magnets (2) | $18–26 | 4% |
| Shipping, 2 orders | $15–35 | 4% |
| Case, carriers, knobs, blanks, printed at home | $12–20 | 3% |
| **Total** | **$440–675** | 100% |

Shares are of the midpoints. JLC's boards and the duty on them are about
two thirds of the build. Fees are from JLC's pricing pages (2026-09-09) and
its PCBA blog (2026-10-14); fabrication is an estimate, so the instant
quote decides it.

Levers that don't cut features:

- **Economic PCBA.** Every board is top-side only, 2-layer 1.6 mm. The base
  boards share one mouse-bite panel under 250 × 250 mm; the module boards
  are their own small designs. The finest pitch is the RP2350B's 0.4 mm,
  right at Economic's limit. That saves ~$24 of setup and stencil over
  Standard per design, and preferred extended parts load free. Keep the
  BOOTSEL switch on top: a bottom-side part forces Standard double-side
  ($51.12 + $16.42). Don't use V-cuts in the panel.
- **Basic and preferred parts (applied 2026-10-17).** The RP2350B's crystal
  is the basic C9002 the USB board uses, with 33 pF load caps (the
  ABM8-272-T3 stays as the tested fallback). The ESD arrays are the
  preferred SRV05-4-P-T7 (C85364, no loading fee). One part, the
  TPS259470ARPWR (C3662799), covers the motor rail and both VBUS branches.
  The input polymer cap is 2 × 22 µF basic ceramics (C45783); a polymer
  footprint stays in case the hot-plug test rings. The 3.3 V regulator is
  the basic AMS1117-3.3 (C6186).
- **In-stock parts (applied 2026-10-17).** The GH header is HCTL's
  HC-GH-8PWT (C3011950), a JST GH clone. The AOTA inductor stays (3 in
  stock, minimum 32, ~$8 extra): no stocked 3.3 µH part has the polarity
  mark Raspberry Pi requires.
- **TMC6300 from DigiKey** (already in the numbers): $2.44 against LCSC's
  ~$5.07.
- **First build: put the module boards in the base panel.** As a fifth
  design in the panel (if the quote allows mixed sizes), the 2 assembled
  panels give 2 haptic modules with no second setup, and the B3U and
  1N4148W fees are already paid: ~$15–20 less. It ties the module count to
  the panel count, so it only suits a first build of 2 of a type.
- **Group buy** (not planned until a device works). Builds share the fixed
  JLC cost and skip the spare set.

### Extended part types

Counted from [bom.md](bom.md), JLC's library checked 2026-10-17 (pogo pins,
module header and encoders 2026-10-19). A part used on two boards of one
design is one type; a separate design pays its own.

**Base panel: 16.** Chosen (13): RP2350B (C42415655), AOTA-B201610S3R3
inductor (C42411119), B3U-1000P (C231329, keys), HC-GH-8PWT GH header
(C3011950, both GH ends), 12-pin ZIF (C19269355, both ends), BM06B-SRSS-TB
(C160392), AT42QT2120 (C614938), SM06B-SRSS-TB (C160405), CH334F
(C5187527), mid-mount USB-C (C2894902), TYPE-C-31-M-12 (C165948),
TPS259470ARPWR (C3662799, motor rail and both VBUS branches), pogo pin
BWCD-L3W2.0H1.0 (C2988082). Not chosen yet, no basic part found (3):
reverse-mount BOOTSEL switch, VBUS TVS, ~470 µF bulk cap. Was 19 on the
old single knob board: the TMC6300, MT6701 and inverter moved to the
modules, the motor header went with them, and the pogo pin is new.

**Haptic module design: 5.** TMC6300 (Global Sourcing), MT6701 (C3003196),
SN74LVC3G04 (C139324), B3U-1000P (C231329), 1×3 vertical SMD header
(C41417360).

**Lite module design: 1.** The PEC11R encoder (one type whichever variant;
it's through-hole and hand-soldered, so JLC may not charge a feeder fee for
it: the quote decides).

Preferred extended, no fee: SRV05-4-P-T7 (C85364, all ESD arrays).
Basic: the 12 MHz crystal C9002 (both boards), the W25Q128JVSIQ flash,
1N4148W, the AMS1117-3.3 (C6186), the 22 µF ceramics (C45783), the passives
and ferrite. Add one type each for the optional HY2.0 header, the PD sink if
fitted, the input polymer cap if the hot-plug test needs it, or the
ABM8-272-T3 if the C9002 fails its start-up test.

Global Sourcing has no listed handling fee, and shipping to JLC is free.
Some sourced parts pay 3–30% Chinese import duty, prices can differ a
little from DigiKey's, and switches and connectors pay a $20 inspection
fee per kind (not the TMC6300). The quote shows it.

One small extra to check on the quote: JLC's countersink option for the
frame PCB's countersunk M2 holes, and whether it keeps the order Economic.

**Large-size fee, not in the totals.** JLC adds $57.46 when "PCB area >
650 cm²" and doesn't say what area it counts. `cad/build.py` estimates the
base panel at ~362 cm² (2 mm gaps, 5 mm rails). Two assembled panels are
~724 cm². If JLC counts the assembled area, a single build pays the fee
(~$78 with duty). The quote decides. Splitting the panel avoids it, but
costs a second setup.

**Lite modules are through-hole.** JLC hand-solders through-hole parts under
Economic assembly: the hand-soldering fee ($3.5 per order) plus ~$0.0173 per
joint (JLC's FAQ, 2026-09-09): 7 joints per encoder. Still one side, still
Economic (D6). An SMD encoder with a push switch is in stock (Alps
EC11J1525402, C209762), but only with detents; details in [bom.md](bom.md).

## Other builds: 5 haptic, 5 lite, mixed

The base is the same in every build. The per-module rows in the summary add
up the rest: for 5 haptic, the haptic design's fixed $51–77 and 5 × $20–27
of motors, parts, carriers and knobs ($495–750 in all); for 5 lite, the
lite design's $39–50 and 5 × $6–8 ($415–630). With a case from JLC3DP, add
~$35–75 to any single build.

## 5, 25 and 100 ordered together (estimate)

Per device, one order per batch (the base panel and each module design's
fees shared), no spare boards, case, carriers and knobs printed by the
builders, US duty included. Prices from the BOM at higher LCSC quantity
breaks; motors at AliExpress lot prices (V). JLC3DP SLA per cap. Not quotes.

| Base device, per device | 5 | 25 | 100 |
|---|---|---|---|
| Display board (Waveshare's list price) | $34 | $34 | $34 |
| JLC base boards: parts (5 slot connectors included), fabrication, shared fees, placement | $50–80 | $38–48 | $31–40 |
| SLA key caps + knob windows | $20–32 | $19–29 | $16–25 |
| Case (printed) | $9–15 | $9–15 | $9–15 |
| Cables + hardware | $15–22 | $13–19 | $10–16 |
| Shipping (bulk, then on to each builder) | $10–20 | $8–15 | $6–12 |
| Import duty, US (~35%) | $37–57 | $19–35 | $19–38 |
| **Base total** | **$175–260** | **$140–195** | **$125–180** |

| Per module | 5 | 25 | 100 |
|---|---|---|---|
| Haptic: motor + magnet, driver, sensor, inverter, switch, header, module PCB and its share of fees, carrier, knob, screws, duty | $24–33 | $20–26 | $16–21 |
| Lite: encoder, module PCB and fees share, carrier, knob, screws, duty | $7–10 | $5–7 | $4–5 |
| Blank: printed cover, two screws | ~$1 | ~$1 | ~$1 |

The haptic module's cost is mostly the motor ($6–9 at lot prices), the
TMC6300 ($2.44) and the MT6701, and the duty on them. The slot overhead
(module PCB, carrier, screws, and the connector in the base) is ~$1.7–2.3
per slot at 100 (above).

## Development cost (the designer's, not a builder's): ~$715–1,280

Plan changed 2026-10-18 (D3), and 2026-10-19 (D23): final parts bought
early, a throwaway test kit with bought breakouts, then **Rev A**: the base,
the backplane, **2 haptic modules and 1 lite module** (so both module types
are proven; the lite design's minimum of 2 leaves one spare) and blanks,
with one revision of whichever board fails.

| | ~Cost |
|---|---|
| Throwaway test kit (below) | $100–170 |
| Bench tools (below; skip what you have) | $70–140 |
| Spare 2204 motors (2; the other 2 are in Rev A) | $15–25 |
| Rev A: base ($345–540), haptic module design with 2 ($91–131), lite module design with 2 ($47–60), 2 blanks (includes the 7B, motors, magnets and cable bought early) | $485–735 |
| One single-board revision (only the board that fails; table below) | $45–210 |
| **Total, likely through a working device** | **$715–1,280** |

Without the tools (already owned): ~$645–1,140. Not included: a second
7B (~$46 with duty), JLC's large-size fee if the quote shows it, and a
second failed board.

### Single-board revision, per board

JLC: 5 PCBs, 2 assembled, Economic, the setup and extended-part fees for
that board alone, parts for 2 boards, shipping and 35% duty. A board
ordered alone can't share the panel's setup fee, but it's still much
less than redoing the whole panel ($270–400). The backplane and the module
boards are separate now, so a module fault doesn't touch the backplane and
the other way round.

| Board | Extended part types | ~Cost |
|---|---|---|
| Backplane (RP2350B, 90 pogo pins, connectors, eFuse, BOOTSEL; the inductor's minimum of 32) | ~10 | $150–210 |
| Haptic module (tongue and hinge, TMC6300, MT6701, inverter, switch, header) | 5 | $70–105 |
| Lite module (PEC11R) | 1 | $45–60 |
| Frame PCB (21–42 B3U, ZIF; countersinks, maybe the keyboard-PCB surcharge) | 2 | $75–145 |
| USB board (CH334F, two USB-C, two eFuses, GH header, TVS) | ~6 | $80–105 |
| Touch band (AT42QT2120, SH header) | 2 | $45–65 |

The haptic module is the likeliest to fail (hinge, motor fit and the slot
connector meet there first) and is now one of the cheaper boards to redo.
The backplane carries the RP2350B and stays the most expensive.

## Prototype (2 keys on the 7B + a knob test stand): ~$270–460 up front

Of that, ~$100–150 are final parts that go into Rev A, so the prototype
itself costs ~$170–310 (throwaway kit plus tools). Details:
[parts.md](parts.md).

**Final parts, bought early (reused in Rev A; counted in the full build):**

| Item | ~Cost |
|---|---|
| Waveshare ESP32-S3-LCD-7B | $34 |
| 4 × 2204 motors from two sellers (2 for Rev A's haptic modules + 2 spare) | $30–50 |
| Diametric magnets, 10 cm right-angle USB-C display cable | $5–10 |
| Shipping (Waveshare) | $5–15 |
| **Import duty, US** (~35%) | $26–38 |
| **Subtotal** | **$100–150** |

**Throwaway test kit:**

| Item | ~Cost |
|---|---|
| SparkFun TMC6300 breakout ROB-21867, with US shipping (no China duty) | $23–27 |
| WeAct RP2350B core board, CH334F hub module, MT6701 breakout, breadboard and jumpers (AliExpress), with ~35% duty. The core board and hub stay as the firmware dev bench | $18–31 |
| JLC order: rev C prototype frame PCB (5 made, 2 assembled with 4 B3U each), 2 + 2 clear caps, the prototype top plate (it carries the cap guides), the knob test stand, knob and hub (JLC3DP), shipping, 35–40% duty | $50–90 |
| Laser-cut acrylic base plate (US, shipping included) | $10–20 |
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
2026-10-16). clickdeck has 21 keys and up to 5 haptic knobs and costs more:
about $440–675 for the first build with 2 haptic knobs, $495–750 with 5.
Lite modules (D22) are the cheaper knobs and drop the haptics. That's accepted: it's for the knob feel
and the switch feel, which the + XL can't give. The biggest costs are
JLC's boards (fees and parts), import duty, the motors and the display
board. Sourcing the TMC6300 through Global Sourcing/DigiKey (~$2.44
instead of LCSC's ~$5.07) saves about $2.6 per haptic module (2 chips per
module design order, one is the spare), less any sourcing duty. The internal hub (2026-10-17) adds ~$25 to a single build,
mostly JLC's per-part-type fees; it buys plug-in cabling, USB updates for
both chips and reading the port's current.
