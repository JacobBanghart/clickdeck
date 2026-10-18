# Design review summary

Date: 2026-10-17. Nothing here has been built or tested. Every finding is about the CAD, the docs and the PCB generator.

## What was reviewed and how

Seventeen reviewers worked on their own, with no shared context. Each read the repo (docs/, cad/, hardware/proto-frame) and the datasheets. Some ran `cad/assembly.py --check`, `kicad-cli pcb drc` or probed the model in build123d. Each of 8 areas got a standard senior review and an adversarial (red-team) review. One more review looked only at shorts and rail spacing.

| Area | Senior review | Adversarial review |
|---|---|---|
| Keys (caps, B3U, frame PCB) | [keys-review](reviews/keys-review.md) | [keys-adversarial](reviews/keys-adversarial.md) |
| Knobs (motors, TMC6300, MT6701, press) | [knobs-review](reviews/knobs-review.md) | [knobs-adversarial](reviews/knobs-adversarial.md) |
| Display (Waveshare 7B) | [display-review](reviews/display-review.md) | [display-adversarial](reviews/display-adversarial.md) |
| Touch band | [touch-review](reviews/touch-review.md) | [touch-adversarial](reviews/touch-adversarial.md) |
| Enclosure and assembly | [enclosure-review](reviews/enclosure-review.md) | [enclosure-adversarial](reviews/enclosure-adversarial.md) |
| Power and USB | [power-usb-review](reviews/power-usb-review.md) | [power-usb-adversarial](reviews/power-usb-adversarial.md) |
| Firmware, protocol, host | [firmware-review](reviews/firmware-review.md) | [firmware-adversarial](reviews/firmware-adversarial.md) |
| Sourcing, cost, prototype plan | [sourcing-review](reviews/sourcing-review.md) | [sourcing-adversarial](reviews/sourcing-adversarial.md) |
| Shorts and rail spacing | [shorts-review](reviews/shorts-review.md) | |

Every senior reviewer's verdict was **go with changes**. The architecture holds up: one external port, an internal hub, two USB devices, CC-based power sensing, and plug-in cabling. Most problems are numbers, missing parts and a few mechanical stacks that printed parts can't hold.

**How to read the list.** Duplicates are merged. "Found by N" counts independent reviewers; more means more confidence. Each item has one tag:

