# Sourcing, cost and prototype plan review

Reviewer role: hardware/product engineer, standard review. Date: 2026-10-17. Stock and fee figures come from live pages fetched that day. They move, so check them again before paying.

## Verdict

**Go with changes** for the first purchase (AliExpress Order 1). It is cheap and mostly not wasted, but change what goes in it (buy the real 7B display and motors from two sellers; skip the 2.4" screen).
**No-go** for the JLC knob module (Order 2) until the MT6701 sourcing and footprint are fixed and the motors pass an unpowered cogging check.
The full-build cost is understated. Expect it to come in above the Stream Deck + XL until a real JLC quote proves otherwise.

## Strengths

- The sequence is sound: measure the motor before laying out the knob PCB, and build one knob before five (parts.md:110-115, knob-module.md:15).
- Every unverified claim is tracked, with how and when it gets answered (open-questions.md). The README has a clear "untested" disclaimer.
- Most risky parts have a named fallback: DRV8316 for the TMC6300, FE1.1s for the CH334F, XKB/HX parts for the B3U, SparkFun ROB-21867 if Rev 0 fails.
- Commodity parts have healthy stock: CH334F C5187527 has 8,489 at $0.63, and B3U-1000P C231329 has 110,060 at $0.19 (5+) with no NRND flag on LCSC now (open-questions.md:23 can be downgraded).
- Some pass/fail criteria are numeric and testable: press force 150–400 g, key image under ~50 ms, 20/20 taps (prototype-tests.md:22,41,49).
- The cost comparison is honest: the docs say outright that the build costs about the same as a + XL (cost.md:66-72).

## Issues

### Blocker

**B1. MT6701QT-STD is out of stock, and the doc gives the wrong package.** [decision]
- Evidence: LCSC C2913974 showed "Out of Stock" on 2026-10-17 (https://www.lcsc.com/product-detail/C2913974.html). bom.md:27 and knob-module.md:22 list it. knob-module.md:22 calls it "SOP-8", but the -QT suffix is the 3×3 QFN-16 package. The SOP-8 variant is MT6701CT (JLC C3003196, extended part).
- Effect: a footprint drawn from the doc would be wrong, and JLC can't place a part it doesn't stock.
- Recommendation: pick whichever package is in stock in **JLC's** library (not LCSC's) on the day the layout starts, and draw that footprint. Check how its MODE/SSI pins differ. Keep a pin-compatible alternative noted (AS5600 is the SimpleFOC-supported fallback, at lower resolution).

### High

**H1. Motor-driver stock is thin and has a single source.** [no-decision]
- Evidence: TMC6300-LA-T C5274455 showed **59 in stock** on 2026-10-17 at $5.93 (1+) / $5.12 (10+). bom.md:26 records 200 the same day. The -LA variant is already out (open-questions.md:15).
- Effect: the prototype needs 2, one full build needs 10 (JLC assembles two sets), and a 5-person group buy needs 25–50.
- Recommendation: before committing to the TMC6300 for five knobs, draw the DRV8316 fallback (pcb.md:39-41). Order Rev 0 promptly once the layout is ready. If Rev 0 passes, consider buying the full build's 10 drivers into JLC's private parts inventory.

**H2. The cost model leaves out US import duty and the cost of Standard PCBA.** [decision]
- Duty evidence: JLC's US tariff FAQ (updated 2026-03-25) gives a total DDP rate of **~35–92.5%** by HS code, and forum reports say ~35% is typical for assembled boards (https://jlcpcb.com/help/article/us-tariff-policy-faq). cost.md:34 has only "Shipping, 2 orders $15–35", and the AliExpress links are .us, so the owner is presumably in the US.
- Why the panel can't use Economic PCBA: the knob board's press switches are on the **underside** (pcb.md:24-27, knob-module.md:24). The motor headers (bom.md:30) and USB-C shell legs (bom.md:41-42) are through-hole. Economic PCBA is top-side SMD only. One panel (pcb.md:82-89) therefore puts **every** board on Standard double-sided assembly.
- Standard double-sided fees (JLC fee page, updated 2026-09-09, https://jlcpcb.com/help/article/pcb-assembly-price): setup $51.12, stencil $16.42, fixtures $16.42, multi-design panel $8.21, $1.53 per unique part (basic or extended; about 30–40 lines here), manual-assembly fee $3.58 plus per-joint charges. That is about **$140–160 in fees alone**, against the "one setup fee" assumed at cost.md:36-37.
- My rough estimate: the JLC order lands at about $300–420 with duty, against about $190–255 implied by cost.md:25-30. A single build comes to about **$400–600**, not $300–450 (README:165).
- Recommendation: get a real JLC quote before quoting a price anywhere. Design changes that cut cost:
  - put the press switch on the top side, or on a separate small board;
  - use SMD motor connectors (e.g. JST-SH/GH SMD);
  - use a USB-C socket with SMD legs.

**H3. The prototype buys a throwaway screen and leaves the real display untested.** [decision]
- Evidence: parts.md:16 orders a 2.4" SPI display and an ESP32-S3 devkit, against the "no parts thrown away" goal (parts.md:3). The display-side unknowns can only be answered on the 7B: whether the ESP32-S3 can do a 1024×600 redraw and USB transfers at the same time, which USB port is native, the real depths, and how the image looks through a cap at the real glass depth (open-questions.md:29,32,58; plan.md:150-151). The open-questions file puts these after the prototype.
- Recommendation: buy the Waveshare ESP32-S3-LCD-7B (SKU 31727; $33.99–38.99 on waveshare.com, 2026-10-17; check shipping cost) in Order 1 instead of the 2.4" screen and the devkit. It is a part the full build reuses, and it moves the display risk forward.

### Medium

**M1. Rev 0 is also double-sided, so its estimate is low.** [decision]
- Evidence: SW1 is on the bottom side (knob-module.md:24). The estimate is $30–45 (parts.md:79-80), and the board also has through-hole J1/J2/J3.
- Estimate: Economic, top-side only, comes to about $50–75 landed with duty. Standard double-sided adds about $60–80.
- Recommendation: have JLC fit only the top-side SMD parts, and hand-solder the B3U and the headers. The B3U is solderable with an iron; the QFN chips are not.

**M2. The riskiest mechanical question is tested last.** [no-decision]
- Evidence: whether pressing a key's far corner reliably clicks a B3U with 0.15 mm travel through the cap's tab is a go/no-go item (prototype-tests.md:32, 57-61). It sits in stage 4 / Order 3, which is ordered after the knob work (plan.md:232-234, parts.md:89-104).
- Recommendation: add the JLC3DP caps and the prototype frame PCB (already generated, hardware/proto-frame/jlc) to the **same** JLC order as Rev 0. That pays shipping and duty once and answers both feel risks together.

**M3. The tests record numbers but don't set limits for them.** [decision]
- Evidence: current while clicking and current at an end stop say only "Record" (prototype-tests.md:19-20). "Go" requires that the current "fits the power budget" (prototype-tests.md:58), but there are no limits.
- No test covers: TMC6300 temperature at a held stop; 5 V droop against the 4.6 V brownout guard (wiring.md:135); total current on a default (500 mA) port; or the 3-PWM inverter drive.
- Recommendation: add thresholds. Examples:
  - peak motor current ≤ 500 mA on a default port;
  - VBUS ≥ 4.75 V while clicking;
  - driver case temperature < 70 °C after 30 s at a stop;
  - standby ≤ 5 mA above idle.
  
  Add a cogging measure: spin the knob gently with zero current and log sensor speed ripple, or count the bumps felt per turn.

**M4. The prototype order is missing parts and tools needed for bring-up.** [no-decision]
- A current-limited 5 V supply: the bring-up needs a "bench supply with a current limit ~300 mA" (knob-module.md:36,104), but parts.md doesn't list one. A USB-C PD trigger board plus the power meter is not current-limited.
- A soldering iron and solder for J1–J3, the devkit headers and the frame PCB wire pads.
- Female-female jumper wires.
- M2 screws and 3 mm standoffs for the frame PCB (hardware/README.md:137-139). parts.md:94 lists only M3 standoffs.

**M5. Only one motor seller is planned, though motor cogging can sink the project.** [no-decision]
- Evidence: a second seller is "if budget allows" (parts.md:51-53). The AliExpress listing couldn't be checked; it redirects to a login page.
- Recommendation: buy from two sellers as standard (about $10–15 more). **Spin each motor by hand, unpowered, on arrival.** Smooth mode is zero torque, so what you feel is the motor's own cogging. This costs nothing and should gate Order 2.

**M6. The full-build BOM is incomplete.** [no-decision]
- 5 knob-press diodes are missing. The key matrix has 28 switches with one diode each (wiring.md:239-242), but the BOM lists only 21 diodes (bom.md:36).
- RP2350B support parts have no part numbers (bom.md:25,34): the core-regulator inductor (Raspberry Pi specifies a particular 3.3 µH part), the QSPI flash, the crystal, the 3.3 V regulator, and the soft-start load switch ("part TBD", wiring.md:106).
- The touch controller hasn't been chosen (bom.md:38).
- Recommendation: list these before quoting the full build. They don't block the prototype.

### Low

**L1. The touch test doesn't match the final design.** [decision] The prototype uses an MPR121 module (an NXP part that is no longer made; the AliExpress boards are clones) with copper tape under 3 mm acrylic (parts.md:21). The final design uses a controller that hasn't been chosen, on a 1.6 mm PCB under a 2 mm plate (open-questions.md:52). Pick the final controller first, or consider sensing directly on the RP2350B, which removes a part.

**L2. Docs disagree on dates and stock.** [no-decision] cost.md:3 says estimates are from 2026-10-16. Stock counts already disagree with the live pages (TMC6300 200 vs 59; MT6701 listed as available). Add a "checked on" column, or one dated stock table.

**L3. 10 + 21 B3U switches but no spares.** [no-decision] The prototype hand-solders tiny parts, so buy 20+ B3U switches (they cost about $0.19 each) plus the alternative switches.

## Missing

- A lead-time plan. Rough calendar: AliExpress to the US takes about 1–3 weeks. JLC PCBA takes about 1–2 weeks to build plus about 1 week to ship. Waveshare usually ships from China. As planned, the critical path is motor arrival → layout → JLC, about 5–7 weeks.
- A stock-check step at quote time against **JLC's** parts library, and a rule for when to reserve parts.
- Duty and taxes, in every cost table.
- A firmware-readiness check before Order 2: confirm SimpleFOC runs on the RP2350 Arduino core with the chosen PWM pins, or plan to drive Rev 0 from the ESP32-S3 first.
- A list of money at risk per order, and what to do if a gate fails.

## Actions before ordering (in order)

1. Fix B1. Look up the MT6701 variants in JLC's library, pick one that is in stock, correct the package in knob-module.md and bom.md, and record the date checked.
2. Revise Order 1:
   - add the 7B display, 2+1 motors from two sellers, the magnets, 20+ B3U plus alternatives, the RP2350B core board, the power meter, calipers, the 90° USB-C cable, and the tools from M4;
   - drop the 2.4" screen and the ESP32-S3 devkit.
   
   Expected about $90–130. Most of it carries into the full build.
3. On arrival: spin the motors unpowered, measure their bolt patterns and leads, find the 7B's native USB port, and test a full-screen redraw while sending data over USB. Stop if every motor cogs.
4. Draw the Rev 0 schematic and layout for top-side Economic assembly (M1). Get a real JLC quote including duty. Add the caps and the prototype frame PCB to the same order (M2).
5. Add numeric thresholds to prototype-tests.md (M3).
6. Before the full build: fill the BOM gaps (M6), decide on single- vs double-sided assembly and SMD connectors (H2), get a real panel quote, and update README/cost.md with the landed price.

Sources (fetched 2026-10-17): LCSC C5274455, C2913974, C5187527, C231329; JLC part C3003196; https://jlcpcb.com/help/article/pcb-assembly-price; https://jlcpcb.com/help/article/us-tariff-policy-faq; https://www.waveshare.com/esp32-s3-lcd-7b.htm; CNX Software, WeAct RP2350B core board (~$4.21, 2025).
