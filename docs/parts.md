# Prototype parts (2 keys + 1 knob), cheapest-first

Goal: as cheap to prototype as possible, with no parts that get thrown away.
Two orders: **AliExpress** (all the loose parts) and **JLCPCB** (the knob
module, assembled). Prices are rough estimates from 2026-10-16; check
listings before ordering. The AliExpress links below are searches. Pick a
listing with good ratings and a clear pinout photo.

## Order 1 — AliExpress (~$55–80)

| Qty | Part | ~Price | Search |
|---|---|---|---|
| 1 | ESP32-S3 dev board, **N16R8 or N8R8** (must have the "R8" = 8 MB PSRAM), two USB-C ports | $6–9 | [esp32-s3 n16r8 devkit](https://www.aliexpress.us/w/wholesale-esp32-s3-n16r8-devkitc.html) |
| 1 | **2.4"** 240×320 IPS SPI display, ST7789 or ILI9341. 2.4" (not 2.0") fits 2 keys at the real 22 mm pitch plus a knob display strip | $5–8 | [2.4 inch 240x320 spi ips](https://www.aliexpress.us/w/wholesale-2.4-inch-240x320-spi-ips-display.html) |
| 1 (2-pack) | **Mitoot 2204 260KV gimbal motor**, ~28 × 13 mm, 3.4 mm hollow shaft | $15–25 | [listing](https://www.aliexpress.us/item/2251832766811717.html) |
| 1 pack | Diametric (side-magnetized) magnets, 6 × 2.5 mm, for the MT6701 | $3–6 | [diametric magnet 6x2.5mm](https://www.aliexpress.us/w/wholesale-diametric-magnet-6x2.5mm.html) |
| 10 | **Omron B3U-1000P** SMD tactile switch, 3.0 × 2.5 × 1.6 mm, crisp click, 0.15 mm travel. The only size that fits between keys at 22 mm pitch (see cad/) | ~$0.30–0.60 ea | [b3u-1000p](https://www.aliexpress.us/w/wholesale-b3u-1000p.html) (also LCSC, so JLC can solder them onto the frame PCB) |
| optional | Mouse micro switches (Kailh GM 8.0 / Omron D2FC) to compare feel on the desk. They don't fit the key layout | $3–6 | [mouse micro switch set](https://www.aliexpress.us/w/wholesale-mouse-micro-switch-set.html) |
| 1 pack | 6 mm through-hole tactile switches, for the breadboard stage (B3U is surface-mount and won't plug into a breadboard) | $1–3 | [6x6 tactile switch](https://www.aliexpress.us/w/wholesale-6x6-tactile-switch.html) |
| 1 | Breadboard + jumper wire kit, machined female header strip | $4–6 | [breadboard jumper kit](https://www.aliexpress.us/w/wholesale-breadboard-jumper-wire-kit.html) |
| 1 | MPR121 capacitive touch breakout (12 electrodes, I²C) + a roll of copper tape, to test the touch band: tape electrodes under the acrylic top plate | $3–6 | [mpr121 module](https://www.aliexpress.us/w/wholesale-mpr121-module.html), [copper foil tape](https://www.aliexpress.us/w/wholesale-copper-foil-tape.html) |
| 1 | Digital calipers (to measure the motor bolt pattern) | $8–15 | [digital caliper](https://www.aliexpress.us/w/wholesale-digital-caliper.html) |
| 1 | USB-C power meter (inline, shows volts/amps), to measure knob current for the power budget | $8–15 | [usb c power meter](https://www.aliexpress.us/w/wholesale-usb-c-power-meter.html) |
| 1 | 0.1 g kitchen/jewelry scale, to measure press force on keys and knob | $5–10 | [0.1g digital scale](https://www.aliexpress.us/w/wholesale-0.1g-digital-scale.html) |

Notes
- Generic displays and ESP32 clones differ in pin order. Wire from the
  listing's pinout, not a tutorial.
- Seller specs for the 2204 disagree on KV and mounting pattern (M3 thread
  vs 12×12 / 16×16 mm M2/M3). **Measure it when it arrives.**
- Cheap gimbal motors vary a lot in cogging, which ruins smooth mode.
  If budget allows, buy a second 2204 from a different seller and compare
  by hand ([lessons.md](lessons.md) #1).
- Power the motor with short, thick leads straight from the supply, not
  through breadboard jumpers ([lessons.md](lessons.md) #2).
- MT6701 breakouts often default to ABZ/I²C mode; set the mode pad for SSI.
- Skip the breadboard, calipers, power meter or scale if you already have
  them. The meter and scale are for the pass/fail tests in
  [prototype-tests.md](prototype-tests.md).

## Order 2 — JLCPCB knob module (~$20–30, after the motor arrives)

Rev 0 PCB, one knob's section of the full knob board (same tongue design),
so it isn't throwaway: it proves the design that gets repeated 5×.
Outline from CAD: `cad/out/proto_knob_module_outline.dxf`.
- **MT6701** magnetic angle sensor, centered under the motor shaft.
- **TMC6300** brushless driver (2–11 V, runs from USB 5 V). It's a tiny QFN
  chip, so **JLC assembles it**; it can't be hand-soldered.
- **Inverter** (e.g. 74LVC1G04 ×3) so the driver runs from 3 PWM signals,
  as in the full build. Solder jumpers to bypass it and use 6 PWM instead,
  in case the TMC6300 needs separate low-side control.
- **Press to click:** the motor sits on a tongue (U-shaped slot, hinged at
  the back) with a **B3U** switch under its front tip.
- Screw holes matching the measured motor, so the board itself keeps the
  magnet centered over the sensor (no printed jig needed).
- Header to the ESP32-S3: 5 V, 3V3, GND, 3–6 PWM, sensor SSI (CS/CLK/DO),
  press switch.

Cost: 5 bare boards + assembly on 2 of them (setup fee + LCSC parts +
"extended part" fees). Roughly $20–30 with economy shipping. Confirm both
chips are in LCSC stock when ordering.

Why not an $18 SparkFun TMC6300 breakout instead: it costs about the same as
assembly and gets thrown away later. The trade-off is risk: if the first
driver circuit has a mistake, that's a second ~$20 board and ~2 weeks. Use
the breakout as the fallback if Rev 0 has problems:
[SparkFun ROB-21867](https://www.sparkfun.com/sparkfun-brushless-motor-driver-3-phase-tmc6300.html).

## Order 3 — prototype plates, frame PCB and caps (stage 4)

Generated by `cad/build.py` into `cad/out/`:
- `proto_top_plate_3mm_acrylic.dxf`, `proto_base_plate_3mm_acrylic.dxf`:
  laser-cut 3 mm acrylic (SendCutSend/Ponoko take DXF), plus 4× M3 standoffs.
- `proto_frame_pcb_outline.dxf`: import into KiCad as the board outline for
  the 2-key frame PCB (B3U switches can be JLC-assembled).
- `key_cap_clear_resin.stl`, `knob.stl`: JLC3DP.

Add to a later JLC order so it ships together:
- **JLC3DP clear resin (SLA)** prints for caps, frame and guides.
  [JLC3DP clear printing guide](https://jlc3dp.com/fr/blog/clear-3d-printing-guide)
- Alternative: laser-cut 3 mm / 5 mm cast acrylic (SendCutSend, Ponoko, or a
  local makerspace).

## Rough total
AliExpress ~$55–80 (including test tools) + JLC knob module ~$20–30 ≈
**$75–110** for the working electronics, plus roughly $30–60 later for
plates, frame PCB and caps (stage 4). Estimates; get real quotes from the
generated files.

## Sequence
1. Order 1 now.
2. While it ships: firmware/host skeleton, knob module schematic.
3. Motor arrives → measure bolt pattern → finish knob PCB layout → Order 2.
4. While the PCB is being made: screen + switches + USB working on the
   breadboard (stages 1–2).
5. Knob module arrives → stage 3 (clicky/smooth/stops, press, current).
6. Run the tests in [prototype-tests.md](prototype-tests.md) and decide.
