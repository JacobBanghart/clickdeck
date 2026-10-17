# Knobs: adversarial review (red team)

**Summary.** The knob caps can't transmit torque (plain 10.2 mm bore on a plain 10 mm hub), and the motor floats 5 mm above its tongue with no spacer, screw length or magnet locator specified. So no knob can be built from the current model.
The press mechanism sits on a 0.05 mm gap that one FDM layer (0.2 mm) erases. The hinge is probably several times stiffer than the 150–400 g target, and sideways finger force is levered ~2.8× into the press direction.
The electrical design mostly holds up (TMC6300 BBM, standby, back-EMF). The risks are undefined driver state during RP2350 reset (E9 on pre-A4 silicon, no pull-downs), uncalibrated voltage-mode current, and a stored phase order that goes wrong when a reversible plug is reseated.

Geometry below is from `model.full_device(tilt=False)` and `make_stack(P.FLOOR, P.TOP_PLATE_T)`.

## Blocker

### B1. Knob cap has no drive feature and no retention
- **Assumption attacked:** "Press each knob cap onto its hub" (assembly.md:119), "press-on caps".
- **Evidence:** `cad/model.py:240-244`: the hub is `Cylinder(KNOB_HUB_D/2)` (10.0 mm) and the cap bore is `Cylinder(KNOB_HUB_D/2 + 0.1)` (10.2 mm). That is 0.2 mm diametral *clearance*, round on round, with no flat, key or knurl. The slab is tilted 42° (params.py:125).
- **Failure:** The cap spins on the hub, so haptic torque never reaches the hand, and caps slide off the tilted slab.
- **Test:** Print the hub and cap and try to turn the hub through the cap.
- **Fix [no-decision]:** Add a D-flat or 6–8 splines to the hub, with a 0.1–0.15 mm interference or a crush rib in the cap, and keep the bore depth.

### B2. Motor stack has a 5 mm unsupported gap and no mounting hardware
- **Assumption attacked:** "Screw each motor's base to its tongue … centered over the MT6701" (assembly.md:81). The BOM asks to "check length vs the 1.6 mm board" (assembly.md:34).
- **Evidence:** In the model the PCB top is at z = 6.25 and the motor bottom at z = 11.25. Those 5.0 mm are `MT6701[2] + SENSOR_GAP + MAGNET_H` (model.py:99), and no spacer part exists. The magnet (z 8.75–11.25) hangs entirely below the base, so it assumes the hollow shaft ends flush with the base underside. Nobody has checked that.
- **Failure:** Screwed flat, the base crushes the magnet into the MT6701. With improvised spacers, the supplied short screws don't reach. Long screws in a gimbal base often bottom out in the stator windings and short a phase (a common gimbal-motor failure). The air gap, which sets field strength, is then set by whatever washers come to hand.
- **Test:** Calipers on the arriving motor: shaft end relative to the base face, thread depth, bolt circle.
- **Fix [no-decision]:** Model a printed or machined spacer ring with screw clearance, a magnet pocket or centering sleeve that fits the shaft bore, and a specified screw length. Add a check in `assembly.py` that screw tip < thread depth.

## High

### H1. KNOB_PRESS_GAP 0.05 mm against a printed floor
- **Evidence:** params.py:83 sets 0.05 mm. The switch is at z 3.05, so the gap from the floor at 3.0 is 0.05 mm. The board front sits on printed bosses at 1.65 mm above the floor (model.py:762), and back ribs (model.py:766) are at x = −40/0/40 only, while the knobs are at x = ±61.5. FDM layers are 0.2 mm, so 1.65 prints as 1.6 or 1.8, which makes the gap −0.05 mm (switch preloaded, permanently half-pressed) or +0.15 mm (double the travel). A 160 mm floor also warps 0.1–0.3 mm.
- **Failure:** Some knobs register as always pressed or press at a touch. Others need a hard shove. Which knobs fail varies from print to print.
- **Test:** Print the tray, then use a feeler gauge or shims under each of the 5 switch positions with the board screwed down.
- **Fix [no-decision]:** Put the switch's reaction surface on an adjustable or shimmed pad (an M2 set screw from below, or a glued 0.1 mm shim stack), or let the switch press a feature on the fixed PCB rather than the floor.