- **[fix]**: no real owner decision. Just do it.
- **[decision]**: the owner has to choose. The options and a recommendation are in [Decisions for the owner](#decisions-for-the-owner) (D1–D18).

Short names: keys-r = keys-review, keys-a = keys-adversarial, and so on; shorts = shorts-review.

---

## Ranked findings

### Blockers

**B1. The keys likely won't click: the frame PCB is held on two edges only, and the LCD glass ends up carrying the load.** [decision → D8]
Found by 7: keys-r (H3), keys-a (B1), display-a (B1), enclosure-r (H1), enclosure-a (B1), display-r (H4), shorts (L1).
The 170 × 96 mm lattice of 3.6 mm strips is screwed only at the back and left (`cad/model.py:651-655`). Estimates of the front-right deflection range from 0.5 mm to 7 mm per newton (keys-a grillage: 4.7 mm/N at the front-right key). The gap to the glass is 0.2 mm. So the PCB lands on the glass before the B3U trips, and every press loads the panel (mura, scuffs). The 2-key prototype is held on both sides and can't show this. Fix: add support at the front and right edges, and give the cap a down-stop that isn't the glass. See D8.

**B2. The vertical key stack has 0.05 mm of margin, and the glass is the overtravel stop.** [decision → D8]
Found by 6: keys-r (H2), keys-a (B1, H2), enclosure-r (B1), enclosure-a (B1), display-r (H4), display-a (B1).
The cap bottom is 0.2 mm above the glass (`params.py:31`, `model.py:141`). B3U pretravel is 0.15 mm nominal and up to 0.35 mm per the Omron datasheet (A162-E1-07). The tolerances add up to about ±0.4 mm RSS: PCB ±0.16, printed posts ±0.1–0.2, switch height +0.15/−0.10, and `PANEL_T` taken from the STEP. Fix: a cap hard stop on the plate or PCB, a larger gap or a shorter cap, and shim points (see D8 and Disagreement 6).

**B3. One switch at one edge turns the cap into a lever that pivots on the glass.** [decision → D8]
Found by 3: keys-r (H1), keys-a (B2), enclosure-a (B1).
The nub is 10.75 mm off center (`model.py:117`). The far edge reaches the glass after 0.58° of tilt, but the guide allows 3.3°. A center press needs about 3.3 N, a press 4 mm from the far edge about 7.4 N, and the far edge never clicks. The "guides in the case" in plan.md don't exist in the model. Fix now at no cost: add a second B3U footprint per key on the proto frame PCB and order caps with a nub at both ends, so the prototype can compare one switch with two. The full-build choice is in D8.

**B4. Prototype frame PCB: screws and through-hole wire pads sit over the 2.4" glass with 0.2 mm of clearance.** [fix]
Found by 2: keys-r (B1), shorts (L5).
The proto board (±26.98 × ±20.86 mm) lies entirely inside the glass (±30.13 × ±21.36 mm). The M2 holes (`model.py:1138`) and TP1–3 (`gen_pcb.py:126-131`) put screw heads and solder tails on the glass. Fix: widen the outline to about ±36 mm in X and put holes and pads outside the glass, or use top-side SMD pads plus adhesive. Re-run DRC. Also move copper 0.5 mm from the window edges, not 0.3 mm.

**B5. Wrong MT6701 part and package, and that part is out of stock.** [fix]
Found by 3: knobs-r (#2), sourcing-r (B1), sourcing-a (B1).
`docs/knob-module.md:22` and `docs/bom.md:27` list "MT6701QT-STD, SOP-8, C2913974". The QT is a 3×3 mm QFN-16; the SOP-8 part is MT6701CT-STD (JLC C3003196). On 2026-10-17 LCSC showed C2913974 out of stock. Fix: switch to the CT SOP-8 if JLC (not LCSC) stocks it, then fix the BOM, `params.py:75` and the magnet gap (QFN adds about 0.75 mm). Second-sourcing is in D2.

**B6. The TMC6300 netlist is missing pins.** [fix]
Found by 1: knobs-r (#1).
BRUV/BRW (pins 16, 20), the low-side source foot points, are never connected (`knob-module.md:47-56`), so the motor won't drive. Pins 8 and 9 (GND) and pin 19 (NC) aren't stated either. Fix: add them all. Route each foot point to GND through a 0 Ω/shunt footprint so Rev 0 can measure motor current. State MODE tied high on the MT6701.

**B7. Knob caps can't transmit torque.** [fix]
Found by 3: knobs-r (#5), knobs-a (B1), enclosure-r (H4).
The hub is a plain Ø10 cylinder and the cap bore Ø10.2 (`model.py:240-244`): a round-on-round clearance fit. Fix: D-flat or splines on the hub, crush ribs in the cap. Screw the hub to the bell's threaded holes and center it on the bore instead of epoxying it by hand.

**B8. The motor mount is undefined: a 5 mm unsupported gap, no spacer, no screw length.** [fix]
Found by 3: knobs-r (#4), knobs-a (B2), shorts (M1).
The stator base floats 5 mm above the tongue (sensor 1.5 + gap 1.0 + magnet 2.5, `model.py:99`), and nothing holds it there. The supplied screws won't reach. Long screws in gimbal bases can bottom in the windings and short a phase. Fix: after measuring the motor, model a spacer ring that also centers the magnet (≤0.3 mm offset). Specify the maximum screw length (board + thread depth − 0.5 mm). Make the motor holes NPTH with a copper keep-out. Add a "screw tip < thread depth" check.

**B9. A reversed JST-GH link cable puts PC VBUS onto RP2350B ADC pins.** [fix]
Found by 3: shorts (B1), power-usb-r (H3), power-usb-a (H1).
Pinout `1 VBUS · 2 VBUS … 7 CC1 · 8 CC2` (`wiring.md:162`). Reversed cables are sold next to straight ones. The 10 kΩ resistors are on the USB-board side, so 5 V lands on unpowered, non-5 V-tolerant ADC pins. Fix: use the palindromic pinout `1 GND · 2 VBUS · 3 CC1 · 4 D− · 5 D+ · 6 CC2 · 7 VBUS · 8 GND`. A reversed cable then only swaps D± (no enumeration, no damage) and CC1/CC2. Add 10–22 kΩ in series at the knob end too. Check pin-1-to-pin-1 continuity before first power-up.

**B10. The external USB-C notch leaves 0.4–0.45 mm of PCB behind the socket.** [fix]
Found by 2: power-usb-r (B1), power-usb-a (H5).
The arm is 8.1 mm deep and the cutout 7.65 mm (`model.py:669,687`; `params.py:178`). There's no room for the 16 SMD pads or the D±/CC routing, and the web will crack. LCSC lists C2894902 as SMD-only, so the strain-relief claim (`wiring.md:195-197`) is unverified. Fix: get the HC-TYPE-C-16P-CB1.6 drawing and model its real slot. If it doesn't fit, widen the arm or pick a mid-mount part with real THT legs. Regenerate the outline DXF.

**B11. The CH334F hub may not run without a crystal.** [fix]
Found by 2: power-usb-a (B1), power-usb-r (M5).
CH334 datasheet §6.2: crystal-free mode "is not turned on by default" on some package forms and "can be confirmed at the time of ordering", which JLC can't do. Fix: add a 12 MHz crystal footprint on XI/XO (load caps are built in) plus a 0 Ω link that can ground XI. Fit the crystal (~$0.10). Confirm MTT and the integrated terminations.

**B12. Linux will refuse to configure devices behind the bus-powered hub.** [fix]
Found by 3: firmware-a (B2), power-usb-r (H1), power-usb-a (H4).
For a bus-powered hub, Linux allows 100 mA per port (`hub.c`, `mA_per_port = unit_load`). Arduino-ESP32 defaults to `usb_power_ma(500)`. CH334 PSELF has an internal pull-up, so by default the hub claims to be self-powered. Fix: declare bMaxPower ≤ 100 mA in both firmwares, and strap PSELF on purpose (see Disagreement 4). Add `lsusb -t`/dmesg checks to bring-up.

**B13. Writing images to flash will glitch or permanently shift the RGB panel.** [fix]
Found by 4: display-r (H2), display-a (H2), firmware-r (B1), firmware-a (H3).
ESP-IDF RGB LCD docs: "the LCD CANNOT function if the external memory cache is disabled, such as during OTA or NVS writes." Yet `protocol.md:89-93` writes every image, page and setting to flash. Fix: framebuffer in PSRAM, bounce buffers (≥10 lines) in SRAM, `CONFIG_SPIRAM_XIP_FROM_PSRAM`, `LCD_RGB_RESTART_IN_VSYNC`, PCLK ≤ 30 MHz. Keep the cache in PSRAM and write flash lazily in batches, only when the host says "persist". Add LRU eviction. The toolchain choice is D13.

### High

**H1. Panel screws (M3×14) go about 0.45 mm into the LCD's back plate, and the check can't see it.** [fix]
Found by 4: display-r (H1), display-a (H1), enclosure-a (H1), shorts (unverified note).
In the STEP the tab boss gives about 1.7 mm of thread and the module back sits 2.5 mm above the tab. The tip ends 2.95 mm past it (`model.py:834`). `check_interference` skips every screw/target pair (`assembly.py:182-188`). Fix: M3×12 with the counterbore 1 mm shallower (tip about +1.95 mm). Add a "tip stays inside the target" check. Measure a real tab.

**H2. The knob press gap of 0.05 mm is smaller than one printed layer.** [fix]
Found by 4: knobs-r (#3), knobs-a (H1), enclosure-r (B1), enclosure-a (M1).
`KNOB_PRESS_GAP = 0.05` (`params.py:83`) against 1.65 mm printed bosses, 0.2 mm layers and a warping floor. Some knobs will read always-pressed and others dead. Fix: an adjustable striker per switch (an M2 set screw up through the floor) or a shim pad. Design for ≥0.2 mm nominal.

**H3. The press-to-click hinge is several times too stiff.** [decision → D10]
Found by 2: knobs-r (#7), knobs-a (H2).
An 8 × 1.6 mm FR-4 neck needs about 8–27 N (0.8–2.7 kg) at the knob, against the 150–400 g target (`prototype-tests.md:22`). Test first for $0: saw a scrap FR-4 tongue and load it on the kitchen scale.

**H4. The display's 5 V back-feeds the hub, the knob board and the PC's VBUS.** [fix]
Found by 3: shorts (H1), power-usb-a (M1), power-usb-r (L2). Confirmed from the schematic (Disagreement 1).
Type_C2 VBUS is wired straight to the 7B's 5V net. The SY6280 blocks reverse current only while disabled, and it's always on (`wiring.md:98`). Power the 7B from its UART port, or fit a LiPo to J3, and the device drives VBUS out of its upstream port. Fix: replace the SY6280 with a switch that has true reverse blocking (or add an ideal diode). Document "no battery on J3; unplug the back cable before using the UART port". This also covers the "port 2 VBUS always live" point (power-usb-a L3).

**H5. The VBUS branch to the knob board has no current limit.** [fix]
Found by 2: shorts (H2), power-usb-r (M3).
Only the display branch has a limiter. A pinched GH cable or a shorted bulk cap goes straight to the PC port. Fix: a current-limited, reverse-blocking switch on that branch (for example a second SY6280-class part at about 1.8 A) or at least a 1.5–2 A PTC. Specify 26 AWG GH cable: JST rates 1 A per contact at 26 AWG, and cheap cables are 28–30 AWG.

**H6. On default 500 mA ports the device draws about 1 A, and the docs contradict themselves.** [decision → D9]
Found by 4: power-usb-r (H4), power-usb-a (H3), firmware-r (M4), firmware-a (M3).
`wiring.md:127` says the device stays under the offer. Lines 128-131 add up to 960 mA. The baseline (display 350 + hub up to 85 + logic 60 mA) is already about 0.5 A before configuration. A non-compliant A-to-C cable with 10 kΩ Rp reads as a 3 A port.

**H7. The 4.6 V brownout guard trips on compliant ports.** [fix]
Found by 3: power-usb-r (M1), power-usb-a (H2), firmware-a (M3).
Source 4.75 V minus cable, GH contact and load-switch drops gives 4.2–4.4 V at the knob board on a legal 3 A port. Fix: trip on a drop relative to idle (>300 mV) with an absolute floor near 4.2–4.3 V, using a fast comparator. Add hysteresis and budget recovery, and log trips in `STATUS`.

**H8. The upstream link runs at 480 Mbit/s over about 50 mm of a cramped 2-layer arm.** [fix]
Found by 1: power-usb-r (H2).
The CH334 runs high speed toward the PC; the docs only mention full speed. Fix: put the hub next to the external socket (<15 mm high-speed run), as a 90 Ω coplanar pair with no vias over unbroken ground, with the USBLC6 in line.

**H9. The prototype doesn't test what the expensive order adds.** [decision → D3]
Found by 4: display-r (H3), firmware-r (B1), sourcing-r (H3, M2), sourcing-a (H4).
These meet for the first time on the full JLC panel: the 7B, the RP2350B custom circuit, the CH334F, the touch IC, ZIF/FFC/GH/SH, and the full key frame. One wrong footprint means respinning a 4-board panel for about $150–250, not the "$30–60" in `cost.md`. The riskiest mechanical test (key feel) is scheduled last.

**H10. OpenDeck's device-plugin API can't carry knob feel, haptics, pages or swipes.** [decision → D4]
Found by 2: firmware-a (B1), firmware-r (host section).
`openaction` 2.8.0 `device_plugin` has nine calls: ticks, key up/down, touch position, images, brightness. Nothing carries detent or haptic config or a page number.

**H11. With no host, the screen blanks and can't be woken, and the keys don't match the icons.** [decision → D5]
Found by 2: firmware-r (H1), firmware-a (H1).
Wake is relayed by the app (`protocol.md:139-141`). `HID_MAP` is one map, but images are per page. Also, needing no decision: add `PING`/timeout to the display device, and release all HID keys on every mode switch.

**H12. Cost is understated: no import duty, and the panel needs Standard double-sided assembly.** [decision → D1, D6]
Found by 2: sourcing-r (H2, M1), sourcing-a (H1, H3, M1, M3, M5).
JLC's US tariff FAQ gives 35–92.5% DDP (about 35% typical). Bottom-side press switches and THT parts force Standard assembly (about $140–160 in fees). There are 17–19 extended-part types, not about 5. A single build comes to about $375–600 against a $350 Stream Deck + XL, which has 36 keys and 6 dials. The prototype is about $160–280, not $120–200.

**H13. TMC6300 stock is 59 (docs say 200), and the MT6701 is out of stock.** [decision → D2]
Found by 4: knobs-r (#14), sourcing-r (H1), sourcing-a (B1, H2), and B5 above.
LCSC C5274455: 59 at $5.93. DigiKey lists about 4,100 at $2.44. One build uses 10 (JLC assembles 2 boards).

**H14. The touch band will likely read a hand turning a knob as a touch.** [decision → D11]
Found by 4: touch-a (B1, H3), touch-r (#4), shorts (L2), enclosure-r (B1, bell near plate).
The band edge is 0.8 mm from a PWM-driven bell (`model.py:448`). The knob rim is 5.2 mm away, and the panel's driver border sits 4.3 mm below. Also, needing no decision: grounded guard trace on the motor side, hatched ground on the bottom layer, a ground pour on the frame PCB under the band, and a 300 ms firmware lockout around knob motion or press.

**H15. No touch controller is chosen, and the MPR121 is discontinued.** [decision → D12]
Found by 4: touch-r (#1), touch-a (H4), sourcing-r (L1, M6), sourcing-a (H4).

**H16. A 1.6 mm touch band collides with the frame PCB's ZIF.** [fix]
Found by 1: touch-r (#3).
They overlap by 4.6 × 4.3 mm in plan with 0.5 mm vertical gap; at 1.6 mm the band sits 0.3 mm into the ZIF. Fix: notch the band around the ZIF or stop it at x ≈ 79, then rerun `--check` with `TOUCH_BAR_T = 1.6`.

**H17. The knob-window covers have nothing holding them and aren't in the BOM or STLs.** [fix]
Found by 2: enclosure-r (H3), enclosure-a (H2).
They are flush with no ledge (`model.py:432-437`), so they fall in. The hub has no STL either. Fix: add a 0.8–1 mm ledge, export STLs, and add a BOM line and an assembly step. (A single clear strip under the plate is a look alternative.)

**H18. The stand collides with the tray's front feet, and the feet don't touch the desk.** [fix]
Found by 2: enclosure-r (H2), enclosure-a (M2).
The overlap is 83 mm³ per foot in the tilted model, so the slab rides 1.5 mm off the magnets. The feet sit 0.22 mm above the desk. Fix: move the feet to the lower edge (an angled pad) and add a lip on the stand that catches the slab.

**H19. The checks only test the flat assembly, and they pass zero-clearance fits.** [fix]
Found by 3: enclosure-r (H6), enclosure-a (H1), display-r (H1).
`assembly.py:885` uses `tilt=False`. Overlap counts only above 0.01 mm³. Screw/target pairs are skipped. Fix: check the tilted model too, and add a minimum-gap table per mating pair, a floating-part check and screw-tip checks. Reword the ✅ table as "model checks".

**H20. The prototype standoffs are documented as 3 mm, but the model needs 3.3 mm.** [fix]
Found by 2: keys-r (M2), keys-a (H1).
`hardware/README.md:30`. At 3.0 mm the switch is held down 0.1 mm and may read pressed. Fix: 3 mm standoffs plus 0.3 mm shims and a 0.1/0.2 mm shim kit. List every standoff length in parts.md (M2 3.3, M3 21.65, display 12.45).

**H21. Driver pins float during reset or BOOTSEL (RP2350 erratum E9).** [fix]
Found by 5: knobs-r (#9), knobs-a (M1), firmware-r (L2), power-usb-r (M6), power-usb-a (L1).
NSTDBY and the PWM lines are bare GPIOs, and E9 on A2 silicon floats a pulled-down input to about 2.2 V. Fix: external 10 kΩ pull-downs on NSTDBY and each PWM net, about 1 kΩ in series on the high-side inputs, and a watchdog that drops NSTDBY. Specify RP2350B A4 in the BOM. Disable input buffers on the CC ADC pins.

**H22. Five FOC loops on one RP2350 are unproven.** [fix]
Found by 3: knobs-r (#13), firmware-r (H2), firmware-a (M2).
SimpleFOC's `syncSlices()` resets every slice on each driver init, and the MT6701 SSI driver ignores the CRC. Fix: on Rev 0, run 1 real and 4 dummy loops and target ≥2–5 kHz per motor. Put FOC on core 1 and in RAM. Initialize all drivers before enabling any. Read 24-bit SSI frames with the CRC. Map pins to slices in the schematic.

**H23. Flash writes on the RP2350 stall the FOC loop.** [fix]
Found by 1: firmware-r (H3).
`KNOB_CONFIG` is "stored per page". Fix: keep configs in RAM, write flash only on an explicit `SAVE` with the motors asleep, and use `__not_in_flash_func` for the loop.

**H24. The protocol framing is underspecified.** [fix]
Found by 2: firmware-r (H4), firmware-a (L1).
A single 0xCD magic can appear in payloads, and there's no resync, NAK, error table or `PING` spec. Fix: COBS framing with a CRC over the frame, error codes, per-chunk NAK and retry, version ranges, and a separate seq per direction. One C codec with a Python twin and golden vectors.

### Medium

**M1. Hinge fatigue can crack the sensor traces, and a bad angle then drives the motor.** [fix]
Found by 1: knobs-a (H4). Fix: check the SSI CRC, sanity-check angle jumps and drop NSTDBY on error. Use wide traces on the neutral axis and larger slot-end radii.

**M2. A stored phase order breaks when the reversible motor plug is reseated.** [fix]
Found by 3: knobs-a (M2), knobs-r (low), shorts (L3). Fix: a small open-loop direction check at first wake that invalidates calibration on mismatch, plus a shrouded or keyed header.

**M3. The bell is 0.3 mm from the plate.** [fix]
Found by 3: knobs-r (low), knobs-a (M5), enclosure-r (B1). Fix: `MOTOR_TO_PLATE` ≥ 0.8 mm; confirm `MOTOR_H` with calipers.

**M4. The knob board's back strip is unsupported.** [fix]
Found by 1: knobs-r (#8). Fix: bosses or screws behind each hinge.

**M5. The motor current budget rests on a guessed phase resistance.** [fix]
Found by 2: knobs-r (#10), knobs-a (M3). Similar gimbals measure 6–16 Ω. Fix: measure R and Kt on arrival, store R per knob and scale duty by measured VS. The shunt footprint from B6 gives Rev 0 real current data.

**M6. The full knob-board floorplan is unproven, and the docs and model disagree on driver placement.** [decision → D16]
Found by 2: knobs-r (#6), knobs-a (L1). The model puts the TMC6300 on the tongue; `knob-module.md:94` puts it on the fixed part. The RP2350B is modeled as a 7×7 RP2040.

**M7. Sideways finger force reads as a press.** [decision → D10]
Found by 1: knobs-a (H3). The cap top is 36 mm above the hinge, which levers sideways force 2.8× into the press direction.

**M8. Cogging (84 per turn) doesn't line up with 24/48 detents, and the knob snaps on wake.** [fix]
Found by 1: knobs-a (M4). Fix: a per-knob cogging feed-forward table, and re-anchor the detent grid at the current angle on wake.

**M9. Smooth mode drags because 3-PWM shorts the windings at zero torque.** [fix]
Found by 2: firmware-r (M5), knobs-a (L2). Fix: keep the driver in standby in free-smooth mode and wake it for effects.

**M10. Knob electrical details.** [fix]
Found by 1: knobs-r (#11, #12, low). Use 2 × 22 µF per driver (10 µF derates below spec). Use a shared CS + CLK with 5 separate DO lines, read by PIO. SN74LVC3G04DCT is SM8, not VSSOP. The MT6701 draws 10–14 mA, so logic is about 120 mA.

**M11. Key ESD path straight onto the matrix (and touch, BOOT/RESET pinholes).** [fix]
Found by 6: keys-a (M2), keys-r (L2), touch-a (M3), display-a (L4), enclosure-a (L2), power-usb-r (L1).
The cap gaps give about 5.6 mm air paths to the B3U terminals, and the lines run 80 mm of FFC to bare GPIO. Fix: a GND guard ring around each window, series resistors plus a TVS array at the knob-board ZIF and SH connector, 1–10 kΩ on touch electrodes, and ESD parts for CC lines. Name the VBUS TVS part (5–5.5 V standoff, clamping below the SY6280's 6 V absolute max).

**M12. Window and cap corners will bind.** [fix]
Found by 2: keys-r (M1, L5), enclosure-r (H5). JLC mills inside corners at about R0.5. Fix: draw R0.5 window corners, give caps R1.0 vertical edges, open the PCB window 0.2 mm so the plate is the guide, add a `HOLE_COMP` parameter and print a coupon.

**M13. The proto board doesn't test the full frame PCB's routing.** [fix]
Found by 2: keys-r (M5), keys-a (H3, L3). A B3U, a row trace and an SOD-123 must fit on each 3.6 mm strip, top side only. Fix: route one full row before the full order (consider SOD-523). Optionally add a ZIF and two diodes to the proto board, and cut a test frame from a full-size front-right corner.

**M14. Nub-to-plunger alignment and the acrylic cap route.** [fix]
Found by 1: keys-a (M3, M4). Fix: a 2.0 mm domed nub and locating pins for the frame PCB. Drop the laser-cut acrylic cap option: sheet tolerance alone is larger than the budget.

**M15. Key tests aren't measurable.** [fix]
Found by 2: keys-r (M6), keys-a (B2 test). Fix: actuation force at 5 positions (pass if the far edge needs ≤ 2× the center force), a witness-film glass check at 10 N, a measured gap, and 0 missed events in 500 presses on a logic analyzer.

**M16. Display parameters disagree with Waveshare's STEP.** [fix]
Found by 2: display-r (M2–M4), display-a (M4). `USB_BELOW_PCB` is 1.22 mm, not 2.97. `DISPLAY_PCB_LEFT` is 26.0 and `_BACK` 0.2. The connector pocket should be centered at 46.7 mm and 47 mm long. Button positions are off by 0.4–0.7 mm and may be top-actuated. Fix: correct the values, make the pinholes Ø3 mm or add guide tubes, and verify on a real board.

**M17. The 7B's EXIO5 USB/CAN mux isn't documented.** [fix]
Found by 3: display-r (M1), power-usb-r (M4), display-a (M4/L2). FSUSB42 U9 switches GPIO19/20 to CAN if EXIO5 goes high, and an ESP32 reset doesn't reset the CH32V003. Fix: document "never drive EXIO5 high", and that recovery is "unplug, hold BOOT, plug in".

**M18. Unknowns that only a real 7B answers: cover glass, front profile, backlight dimming.** [fix]
Found by 4: keys-r (H2), keys-a, display-a (M2, M3), display-r (L2). The only STEP is the touch SKU, and the non-touch 31727 may be a bare polarizer. Which dimming resistors are fitted is unknown. Fix: measure `PANEL_T` and the front lip, probe EN/FB while sweeping brightness, and record the board revision.

**M19. Image throughput is about half the plan's figure.** [fix]
Found by 4: display-r (M6), display-a (M1), firmware-a (H2), firmware-r (docs). Espressif's FAQ says about 500 KB/s, so one raw key takes about 85 ms and a page about 1.8 s. Fix: plan on 0.5 MB/s, make JPEG/RLE the default, use dirty rects and 2 framebuffers, and change the pass test to "full page < 300 ms". Vendor bulk/WinUSB is the fallback.

**M20. Heat and case material aren't specified.** [fix]
Found by 4: display-r (M5), enclosure-r (M2), enclosure-a (M3), display-a (L4). The case dissipates about 2.3 W steady in a sealed box, and the 7B is rated 0–65 °C. Fix: specify PETG or ASA, 4 walls and ≥25% infill at bosses. Log 2 h at full brightness on the first build.

**M21. Self-tapping screws in the service path will strip.** [decision → D14]
Found by 2: enclosure-r (M1), enclosure-a (M4). Plastic threads last about 5–10 cycles, the M2 bosses have 1.4 mm walls, and screw heads bear on 0.7 mm of floor. Also, needing no decision: floor web ≥ 1.2 mm, M2 bosses Ø5.5, and name the thread-forming screw type.

**M22. The stand is a solid 852 cm³ wedge, and stability rests on its guessed density.** [fix]
Found by 2: enclosure-r (M3), enclosure-a (M2, L3). Tip force is still 10–11 N at realistic infill. A 4 N pull on the cable tips it backward. Fix: shell it (3 mm walls plus ribs), recompute stability with 0.25 g/cm³, and get a JLC3DP quote.

**M23. Assembly steps need three hands.** [fix]
Found by 2: enclosure-r (M4), enclosure-a (H3). Fix: locating pins on the panel posts and plate, a printed prop for the 40 mm plate lift, and a build block or cradle. Fit the knob caps before inverting the case.

**M24. Inrush and hot-plug overshoot.** [fix]
Found by 2: power-usb-r (M2), power-usb-a (M2). The 7B carries ≥120 µF and the knob board 470 µF. Fix: RC-delay the SY6280 enable and put the knob-board soft start on the motor rail only. Add 22–47 µF of polymer at the input, set Rset explicitly, and pick a TVS that clamps below 6 V.

**M25. Hub resets on motor dips.** [fix]
Found by 1: power-usb-a (M4). The CH334 datasheet warns of LVR resets under dynamic load. Fix: 22 µF on VDD33, or feed it from its own LDO behind a diode.

**M26. Rev 0 bench connectors can short.** [fix]
Found by 1: shorts (H3). J2 power pads are unpolarized, and J1 puts 3V3 next to GND on a loose header. Fix: a polarized connector, a reverse-polarity FET or Schottky, an SMBJ6.0A across VS, and GND on J1 pins 1 and 14.

**M27. Touch cable reversal can reverse-power the touch chip.** [fix]
Found by 2: shorts (M4), touch-r (#9). Fix: palindromic `GND·3V3·SDA·SCL·3V3·GND`, or leave pin 6 unpoured. Put pull-ups on the knob board, and a ferrite bead plus 10 µF on the band's 3V3.

**M28. Loose metal and cables near moving parts.** [fix]
Found by 1: shorts (M2, M3). Spare FFC and SH cable fold within 1.5 mm of knob 4's bell, and the tray magnets sit under the motor-header tails. Fix: a printed fence by motor 4, 70–80 mm cables, magnets moved out from under the knob board, and a "shake out before closing" step.

**M29. The plate isn't specified as a sensing surface.** [fix]
Found by 3: touch-r (#5), touch-a (H2), enclosure-r (missing). Air gaps and voids kill sensitivity. Fix: 100% solid band area, a flat recess, full-coverage 3M 467MP/468MP (add it to the BOM), and no CF or metal-filled filament.

**M30. The touch prototype test can't validate the design.** [fix]
Found by 3: touch-r (#6), touch-a (H1), sourcing-r (L1). It uses a 26 mm copper-tape band on 3 mm acrylic, with no motors and no panel. Fix: a full-length, 10–12-segment strip under a printed-plate offcut, with motors running and the panel lit. Pass criteria: ±5% position, <50 ms latency, 0 false touches in 10 min of knob use.

**M31. Touch electrode pattern and events.** [fix]
Found by 1: touch-r (#7, #8). Fix: 10–12 chevron segments at 13–15 mm pitch with half-width ends, and 1–10 kΩ series resistors. Add `long` and `segment` to `TOUCH`. Export the band DXF.

**M32. Firmware hygiene.** [fix]
Found by 3: firmware-r (M1, M3, M6, L1, L3, L4), firmware-a (L1–L3), power-usb-a (L2). Interactive first pairing (a code on screen, press a key). A udev rule (`ID_MM_DEVICE_IGNORE`, `uaccess`). KNOB events at ≤200 Hz with timestamps. Two HID interfaces (boot keyboard + consumer). Probe ports by product string, and apply for real PIDs. A/B UF2 rollback or a BOOTSEL pinhole. Blank and sleep on USB suspend. Pinned toolchains and CI.

**M33. Missing BOM lines and tools.** [fix]
Found by 2: sourcing-r (M4, M6, L3), sourcing-a (M2, L3). The BOM lists 21 diodes, but 26 are needed (21 keys + 5 knob presses). RP2350B support parts have no part numbers (3.3 µH inductor, QSPI flash, crystal, regulator, load switch). Order 1 lacks a current-limited 5 V supply, an iron, jumpers, M2 screws and 3 mm standoffs. Buy 20+ B3U. "No soldering, no throwaway" is false for the prototype; reword it.

**M34. Tests record numbers without limits.** [fix]
Found by 3: sourcing-r (M3), power-usb-r (test plan), firmware-r (missing). Fix: peak motor ≤ 500 mA on a default port, VBUS ≥ 4.75 V while clicking, driver < 70 °C after 30 s at a stop, standby ≤ 5 mA. Add the 12-step power/USB bring-up plan and firmware stress tests: replug, sleep/resume, flash-while-running, fuzz.

**M35. Motor cogging risk rests on one seller.** [fix]
Found by 1: sourcing-r (M5). Fix: buy from two sellers and spin each motor by hand, unpowered, on arrival. Make this a gate for Order 2.

**M36. No lead-time plan.** [fix]
Found by 2: sourcing-r (missing), sourcing-a (M4). The critical path is serial, about 10–14 weeks. Fix: add durations and a JLC stock check on quote day.

**M37. Tall clear caps act as light pipes.** [decision → D15]
Found by 2: keys-r (M3), keys-a (M1). At 45°, an 8.4 mm cap shifts the line of sight 4.7 mm (26% of the cap), producing a mirror strip on the side walls. Also, needing no decision: black solder mask so the window edges don't glow.

**M38. Bypassing the host app to reflash or remap keys needs no authentication.** [decision → D17]
Found by 1: firmware-a (M4).

**M39. ESP32 updates need esptool and a PID switch.** [decision → D18]
Found by 1: firmware-r (M2).

### Low

**L1. Doc errors.** [fix] Found by 8: keys-r (L4), keys-a (L1), knobs-r (low), display-r (L1), touch-r (#10), firmware-r (docs), sourcing-r (L2), sourcing-a (L1, L2, L4). Some examples:
- `pcb.md` says "diodes if needed".
- plan.md says "guides in the case" and "3–5 mm caps".
- plan.md says Arduino-ESP32 for the RP2350.
- knob-module.md says the knob runs from the ESP32.
- The band height is given as 10 mm, but the model has 11.2.
- The FFC "4.6 mm past the panel" is really 1.2 mm inside it.
- Stock figures are stale.
- The deepest 7B part is the microSD socket, not the USB-C port.
- "146 px per key" is the pitch; about 120 px is visible.
- B3U NRND is stale.
- "Drivers are the biggest cost" is wrong.

Add a "checked on" date to stock tables.

**L2. Rattle.** [fix] keys-r (M4). The cap has 0.2 mm of free play. Plan an optional foam or silicone ring on the flange.

**L3. Force spread.** [fix] keys-a (L2). OF is 1.01–1.99 N. Buy extra switches and sort them by feel. Order alternative switches with the prototype.

**L4. USB wall pocket too loose.** [fix] power-usb-r (L3), power-usb-a (L4). Shrink it from 14 × 8 to about 13 × 7 mm.

**L5. GH has no staggered contacts.** [fix] shorts (L4, L6). Add "PC unplugged" to steps 4 and 7, and label the knob USB test pads "unplug GH first".

**L6. Small enclosure fixes.** [fix] enclosure-r (L2, L3, L5), enclosure-a (L1). Export the plate STL face-down, clarify the magnet polarity wording, use the rear foot contact in `stability.py`, and watch the 0.7 mm counterbore skin.

**L7. Look items.** [decision → D15] enclosure-r (L1, L4), touch-a (M2). Plate-to-tray seam and over-constraint, the cable exiting upward (a right-angle cable), and an invisible touch band (a groove or texture).

**L8. Knob lead coil margin.** [fix] knobs-a (L3). The lead coil is 6.6 mm in 6.7 mm. Measure the leads.

**L9. Single-source display.** [fix] display-r (L3). Waveshare revises boards. Buy two 7Bs if the budget allows, and record the silkscreen revision against the STEP.

**L10. Cost doc fixes.** [fix] sourcing-a (H4, M1, M5). Raise the PCB-redo line to $150–250. Count extended parts from the BOM, and consider the RP2354B (on-chip flash). Show key and dial counts in the + XL comparison.

---

## Disagreements

**1. Does the 7B's native-port VBUS go straight to its 5 V rail?** display-review (L1) and display-adversarial (L1) say no: it passes through an AO3401 ideal diode (Q5). shorts-review (H1) and power-usb-adversarial (M1) say yes.
*Resolved from the Waveshare schematic (ESP32-S3-Touch-LCD-7B-Schematic.pdf, page 1).* Type_C2 ("USB") VBUS pins A4/B9 and A9/B4 join the **5V** net directly, with only TVS2 (LTVS16H5.0ET5G) to ground. The two AO3401/MMBT3906 ideal-diode stages both take their input from **VUART**, the UART port Type_C1: Q5 feeds the VBUS/charger net and Q10 feeds 5V. So `wiring.md:80` is correct, and the display reviewers misread which port Q5 serves. The back-feed path in H4 is real. The SY6280 quote ("can block … under the shutdown") supports it: it blocks only while disabled, and the design keeps it always on.

**2. MPR121: usable or dead?** touch-adversarial says it's been discontinued since 2019. touch-review recommends it anyway (JLC C91322, 3,003 in stock).
*Both are right.* NXP staff on the NXP community forum confirm it's discontinued under PCN16772 and no longer made, with no replacement; Seeed's forum cites a 2019 longevity end. Distributor stock remains. For a handful of builds the existing stock is enough, but don't treat it as a long-term part. See D12.

**3. B3U-1000P: NRND or not?** keys-review and `open-questions.md:23` say LCSC marks it "not recommended". sourcing-review and sourcing-adversarial checked live on 2026-10-17 and found 110,060 in stock with no lifecycle flag.
*Resolved for the live checks* (two independent fetches, newer than the doc). I didn't re-fetch LCSC myself. Downgrade the warning, but still order alternatives for feel.

**4. CH334F power strap.** firmware-adversarial: strap self-powered. power-usb-review: set bMaxPower ≤ 100 mA and set the strap on purpose. power-usb-adversarial: an owner decision.
*Resolution:* declaring bMaxPower ≤ 100 mA in both firmwares works under either strap, so do that regardless. Then strap PSELF low (bus-powered), which is truthful. Keep a 0 Ω option to flip it if a host misbehaves. This needs no owner choice, so B12 is tagged [fix].

**5. Which palindromic GH pinout.** Three variants were proposed. Two reviewers (shorts, power-usb-adversarial) put GND on the outer pins: `GND·VBUS·CC1·D−·D+·CC2·VBUS·GND`. power-usb-review put VBUS outermost.
*Resolution:* use GND outermost. All three are safe when reversed. GND at the ends keeps VBUS off the edge pins, which are the likeliest to touch when a plug goes in at an angle.

**6. How to stop caps loading the glass.** keys-adversarial: shorten the cap so its bottom sits at the PCB top, which gives ≥ 1.8 mm to the glass, "image unaffected", no decision. display-review, display-adversarial and enclosure-adversarial: raise `GLASS_GAP` to 0.5–0.8 mm and accept parallax.
*Resolution:* these fix different parts. Shortening the cap clears the cap but leaves the PCB 0.2 mm from the glass, so B1 (support) still applies. The image isn't strictly unaffected either: swapping 1.6 mm of resin for air moves the apparent image depth by about 0.5 mm. That's small but not zero. Recommended combination in D8.

**7. USB throughput.** display-review: 0.5–0.9 MB/s. display-adversarial: 0.6–0.9. firmware-adversarial: about 0.5 MB/s max, from Espressif's FAQ.
*Resolution:* plan on 0.5 MB/s, the vendor's own figure, until it's measured on a 7B.

**8. Is frame-PCB support a decision?** enclosure-review tags it no-decision. keys-review and display-adversarial tag it decision.
*Resolution:* a decision (D8). The options differ in cost, look and part count, and it's on the owner's known list.

**9. TMC6300 on the tongue or off it?** The model puts it on the tongue (`model.py:250`); the doc puts it on the fixed part. knobs-adversarial: follow the doc. knobs-review: decide by floorplanning.
*Resolution:* D16. Recommend the doc (off the tongue) unless a real-footprint floorplan shows it won't fit.

**10. Is the native port identified?** display-review says it's settled (Type_C2, 35.7 mm from the back edge). display-adversarial says it's half answered.
*Resolution:* the schematic confirms Type_C2 → R65/R66 → U9 → GPIO19/20 is native. Its physical position comes from Waveshare's PCB view per display-review. Confirm on hardware, then close `open-questions.md:379`.

**11. Single-build cost.** sourcing-review: $400–600. sourcing-adversarial: $375–575 ($410–650 with a JLC3DP case).
*Resolution:* quote about $375–600 until a real JLC cart quote with a US address exists.

**12. Is the 6.2 mm panel depth right?** display-review says it matches the STEP. display-adversarial notes the STEP is the touch SKU.
*Both are true.* The number fits the bare module inside the touch model; the non-touch front is unmeasured (M18).

---

## Decisions for the owner

| # | Decision | Options | Recommendation | Rough cost / impact |
|---|---|---|---|---|
| D1 | **Cost and import duty** | (a) Accept and restate honestly. (b) Cut cost: top-side-only assembly, SMD connectors, RP2354B, TMC6300 from DigiKey. (c) Group buy. | (a) + (b). Get a JLC cart quote with a US address first. Put duty in every table. README says "costs more than a + XL (36 keys, 6 dials, $350)". | Single build about $375–600 now. (b) may save $50–100. Prototype about $160–280. |
| D2 | **TMC6300 / MT6701 stock** | TMC6300: LCSC (59 left), JLC Global Sourcing or consigned from DigiKey (~$2.44, ~4,100 stock), or draw the DRV8316 fallback. MT6701: CT SOP-8 (C3003196), or a second-source footprint (AS5600/AS5047). | MT6701CT SOP-8 if JLC stocks it. Source the TMC6300 via Global Sourcing/DigiKey. Reserve the full-build quantity in JLC's parts library once Rev 0 passes. | Saves about $25/build on drivers. Avoids a stalled order. |
| D3 | **Widen the prototype scope** | Add the 7B (replaces the 2.4" screen + devkit). Put caps + proto frame on the Rev 0 JLC order. Add a "Rev 0.5" RP2350B + CH334F + touch IC + connector test board to the same panel. Run a full-length touch test. | Do all four. They retire the risks that would otherwise cost a $150–250 four-board respin. | About +$50–80 net; one shipping and duty charge instead of three. |
| D4 | **Host software** | (a) OpenDeck plugin only: no haptics, pages or swipes. (b) Companion Satellite: encoders and per-control bitmaps, no haptic config. (c) Own host core ("clickdeckd") with a Python library, plus a thin Satellite client and OpenDeck plugin. | (c). The own app is primary and owns knob feel. OpenDeck/Satellite are "basic mode". Say so in the README now. | Most software work. The only path that keeps the haptics requirement. |
| D5 | **Offline page switching / screen wake** | (a) Optional one-wire UART from the RP2350 to the 7B's J8 GPIO6 (HY2.0 lead). (b) No link: firmware disables idle blanking with no host and shows a "keyboard mode" page. | (a), with the footprint and connector on the knob board now. Do (b) in firmware anyway as the fallback. | About $1 and 1 GPIO. Makes offline mode coherent. |
| D6 | **Double-sided assembly** | (a) Standard double-sided for the panel. (b) Redesign for top-side only: press switch on top or a small separate board, SMD motor connectors and USB-C. (c) JLC fits the top side; hand-solder the B3U press switches and THT parts. | (c) for Rev 0 now. Quote (a) against (b)/(c) before the full build. Keep THT shell legs on the external USB-C for strength. | (a) adds about $60–140 in fees per order. (c) needs about 30 min with an iron. |
| D7 | **Internal hub cabling (+$25)** | (a) Keep the CH334F hub, two USB devices, CC sensing. (b) Drop it: one MCU on USB with a UART relay and custom bootloader, or two external cables. | (a). Reviewers rate it the right architecture. Its fixes (crystal, strap, routing, reverse blocking) cost cents. | About $25/build, mostly extended-part fees. |
| D8 | **Key support** | (1) More frame support: plate bosses between knob windows and along the right edge, or spacers onto the panel's inactive border (9.5 mm front, ~8.8 mm right). (2) Cap down-stop on the plate/PCB, gap 0.5–0.8 mm or a shorter cap, plus shims. (3) Stiffer frame: 2.0 mm PCB, or an aluminium/steel stiffener. (4) A second switch per key (or rocker/hinged cap). (5) Seat the PCB on the glass with PET pads (loads the LCD; not advised). | (1) + (2) now. Put the second-switch footprint on the proto board and decide (4) after the 5-point force test. (3) only if a frame offcut test still sags. | (1)(2) are nearly free; parallax goes up about 0.3–0.6 mm. (4) costs 21 more B3U (~$4) plus routing. (3) costs about $10–30. |
| D9 | **Power on default 500 mA ports** | (a) Require C-to-C at 1.5 A or more; haptics almost off on default ports. (b) Keep 500 mA for motors and accept resets on some ports. (c) Add a PD sink (CH224-class) for 5 V/3 A. | (a) as policy, with firmware holding backlight low and motors off until configured, and polling CC continuously. Add (c) as an optional footprint. Use about 0.8 A for the motor budget on 1.5 A until measured. | (c) about $0.5 plus a $3 extended fee. (a) degrades A-to-C users. |
| D10 | **Knob press hinge redesign** | Serpentine or double-beam flexure, a separate hinged carrier, a softer switch, or a pivot on the knob axis / parallel-guided flexure (fixes the sideways false clicks of M7). | Do the $0 scrap-FR-4 test first. Then make the Rev 0 hinge tunable (perforations) with a set-screw striker. Go to a parallel-guided flexure if sideways false clicks show up. | Board area. Rev 0 may need one respin. |
| D11 | **Touch band vs motor bell proximity** | (a) Keep the layout; guard trace + hatch + 300 ms lockout. (b) Move the knobs ≥ 4 mm forward for more gap. (c) Put the band above the windows. (d) Drop the band. | (a), then the realistic test (M30) before freezing the layout. If it fails, (b). The band unplugs, so it never blocks the build. | (a) free; (b) means re-laying the plate and knob board. |
| D12 | **Touch controller** | MPR121QR2 (EOL, ~3,000 at JLC, matches the breakout). AT42QT2120 (69 in stock, 3-channel slider, coarse). CY8CMBR3108 (cheap, no slider). RP2350 PIO self-cap (needs about 10 pins plus an expander). | MPR121QR2 for this small run, with interpolation in firmware. Buy spares. Note the EOL and revisit for any larger run. | About $2.70 plus the extended fee. |
| D13 | **Display firmware toolchain** | ESP-IDF 5.x (esp_lcd + esp_tinyusb), Arduino as an IDF component, or Waveshare's patched "esp32-XIP" Arduino core. | ESP-IDF 5.x for the display. Pin arduino-pico + SimpleFOC (or pico-sdk) for the RP2350. Both in CI. | Needed for the B13 sdkconfig. Steeper than plain Arduino. |
| D14 | **Case fasteners and material** | Self-tapping into thicker bosses, or heat-set inserts. PLA vs PETG/ASA. | M3 heat-set inserts in the plate posts and PETG. | About $3 plus a soldering-iron tip. |
| D15 | **Look items** | Cap finish (frosted sides, polished faces, thinner top), window covers (individual with a ledge, or one clear strip), plate seam lip, cable exit, a band marker groove. | Order 3–4 cap variants with the prototype. Individual covers with a ledge. Add a groove over the band. | A few dollars of SLA. |
| D16 | **Knob-board floorplan** | Driver on the tongue (about 19 traces cross the hinge) or off it (only sensor/switch traces cross). 2 or 4 layers. Shunts on all 5 drivers (5 ADC pins; 44 of 48 GPIO used). | Off the tongue, per the doc. Floorplan with real footprints (QFN-80) before the full order, and mirror it on Rev 0. Shunt footprints on Rev 0 only. | 4 layers add roughly $10–30. |
| D17 | **Reflash / keymap security** | Open (status quo), or physical confirmation (hold a knob press 3 s) before `REBOOT_BOOTLOADER` or `HID_MAP` changes. | Physical confirmation; keep the bootloader open. | Firmware only. |
| D18 | **ESP32 update path** | esptool + BOOT pinhole only, or in-app OTA with an A/B layout and rollback. | In-app OTA once B13 is done; keep esptool for recovery. | Uses flash for two app slots. |

Count: 86 findings, 67 tagged [fix] and 19 tagged [decision]. Every [decision] finding maps to D1–D18; D7 comes from the owner's list rather than a single finding.

## Owner's answers (2026-10-17)

| # | Answer |
|---|---|
| D1 | Cost is not a design driver. Keep the numbers accurate (add import duty, get a real quote), but don't cut features to compete with the + XL. |
| D2 | As recommended: MT6701CT SOP-8; TMC6300 via JLC Global Sourcing or DigiKey; reserve full-build stock after Rev 0 passes. |
| D3 | As recommended: widen the prototype (7B, caps + proto frame, RP2350B/hub/touch/connector test board, full-length touch test). |
| D4 | Changed: a VIA-style web configurator (WebUSB/WebHID, Chromium) is the main tool. It sets key layout, HID shortcuts and macros, knob feel, images and firmware, all stored on the device, so the device works standalone. A small optional host daemon adds live integrations (changing images, app state, scripts). OpenDeck/Companion Satellite stay possible later as thin clients. |
| D5 | As recommended: GPIO6 link footprint on the knob board now (optional fit); no idle blanking without a host. |
| D6 | Explore a top-side-only redesign first. Hand-soldering bottom parts is the last resort if top-side gets too complicated. |
| D7 | Keep the internal hub. |
| D8 | As recommended: more frame support + cap down-stop + 0.5–0.8 mm gap with shims; second-switch footprint on the proto board, decide after the force test. |
| D9 | As recommended: require a 1.5 A+ port (C-to-C), haptics nearly off on 500 mA ports, optional PD sink footprint, ~0.8 A motor budget until measured. |
| D10 | As recommended: scrap-FR4 test, then a tunable hinge + set-screw striker on Rev 0; parallel flexure if side force causes false clicks. |
| D11 | As recommended: guard trace + hatch + 300 ms lockout, then the realistic test; move knobs forward only if it fails. |
| D12 | Touch is a nice-to-have. Use the AT42QT2120 if it's cheap and available; if sourcing an alternative to the MPR121 is expensive, drop the touch band. |
| D13 | As recommended: ESP-IDF 5.x for the display, pinned arduino-pico + SimpleFOC for the RP2350B. |
| D14 | As recommended: M3 heat-set inserts, PETG. |
| D15 | One standard clear finish for now; revisit after seeing it. |
| D16 | As recommended: drivers off the tongue, floorplan with real footprints first, shunts on Rev 0 only. |
| D17 | Changed (2026-10-18): VIA-style trust; the browser's WebUSB/Web Serial device picker is the confirmation, with no pinhole or knob hold by default. An optional lock (stored on the device) brings back the 3 s knob hold for reflash and keymap changes. |
| D18 | Changed: no OTA slots. Firmware updates go through the web configurator using each chip's ROM bootloader (ESP32-S3 via esptool-js over Web Serial; RP2350B via its UF2 bootloader), so a failed update can always be retried. Images use a WebUSB bulk interface, since WebHID's 64-byte reports are too slow. Linux needs a udev rule. |

### Added after the review: recovery ("factory reset") plan (2026-10-17)

Owner asked for a way back to factory for anyone experimenting. To apply (no decision needed):

- Knob board BOOTSEL reachable from outside: a third pinhole in the back wall (or the base), next to the display board's BOOT/RESET pinholes. Checked by `assembly.py --check` like the others.
- Settings reset: hold the top-left key while plugging in to clear stored settings (firmware kept). Bad settings checksum also boots defaults.
- Web configurator "Restore factory firmware": flashes the pinned GitHub Release builds to both chips through their ROM bootloaders (ESP32-S3 download mode via esptool-js; RP2350B UF2), with step-by-step prompts.
- Docs warn: never burn ESP32 eFuses or RP2350 OTP (secure boot, flash encryption). That is the only truly irreversible brick. Our firmware never writes them.
- Recovery steps start with "unplug for 10 s": the 7B's CH32V003 expander isn't reset by an ESP32 reset, so a stuck USB/CAN switch (EXIO5) only clears on power-off.
