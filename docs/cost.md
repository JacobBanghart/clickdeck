# Cost

Rough estimates, updated 2026-10-19 (D24). Nothing here is a live quote;
JLC/LCSC prices depend on board size, quantity and part stock. **Before
ordering, get a real JLC cart quote** from the generated files, with a US
shipping address so it shows the duty.

**Cost isn't a design driver** (owner decision D1 in
[design-review.md](design-review.md)). clickdeck is built for the knob feel
and the switch feel, and features aren't cut to save money. But the numbers
here should be honest: **a single build costs more than a Stream Deck + XL**
(~$350, 36 keys, 6 dials).

**Owner target (D24, 2026-10-19): the full version (5 haptic knobs) at $250
retail at 100 units**, plus shipping and taxes. The easy cuts toward it are
applied in every table below: the DRV8311H driver instead of the TMC6300
and its inverter, the touch band off by default (an optional add-on), and,
for a 100-unit run, factory-direct motors, owner-printed resin caps and
bulk cables and hardware. Whether $250 is reachable: "Path to $250" below.

**Knobs are modules (D23).** A device is the **base** (display, keys, case,
backplane, USB board, cables: no knobs) plus one item per knob slot: a
**haptic module** (motor, software clicky/smooth), a **lite module** (push
encoder, detented or smooth as ordered, D22) or a **blank**. The owner's
first build is 2 haptic + 3 blanks; knobs can be added later. The touch
band adds ~$30 to a single build and ~$5–8 per device at 100 (below).

**Import duty (US).** The US de minimis exemption is gone, so every order
from China pays duty. JLC ships DDP (duty paid at checkout); its US tariff
FAQ gives 35–92.5% depending on the goods: PCBs and assembly 35%, stencils
90%, resin and PETG prints 40%, CNC aluminum 90% (rates from 2026-03-17,
FAQ updated 2026-09-09). 35% is used below, 40% on prints. AliExpress and
Alibaba orders also pay duty. Outside the US, replace the duty lines with
your own VAT/duty.

## Summary: base + per module

Per device, US duty included, case, carriers and knobs printed at home.
"1" is a single build with the module boards ordered in the same JLC order
as the base (each module type is its own small JLC design: 5 PCBs made, at
least 2 assembled). 5, 25 and 100 are devices ordered together (none
planned until a device works); they are estimates from the BOM and JLC's
published fees, not quotes. The 100 column uses the production plan below
(factory motors, owner-printed caps, bulk cables and hardware).

| Per device | 1 | 5 | 25 | 100 |
|---|---|---|---|---|
| **Base device** (no knobs, no touch band; 5 slot connectors included) | $320–505 | $175–255 | $155–200 | $110–140 |
| + **haptic module**, each | $18–25, plus $48–64 once per order for the module design | $22–31 | $18–24 | $11–16 |
| + **lite module**, each | $6–8, plus $39–50 once per order | $7–10 | $5–7 | $4–5 |
| + **blank**, each | ~$1 | ~$1 | ~$1 | ~$1 |
| + touch band (optional add-on) | ~$30 | ~$10–14 | ~$7–10 | ~$5–8 |

A module design's fixed cost (PCB fabrication, assembly setup, its
extended-part fees, duty) is paid once per order, however many of that
module are assembled, and JLC assembles at least 2. So one haptic module
costs ~$66–89, two ~$84–114 ($42–57 each), five ~$138–189 ($28–38 each).

**Common configurations:**

| Configuration | 1 | 5 | 25 | 100 |
|---|---|---|---|---|
| 0 knobs (5 blanks) | $325–510 | $180–260 | $160–205 | $115–145 |
| **2 haptic + 3 blank** (the owner's first build) | **$405–620** | $220–320 | $195–250 | $135–175 |
| 5 haptic (the full version) | $460–695 | $285–410 | $245–320 | **$165–215** |
| 5 lite | $390–595 | $210–305 | $180–235 | $130–165 |
| 3 haptic + 2 lite (mixed) | $475–710 | $255–370 | $220–285 | $150–200 |

Before D24 the same table read: first build $440–675, 5 haptic $495–750
for one build and $205–285 at 100. Part of the change at 5, 25 and 100 goes
the other way: the old duty lines there were lower than 35–40% of the
dutiable lines, and now they aren't (details under "5, 25 and 100").

**Adding modules later.** A later small order pays its own JLC setup and
fees for the module design ($48–64 haptic, $39–50 lite), its own shipping
and duty (~$12–27 more), and needs at least 2 assembled. Going from the
first build's 2 haptic to 5 later is ~$115–165 for 3 haptic modules (vs
~$55–75 more had all 5 been in the first order). The first order's spare
module PCBs come bare: JLC only fits parts on the ones it assembles.

