# Rev 0 knob module (prototype)

One knob's section of the full knob board: MT6701 sensor, TMC6300 driver
with 3-PWM drive, B3U press switch, motor and sensor on a hinged tongue. It plugs into the
Rev 0.5 test board (RP2350B + hub, same JLC order; [pcb.md](pcb.md)), or
into an RP2350B core board with jumper wires before that arrives. This is
the netlist-level spec to draw the KiCad schematic from. Untested.

In the full build the knobs run on the knob board's RP2350B, which has its
own USB connection through an internal hub ([wiring.md](wiring.md)). Rev 0's
J1 header is plain 3.3 V signals, so any 3.3 V controller can drive it
([parts.md](parts.md)).

Outline (with the tongue slots): `cad/out/proto_knob_module_outline.dxf`.
**Layout waits on measuring the 2204 motor** (bolt pattern, base height).

## Parts

| Ref | Part | Package | LCSC | Notes |
|---|---|---|---|---|
| U1 | TMC6300-LA-T | QFN-20 3×3 | C5274455 (59 in stock at LCSC, $5.93, checked 2026-10-17); C5196961 is out of stock | Extended part; JLC assembles it. Source through JLC Global Sourcing or consign from DigiKey (~$2.44, ~4,100 in stock); reserve the full-build quantity once Rev 0 passes |
| U2 | MT6701CT-STD | SOP-8 | C3003196 (JLC, extended; check JLC stock on layout day) | Magnetic angle sensor, SSI mode. Not the MT6701**QT** (C2913974): that's a 3×3 QFN-16, and it was out of stock at LCSC on 2026-10-17. The package sets the sensor height and so the magnet gap |
| U3 | SN74LVC3G04DCTR | SM8 (DCT, SSOP-8 class; not VSSOP) | C139324 | Triple inverter, derives low-side inputs. Check the footprint |
| SW1 | B3U-1000P | SMD | C231329 | Press switch, **top side**, on the board's fixed front border in front of the tongue. An arm on the printed motor spacer reaches over the slot; an M2×3 set screw in the arm is the adjustable striker. Same as the full knob board ([pcb.md](pcb.md)) |
| C1, C2 | 22 µF 10 V X5R | 0805 | (basic part) | VS bulk, at U1 |
| C3 | 220 µF 10 V electrolytic | footprint only | — | Optional extra bulk; fit if motor current dips the 5 V |
| C4 | 100 nF | 0402 | (basic) | VS high-frequency, at U1 |
| C5 | 100 nF | 0402 | (basic) | U1 1.8VOUT |
| C6 | 22 nF 10 V | 0402 | (basic) | U1 VCP to VS (charge pump, 1–100 nF) |
| C7 | 100 nF | 0402 | (basic) | U1 VIO |
| C8 | 100 nF + 1 µF | 0402 | (basic) | U2 VDD |
| C9 | 100 nF | 0402 | (basic) | U3 VCC |
| R1 | 10 kΩ | 0402 | (basic) | U2 CSN pull-up (keeps the sensor idle when unwired) |
| R2–R5 | 10 kΩ | 0402 | (basic) | Pull-downs on `NSTDBY`, `PWM_U`, `PWM_V`, `PWM_W`, so the driver stays off during reset, BOOTSEL or a crash (RP2350 erratum E9 makes the internal pull-downs unreliable) |
| R6–R8 | 1 kΩ | 0402 | (basic) | Series resistors on UH, VH, WH (limit current if a PWM pin is high while the driver is in standby) |
| RS1, RS2 | 0 Ω (or a ~0.1 Ω shunt) | 1206 | (basic) | BRUV and BRW (low-side foot points) to GND. Fit 0 Ω; swap in a shunt to measure motor current. Rev 0 only: the full board ties them straight to GND |
| Q1 | P-FET (or a Schottky) | SOT-23 / SMA | TBD | Reverse-polarity protection on the 5 V input |
| D1 | SMBJ6.0A TVS | SMB | TBD | Across VS, clamps bench-supply mistakes |
| JP1–JP3 | Solder jumpers, 3-pad | — | — | Low-side source: inverter (default) or header pin (6-PWM mode) |
| J1 | 1×15 pin header, 2.54 mm | THT | — | Signals to the controller board. GND on both end pins (see pinout) |
| J2 | Polarized 2-pin connector (JST-VH or XT30), large +/− silkscreen | THT | TBD | 5 V and GND from the bench supply (short, thick wires) |
| J3 | 1×3 pin header, 2.54 mm, right angle | THT | C2886703 (verify male pins) | Motor phases U, V, W. Matches the 3-pin servo-style plug one 2204 listing shows, as on the full knob board; if the motor arrives with bare wires or another plug, fit pads instead. Use a shrouded or keyed header if the plug has a key |

