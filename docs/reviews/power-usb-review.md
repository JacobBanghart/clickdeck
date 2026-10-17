# Design review: power and USB subsystem

Reviewer role: senior hardware design engineer, standard review (not red-team), 2026-10-17. Scope: USB board, JST-GH link, internal USB-C cable to the Waveshare 7B, power budget and protection. Sources: repo docs/CAD, the Waveshare 7B schematic, the SY6280 datasheet, JST GH ratings, and the WCH CH334 family datasheet. Nothing here has been built.

## Verdict

**Go with changes.** The architecture (one external port, internal hub, two full-speed devices, CC-based budget) is sound and well chosen.
One geometry blocker: the external socket as modeled cuts the USB board's arm almost in two. Four high-priority fixes are needed before the PCB order: hub power descriptors, upstream high-speed routing, a GH pinout that survives a reversed cable, and the default-port budget.
None of these needs a new architecture. All are fixable in the schematic, layout or firmware for little or no extra cost.

## Strengths

- **The architecture fits the goal.** Owning the external port gives real CC sensing. The 7B can't sense CC itself: its native port has fixed 5.1 kΩ pull-downs (Type_C2, R62/R63 in the schematic). Two USB devices behind a hub give each chip its own USB update path, so no custom bootloader is needed.
- **The CC thresholds are correct.** They match the Type-C spec's vRd bands (docs/wiring.md:121-125). Both upstream CC pins have Rd, the downstream port has 56 kΩ Rp to 5 V, and an A-to-C cable correctly reads as default power.
- **Full speed over 100 mm of JST-GH is fine** (docs/wiring.md:163-165). D+/D− sit on pins 4 and 5, flanked by GND on pins 3 and 6.
- **The display port's VBUS goes through a current-limited switch.** A fault in the internal cable is contained (docs/wiring.md:102-105).
- **Strain relief is designed in.** There is a backstop for push-in, the board edge bears on the wall for pull-out, a wall pocket takes sideways levering, the cables are clipped, and the plugs are checked for insertion. `assembly.py --check` passes: 0 problems, 14 of 14 plugs insertable, 23 of 23 screws reachable.
- **The docs are honest about what is unverified.** Open questions are tracked (docs/open-questions.md).

## Issues

### Blocker

**B1. The external socket's notch leaves 0.45 mm of PCB behind it.** [no-decision]
- Evidence: the arm is 8.1 mm deep (`arm_y0 = dy1 + 0.4` to `iy1`, cad/model.py:669). The socket cutout is 7.65 mm deep (cad/model.py:687, `USB_C_SOCKET` depth 7.35 mm, cad/params.py:178).
- Effect: there is no room left for the socket's 16 SMD pads or its rear legs, or for routing VBUS, CC and the D± pair past the socket. The arm segment holding the right-hand screw (x = −8.3) hangs on that sliver. `full_usb_board_outline.dxf` inherits all of this.
- Further evidence: LCSC lists C2894902 as "SMD, recessed", 6.5 mm long, with no through-hole legs listed. The strain-relief claim at docs/wiring.md:195-197 and docs/bom.md:238 is therefore unverified (this is also open in docs/open-questions.md:144).
- Recommendation: get the real HC-TYPE-C-16P-CB1.6 drawing. Model the cutout at the drawing's slot length, which is usually shorter than the shell. Check that pads, legs and a routing channel fit within 8.1 mm. If they don't, pick a mid-mount part with a shorter slot that has real THT legs, or widen the arm where it passes behind the display board (check its underside parts).

### High

**H1. Bus-powered hub vs. bMaxPower: the host may refuse to configure the devices.** [no-decision]
- A bus-powered USB 2.0 hub can only promise 100 mA per downstream port. Linux then rejects configurations above that ("insufficient available bus power"), and Windows flags them.
- Default descriptors are often above 100 mA. The Pico SDK uses 250 mA, and Arduino-ESP32 commonly uses 500 mA. Nothing in docs/protocol.md:7-31 or docs/pcb.md:61-73 covers this.
- Recommendation: declare bMaxPower ≤ 100 mA in both firmwares. Separately, check the CH334F's self-powered/bus-powered strap (the family datasheet says it is set by pin or EEPROM) and set it on purpose. Add this to the bring-up test.

