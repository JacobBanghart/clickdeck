# Knobs: design review (senior, standard)

Scope: the 5 haptic knobs and the Rev 0 single-knob module. Sources: docs/, cad/params.py, cad/model.py, a run of `cad/assembly.py --check` (0 problems, but it doesn't check the motor mount or press stroke), the TMC6300 datasheet (rev 1.01) and the MT6701 datasheet (v1.8). Reviewed 2026-10-17.

## Verdict
**Go with changes** for the Rev 0 knob module order. The architecture is sound.
The netlist has two errors that would kill the board: missing driver pins, and the wrong sensor part/package. The press, mount and hub mechanics are underspecified.
**Not ready** for the full knob board: the floorplan isn't proven and the docs contradict the model.

## Strengths
- The driver choice fits USB 5 V (TMC6300, 2–11 V). The 3-PWM + inverter plan rests on the datasheet's BBM statement. Powering the inverter from the NSTDBY net correctly follows the datasheet's standby back-powering warning (TMC6300 §3.3). The 22 nF VCP cap is the right call, because center-aligned 3-PWM switches all three bridges together (§3.1).
- Sensor plan: SSI, a 6×2.5 mm diametric magnet and a 1.0 mm gap match the MT6701 recommendations (gap 0.5–2.0 mm, offset ≤0.3 mm).
- The firmware lessons are good: stored calibration instead of a boot-time spin, pinned toolchain, wake-on-move standby. TMC6300 standby draws <1 µA and wakes in ≤500 µs, which supports the arbiter.
- Control load is easy on the RP2350B (dual M33 with FPU): five voltage-mode FOC loops plus SSI reads fit at several kHz per motor. Put USB on core 0 and FOC on core 1.
- The press is a real switch on a hinged tongue, so no strain gauges to calibrate. Cogging risk is acknowledged and has a fallback motor.

## Issues

### Blocker
1. **TMC6300 BRUV/BRW pins missing from the netlist.** Pins 16 and 20 are the low-side source "foot points" and must go to GND, directly or through a shunt. The netlist never names them (docs/knob-module.md:47–56). A schematic drawn from this spec could leave the low sides unconnected, and the motor won't drive. Pins 8 and 9 (tie to GND) and pin 19 (leave open) aren't stated either. → Add all three explicitly. Put each foot point to GND through a 0 Ω/shunt footprint, so Rev 0 can measure real motor current (see M4). [no-decision]
2. **Wrong MT6701 part and package.** docs/knob-module.md:22 and docs/bom.md:27 list "MT6701QT-STD, SOP-8, C2913974". The QT is **QFN-16 3×3**; the SOP-8 part is **MT6701CT-STD**. LCSC also shows C2913974 **out of stock** today. The model assumes a 1.5 mm SOIC body (cad/params.py:75), so the package also sets the magnet gap: QFN adds ~0.75 mm. → Use MT6701CT-STD SOP-8 (JLC C3003196, Extended; confirm stock). Fix the BOM and params, and re-derive the gap. [no-decision]

### High
3. **Press-switch stack-up can't hit 0.05 mm.** The B3U actuator sits 0.05 mm above the printed floor (cad/params.py:83). That gap depends on PCB thickness (±10% = ±0.16 mm), printed boss height (0.2 mm layers) and floor flatness, against 0.15 mm of switch travel. Some knobs would be pre-pressed and others dead. Rev 0 has the same problem against an acrylic base and stock standoffs. → Put an adjustable stop under each switch (an M2 set screw threaded into the floor, or a shim pad), or set the gap to ~0.2 mm plus a tuning feature. [no-decision]
4. **Motor mount isn't defined.** The model floats the stator base 5 mm above the tongue: sensor 1.5 + gap 1.0 + magnet 2.5 (cad/model.py:99). Nothing holds it there, so it needs spacers. The magnet glues to the hollow shaft's lower end, whose protrusion and circlip are unknown. The BOM's "screws supplied with motors" (bom.md:233) won't reach through 1.6 mm of PCB plus 5 mm. Nothing centers the magnet to ≤0.3 mm. → After measuring the motor, specify spacers (or a printed spacer ring that also centers the magnet), screw length, and screw-head clearance under the tongue (1.65 mm to the floor). [no-decision]
5. **Knob cap would spin on the hub.** The hub is a plain 10 mm cylinder and the cap bore is 10.2 mm (cad/model.py:241–242). That's a slip fit with no key, so detent torque slips. The hub is also epoxied to the bell by hand, which invites wobble. → Add a D-flat or spline plus a crush rib. Screw the hub to the bell's threaded holes (most 2204 bells have them) and center it on the shaft bore. [no-decision]
6. **Full knob-board floorplan unproven and contradictory.** The docs put U1/U3 on the fixed part (knob-module.md:95). The model puts the TMC6300 on the tongue under the bell (cad/model.py:250). The fixed area is small: 2.77 mm ribs between tongues and an 18 mm back strip that also holds 5 headers and 5 lead coils (no parts under the coils). The RP2350B is modeled as a 7×7 RP2040 (params.py:77,85–86). The real chip is 10×10 QFN-80 plus flash, crystal, SMPS inductor and ~20 caps, along with 5 drivers, 5 inverters, the load switch and 470 µF bulk. → Before the full order, place real footprints on the DXF. Decide driver-on-tongue (≈19 traces including phase currents across an 8 mm hinge) vs off-tongue. Make Rev 0 copy that placement so it really is "one section of the full board". Consider 4 layers. [decision: size/cost]

### Medium
7. **Tongue is probably too stiff.** My cantilever estimate (FR-4, 8 mm neck, 1.6 mm board, knob at 14 mm, switch at ~26 mm) is ~8–12 N, or 0.8–1.2 kgf, to close the switch. The pass target is 150–400 g (prototype-tests.md:22). → On Rev 0, make the hinge tunable: perforations or knife-cut relief in the neck, or two narrower flexures. Measure, then fix params. [no-decision]
8. **Back strip is unsupported.** Knob-board screws are only on the front edge and at the ends (model screws `screw_knobboard_*`). Press reactions go through the hinge into a free 18 mm strip that carries the MCU. → Add bosses/screws behind each hinge. [no-decision]
9. **Boot and fault states of NSTDBY/PWM.** Nothing holds NSTDBY low during reset, BOOTSEL or a crash. The RP2350 internal pull-downs are unreliable (erratum E9), and C7 (100 nF) holds charge. High-side PWM pins drive the TMC6300 directly, so a PWM-high in standby back-powers it (10 mA pin max). → External 10–100 kΩ pull-downs on NSTDBY and each PWM net, ~1 kΩ series on the high-side inputs, and a watchdog that drops NSTDBY. [no-decision]
10. **No current sensing; budget numbers are borrowed.** The arbiter is sized from SmartKnob's motor (plan.md:111). A 2204 260 KV gimbal motor is likely several Ω, so at 5 V it is resistance-limited to roughly 0.5–1 A. Torque is then ~15–30 mN·m, or ~2–3 N at a 19 mm rim: fine for detents, and "firm" end stops will be soft. → Measure R and Kt on arrival and fit the budget and the "End stops" pass criterion (prototype-tests.md:17) to them. With the shunt footprint from #1, one RP2350B ADC could read current on Rev 0. [decision: features]
11. **Shared SSI bus with MT6701 I²C on the same pins.** Unselected sensors sit in I²C mode on CLK/DO. No pins are lost by changing the scheme: one shared CS + shared CLK + 5 separate DO lines (still 7 pins) reads all five at once via PIO and removes the bus-contention question. Rev 0 has one sensor, so it can't test the current scheme. [no-decision]
12. **VS decoupling is thin in the full build.** wiring.md:108 gives "10 µF at each driver"; at 5 V DC bias that's ~4–5 µF effective, below the datasheet's ">10 µF". Rev 0's 2×22 µF is fine. → Use 2×22 µF 0805 per driver on the full board too. [no-decision]
13. **SimpleFOC on RP2350 × 5 motors is unproven.** RP2350 support arrived around SimpleFOC v2.3.5 on the earlephilhower core ([forum](https://community.simplefoc.com/t/rp2350-support-raspberry-pico-2/5607)). Five motors sharing PWM slices haven't been shown. GPIO n and n+16 share a PWM channel, and 15 unique channels must be assigned in the schematic. plan.md:176 still says "Arduino-ESP32 core". → Fix the doc. Pin the core. On Rev 0, configure all 15 PWM outputs and 5 sensor reads and time the loop. [no-decision]
14. **TMC6300 stock is thin.** C5274455 shows **59** in stock today (docs say 200: knob-module.md:21, bom.md:26). Rev 0 needs 2 and a full build needs 10 (2-board assembly minimum). → Re-check stock, or pre-order through JLC parts. [decision: cost]

### Low
- SN74LVC3G04**DCT** is SM8/SSOP-8, not VSSOP-8 (knob-module.md:23); check the footprint.
- MT6701 draws 10–14 mA, not "a few mA" (plan.md:116). Knob-board logic is more like ~120 mA than 60 (wiring.md:128).
- Netlist should say MODE tied **high** (to VDD) for I²C/SSI. R1 is redundant with the internal 200 kΩ pull-up but harmless.
- `KNOB_STYLE` comment says the cap "bolts straight onto the bell" (params.py:92); the model uses hub plus press-on cap.
- Bell-to-plate clearance is 0.3 mm (params.py:119). Rubbing would ruin smooth mode, so give it ≥0.6 mm or relieve the plate.
- Unkeyed 1×3 header: a re-plugged motor invalidates stored direction. Add a boot sanity check or a keyed header.
- DFM: B3U on the bottom side means two-sided assembly at JLC (extra fee). Use small tented vias under the QFN pad, with a windowpane paste pattern.
- DIAG is active-high push-pull, so diode-OR (Schottky + pull-down) works.

## Missing
- Motor measurements (bolt pattern, shaft protrusion/circlip, phase R, Kt) before layout. They are listed as open, but they gate items 2–5 and 10.
- Thermal test: driver and motor temperature after holding an end stop.
- Prototype tests for: angle jitter with PWM running, magnet-offset tolerance, DIAG/fault recovery, standby back-power (VIO stays <0.4 V with PWM high), press force at several points on the cap, 5-sensor/15-PWM loop timing.
- RP2350B minimum-system spec: SMPS inductor part, USB series resistors, flash, crystal load caps, BOOTSEL.
- Power sequencing on Rev 0 (bench 5 V vs dev-board 3.3 V) and reverse-polarity protection on J2.

## Actions before ordering Rev 0 (in order)
1. Fix the netlist: BRUV/BRW (with shunt/0 Ω footprints), GND pins 8 and 9, pin 19 NC, MODE high (#1).
2. Change the sensor to MT6701CT-STD SOP-8, confirm stock, update BOM/params (#2).
3. Receive and measure the motor. Design spacers, magnet centering, screw lengths and keyed, screwed hub (#4, #5).
4. Add an adjustable switch stop and a tunable hinge to Rev 0 (#3, #7).
5. Add pull-downs, series resistors and the watchdog plan (#9). Use 2×22 µF per driver everywhere (#12).
6. Decide driver placement (on or off tongue) by floorplanning the full board with real footprints, and mirror it on Rev 0 (#6).
7. Switch to separate DO lines if adopting #11. Fix stale docs (#13, Low items).
8. Re-check TMC6300/MT6701 stock the day of the order (#14). Extend prototype-tests.md with the Missing tests.