## Path to $250 (D24)

The owner's target: the full version (5 haptic knobs, 21 keys, display)
at **$250 to the customer, plus shipping and taxes, at 100 units**.

**What $250 leaves for the device:**

| | Per device |
|---|---|
| Retail price | $250 |
| Kickstarter and payment fees (~8–10%) | −$20–25 |
| Spares and failures (~5%: dead boards, motors that cog, returns) | −$10–12 |
| **Left for the device at zero margin** | **~$213–220** |
| Keeping 15–25% of that as margin | ~$160–185 |

**Per device at 100 units, 5 haptic, before and after the cuts.** Each line
includes its duty; parts, prints and fees as in the tables below.

| Line | Before | After | Saved |
|---|---|---|---|
| Motor drivers ×5: TMC6300 ($2.44, DigiKey) + inverter → DRV8311H ($0.95 at 500, JLC stock) | $17–18 | ~$6.5 | ~$11 |
| Motors ×5: AliExpress lots ($6–9 + 35%) → factory-direct ($3.5–6 FOB, landed $5–9) | $40–61 | $25–45 | ~$15–16 |
| Key caps + knob windows: JLC3DP SLA ($16–25 + 40%) → owner-printed resin | $22–35 | $4–6 | ~$18–29 |
| Cables + hardware: retail packs → bulk sets of 100 (landed) | $13.5–21.6 | $7–11 | ~$6.5–10.5 |
| Touch band (its share of the panel, AT42QT2120, headers, cable, tape) | $5–8 | — (optional) | $5–8 |
| Everything else (display, the base boards, the rest of each module, case, shipping, duty on them) | ~$122–147 | same | — |
| **5 haptic, per device** | **$220–290** | **$165–215** | **~$55–75** |
| 2 haptic + 3 blank | $175–230 | $135–175 | |
| 5 lite | $160–210 | $130–165 | |

"Before" is the pre-D24 estimate at 100 ($205–285) with the duty line made
consistent: 35% of the display, boards and cables plus 40% of the SLA prints
is $32–42 per device, not the $19–38 the old table used. The research
estimate for the cuts was ~$37–70 plus the touch band (~$5–8); this table
lands at ~$55–75 with the band. Labor isn't in any per-device figure: cap
finishing plus assembly is ~0.75–1.25 h per device (75–125 h for 100).

**One-time costs, spread over the run:**

| One-time | Total | Per device at 100 | at 300 | at 500 |
|---|---|---|---|---|
| Patent clearance (professional freedom-to-operate, US + EU) before a Kickstarter | $5–15k | $50–150 | $17–50 | $10–30 |
| FCC Part 15B testing | $1–3k | $10–30 | $3–10 | $2–6 |
| Development (test kit, tools, Rev A, one revision; below) | $0.7–1.3k | $7–13 | $2–4 | $1–3 |
| Printers: resin set ($650–800) and 3–4 FDM printers ($1.2–2.2k) | $1.9–3k | $19–30 | $6–10 | $4–6 |
| **Total** | **$8.6–22k** | **$86–223** | **$29–74** | **$17–45** |

**Is $250 reachable at 100 units?**

- **Without the one-time costs** (paid separately, not recovered from the
  run): yes at roughly zero margin. The estimate of $165–215 sits at or
  under the ~$213–220 left after fees and spares. With a 15–25% margin
  (~$160–185 for the device), only the low end of the estimate gets there.
- **With the one-time costs spread over 100 units:** no. $165–215 plus
  $86–223 is $250–440 per device, over the ~$215 even at the best end.
- At **300 units** (+$29–74, and the parts get a little cheaper) it's
  borderline at zero margin; at **500 units** (+$17–45) zero margin works
  and a small margin works at the low end of the estimate.