LCSC numbers were looked up on 2026-10-17; "basic" parts avoid JLC's
extended-part fee. Confirm everything in JLC's parts library when ordering.

## Netlist

**Power**
- `+5V`: J2 → Q1 (reverse-polarity protection) → U1 VS (pins per
  datasheet), C1–C4, D1 (SMBJ6.0A) to GND.
- `+3V3`: J1 (from the controller board's 3.3 V) → U2 VDD, R1, C8.
- `GND`: everything, plus U1's exposed pad (thermal: stitch vias under it)
  and U1 pins 8 and 9.

**Driver (U1, TMC6300)**
- `VIO` (VIO/NSTDBY) ← J1 `NSTDBY` (a GPIO: high = run, low = standby).
  **Also powers U3** (see "Standby" below). C7 to GND. R2 pull-down.
- `UH`, `VH`, `WH` ← R6–R8 (1 kΩ) ← J1 `PWM_U`, `PWM_V`, `PWM_W`. R3–R5
  pull-downs on the `PWM_x` nets.
- `UL`, `VL`, `WL` ← JP1–JP3 common pin; JP default side = U3 outputs
  (inverted `PWM_x`), other side = J1 `UL`/`VL`/`WL` for 6-PWM mode.
- `BRUV` (pin 16) → RS1 → GND; `BRW` (pin 20) → RS2 → GND. These are the
  low-side source foot points: left open, the motor won't drive. Put a test
  pad on each, so a shunt can be read with a scope.
- Pin 19: NC, leave open.
- `U`, `V`, `W` outputs → J3 (motor).
- `VCP` → C6 → `+5V`. `1.8VOUT` → C5 → GND. `DIAG` → J1 `DIAG`.

**Inverter (U3, SN74LVC3G04)**
- `VCC` = `NSTDBY` net (not 3V3). C9 to GND.
- Inputs `PWM_U`, `PWM_V`, `PWM_W`; outputs to JP1–JP3.

**Sensor (U2, MT6701)**
- `MODE` pin tied **high** (to VDD) for I²C/SSI (breakout boards often
  default to ABZ, lessons.md #5).
- SSI: `CSN` ← J1 `CS` (R1 pull-up), `CLK` ← J1 `CLK`, `DO` → J1 `DATA`.
  Read the full 24-bit frame and check its CRC.
- ABZ/UVW/PWM outputs unused (leave open or per datasheet).
- Centered exactly under the motor shaft; the board's motor holes set the
  magnet position.

**Press switch (SW1)**
- Between J1 `PRESS` and GND. Firmware enables the GPIO pull-up.

**J1 pinout (1×15, 2.54 mm)**
`1 GND · 2 PWM_U · 3 PWM_V · 4 PWM_W · 5 NSTDBY · 6 CS · 7 CLK · 8 3V3 ·
9 DATA · 10 PRESS · 11 DIAG · 12 UL · 13 VL · 14 WL · 15 GND`
(pins 12–14 only matter in 6-PWM mode). GND sits on both ends and 3V3 is
never next to GND, so a jumper shifted by one pin can't short the rail.

## Design notes

- **3-PWM is safe:** the TMC6300 datasheet: *"Internal break-before-make
  (BBM) logic ensures that no cross-conduction occurs."* So a low-side
  input driven by an inverted copy of the high-side input can't short the
  half-bridge.
- **Standby:** the datasheet says no digital input may be high while
  VIO/NSTDBY is pulled low (the input protection diodes would power the chip
  back up through those pins). An inverter outputs *high* when its input
  is low, so U3 is powered from the `NSTDBY` net: pulling `NSTDBY` low
  unpowers U3 and its outputs drop. Firmware must also drive `PWM_U/V/W`
  low before standby, and stop the motor first.
- **Reset and fault states:** R2–R5 hold `NSTDBY` and the PWM nets low
  while the MCU is in reset, in BOOTSEL or crashed. A watchdog drops
  `NSTDBY`. On the full board, specify RP2350B stepping A4 (erratum E9 is
  fixed there).
- **NSTDBY from a GPIO:** VIO accepts 1.8–5.25 V; a 3.3 V GPIO is fine. It
  supplies the TMC6300's logic and U3, both small loads.
- **Thermal and supply:** TMC6300 VS wants >10 µF ceramic close to the pin
  (100 µF electrolytic or 10 µF ceramic minimum per the datasheet). A
  10 µF ceramic derates to ~4–5 µF at 5 V, so use 2 × 22 µF 0805 per driver,
  here and on the full board. Keep the VS/GND loop tight; stitching vias
  under the exposed pad.
- **Tongue:** the motor and U2 are on the tongue; U1, U3, SW1 and the
  connectors are on the fixed part, so only the sensor's traces cross the
  hinge (route them straight across, no vias on it). Make the hinge traces
  wide, put them on the neutral axis (mid-width of the neck), and give the
  slot ends large radii, so fatigue doesn't crack them. The full board
  keeps this split: drivers off the tongue (design review D16).
- **Hinge stiffness (D10):** a plain 8 × 1.6 mm FR-4 neck likely needs
  8–27 N at the knob, against a 1.5–4 N target. Before ordering, saw a
  tongue into scrap FR-4 and load it on the kitchen scale. Rev 0's hinge has
  perforations that can be drilled or cut open to soften it, so one board
  can be tuned instead of reordered. If side force on the knob causes false
  clicks, the next revision uses a parallel-guided flexure.
- **Press gap:** an M2×3 set screw in the motor spacer's arm, above the
  switch, acts as an adjustable striker, so each knob's gap is set on the
  bench instead of relying on printed or cut parts to a tenth of a
  millimeter.
- **Motor holes:** NPTH, with a 1 mm copper keep-out and no pour under the
  motor base. Maximum screw length = board thickness + the motor base's
  thread depth − 0.5 mm; a longer screw can reach the windings and short a
  phase. Measure the thread depth on arrival.
- **Sensor faults:** firmware checks the SSI CRC and rejects impossible
  angle jumps; on either, it drops `NSTDBY` (a cracked hinge trace must not
  drive the motor).
- **Motor plug orientation:** the 1×3 plug fits either way, which swaps
  phases. At first wake, firmware runs a small open-loop move and checks the
  sensor direction; on a mismatch it invalidates the stored calibration.
- **DIAG:** one per driver, active-high push-pull. On the full knob board,
  diode-OR the five DIAG lines (Schottky + pull-down) into one spare pin.

## Bring-up order

0. Before any power: check J2 polarity and that 5 V, 3V3 and GND aren't
   shorted to each other. Measure the motor's phase resistance R and
   phase-to-stator resistance (must be open).
1. 3.3 V only: read the MT6701 over SSI (24-bit frames, CRC checked) while
   turning the motor by hand.
2. Add 5 V on the bench supply with a current limit (~300 mA): open-loop
   spin at low voltage limit. With `NSTDBY` low and a PWM pin high, VIO
   stays below 0.4 V (no back-powering).
3. Closed-loop FOC; store calibration (lessons.md #4). Measure Kt. Store R
   per knob and scale duty by the measured VS. Read motor current across a
   shunt in RS1/RS2.
4. Haptics: detents, smooth, end stops; then the press switch. Reseat the
   motor plug reversed and confirm the direction check catches it.
5. Standby/wake cycling: confirm ≤ 5 mA in standby on the power meter.
6. Loop timing for the full board: run 1 real and 4 dummy FOC loops (all 15
   PWM outputs, 5 sensor reads) on the RP2350B. Target ≥ 2–5 kHz per
   motor, with FOC on core 1 running from RAM. Initialize every driver
   before enabling any (SimpleFOC's `syncSlices()` resets all slices on each
   driver init).
