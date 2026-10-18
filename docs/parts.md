# Prototype parts (2 keys + 1 knob on the 7B)

Goal: a prototype that retires the full build's risks before the expensive
order, with most parts carrying over. Owner decision D3
([design-review.md](design-review.md)) widened it: the real Waveshare 7B
instead of a small screen and dev board, and one JLC order that carries the
Rev 0 knob module, a "Rev 0.5" test board (RP2350B + CH334F hub + touch
controller + the full build's connectors), the prototype frame PCB and the
caps. Unlike the full build, the prototype needs some soldering (headers,
the knob module's connectors). Three orders: **AliExpress + Waveshare**
(loose parts and the display board), **JLCPCB** (all prototype boards,
assembled, plus caps and knobs) and the **laser-cut plates**. Prices are
rough estimates from 2026-10-17, before US import duty (see
[cost.md](cost.md)); check listings before ordering. The AliExpress links below are searches. Pick a
listing with good ratings and a clear pinout photo.

## Order 1 — AliExpress + Waveshare (~$120–195)

| Qty | Part | ~Price | Search |
|---|---|---|---|
| 1 (2 if the budget allows) | **Waveshare ESP32-S3-LCD-7B** (non-touch, SKU 31727), the full build's display board. Firmware, flash-write glitches, throughput and the key stack get tested on the real panel. A second board covers Waveshare revising it mid-project | $34 each | [Waveshare](https://www.waveshare.com/esp32-s3-lcd-7b.htm) |
| 2 (2-packs, from two different sellers) | **Mitoot 2204 260KV gimbal motor**, ~28 × 13 mm, 3.4 mm hollow shaft (or the same spec from a second seller) | $30–50 | [listing](https://www.aliexpress.us/item/2251832766811717.html) |
| 1 pack | Diametric (side-magnetized) magnets, 6 × 2.5 mm, for the MT6701 | $3–6 | [diametric magnet 6x2.5mm](https://www.aliexpress.us/w/wholesale-diametric-magnet-6x2.5mm.html) |
| 20+ | **Omron B3U-1000P** SMD tactile switch (plus a few same-size alternatives such as XKB TS-3025-B-A-B to compare, see [open-questions.md](open-questions.md)), 3.0 × 2.5 × 1.6 mm, crisp click, 0.15 mm travel. The only size that fits between keys at 22 mm pitch (see cad/). Operating force spreads 1.01–1.99 N, so buy extra and sort them by feel | ~$0.20–0.60 ea | [b3u-1000p](https://www.aliexpress.us/w/wholesale-b3u-1000p.html) (genuine parts are cheaper at LCSC, ~$0.19, and JLC can solder them onto the frame PCB) |
| optional | Mouse micro switches (Kailh GM 8.0 / Omron D2FC) to compare feel on the desk. They don't fit the key layout | $3–6 | [mouse micro switch set](https://www.aliexpress.us/w/wholesale-mouse-micro-switch-set.html) |
| 1 pack | 6 mm through-hole tactile switches, for the breadboard stage (B3U is surface-mount and won't plug into a breadboard) | $1–3 | [6x6 tactile switch](https://www.aliexpress.us/w/wholesale-6x6-tactile-switch.html) |
| 1 | Breadboard + jumper wire kit, machined female header strip | $4–6 | [breadboard jumper kit](https://www.aliexpress.us/w/wholesale-breadboard-jumper-wire-kit.html) |
| 1 roll | Copper foil tape, for the touch test: a full-length strip of 10–12 tape segments under an offcut of the printed plate, read by the AT42QT2120 on the Rev 0.5 board ([prototype-tests.md](prototype-tests.md)) | $2–3 | [copper foil tape](https://www.aliexpress.us/w/wholesale-copper-foil-tape.html) |
| 1 | Digital calipers (to measure the motor bolt pattern) | $8–15 | [digital caliper](https://www.aliexpress.us/w/wholesale-digital-caliper.html) |
| 1 | USB-C power meter (inline, shows volts/amps), to measure knob current for the power budget | $8–15 | [usb c power meter](https://www.aliexpress.us/w/wholesale-usb-c-power-meter.html) |
| 1 | 0.1 g kitchen/jewelry scale, to measure press force on keys and knob | $5–10 | [0.1g digital scale](https://www.aliexpress.us/w/wholesale-0.1g-digital-scale.html) |
| 1 | 8-channel USB logic analyzer (sigrok-compatible), for the missed-press and timing tests | $5–10 | [usb logic analyzer 24mhz](https://www.aliexpress.us/w/wholesale-usb-logic-analyzer-24mhz.html) |
| 1 | **USB-C to USB-C cable, ~10 cm, one 90° side-exit (left/right) end**, USB 2.0. The same cable the full build uses for the display board: measure its plugs against the CAD (12.5 × 6.5 mm overmold assumed) and check the bend | $2–4 | [usb c to usb c 90 degree 10cm](https://www.aliexpress.us/w/wholesale-usb-c-to-usb-c-90-degree-10cm.html) |
| 1 | Small USB 2.0 hub (any) — put the 7B and the RP2350B core board behind it and build the configurator's device pairing before the Rev 0.5 board arrives | $3–5 | [usb 2.0 hub type c](https://www.aliexpress.us/w/wholesale-usb-2.0-hub-type-c.html) |
| 1 | RP2350B core board (48 GPIO, e.g. WeAct Studio), for knob and keymap firmware before the Rev 0.5 board arrives. Many still carry A2 silicon (erratum E9): the knob module's external pull-downs cover it | $5–8 | [rp2350b core board](https://www.aliexpress.us/w/wholesale-rp2350b-core-board.html) |
| 1 | 5 V bench supply with an adjustable current limit (e.g. a CC/CV buck module plus a 12 V adapter), for knob-module bring-up at ~300 mA | $10–20 | [cc cv buck module](https://www.aliexpress.us/w/wholesale-cc-cv-buck-module.html) |
| 1 | Soldering iron and solder, for headers, the knob module's J1–J3 and the frame PCB's wires | $10–25 | [soldering iron](https://www.aliexpress.us/w/wholesale-soldering-iron.html) |
| 1 set | M2 and M3 screws, M2 × 3 mm standoffs, M3 standoffs, 0.1/0.2/0.3 mm shims, M2 set screws (see Order 3 for all standoff lengths) | $4–8 | [m2 standoff kit](https://www.aliexpress.us/w/wholesale-m2-standoff-kit.html) |

Notes
- **Internal hub (2026-10-17):** in the full build the RP2350B runs keys,
  knobs and touch on its own USB connection, and the ESP32-S3 only draws the
  screen ([wiring.md](wiring.md)). The prototype mirrors that: the 7B draws
  the screen, and the Rev 0.5 board carries the hub, the RP2350B, the knob
  module header, the touch controller and the full build's connectors
  (JST-GH link, FFC + ZIF, JST-SH, GPIO6 link). Until it arrives, the
  RP2350B core board and a store-bought hub stand in.
- **Motor plug:** the Rev 0 module has a 1×3 2.54 mm header for the motor
  ([knob-module.md](knob-module.md)). Check the plug on the motors that
  arrive.
- Generic displays and ESP32 clones differ in pin order. Wire from the
  listing's pinout, not a tutorial.
- Seller specs for the 2204 disagree on KV and mounting pattern (M3 thread
  vs 12×12 / 16×16 mm M2/M3). **Measure it when it arrives.**
- Cheap gimbal motors vary a lot in cogging, which ruins smooth mode
  ([lessons.md](lessons.md) #1). Buy from two sellers and spin each motor by
  hand, unpowered, on arrival. **Gate:** don't place Order 2 until at least
  one motor feels smooth.
- Power the motor with short, thick leads straight from the supply, not
  through breadboard jumpers ([lessons.md](lessons.md) #2).
- MT6701 breakouts often default to ABZ/I²C mode; set the mode pad for SSI.
- Skip the hub, core board, breadboard, calipers, power meter, scale,
  logic analyzer, supply or iron if you
  already have them. The meter and scale are for the pass/fail tests in
  [prototype-tests.md](prototype-tests.md).

## Order 2 — JLCPCB prototype panel (~$75–125, after the motor arrives)

One order, one shipping and duty charge. Everything waits for the motor,
because the knob module's holes come from measuring it.

### Rev 0 knob module

One knob's section of the full knob board (same tongue design), so it isn't
throwaway: it proves the design that gets repeated 5×.
Outline from CAD: `cad/out/proto_knob_module_outline.dxf`.
- **MT6701CT-STD** (SOP-8) magnetic angle sensor, centered under the motor
  shaft ([knob-module.md](knob-module.md)).
- **TMC6300** brushless driver (2–11 V, runs from USB 5 V). It's a tiny QFN
  chip, so **JLC assembles it**; it can't be hand-soldered.
- **Inverter** (SN74LVC3G04, triple) so the driver runs from 3 PWM signals,
  as in the full build. Solder jumpers to bypass it and use 6 PWM instead,
  in case the TMC6300 needs separate low-side control.
- **Press to click:** the motor sits on a tongue (U-shaped slot, hinged at
  the back). A **B3U** switch sits on the top side of the fixed front
  border; an arm on the printed motor spacer reaches over the slot, and an
  M2×3 set screw in the arm is the adjustable striker. The hinge is tunable
  (perforations). Do the scrap-FR-4 hinge test before ordering
  ([knob-module.md](knob-module.md)).
- Screw holes matching the measured motor, so the board itself keeps the
  magnet centered over the sensor (no printed jig needed).
- Header to the controller (the Rev 0.5 board or an RP2350B core board): 3V3, GND on both
  ends, 3–6 PWM, standby, sensor SSI (CS/CLK/DO), press switch, DIAG. A
  polarized 2-pin connector for 5 V from the bench supply, with
  reverse-polarity protection. A 1×3 header for the motor's plug.

TMC6300: LCSC had only 59 TMC6300-LA-T on 2026-10-17 ($5.93). For Rev 0
that's fine; for the full build, source it through JLC Global Sourcing or
consign it from DigiKey (~$2.44), and reserve the full-build quantity once
Rev 0 passes. Confirm the MT6701CT-STD is in **JLC's** parts library stock
(separate from LCSC's) on quote day.

Fallback if Rev 0's driver circuit has a mistake: an $18 SparkFun TMC6300
breakout
([ROB-21867](https://www.sparkfun.com/sparkfun-brushless-motor-driver-3-phase-tmc6300.html)).

### Rev 0.5 test board

Outline only so far: 70 × 45 mm, `cad/out/proto_rev05_board_outline.dxf`.
Everything the full build adds that the knob module doesn't test
([pcb.md](pcb.md)): RP2350B with its support parts, CH334F hub with
crystal, external and downstream USB-C, power switches, CC sensing, a
JST-GH link pair, a 12-pin ZIF, JST-SH plus the **AT42QT2120** touch
controller (LCSC C614938), the GPIO6 link header, BOOTSEL, and a header for
the Rev 0 knob module. Bought with it: a 100 mm JST-GH 8-pin cable, an
80 mm 12-pin FFC, an 80 mm JST-SH 6-pin cable and a 50 mm HY2.0 3-pin
lead, the same as the full build ([wiring.md](wiring.md)).

### Rev C frame PCB, caps and knobs

- `proto_frame_pcb_outline.dxf` / [hardware/](../hardware/): the prototype
  frame PCB, rev C, 58.3 × 30.7 mm: the full build's two top-left keys at
  the same place on the 7B. Four B3U footprints, JLC-assembled: SW1/SW2
  under the keys, SW3/SW4 the optional second switches to compare one
  switch per key with two. 4 M2 pan-head holes off the glass and 2
  countersunk holes over it (JLC's countersink option). The prototype also
  has knob 0 with its display window and a full-length touch band.
- `key_cap_clear_resin.stl`, `knob.stl`: **JLC3DP clear resin (SLA)**, one
  standard clear finish
  ([JLC3DP clear printing guide](https://jlc3dp.com/fr/blog/clear-3d-printing-guide)).
  Order both cap versions: one-nub caps (`key_cap_clear_resin.stl`) for
  the one-switch test and two-nub caps (`key_cap_two_nub_clear_resin.stl`)
  for two switches.
- Not laser-cut acrylic caps: sheet tolerance alone is larger than the key
  stack's budget.

## Order 3 — laser-cut plates

Generated by `cad/build.py` into `cad/out/`:
- `proto_top_plate_3mm_acrylic.dxf`, `proto_base_plate_3mm_acrylic.dxf`:
  laser-cut 3 mm acrylic (SendCutSend/Ponoko take DXF), sized for the 7B.
  The assembled prototype is 183.7 × 149.5 mm and 30.5 mm to the top plate.
- Standoff lengths (from the model): **M3 24.5 mm** between the plates
  (six, at the corners and sides), **M3 12.6 mm** from the base plate to
  the 7B's four tabs, **M2 3.3 mm** between the frame PCB and the top plate
  (3 mm plus a 0.3 mm shim; at 3.0 mm the switch is held down and may read
  pressed), **M2 2.0 mm** under the knob module and the Rev 0.5 board.
  Round to stock lengths and make up the rest with shims; keep a 0.1/0.2 mm
  shim kit to tune the key stack.

## Rough total
Order 1 ~$120–195 (including the 7B, test tools, supply and iron) + JLC
panel ~$75–125 + plates ~$15–30 ≈ **$210–350** before US import duty
(~$60–110 more; [cost.md](cost.md)). Estimates; get real quotes from the
generated files.

## Sequence
Rough durations; the path is serial, so plan on 10–14 weeks to the
go/no-go and the full order.
1. Order 1 now (AliExpress to the US: 1–3 weeks).
2. While it ships: firmware skeletons (ESP-IDF on the 7B, arduino-pico on
   the core board), configurator skeleton, knob module and Rev 0.5
   schematics, scrap-FR-4 hinge test.
3. Motor arrives → spin it by hand (cogging gate) → measure bolt pattern,
   thread depth and leads → finish the knob module layout → check JLC stock
   on quote day → Order 2 (about 1 week to build, about 1 week to ship) and
   Order 3 at the same time.
4. While the boards are being made: images over WebUSB on the 7B, switches
   and keymap on the core board (stages 1–2).
5. Boards arrive → stage 3 (knob: clicky/smooth/stops, press, current),
   3b (touch), 3c (USB and connectors), stage 4 (keys).
7. Run the tests in [prototype-tests.md](prototype-tests.md) and decide.
8. Full order (2–3 weeks, longer if the TMC6300 or MT6701 need
   pre-ordering). Check JLC stock again on quote day.