These are estimates from listings and published fees, not quotes. The
range is wide because the motors, the display price at quantity and JLC's
real cart are unknown until they're quoted.

**Remaining levers, not taken yet** (each is real design work, held for
after Rev A or a 300-unit run):

- **Own display board:** a bare 7" panel and an ESP32-S3 module on our own
  board instead of the Waveshare 7B: ~$15–20 per device. It's the hardest
  board in the project (RGB panel timing, backlight), so not before Rev A
  works.
- **Merged main board:** the hub moves onto the backplane and the USB
  board goes: ~$8–12 per device (one board, one cable, two connectors
  less). Needs a new layout of the back of the case.

With both, 5 haptic at 100 would be ~$135–190.

**Options for the one-time costs:**

- **Run 300–500 units.** The one-time costs drop to ~$17–74 per device and
  the parts get a little cheaper. It needs demand that 100 units doesn't
  prove.
- **An at-cost group buy** instead of a Kickstarter: no platform fee (payment
  fees ~3% remain), no margin, and the earlier patent screen rated a small
  at-cost group buy as low risk, so the largest one-time line might wait.
  FCC rules for kits and group buys need checking (V).
- **Early-backer pricing:** $250 for the first backers and a higher later
  price (~$279–299), so later units carry the margin and the one-time
  costs.

## Production plan for a 100-unit run (D24)

Not planned until a device works. These are the assumptions behind the
100 column.

**Motors: factory-direct.** Unbranded 2204 260KV hollow-shaft gimbal
motors cost ~$3.5–6 FOB at a 50–100 piece minimum on Alibaba (e.g.
Dongguan HSK RC $3.50–8.50 at 50 pieces, Shenzhen Uangel $4.98–6.07),
~$5–9 landed with freight and 35% duty. Buy samples from 2–3 factories
first and measure phase resistance, KV, the bolt patterns and thread depths
(against `params.py`) and cogging by hand before a bulk order: cheap gimbal
motors vary a lot ([lessons.md](lessons.md) #1).

**Key caps and knob windows: printed by the owner in clear resin.** The
model's 21 caps and 5 windows are 61.1 cm³ (~67 g of resin); with supports
and waste ~87 g per device, ~$4–6 per device with resin, IPA, gloves, film
wear and clear coat. Printer: Elegoo Saturn 4 Ultra 16K ($420–520), a
wash and cure station ($100–150) and a clear coat; ~$650–800 one-time.
About one device per build plate, ~1–1.5 h per plate; hands-on (supports,
sanding, clear coat) ~45–75 min per device. It saves ~$16–30 per device
against JLC3DP with its 40% duty and pays for itself after ~25–50 devices.
Open: whether home-printed caps come out as clear as JLC3DP's (compare one
plate side by side, [open-questions.md](open-questions.md)).

**Case and carriers: FDM at home** (PETG, already assumed in every table).
~0.55–0.65 kg of filament and 12–20 printer-hours per device; the stand
alone is ~290 g and most of the hours (a hollower stand would cut both).
100 devices in ~3–4 weeks takes 3–4 Bambu P1S/P2S-class printers
(~$1,200–2,200).

**Cables and hardware: bulk.** Sets of 100 (USB-C and GH cables, FFC,
screws, inserts, magnets, feet) come to ~$7–11 per set landed, against
~$13.5–21.6 per set bought in retail packs. The key FFC is LCSC C80646
(12-pin, 1.0 mm, 100 mm, reverse; $0.05 at 100): LCSC has no 80 mm part,
and the model's route needs 74 mm with the top plate lifted for service, so
100 mm fits (the extra folds with the rest by the right wall; check on
Rev A).

**Labor, not in any figure:** ~0.75–1.25 h per device of cap finishing and
assembly.

## Module overhead per slot (vs the old single knob board)

What the slots cost on top of the old design, where all five knob channels
sat on one knob board. The knob channel itself (driver, sensor, switch,
header, motor, magnet, spacer, hub, cap) costs the same either way.