### H2. Hinge stiffness is far above the 150–400 g target
- **Evidence:** The neck is 8 × 1.6 mm FR4 and 1 mm long (params.py:81-82). The switch sits 23.75 mm from the hinge and the knob axis 13 mm (model.py:252). To reach operating travel (~0.15 mm at the switch, θ ≈ 0.0063 rad), with E ≈ 18 GPa and I = 2.73 mm⁴, the neck needs a moment of 310 N·mm (for an effective length of 1 mm) down to 62 N·mm (for 5 mm). That is 4.8–24 N at the knob, before adding the B3U's own force (≈1.5 N per Omron, ×1.83 lever ≈ 2.8 N). Total: about 0.8–2.7 kg.
- **Failure:** The press feels like pushing on a solid board. To make it softer, the hinge has to get narrower, which makes H3 and H4 worse.
- **Test:** Saw a 26 mm U-tongue with an 8 mm neck into 1.6 mm FR4 scrap and load it on the kitchen scale. This costs $0 and should happen before Rev 0 is ordered.
- **Fix [decision]:** A longer, narrower serpentine or double-beam flexure (more board area), a separate hinged carrier (extra part), or a softer switch (B3U-1000PM or similar; changes the feel).

### H3. Sideways force while turning reads as a press
- **Evidence:** The cap top is about 36 mm above the hinge plane (cap max z 42.65, PCB 6.25), and the hinge is 13 mm behind the knob axis. A sideways force F toward the user produces a moment of 36·F about the hinge axis, the same sign as a press, which acts like a downward push of 2.8·F. With the slab at 42°, fingers naturally pull toward the user.
- **Failure:** Fails the "Press while turning" test (prototype-tests.md:303), especially with H1's preload.
- **Test:** Push the cap sideways at its top with a spring scale on Rev 0 and record the force at the first false click.
- **Fix [decision]:** Put the hinge on the knob axis line (pivot under the switch side) or use a parallel-guided flexure. A firmware debounce that requires little rotation during a press is a partial [no-decision] mitigation.

### H4. Hinge fatigue cracks the sensor traces, and a bad angle drives the motor
- **Evidence:** Surface strain is ε = (t/2)θ/L, about 0.5 % for a 1 mm effective length. The 0.5 mm-radius slot ends add a concentration factor of 2–3. Dynamic flex practice keeps copper strain below ~0.2–0.3 %. At 50 presses a day, 5 years is ~90 k cycles. The traces crossing the hinge are MT6701 CLK, DO, CSN, VDD and GND (knob-module.md:94-97).
- **Failure:** DO cracks open or intermittent, the angle reads all 1s or garbage, and FOC commutates on the wrong angle. The knob runs away or buzzes at full voltage.
- **Test:** Flex the scrap tongue from H2 100 k times with a servo or cam while monitoring trace resistance.
- **Fix [no-decision]:** Check the MT6701 SSI CRC (part of the frame) and sanity-check angle jumps. On error, drop NSTDBY. Use wide traces at the neck's neutral axis, put pours on both sides, and use larger slot-end radii.

## Medium