**H2. The upstream link runs at 480 Mbit/s over about 50 mm of a 2-layer arm.** [no-decision]
- The CH334 is a USB 2.0 high-speed hub, so the PC side runs at high speed. Only the downstream legs are full speed.
- The model puts the hub at (−63.5, 44.5) and the socket at x = −16 (cad/model.py:907). The pair would run about 48 mm along the cramped arm, past two screw holes.
- The docs only mention full speed (docs/wiring.md:163) and specify a 2-layer 1.6 mm board (docs/bom.md:216).
- Recommendation: put the hub on the arm next to the external socket, so the high-speed run is under 15 mm and the long legs are the tolerant full-speed ones. Route a 90 Ω differential pair as coplanar with ground (use JLC's impedance calculator), with no vias. Place the USBLC6 in-line at the socket. Keep the bottom-layer ground unbroken under the pair. Join the A6/B6 and A7/B7 contacts with minimal stubs.

**H3. A reversed JST-GH cable puts 5 V directly on RP2350 ADC pins.** [no-decision]
- With pin order `1 VBUS · 2 VBUS … 7 CC1 · 8 CC2` (docs/wiring.md:162), a "reverse direction" cable maps VBUS to knob pins 7 and 8. The 10 kΩ resistors sit on the USB board side, so 5 V reaches an unpowered RP2350's ADC pins with no current limit.
- AliExpress listings mix same-direction and reverse cables (docs/bom.md:275).
- Recommendation: make the pinout mirror-symmetric: `1 VBUS · 2 GND · 3 CC1 · 4 D− · 5 D+ · 6 CC2 · 7 GND · 8 VBUS`. A reversed cable then only swaps CC1/CC2 (harmless) and D+/D− (it fails to enumerate, but nothing is damaged). Also add about 10 kΩ in series at the knob end of each CC line.

**H4. Default-port budget: the docs contradict themselves, and the device is over spec.** [decision: features/cost]
- docs/wiring.md:127 says the defaults "keep the whole device under the offer". Lines 128-131 then admit about 1 A on a 500 mA port: 350 mA display + 50 mA hub + 60 mA logic + 500 mA motors = 960 mA, which also exceeds a USB 3 port's 900 mA.
- Ports with electronic current limits trip and drop the whole device, re-enumerating both chips. A voltage brownout guard can't see that coming.
- Options:
  - (a) "C-to-C on a 1.5 A or 3 A port required", with haptics nearly off on default ports (about 40 mA of headroom). docs/lessons.md:47 already says "Require a C-to-C cable".
  - (b) Keep 500 mA for motors and document that some ports will reset.
  - (c) Add a USB PD sink (for example a CH224-class chip) to ask for 5 V/3 A on hosts that only offer 1.5 A on Rp. This costs about $0.5 and one more extended part.
- The 1.5 A case is also tight: 1.46 A against a 1.5 A offer, using an unmeasured 350 mA display figure. Use about 0.8 A of motor budget until it is measured.

### Medium

**M1. The brownout threshold of 4.6 V will false-trip** (docs/wiring.md:135-136). Type-C allows 4.75 V at the source plus up to about 250 mV of drop on each of VBUS and GND in the cable at 3 A. Add the GH contacts and the load switch, and a compliant setup can reach the knob board at about 4.3-4.4 V. Nothing downstream needs 4.6 V (the TMC6300 runs from 2 V). Use about 4.3 V plus a dV/dt trigger, and treat the CC budget as the primary limit. [no-decision]

**M2. Inrush stacks up.** The SY6280 turns on in 120 µs and has no real soft start (datasheet: TON 120 µs, ILIM 0.75-1.25 A at 6.8 kΩ). The 7B has at least 100 µF on its 5 V rail (C4 100 µF plus several 10 µF), so the display port draws about 1 A for close to 1 ms at plug-in. The knob board's 470 µF ramps at the same time.
- Recommendation: delay the SY6280's EN with an RC (EN must not float, and needs ≥ 2.4 V). Keep the upstream VBUS capacitance at 10 µF or less. Put the knob board's soft-start switch on the motor rail only, enabled by firmware after it reads CC, and power the logic directly. [no-decision]

**M3. Nothing in hardware limits current on the knob path.** Only firmware enforces the "~1.8 A cable cap" (docs/wiring.md:132-134). A short on the knob board or a stuck driver goes straight to the PC port and the 2 × 1 A GH contacts.
- Recommendation: make the knob board's load switch current-limited, for example a second SY6280 with ILIM set to about 1.8 A, which also has reverse blocking. Specify AWG 26 for the GH cable: JST rates GH at 1 A for AWG 26, and cheap cables are often AWG 28-30. [no-decision]

**M4. Undocumented 7B detail: a USB/CAN mux.** The ESP32's GPIO19/20 reach Type_C2 through an FSUSB42 mux (U9) selected by expander pin EXIO5, with a 10 kΩ pull-down that selects USB. Waveshare: "Pull down to USB mode, otherwise CAN mode." The display firmware must never drive EXIO5 high, or USB disappears. Add this to docs/wiring.md:78-90. [no-decision]

**M5. Hub chip details are unconfirmed.** Check the CH334F's own row in the datasheet for: MTT (otherwise both full-speed devices share one 12 Mbit/s translator, at the same time as about 1 MB/s of images), crystal-free operation, the power-mode strap, and integrated terminations. Also check its stock (docs/open-questions.md:141). [no-decision]

**M6. RP2350 ADC pins used for CC sensing.** Disable the digital input buffer on the ADC pins (RP2350 erratum E9: leakage on inputs). Use 27 Ω series resistors on the RP2350's D±. [no-decision]

### Low

- **L1. Unspecified protection parts.** The "TVS" on VBUS (docs/bom.md:243) has no part number: pick one with a 5-5.5 V standoff. CC1/CC2 are exposed with no ESD part; the 10 kΩ helps, but consider a 4-channel array that covers D± and CC. Connect the shell to GND at the socket. [no-decision]
- **L2. SY6280 notes.** The ~1 A limit is set by a resistor: 6800/Rset, ±25% (docs/wiring.md:104). Its reverse blocking only works while disabled. If the 7B's UART port is plugged in during service, it can backfeed through the display port: add a warning to the service docs. [no-decision]
- **L3. The wall opening barely restrains levering.** At 14 × 8 mm with a 12.5 × 6.5 mm overmold there is 0.75 mm of clearance, so a tilting plug loads the socket before it reaches the wall. A tighter opening rejects some cables. [decision: size/look]
- **L4. Suspend behaviour.** USB suspend (PC asleep) should blank the backlight and sleep the motors. The docs don't cover it. [no-decision]

## Missing

- A power tree with numbers: currents per rail, voltage drops from PC to knob board, and capacitance per rail.
- A measured 7B current at full backlight. Waveshare gives only "5V 350mA".
- Exact part numbers for the knob board's load switch and the VBUS TVS.
- A host compatibility matrix:

  | Host or path | Expected behaviour |
  |---|---|
  | Linux, Windows, macOS | All supported |
  | A-to-C cable | Works, default power |
  | Bus-powered external hubs | Unsupported: say so |
  | Docks and monitor hubs | To be tested |
  | KVMs | To be tested |

- A bring-up and test plan for this subsystem (there is none in docs/prototype-tests.md):
  1. Bare-board short check.
  2. Current-limited bench power-up.
  3. CC readings with 0.5/1.5/3 A sources in both cable orientations.
  4. `lsusb -t` showing the hub at 480M and both devices at 12M on separate ports, with no power rejections in dmesg; repeat on Windows and macOS.
  5. Scope the VBUS inrush at hot-plug.
  6. Electronic-load sweep of each budget for 10 minutes on real laptop ports.
  7. Short the display port's output.
  8. Plug in a reversed GH cable (after H3).
  9. Stream images while knob HID traffic runs at the same time.
  10. Sleep and wake the PC.
  11. Sideways and axial pull test on the external cable, about 30 N.
  12. ESD at the external port, if a gun is available.

## Actions before ordering

1. Get the C2894902 drawing. Fix the cutout and the arm in the CAD and regenerate the outline DXF (B1).
2. Move the hub next to the external socket in the model, and plan the 90 Ω coplanar pair (H2).
3. Change the GH pinout to the mirror-symmetric one and add knob-side CC resistors (H3). Update docs/wiring.md:162.
4. Decide the default-port policy: require C-to-C, keep 500 mA, or add a PD sink (H4). Fix docs/wiring.md:127-131 and set the 1.5 A budget to about 0.8 A until measured.
5. Confirm the CH334F's MTT, clock, power strap and terminations. Set bMaxPower ≤ 100 mA in both firmware plans (H1, M5).
6. Choose a current-limited, reverse-blocking switch for the knob board; delay the SY6280's EN with an RC; pick the TVS and ESD parts (M2, M3, L1).
7. Lower the brownout threshold and add dV/dt detection (M1). Document the 7B's EXIO5 mux (M4).
8. Measure the 7B's current at full backlight on a bench before freezing the budgets.
9. Check JLC basic/extended status and stock for every USB-board part on order day.
10. Add the test plan above to docs/prototype-tests.md.

Sources: [7B schematic](https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-7B/ESP32-S3-Touch-LCD-7B-Schematic.pdf), [7B wiki](https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-7B), [SY6280AAC datasheet](https://olimex.com/Products/Components/IC/SY6280/resources/SY6280AAC.PDF), [JST GH ratings (Mouser)](https://www.mouser.com.tr/new/jst-connectors/jst-connectors-gh-wire-to-board-connectors), [CH334 family datasheet (LCSC)](https://atta.szlcsc.com/upload/public/pdf/source/20240313/2136C33A6EB724334E520DEFC33CFBA6.pdf), [C2894902 at LCSC](https://www.lcsc.com/product-detail/C2894902.html).