| Per slot | 1 build | 100 units |
|---|---|---|
| Slot connector: 18 pogo pins on the backplane (C2988082; $0.0596 at 50+, $0.0378 at 4,500+, 2026-10-19). On every slot, filled or blank, so it's in the base | $1.07 (×2 for the spare backplane JLC assembles) | $0.68 |
| Module-ID diode (and pads, which cost nothing) | ~$0.01 | ~$0.01 |
| Module PCB, 28.4 × 30.5 mm 2-layer ENIG, its own design | in the design's fixed $48–64 | $0.30–0.50, plus ~$0.05 of setup and fees |
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

## Build one, the owner's first build (2 haptic + 3 blank): ~$405–620

What someone pays to build the finished design. No prototype, no PCB
revisions: JLC fits every part and connector, and the internal cables are
bought ready-made. Every part is on the top side of each board (D6;
[pcb.md](pcb.md)). All parts with sources: [bom.md](bom.md) (generated
from the CAD model, so it matches the assembly guide). PCB lines include
JLC's 5-board minimum, and JLC assembles at least 2 of each design, so the
builder pays for parts on 2 and ends up with a spare backplane, frame PCB
and USB board. Two haptic modules is exactly the module design's assembly
minimum. No touch band (D24); it adds ~$30 to a single build.

Two orders: **JLC** (the base panel, the haptic module design, 3D prints)
and **AliExpress/Waveshare** (display board, motors, magnets, cables,
hardware).

| Item | ~Cost |
|---|---|
| ESP32-S3 + 7" 1024×600 display board (Waveshare ESP32-S3-LCD-7B, non-touch, SKU 31727; $33.99 from Waveshare) | ~$34 |
| Base panel, JLC-assembled, 2 of each: backplane (RP2350B, 90 pogo pins, connectors, motor-rail eFuse), frame PCB with 21 B3U switches, USB board with the CH334F hub. Fabrication, fees and parts | $145–225 |
| Haptic module design, 2 assembled (5 PCBs): DRV8311H, MT6701, B3U, header (all in JLC's library); fabrication, setup, 4 extended types | $45–55 |
| 2× 2204 gimbal motors + magnets | $18–26 |
| Internal cables, ready-made: 100 mm USB-C to USB-C (one 90° end), 100 mm JST-GH 8-pin, 100 mm 12-pin FFC (LCSC C80646) (optional: HY2.0 3-pin link lead, ~$1) | $4–7 |
| 21 clear resin key caps + 5 knob-window covers (JLC3DP SLA, one standard clear finish) | $23–46 |
| Case (tray, top plate, stand), 2 module carriers, 2 knobs and hubs, 3 blanks, in PETG at home (case from JLC3DP: +$35–75) | $12–20 |
| Screws, M3 and M2 heat-set inserts, magnets, rubber feet, shims, epoxy, a USB-C to USB-C cable to the PC (1.5 A+ port for full haptics) | $18–24 |
| Shipping, 2 orders | $15–35 |
| **Import duty, US** (~35% of the goods, 40% on prints) | $90–145 |

The three base boards go in one panel so JLC charges one assembly setup
fee; the module design is a second item in the same order, so it shares the
shipping and the duty line. All case parts fit a 256 mm print bed (checked
by `cad/build.py`).

### Where the money goes (first build, own printer)

| Bucket | ~Cost | Share |
|---|---|---|
| **JLC base boards** (all three, 2 of each) | **$145–225** | **36%** |
| – PCB fabrication: 5 panels, ~215 × 155 mm (`cad/build.py` estimate), 2-layer, ENIG (owner decision). JLC's fee for 3 designs in one panel, the countersink option, maybe its keyboard-PCB surcharge (~$24) for the frame PCB | $43–67 | 11% |
| – Setup, stencil, hand-solder labor: Economic $8.18 + $1.53 + $3.58; Standard $25.56 + $8.21 + $3.58 | $14–38 | 5% |
| – Extended-part fees: 13 types × $3.07 = ~$40 (Economic) | $40–48 | 9% |
| – Parts for 2 board sets (one is the spare), at LCSC prices for that quantity, 180 pogo pins ($10.7) and the inductor's pre-order minimum (32) included | $48–68 | 11% |
| – Placement: ~1,500 SMD joints × $0.0016, plus the USB-C shell legs by hand | $3–6 | 1% |
| **Haptic module design** (2 assembled): 5 PCBs ($15–25 ENIG), setup ~$10, 4 extended types ($12), parts for 2 (~$8) | $45–55 | 10% |
| Import duty, US | $90–145 | 23% |
| Display board | $34 | 7% |
| SLA key caps + knob windows | $23–46 | 7% |
| Hardware + internal cables (incl. the cable to the PC) | $22–31 | 5% |
| Motors + sensor magnets (2) | $18–26 | 4% |
| Shipping, 2 orders | $15–35 | 5% |
| Case, carriers, knobs, blanks, printed at home | $12–20 | 3% |
| **Total** | **$405–620** | 100% |

Shares are of the midpoints. JLC's boards and the duty on them are about
three fifths of the build. Fees are from JLC's pricing pages (2026-09-09)
and its PCBA blog (2026-10-14); fabrication is an estimate, so the instant
quote decides it.

Levers that don't cut features:

- **Economic PCBA.** Every board is top-side only, 2-layer 1.6 mm. The base
  boards share one mouse-bite panel under 250 × 250 mm; the module boards
  are their own small designs. The finest pitch is 0.4 mm (the RP2350B and
  the DRV8311H), right at Economic's limit. That saves ~$24 of setup and
  stencil over Standard per design, and preferred extended parts load free.
  Keep the BOOTSEL switch on top: a bottom-side part forces Standard
  double-side ($51.12 + $16.42). Don't use V-cuts in the panel.
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
- **DRV8311H driver (D24, applied):** $0.95–1.38 from JLC's own stock,
  against the TMC6300's $2.44 through Global Sourcing plus the inverter
  and its fee. ~$2 per module at 100 with duty, and no Global Sourcing
  extras on a single build.
- **Touch band off by default (D24, applied):** three extended types, a
  chip, two headers, a cable and the tape less: ~$30 on a single build.
- **First build: put the module boards in the base panel.** As a fourth
  design in the panel (if the quote allows mixed sizes), the 2 assembled
  panels give 2 haptic modules with no second setup, and the B3U and
  1N4148W fees are already paid: ~$15–20 less. It ties the module count to
  the panel count, so it only suits a first build of 2 of a type.
- **Group buy** (not planned until a device works). Builds share the fixed
  JLC cost and skip the spare set.

### Extended part types

Counted from [bom.md](bom.md), JLC's library checked 2026-10-17 (pogo pins,
module header and encoders 2026-10-19, driver 2026-10-19). A part used on
two boards of one design is one type; a separate design pays its own.

