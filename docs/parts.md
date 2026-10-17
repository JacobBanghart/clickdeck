# Prototype parts (2 keys + 1 knob), cheapest-first

Goal: as cheap to prototype as possible, with most parts carrying over to
the full build. Unlike the full build, the prototype needs some soldering
(headers, the knob module's connectors, wires to the frame PCB). Two orders: **AliExpress** (all the loose parts) and **JLCPCB** (the knob
module, assembled). Prices are rough estimates from 2026-10-16; check
listings before ordering. The AliExpress links below are searches. Pick a
listing with good ratings and a clear pinout photo.

## Order 1 — AliExpress (~$105–185)

| Qty | Part | ~Price | Search |
|---|---|---|---|
| 1 | ESP32-S3 dev board, **N16R8 or N8R8** (must have the "R8" = 8 MB PSRAM), two USB-C ports | $6–9 | [esp32-s3 n16r8 devkit](https://www.aliexpress.us/w/wholesale-esp32-s3-n16r8-devkitc.html) |
| 1 | **2.4"** 240×320 IPS SPI display, ST7789 or ILI9341. 2.4" (not 2.0") fits 2 keys at the real 22 mm pitch plus a knob display strip | $5–8 | [2.4 inch 240x320 spi ips](https://www.aliexpress.us/w/wholesale-2.4-inch-240x320-spi-ips-display.html) |
| 2 (2-packs, from two different sellers) | **Mitoot 2204 260KV gimbal motor**, ~28 × 13 mm, 3.4 mm hollow shaft (or the same spec from a second seller) | $30–50 | [listing](https://www.aliexpress.us/item/2251832766811717.html) |
| 1 pack | Diametric (side-magnetized) magnets, 6 × 2.5 mm, for the MT6701 | $3–6 | [diametric magnet 6x2.5mm](https://www.aliexpress.us/w/wholesale-diametric-magnet-6x2.5mm.html) |
| 20+ | **Omron B3U-1000P** SMD tactile switch (plus a few same-size alternatives such as XKB TS-3025-B-A-B to compare, see [open-questions.md](open-questions.md)), 3.0 × 2.5 × 1.6 mm, crisp click, 0.15 mm travel. The only size that fits between keys at 22 mm pitch (see cad/). Operating force spreads 1.01–1.99 N, so buy extra and sort them by feel | ~$0.20–0.60 ea | [b3u-1000p](https://www.aliexpress.us/w/wholesale-b3u-1000p.html) (genuine parts are cheaper at LCSC, ~$0.19, and JLC can solder them onto the frame PCB) |
| optional | Mouse micro switches (Kailh GM 8.0 / Omron D2FC) to compare feel on the desk. They don't fit the key layout | $3–6 | [mouse micro switch set](https://www.aliexpress.us/w/wholesale-mouse-micro-switch-set.html) |
| 1 pack | 6 mm through-hole tactile switches, for the breadboard stage (B3U is surface-mount and won't plug into a breadboard) | $1–3 | [6x6 tactile switch](https://www.aliexpress.us/w/wholesale-6x6-tactile-switch.html) |
| 1 | Breadboard + jumper wire kit, machined female header strip | $4–6 | [breadboard jumper kit](https://www.aliexpress.us/w/wholesale-breadboard-jumper-wire-kit.html) |
| 1 | MPR121 capacitive touch breakout (12 electrodes, I²C) + a roll of copper tape, to test the touch band: a full-length strip of 10–12 tape segments under an offcut of the printed plate ([prototype-tests.md](prototype-tests.md)). The MPR121 is discontinued (NXP PCN16772); stock remains | $3–6 | [mpr121 module](https://www.aliexpress.us/w/wholesale-mpr121-module.html), [copper foil tape](https://www.aliexpress.us/w/wholesale-copper-foil-tape.html) |
| 1 | Digital calipers (to measure the motor bolt pattern) | $8–15 | [digital caliper](https://www.aliexpress.us/w/wholesale-digital-caliper.html) |
| 1 | USB-C power meter (inline, shows volts/amps), to measure knob current for the power budget | $8–15 | [usb c power meter](https://www.aliexpress.us/w/wholesale-usb-c-power-meter.html) |
| 1 | 0.1 g kitchen/jewelry scale, to measure press force on keys and knob | $5–10 | [0.1g digital scale](https://www.aliexpress.us/w/wholesale-0.1g-digital-scale.html) |
| 1 | 8-channel USB logic analyzer (sigrok-compatible), for the missed-press and timing tests | $5–10 | [usb logic analyzer 24mhz](https://www.aliexpress.us/w/wholesale-usb-logic-analyzer-24mhz.html) |
| 1 | **USB-C to USB-C cable, ~10 cm, one 90° side-exit (left/right) end**, USB 2.0. The same cable the full build uses for the display board: measure its plugs against the CAD (12.5 × 6.5 mm overmold assumed) and check the bend | $2–4 | [usb c to usb c 90 degree 10cm](https://www.aliexpress.us/w/wholesale-usb-c-to-usb-c-90-degree-10cm.html) |
| 1 | Small USB 2.0 hub (any) — put the two boards below behind it and build the host app's device pairing early | $3–5 | [usb 2.0 hub type c](https://www.aliexpress.us/w/wholesale-usb-2.0-hub-type-c.html) |
| 1 | RP2350B core board (48 GPIO, e.g. WeAct Studio), to run the knob module from the chip the full build uses. Many still carry A2 silicon (erratum E9): the knob module's external pull-downs cover it | $5–8 | [rp2350b core board](https://www.aliexpress.us/w/wholesale-rp2350b-core-board.html) |
| 1 | 5 V bench supply with an adjustable current limit (e.g. a CC/CV buck module plus a 12 V adapter), for knob-module bring-up at ~300 mA | $10–20 | [cc cv buck module](https://www.aliexpress.us/w/wholesale-cc-cv-buck-module.html) |
| 1 | Soldering iron and solder, for headers, the knob module's J1–J3 and the frame PCB's wires | $10–25 | [soldering iron](https://www.aliexpress.us/w/wholesale-soldering-iron.html) |
| 1 set | M2 screws, M2 × 3 mm standoffs, 0.1/0.2/0.3 mm shims (see Order 3 for all standoff lengths) | $3–6 | [m2 standoff kit](https://www.aliexpress.us/w/wholesale-m2-standoff-kit.html) |

Notes
- **Internal hub (2026-10-17):** in the full build the RP2350B runs keys,
  knobs and touch on its own USB connection, and the ESP32-S3 only draws the
  screen ([wiring.md](wiring.md)). The prototype mirrors that cheaply: knob
  module on the RP2350B board, screen and keys on the ESP32-S3, both behind
  the hub, so the knob firmware, the two-device pairing and the cable get
  tested. The ESP32-S3 can still drive the knob module if the RP2350B board
  is skipped.
- **Not in the prototype:** the JST-GH link, the FFC + ZIF and the JST-SH
  touch cable. The prototype boards don't carry those connectors (jumper
  wires do the job), and they're standard parts; the first full-build boards
  test them.
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
- Skip the breadboard, calipers, power meter, scale, logic analyzer, supply
  or iron if you
  already have them. The meter and scale are for the pass/fail tests in
  [prototype-tests.md](prototype-tests.md).

## Order 2 — JLCPCB knob module (~$30–45, after the motor arrives)

Rev 0 PCB, one knob's section of the full knob board (same tongue design),
so it isn't throwaway: it proves the design that gets repeated 5×.
Outline from CAD: `cad/out/proto_knob_module_outline.dxf`.
- **MT6701CT-STD** (SOP-8) magnetic angle sensor, centered under the motor
  shaft ([knob-module.md](knob-module.md)).
- **TMC6300** brushless driver (2–11 V, runs from USB 5 V). It's a tiny QFN
  chip, so **JLC assembles it**; it can't be hand-soldered.
- **Inverter** (SN74LVC3G04, triple) so the driver runs from 3 PWM signals,
  as in the full build. Solder jumpers to bypass it and use 6 PWM instead,
  in case the TMC6300 needs separate low-side control.
- **Press to click:** the motor sits on a tongue (U-shaped slot, hinged at
  the back) with a **B3U** switch under its front tip.
- Screw holes matching the measured motor, so the board itself keeps the
  magnet centered over the sensor (no printed jig needed).
- Header to the controller board (RP2350B or ESP32-S3): 3V3, GND on both
  ends, 3–6 PWM, standby, sensor SSI (CS/CLK/DO), press switch, DIAG. A
  polarized 2-pin connector for 5 V from the bench supply, with
  reverse-polarity protection. A 1×3 header for the motor's plug.

Cost: 5 bare boards + assembly on 2 of them (setup fee + LCSC parts +
"extended part" fees; ~$5.93 per TMC6300). Roughly $30–45 with economy shipping. Confirm both
chips are in **JLC's** parts library stock (separate from LCSC's) on quote
day: on 2026-10-17 LCSC had 59 TMC6300-LA-T and no MT6701QT.

Why not an $18 SparkFun TMC6300 breakout instead: it costs about the same as
assembly and gets thrown away later. The trade-off is risk: if the first
driver circuit has a mistake, that's a second ~$20 board and ~2 weeks. Use
the breakout as the fallback if Rev 0 has problems:
[SparkFun ROB-21867](https://www.sparkfun.com/sparkfun-brushless-motor-driver-3-phase-tmc6300.html).

## Order 3 — prototype plates, frame PCB and caps (stage 4)

Generated by `cad/build.py` into `cad/out/`:
- `proto_top_plate_3mm_acrylic.dxf`, `proto_base_plate_3mm_acrylic.dxf`:
  laser-cut 3 mm acrylic (SendCutSend/Ponoko take DXF), plus 4× M3 standoffs.
- Standoff lengths (from the model): **M2 3.3 mm** between the frame PCB and the top
  plate (3 mm plus a 0.3 mm shim; at 3.0 mm the switch is held down and may read
  pressed), **M3 21.65 mm** between the plates, **12.45 mm** for the
  display. Round to stock lengths and make up the rest with shims; keep a
  0.1/0.2 mm shim kit to tune the key stack.
- `proto_frame_pcb_outline.dxf`: import into KiCad as the board outline for
  the 2-key frame PCB (B3U switches can be JLC-assembled).
- `key_cap_clear_resin.stl`, `knob.stl`: JLC3DP.

Add to a later JLC order so it ships together:
- **JLC3DP clear resin (SLA)** prints for the caps.
  [JLC3DP clear printing guide](https://jlc3dp.com/fr/blog/clear-3d-printing-guide)
- Not laser-cut acrylic caps: sheet tolerance alone is larger than the key
  stack's budget.

## Rough total
AliExpress ~$105–185 (including test tools, supply and iron) + JLC knob
module ~$30–45 ≈ **$135–230** for the working electronics, plus roughly $30–60 later for
plates, frame PCB and caps (stage 4). Estimates; get real quotes from the
generated files.

## Sequence
Rough durations; the path is serial, so plan on 10–14 weeks to the
go/no-go and the full order.
1. Order 1 now (AliExpress to the US: 1–3 weeks).
2. While it ships: firmware/host skeleton, knob module schematic.
3. Motor arrives → spin it by hand (cogging gate) → measure bolt pattern,
   thread depth and leads → finish knob PCB layout → check JLC stock on quote
   day → Order 2 (about 1 week to build, about 1 week to ship).
4. While the PCB is being made: screen + switches + USB working on the
   breadboard (stages 1–2).
5. Knob module arrives → stage 3 (clicky/smooth/stops, press, current).
6. Order 3 (2–3 weeks) → stage 4.
7. Run the tests in [prototype-tests.md](prototype-tests.md) and decide.
8. Full order (2–3 weeks, longer if the TMC6300 or MT6701 need
   pre-ordering). Check JLC stock again on quote day.