### M1. Undefined driver state during reset or BOOTSEL (RP2350 E9)
- **Evidence:** TMC6300 inputs have no pull-downs (only "Input leakage ±1 µA"). VIO rising reset releases at ≤1.8 V and standby needs <0.4 V (datasheet Rev 1.01, Detector levels; [ADI PDF](https://www.analog.com/media/en/technical-documentation/data-sheets/TMC6300_datasheet_rev1.07.pdf)). With E9 on pre-A4 RP2350, an input-enabled pin with a pull-down floats to ~2.2 V ([RPi A4 note](https://www.raspberrypi.com/news/rp2350-a4/), [Hackaday](https://hackaday.com/2025/07/31/)). NSTDBY, U3 VCC and the UH/VH/WH lines are all bare GPIOs (knob-module.md:50-60). The Rev 0 core board is probably A2.
- **Failure:** During boot or UF2 update, NSTDBY sits around 2 V and the drivers half-wake with arbitrary inputs. Standby current is lost and drivers may twitch.
- **Test:** Scope NSTDBY and the PWM lines across reset and BOOTSEL on Rev 0.
- **Fix [no-decision]:** Fit 10 kΩ pull-downs on NSTDBY and the three PWM lines per knob (E9 needs ≤ ~8.2 kΩ on A2) and specify RP2350B A4 in the BOM.

### M2. Stored phase order vs a reversible plug
- **Evidence:** "The plug goes on either way round: the firmware's calibration finds the phase order" (wiring.md:171). Calibration is stored and the boot spin is skipped (lessons.md:65). The servo plug on an unshrouded 1×3 header can also go on offset by one pin.
- **Failure:** After service the plug is reversed, so the electrical direction flips and the closed loop becomes positive feedback. The knob spins away at the voltage limit.
- **Test:** On Rev 0, calibrate, flip the plug and power up.
- **Fix [no-decision]:** At first wake, apply a small open-loop step and confirm the sensor moves the expected way, invalidating calibration if not. Use a shrouded or keyed header.

### M3. Voltage-mode current budget rests on an unknown R and KV
- **Evidence:** There is no shunt (BRUV/BRW to GND). The arbiter's "estimated motor current" (protocol.md:108) is (Uq − BEMF)/R. Sellers disagree on KV (open-questions.md:203). Measured resistance of similar gimbal motors ranges from 6.3 Ω to 16.4 Ω, and seller specs are often wrong ([SimpleFOC forum](https://community.simplefoc.com/t/the-2208-90kv-bldc-has-a-phase-resistance-of-16-4/814), [GBM2804](https://community.simplefoc.com/t/measuring-gimbal-resistance-inductance-and-kv-using-simplefoc/6842)). Copper R rises 0.39 %/°C when the motor heats at an end stop (~5 W stall at 2.5 Ω/phase). Torque also scales with VS, which the brownout guard lets fall to 4.6 V.
- **Failure:** If R is low, the budget is exceeded and the port trips. If R is high, end stops are only ~10 mN·m, which a finger easily overpowers.
- **Test:** Measure line-to-line R with a multimeter and stall torque with a lever and the kitchen scale.
- **Fix [no-decision]:** Store the measured R per knob, scale duty by the measured VS, and log real current with the USB meter. [decision]: add a shunt on BRUV/BRW (one resistor per driver plus 5 ADC pins, which aren't free: 44 of 48 GPIO are used).

### M4. Cogging period doesn't match the detent period, plus snap on wake
- **Evidence:** A 12N14P 2204 cogs 84 times per turn (4.3°), against detents of 24 or 48 per turn (prototype-tests.md:295). In standby the knob rests on a cogging minimum, not a detent. When it wakes it snaps to the nearest detent.
- **Failure:** Clicks are uneven, and a value can change when the knob is only touched.
- **Test:** Turn Rev 0 slowly in 48-detent mode and log the angle. Touch it from standby.
- **Fix [no-decision]:** Store a cogging feed-forward table per knob. On wake, re-anchor the detent grid at the current angle.

### M5. Bell and hub clearances are smaller than the hand-built stack's tolerances
- **Evidence:** The bell is 0.3 mm below the top plate (`MOTOR_TO_PLATE`, params.py:119), and the hub has 0.5 mm radial clearance in its plate hole (params.py:150). The 5 mm spacer (B2), hand-epoxied hub concentricity and the printed posts all add up in this stack. A hub glued only on its 10 mm face peels under an 18 mm lever if someone shoves the cap sideways.
- **Failure:** The bell or hub rubs the plate, which shows up as drag in smooth mode, and hubs pop off.
- **Fix [no-decision]:** Locate the hub on the bell's center bore or screw holes (a spigot plus M2 screws), and set `MOTOR_TO_PLATE` to ≥0.8 mm.

## Low

- **L1. TMC6300 placement: model vs doc.** The model puts U1 at (x+9, y−9), on the tongue under the bell (model.py:250). knob-module.md:94 puts it on the fixed part. Follow the doc so that only sensor and switch traces cross the hinge [no-decision].
- **L2. No coast while awake.** With 3-PWM and inverters, every phase is always driven. Zero command shorts the windings, which adds speed-proportional drag in "free" mode (small at 260 KV). Standby does coast (bridges off). Accept it, or drop NSTDBY when smooth-free and idle [no-decision].
- **L3. Lead coil margin.** The coil is 6.6 mm in 6.7 mm of room (wiring.md:224). Any lead thicker than 2.2 mm touches the panel. Measure it [no-decision].
- **Refuted:** Back-EMF pumping the 5 V rail: 260 KV at a 10 rev/s flick gives ≈2.3 V, well under 5 V. Wake latency: TMC6300 worst-case power-up is 500 µs. Cross-conduction: the datasheet confirms BBM, and its inputs are sampled at 12 MHz. PWM slices: 15 channels fit within the RP2350B's 24 distinct slice channels with the ADC on GPIO40–47. Magnetic crosstalk between motors 31 mm apart: the 14-pole rotor field cancels near the axis, so it is small compared with a 6 mm magnet at 1 mm.

## What I could not verify
- 2204 phase R, KV, shaft OD and material, and whether the shaft rotates with the bell and reaches the base face (all seller-dependent). Whether a steel shaft shunts the magnet's field.
- MT6701 field range and SSI timing from the primary MagnTek datasheet (mirror unreachable).
- The hinge stiffness and strain figures are beam estimates. The surrounding board and back strip (resting on ribs, not screwed) add compliance of unknown size.
- B3U-1000P operating force (≈1.5 N from memory of the Omron sheet).
- SimpleFOC support for RP2350B GPIO32–47 and synchronized multi-slice PWM.
