# Prototype parts (2 keys on the 7B + a knob test stand)

Plan changed 2026-10-18 (D3 in [design-review.md](design-review.md)). The
prototype no longer has custom knob or controller boards. It has three
parts:

1. **Final parts, bought early.** The Waveshare 7B, six 2204 motors (5 + 1
   spare), the magnets and the internal display cable. They get tested on
   the bench and then go into the full build ("Rev A").
2. **A throwaway test kit.** Bought breakouts for the knob (SparkFun
   TMC6300, an MT6701 board), a WeAct RP2350B core board and a CH334F hub
   module (both stay as the firmware dev bench), and one custom PCB: the
   rev C 2-key frame PCB on the real 7B, with 2 + 2 caps and laser-cut
   plates. A printed knob test stand holds the motor over the sensor.
3. **Free tests:** the scrap-FR-4 hinge test (D10).

Dropped: the Rev 0 knob module and the Rev 0.5 test board. Rev A is the
first time the hinge, the motor mount fit, our RP2350B, hub and touch
circuits and the connectors meet. Plan on one revision of whichever board
fails, and order only that board ([cost.md](cost.md)).

Prices are rough estimates from 2026-10-18, before US import duty (see
[cost.md](cost.md)). Check listings before ordering. The AliExpress links
are searches: pick a listing with good ratings and a clear pinout photo.

## Order 1: Waveshare (~$34–68, final part)

| Qty | Part | ~Price | Link |
|---|---|---|---|
| 1 (2 if the budget allows) | **Waveshare ESP32-S3-LCD-7B** (non-touch, SKU 31727), the full build's display board. Firmware, flash-write glitches, throughput and the key stack get tested on the real panel; then it goes into Rev A. A second board covers Waveshare revising it mid-project | $34 each | [Waveshare](https://www.waveshare.com/esp32-s3-lcd-7b.htm) |

## Order 2: AliExpress (~$115–215)

### Final parts (go into Rev A)