**Base panel: 13.** Chosen (10): RP2350B (C42415655), AOTA-B201610S3R3
inductor (C42411119), B3U-1000P (C231329, keys), HC-GH-8PWT GH header
(C3011950, both GH ends), 12-pin ZIF (C19269355, both ends), CH334F
(C5187527), mid-mount USB-C (C2894902), TYPE-C-31-M-12 (C165948),
TPS259470ARPWR (C3662799, motor rail and both VBUS branches), pogo pin
BWCD-L3W2.0H1.0 (C2988082). Not chosen yet, no basic part found (3):
reverse-mount BOOTSEL switch, VBUS TVS, ~470 µF bulk cap. **The touch band
adds 3** (AT42QT2120 C614938, SM06B-SRSS-TB C160405 on the band, and the
backplane's BM06B-SRSS-TB C160392), 16 in all. Was 19 on the old single
knob board.

**Haptic module design: 4.** DRV8311HRRWR (C5218862), MT6701 (C3003196),
B3U-1000P (C231329), 1×3 vertical SMD header (C41417360). Was 5 with the
TMC6300 and the SN74LVC3G04 inverter (C139324).

**Lite module design: 1.** The PEC11R encoder (one type whichever variant;
it's through-hole and hand-soldered, so JLC may not charge a feeder fee for
it: the quote decides).

Preferred extended, no fee: SRV05-4-P-T7 (C85364, all ESD arrays).
Basic: the 12 MHz crystal C9002 (both boards), the W25Q128JVSIQ flash,
1N4148W, the AMS1117-3.3 (C6186), the 22 µF ceramics (C45783), the passives
and ferrite. Add one type each for the optional HY2.0 header, the PD sink if
fitted, the input polymer cap if the hot-plug test needs it, or the
ABM8-272-T3 if the C9002 fails its start-up test.

Global Sourcing is only needed for the TMC6300 fallback now. It has no
listed handling fee, and shipping to JLC is free; some sourced parts pay
3–30% Chinese import duty, and switches and connectors pay a $20 inspection
fee per kind. The quote shows it.

One small extra to check on the quote: JLC's countersink option for the
frame PCB's countersunk M2 holes, and whether it keeps the order Economic.

**Large-size fee, not in the totals.** JLC adds $57.46 when "PCB area >
650 cm²" and doesn't say what area it counts. `cad/build.py` estimates the
base panel at ~334 cm² without the touch band (362 cm² with it; 2 mm gaps,
5 mm rails). Two assembled panels are ~668 cm², still 18 cm² over. If JLC
counts the assembled area, a single build pays the fee (~$78 with duty).
The quote decides. Splitting the panel avoids it, but costs a second
setup.

**Lite modules are through-hole.** JLC hand-solders through-hole parts under
Economic assembly: the hand-soldering fee ($3.5 per order) plus ~$0.0173 per
joint (JLC's FAQ, 2026-09-09): 7 joints per encoder. Still one side, still
Economic (D6). An SMD encoder with a push switch is in stock (Alps
EC11J1525402, C209762), but only with detents; details in [bom.md](bom.md).

## Other builds: 5 haptic, 5 lite, mixed

The base is the same in every build. The per-module rows in the summary add
up the rest: for 5 haptic, the haptic design's fixed $48–64 and 5 × $18–25
of motors, parts, carriers and knobs ($460–695 in all); for 5 lite, the
lite design's $39–50 and 5 × $6–8 ($390–595). With a case from JLC3DP, add
~$35–75 to any single build; with the touch band, ~$30.

## 5, 25 and 100 ordered together (estimate)

Per device, one order per batch (the base panel and each module design's
fees shared), no spare boards, case, carriers and knobs printed by the
builders, US duty included. Prices from the BOM at higher LCSC quantity
breaks. At 5 and 25: motors at AliExpress lot prices, caps from JLC3DP. At
100: the production plan above. Not quotes.

| Base device, per device | 5 | 25 | 100 |
|---|---|---|---|
| Display board (Waveshare's list price) | $34 | $34 | $34 |
| JLC base boards: parts (5 slot connectors included), fabrication, shared fees, placement | $47–76 | $36–45 | $28–36 |
| Key caps + knob windows | $20–32 (JLC3DP) | $19–29 (JLC3DP) | $4–6 (owner-printed, no duty) |
| Case (printed) | $9–15 | $9–15 | $9–15 |
| Cables + hardware | $14–21 | $12–18 | $7–11 (bulk, landed with duty) |
| Shipping (bulk, then on to each builder) | $10–20 | $8–15 | $6–12 |
| Import duty, US (35% on the display, boards, cables and hardware; 40% on SLA prints) | $41–59 | $36–46 | $22–25 |
| **Base total** | **$175–255** | **$155–200** | **$110–140** |

The duty lines are recomputed from the lines above them (D24). The old
table used $37–57, $19–35 and $19–38, lower than the rates allow at 25 and
100.

| Per module | 5 | 25 | 100 |
|---|---|---|---|
| Haptic: motor + magnet, driver, sensor, switch, header, module PCB and its share of fees, carrier, knob, screws, duty | $22–31 | $18–24 | $11–16 ($14–19 with AliExpress motors) |
| Lite: encoder, module PCB and fees share, carrier, knob, screws, duty | $7–10 | $5–7 | $4–5 |
| Blank: printed cover, two screws | ~$1 | ~$1 | ~$1 |

The haptic module's cost is mostly the motor ($5–9 landed from a factory at
100, $6–9 plus duty from AliExpress), the MT6701 and the DRV8311H ($0.95),
and the duty on them. The slot overhead (module PCB, carrier, screws, and
the connector in the base) is ~$1.7–2.3 per slot at 100 (above).

## Development cost (the designer's, not a builder's): ~$715–1,265

Plan changed 2026-10-18 (D3), and 2026-10-19 (D23, D24): final parts bought
early, a throwaway test kit with bought breakouts and one small driver bench
board, then **Rev A**: the base, the backplane, **2 haptic modules and
1 lite module** (so both module types are proven; the lite design's minimum
of 2 leaves one spare) and blanks, with one revision of whichever board
fails.

| | ~Cost |
|---|---|
| Throwaway test kit (below) | $130–210 |
| Bench tools (below; skip what you have) | $70–140 |
| Spare 2204 motors (2; the other 2 are in Rev A) | $15–25 |
| Rev A: base ($320–505), haptic module design with 2 ($84–114), lite module design with 2 ($47–60), 2 blanks (includes the 7B, motors, magnets and cable bought early) | $455–680 |
| One single-board revision (only the board that fails; table below) | $45–210 |
| **Total, likely through a working device** | **$715–1,265** |

Without the tools (already owned): ~$645–1,125. Not included: a second
7B (~$46 with duty), JLC's large-size fee if the quote shows it, a touch
band (~$30), and a second failed board.

### Single-board revision, per board

JLC: 5 PCBs, 2 assembled, Economic, the setup and extended-part fees for
that board alone, parts for 2 boards, shipping and 35% duty. A board
ordered alone can't share the panel's setup fee, but it's still much
less than redoing the whole panel ($250–380). The backplane and the module
boards are separate now, so a module fault doesn't touch the backplane and
the other way round.

| Board | Extended part types | ~Cost |
|---|---|---|
| Backplane (RP2350B, 90 pogo pins, connectors, eFuse, BOOTSEL; the inductor's minimum of 32) | ~9 | $145–205 |
| Haptic module (tongue and hinge, DRV8311H, MT6701, switch, header) | 4 | $65–95 |
| Lite module (PEC11R) | 1 | $45–60 |
| Frame PCB (21–42 B3U, ZIF; countersinks, maybe the keyboard-PCB surcharge) | 2 | $75–145 |
| USB board (CH334F, two USB-C, two eFuses, GH header, TVS) | ~6 | $80–105 |
| Touch band, optional (AT42QT2120, SH header) | 2 | $45–65 |

The haptic module is the likeliest to fail (hinge, motor fit, the new
driver and the slot connector meet there first) and is one of the cheaper
boards to redo. The backplane carries the RP2350B and stays the most
expensive.

## Prototype (2 keys on the 7B + a knob test stand): ~$300–500 up front

Of that, ~$100–150 are final parts that go into Rev A, so the prototype
itself costs ~$200–350 (throwaway kit plus tools). Details:
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
| Driver bench board (D24), in the same JLC order: 56 × 40 mm 2-layer, HASL, 5 made and 2 assembled with a DRV8311H and an SS6343M channel (2 extended types, $6.14), headers soldered by hand; 35% duty, no extra shipping. ENIG adds ~$15–20 | $30–40 |
| Laser-cut acrylic base plate (US, shipping included) | $10–20 |
| **Subtotal** | **$130–210** |

An earlier estimate (~$50–65) counted only the kit's sticker prices.
Shipping, duty on the JLC and AliExpress parts, and the plates add the
rest.

**Bench tools (kept):** calipers, USB-C power meter, 0.1 g scale, logic
analyzer, current-limited 5 V supply, soldering iron (the breakouts' and
the bench board's headers; Rev A's heat-set inserts), M2/M3 screws,
standoffs and shims: $50–105, ~$70–140 with duty.

## Comparison

A Stream Deck + XL (36 keys, 6 dials) is about $350 (US reseller listing,
2026-10-16). clickdeck has 21 keys and up to 5 haptic knobs and costs more
to build once: about $405–620 for the first build with 2 haptic knobs,
$460–695 with 5. At 100 units the full version comes to ~$165–215 per
device before one-time costs (the target and what's missing: "Path to
$250"). Lite modules (D22) are the cheaper knobs and drop the haptics.
That's accepted: it's for the knob feel and the switch feel, which the
+ XL can't give. The biggest costs are JLC's boards (fees and parts),
import duty, the display board and the motors. The internal hub
(2026-10-17) adds ~$25 to a single build, mostly JLC's per-part-type fees;
it buys plug-in cabling, USB updates for both chips and reading the port's
current.