| Qty | Part | ~Price | Search |
|---|---|---|---|
| 6 (5 + 1 spare), from two sellers | **Mitoot 2204 260KV gimbal motor**, ~28 × 13 mm, 3.4 mm hollow shaft (or the same spec from a second seller) | $45–75 | [listing](https://www.aliexpress.us/item/2251832766811717.html) |
| 1 pack | Diametric (side-magnetized) magnets, 6 × 2.5 mm, for the MT6701 | $3–6 | [diametric magnet 6x2.5mm](https://www.aliexpress.us/w/wholesale-diametric-magnet-6x2.5mm.html) |
| 1 | **USB-C to USB-C cable, ~10 cm, one 90° side-exit (left/right) end**, USB 2.0. The full build's display cable: measure its plugs against the CAD (12.5 × 6.5 mm overmold assumed) and check the bend | $2–4 | [usb c to usb c 90 degree 10cm](https://www.aliexpress.us/w/wholesale-usb-c-to-usb-c-90-degree-10cm.html) |

### Test kit (throwaway, or kept as the dev bench)

| Qty | Part | ~Price | Search |
|---|---|---|---|
| 1 | **WeAct Studio RP2350B core board** (48 GPIO, 16 MB flash, USB-C). Knob, key and keymap firmware runs here until Rev A, and it stays as the firmware dev bench. Many still carry A2 silicon (erratum E9): add 10 kΩ pull-downs on the driver's standby and PWM lines | $5–8 | [weact rp2350b](https://www.aliexpress.us/w/wholesale-weact-rp2350b.html) |
| 1 | **CH334F USB hub module** (the full build's hub chip). The 7B and the core board sit behind it, so the configurator's two-device pairing gets built on the real hub chip. Also stays on the bench. US option: [Adafruit 5997](https://www.adafruit.com/product/5997) | $3–6 | [ch334f usb hub](https://www.aliexpress.us/w/wholesale-ch334f-usb-hub.html) |
| 1 | **MT6701 breakout** (magnetic angle sensor). Sits under the motor in the knob test stand. Set its mode pad for SSI (many default to ABZ/I²C). Measure its width: the stand's rails assume 16 mm (`MT6701_BREAKOUT` in `cad/params.py`) | $2–4 | [mt6701 magnetic encoder module](https://www.aliexpress.us/w/wholesale-mt6701-magnetic-encoder-module.html) |
| 1 | Breadboard + jumper wire kit (M-M, M-F, F-F) | $3–5 | [breadboard jumper kit](https://www.aliexpress.us/w/wholesale-breadboard-jumper-wire-kit.html) |
| optional | A few same-size alternatives to the B3U (XKB TS-3025-B-A-B and others, see [open-questions.md](open-questions.md)), to feel on the desk next to the frame PCB's B3Us | $2–4 | [3x2.5 tactile switch](https://www.aliexpress.us/w/wholesale-3x2.5-tactile-switch.html) |

### Tools (kept; skip what you have)

| Qty | Part | ~Price | Search |
|---|---|---|---|
| 1 | Digital calipers (motor bolt pattern, breakout width, 7B) | $8–15 | [digital caliper](https://www.aliexpress.us/w/wholesale-digital-caliper.html) |
| 1 | USB-C power meter (inline, shows volts/amps), for knob current and the power budget | $8–15 | [usb c power meter](https://www.aliexpress.us/w/wholesale-usb-c-power-meter.html) |
| 1 | 0.1 g kitchen/jewelry scale, for key and knob press force and the hinge test | $5–10 | [0.1g digital scale](https://www.aliexpress.us/w/wholesale-0.1g-digital-scale.html) |
| 1 | 8-channel USB logic analyzer (sigrok-compatible), for the missed-press, SSI and timing tests | $5–10 | [usb logic analyzer 24mhz](https://www.aliexpress.us/w/wholesale-usb-logic-analyzer-24mhz.html) |
| 1 | 5 V bench supply with an adjustable current limit (e.g. a CC/CV buck module plus a 12 V adapter), for motor bring-up at ~300 mA and Rev A's first power-up | $10–20 | [cc cv buck module](https://www.aliexpress.us/w/wholesale-cc-cv-buck-module.html) |
| 1 | Soldering iron and solder. Needed: the SparkFun breakout ships without headers, and the core board and MT6701 breakouts usually come with loose headers. Rev A uses it too, for the M3 heat-set inserts ([assembly.md](assembly.md)). No iron: a makerspace, or listings sold with headers already soldered | $10–25 | [soldering iron](https://www.aliexpress.us/w/wholesale-soldering-iron.html) |
| 1 set | M2 and M3 screws, M2 × 3 mm and M3 standoffs, 0.1/0.2/0.3 mm shims, M2 × 5 screws for the motor (see Order 5 for standoff lengths) | $4–8 | [m2 standoff kit](https://www.aliexpress.us/w/wholesale-m2-standoff-kit.html) |

## Order 3: SparkFun (~$23–27, US, no China duty)

| Qty | Part | ~Price | Link |
|---|---|---|---|
| 1 | **SparkFun TMC6300 brushless motor driver breakout, ROB-21867** (2–11 V, 2 A peak). The same driver chip as the knob board. It takes 6 PWM inputs (UH/UL, VH/VL, WH/WL). Headers aren't fitted: solder them (iron above) or use a makerspace | $17.95 + ~$5–9 shipping | [SparkFun](https://www.sparkfun.com/sparkfun-brushless-motor-driver-3-phase-tmc6300.html) |

## Order 4: JLCPCB + JLC3DP (~$45–80 with shipping and duty, after the motor arrives)

One order, one shipping and duty charge. It waits for the motor, because
the knob test stand's screw holes come from measuring it.

- **Rev C prototype frame PCB** (`hardware/proto-frame/`,
  `proto_frame_pcb_outline.dxf`), 58.3 × 30.7 mm: the full build's two
  top-left keys at the same place on the 7B. Four B3U footprints,
  JLC-assembled: SW1/SW2 under the keys, SW3/SW4 the optional second
  switches to compare one switch per key with two. 4 M2 pan-head holes off
  the glass and 2 countersunk holes over it (JLC's countersink option).
  The only custom PCB before Rev A.
- **Caps: 2 + 2**, JLC3DP clear resin (SLA), one standard clear finish
  ([JLC3DP clear printing guide](https://jlc3dp.com/fr/blog/clear-3d-printing-guide)):
  two one-nub caps (`key_cap_clear_resin.stl`) for the one-switch test and
  two two-nub caps (`key_cap_two_nub_clear_resin.stl`) for two switches.
  The full set of 21 waits for Rev A: JLC3DP prices per part, so 21 now
  isn't cheaper per piece, and the force test may change the cap (one nub
  or two).
- **Knob test stand** (`print_knob_test_stand.stl`, PETG or resin), with
  `knob.stl` and `knob_hub.stl`: a 40 × 40 mm block. The 2204 screws onto
  its deck with 4 × M2 × 5 from below (heads in counterbores); the MT6701
  breakout slides in on two rails under the deck, chip up, 1 mm below the
  magnet, as on the knob board. Solder its header pointing down or back so
  the pins clear the rails. Knob and hub are the full build's.
- Not laser-cut acrylic caps: sheet tolerance alone is larger than the key
  stack's budget.

## Order 5: laser-cut plates (~$15–30)

Generated by `cad/build.py` into `cad/out/`:
- `proto_top_plate_3mm_acrylic.dxf`, `proto_base_plate_3mm_acrylic.dxf`:
  laser-cut 3 mm acrylic (SendCutSend/Ponoko take DXF), sized for the 7B.
  The assembled sandwich is 183.7 × 115.6 mm and 30.5 mm to the top plate.
- Standoff lengths (from the model): **M3 24.5 mm** between the plates
  (six, at the corners and sides), **M3 12.6 mm** from the base plate to
  the 7B's four tabs, **M2 3.3 mm** between the frame PCB and the top plate
  (3 mm plus a 0.3 mm shim; at 3.0 mm the switch is held down and may read
  pressed). Round to stock lengths and make up the rest with shims; keep a
  0.1/0.2 mm shim kit to tune the key stack.

## Free: hinge test (D10)

Saw a tongue with the planned 8 mm neck into scrap 1.6 mm FR-4 and load
its tip on the kitchen scale ([knob-module.md](knob-module.md)). Record the
force for 0.15 mm of travel; it sizes Rev A's hinge perforations.

## Notes

- **Wiring the knob:** RP2350B core board → SparkFun TMC6300 (6 PWM,
  standby) and MT6701 breakout (SSI: CS, CLK, DO). 5 V for the driver
  comes from the bench supply with short, thick leads, not breadboard
  jumpers ([lessons.md](lessons.md) #2).
- **3-PWM on the breakout:** the knob board drives each low side from an
  inverter. On the breakout, drive each low-side input from the inverted
  output of the same PWM slice, which is what the inverter does. Keep the
  standby rule: no input high while standby is low
  ([knob-module.md](knob-module.md)).
- **MT6701 over SSI:** read the full 24-bit frame (3 bytes) and check its
  CRC. On some MCUs the SPI peripheral only sees 13 of the 14 angle bits,
  because SSI isn't quite SPI and the last bit gets no falling clock edge;
  check the SPI mode and the bit shift (SimpleFOC uses mode 2 and a shift
  of 1 on the RP2040) against a full turn by hand
  ([forum: SSI interface](https://community.simplefoc.com/t/mt6701-ssi-interface/4441),
  [half-range readings](https://community.simplefoc.com/t/mt6701-sensor-only-reading-half-a-radian-3-14-to-6-28/3655)).
- **Motor gate:** cheap gimbal motors vary a lot in cogging, which ruins
  smooth mode ([lessons.md](lessons.md) #1). Spin each motor by hand,
  unpowered, on arrival. Seller specs disagree on KV and mounting pattern
  (M3 thread vs 12 × 12 / 16 × 16 mm M2/M3): **measure it**, set
  `MOTOR_SCREW_BC` and `MOTOR_THREAD_DEPTH` in `cad/params.py`, then place
  Order 4. Also check the plug on the motor leads.
- Generic breakouts and ESP32 clones differ in pin order. Wire from the
  listing's pinout, not a tutorial.
- **Touch is deferred to Rev A.** The band is optional (D12); its
  realistic test needs the AT42QT2120 next to a running motor under the
  printed plate, which only Rev A has.

## Rough total

Final parts ~$120–175 (Orders 1–2, with duty; counted in the full build),
throwaway kit ~$100–170 (SparkFun, breakouts, JLC order, plates), tools
~$70–140. Details and the development total: [cost.md](cost.md).

## Sequence

Rough durations; plan on 6–9 weeks to the go/no-go and the Rev A order.
1. Orders 1–3 now (AliExpress to the US: 1–3 weeks; SparkFun: days).
2. While they ship: scrap-FR-4 hinge test, firmware skeletons (ESP-IDF on
   the 7B, arduino-pico on the core board), configurator skeleton, Rev A
   schematics.
3. Motors arrive → spin each by hand (cogging gate) → measure bolt
   pattern, thread depth and leads → update `params.py` → Order 4 (about 1
   week to build, about 1 week to ship) and Order 5 at the same time.
4. While they're made: images over WebUSB on the 7B, two-device pairing
   behind the CH334F module, the knob on the breakouts with the motor held
   by hand or taped down (stages 1–3).
5. Boards and prints arrive → knob on the test stand, keys on the 7B
   (stages 3–4).
6. Run the tests in [prototype-tests.md](prototype-tests.md) and decide.
7. Rev A order (2–3 weeks, longer if the TMC6300 or MT6701 need
   pre-ordering). Check JLC stock again on quote day.
