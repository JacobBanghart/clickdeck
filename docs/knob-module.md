# Knob modules (D23)

Knobs are modules in slots. The case has five slots at the knob positions;
each takes a **haptic module**, a **lite module** or a **blank**, dropped in
from the top through an opening in the top plate and held by two screws
from the top. The first build has two haptic modules and three blanks;
knobs get added later. Untested.

Modules have no MCU. The backplane's RP2350B runs every slot (FOC for up
to five motors), through each slot's 18-pin connector: pogo pins on the
backplane, ENIG pads under the module ([wiring.md](wiring.md) has the
pinout and the GPIO budget). No hot-plugging: unplug USB before swapping.

- **Haptic module:** module PCB with the MT6701 sensor, TMC6300 driver
  with 3-PWM drive, inverter, B3U press switch and the motor's header; the
  2204 motor and the sensor sit on a hinged tongue. Below: parts, netlist,
  design notes.
- **Lite module** (D22): the same PCB outline and pads with a Bourns PEC11R
  push encoder. At the end.
- **Blank:** one printed cover, flush with the plate. No electronics.

The knob was first meant to be tested on a standalone Rev 0 module
(dropped 2026-10-18, D3): it's first tested on bought breakouts (SparkFun
TMC6300 + an MT6701 board on a printed test stand; [parts.md](parts.md)).
Parts marked "bench module only" were for that board and don't go on the
haptic module.

## Mechanics

Each module is a stack, from the bottom (`cad/model.py`, `slot_items`):

- **Base** (printed, 2.5 mm): sits on the backplane and sets the pogo
  pins' working height. Open over the pogo field and under the tongue. Two
  key pins of different sizes (2.0 and 1.4 mm) underneath fit the
  backplane's holes only one way round.
- **Module PCB** (28.4 × 30.5 mm, 1.6 mm, ENIG pads underneath).
- **Haptic:** spacer, magnet, motor, hub and knob cap as before. **Lite:**
  the encoder and its knob cap.
- **Cover** (printed): a bezel flush with the top plate in the slot's
  opening (hub hole in the middle), four posts down to the PCB and base, a
  front wall. Two countersunk M2 screws go down through the bezel's corners
  and posts into M2 heat-set inserts in the tray's slot bosses, which come up
  through the backplane. They clamp cover, PCB and base, and hold against
  the pins' ~18 N.
- **Blank:** a cover with no hole, its posts down to the backplane, the
  same two screws.

**Swap from the top:** pull the knob cap, undo the two screws, lift the
module out by its cover; the case stays closed. The plate's dividers between
the openings guide each module straight down onto its pins, and stiffen the
plate's front strip around the five openings. `cad/assembly.py --check`
lifts every slot's module out with the plate on, for the default build,
all-haptic and all-lite.

**Height:** the module stack (backplane, 2.5 mm of pogo, module PCB) is
3.1 mm taller than the old single knob board, so the whole top (plate,
display, keys) sits 3.1 mm higher. Every knob top sits 16 mm above the plate,
at the old XY, for both module types (checked to 0.05 mm); covers and
blanks are flush with the plate.

**Press (D10, kept inside the module):** the haptic module PCB has the
tongue under the motor, cut free at the front and sides and joined to the
side borders by two torsion necks near its back edge. That's the hinge:
pressing the knob tips the tongue down about the necks. The motor
spacer's arm reaches forward over the slot to the B3U on the fixed front
border, with the M2×3 set screw as the striker, set at calibration on the
bench. Torsion necks are softer than the old 8 mm bending neck, and the
module PCB can be ordered thinner if the scrap test says so. Lite modules
use the encoder's own push switch.

**Layout waits on measuring the 2204 motor** (bolt pattern, base height).

## Parts

| Ref | Part | Package | LCSC | Notes |
|---|---|---|---|---|
| J0 | 18 ENIG pads (slot connector) | — | — | Under the front border, 3 × 6 at 3.0 × 2.5 mm, 1.8 mm across; pinout in [wiring.md](wiring.md). The pogo pins (C2988082) are on the backplane |
| D2, D3 | 1N4148W | SOD-123 | (basic) | D2: press switch into the key matrix (COL_k to ROW_PRESS). D3: module ID (COL_k to ROW_IDA) |
| U1 | TMC6300-LA-T | QFN-20 3×3 | C5274455 (59 in stock at LCSC, $5.93, checked 2026-10-17); C5196961 is out of stock | Extended part; JLC assembles it. Source through JLC Global Sourcing or consign from DigiKey (~$2.44, ~4,100 in stock); reserve the Rev A quantity once the test kit passes |
| U2 | MT6701CT-STD | SOP-8 | C3003196 (JLC, extended; check JLC stock on layout day) | Magnetic angle sensor, SSI mode. Not the MT6701**QT** (C2913974): that's a 3×3 QFN-16, and it was out of stock at LCSC on 2026-10-17. The package sets the sensor height and so the magnet gap |
| U3 | SN74LVC3G04DCTR | SM8 (DCT, SSOP-8 class; not VSSOP) | C139324 | Triple inverter, derives low-side inputs. Check the footprint |
| SW1 | B3U-1000P | SMD | C231329 | Press switch, **top side**, on the module's fixed front border in front of the tongue. An arm on the printed motor spacer reaches over the slot; an M2×3 set screw in the arm is the adjustable striker |
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
| RS1, RS2 | 0 Ω (or a ~0.1 Ω shunt) | 1206 | (basic) | BRUV and BRW (low-side foot points) to GND. Bench module only: the haptic module ties them straight to GND (D16). Motor current is measured on the test kit instead |
| Q1 | P-FET (or a Schottky) | SOT-23 / SMA | TBD | Bench module only: reverse-polarity protection on the bench-supply input. The backplane's motor rail has the TPS259470 eFuse |
| D1 | SMBJ6.0A TVS | SMB | TBD | Bench module only: across VS, clamps bench-supply mistakes |
| JP1–JP3 | Solder jumpers, 3-pad | — | — | Bench module only: low-side source, inverter (default) or header pin (6-PWM mode) |
| J1 | 1×15 pin header, 2.54 mm | THT | — | Bench module only: signals to the controller board. GND on both end pins (see pinout). On the haptic module they go to the slot connector's pads |
| J2 | Polarized 2-pin connector (JST-VH or XT30), large +/− silkscreen | THT | TBD | Bench module only: 5 V and GND from the bench supply (short, thick wires) |
| J3 | 1×3 pin header, 2.54 mm, vertical SMD (HX PZ2.54-1x3P TP-YQ) | SMD | C41417360 (47,856 in JLC stock, $0.039, 2026-10-19) | Motor phases U, V, W, on the front border; the plug stands upright and the spare lead coils beside it. Matches the 3-pin servo-style plug one 2204 listing shows; if the motor arrives with bare wires or another plug, change the header |

LCSC numbers were looked up on 2026-10-17; "basic" parts avoid JLC's
extended-part fee. Confirm everything in JLC's parts library when ordering.

## Netlist

Written for the standalone bench module (J1–J3 headers). On the haptic
module, the J1 signals go to the slot connector's pads (pinout in
[wiring.md](wiring.md)): `+5V` is VMOT, the backplane's eFuse-protected
motor rail; `PRESS` is D2 to `ROW_PRESS` with the switch to `COL_k`; D3
ties `COL_k` to `ROW_IDA` (module ID); the motor plugs into J3, an upright
SMD header. R2–R5 (the E9 pull-downs) stay on the module, next to the
driver.

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

**J1 pinout (1×15, 2.54 mm; bench module only)**
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
- **Tongue:** the motor and U2 are on the tongue; U1, U3, SW1, J3 and the
  pads are on the fixed front border, so only the sensor's traces cross the
  hinge (route them straight across one neck, no vias on it). Make the
  hinge traces wide, put them on the neck's neutral axis, and give the slot
  ends large radii, so fatigue doesn't crack them (D16).
- **Hinge stiffness (D10):** the tongue hangs on two 2 mm torsion necks at
  its back corners. A plain 8 × 1.6 mm FR-4 bending neck likely needed
  8–27 N at the knob, against a 1.5–4 N target; torsion necks are softer,
  but unproven. Before ordering, saw the module's tongue into scrap FR-4
  and load it on the kitchen scale. If it's still too stiff, narrow the
  necks or order the module PCB at 1.0 mm (it's its own small design, so
  that doesn't touch the other boards). If side force on the knob causes false
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
- **DIAG:** one per driver, active-high push-pull. It would need a 19th
  slot contact; for now it's a test pad on the module, and the reserved
  contact can carry it to the backplane's spare pin (diode-OR) later.

## Bring-up order

Steps 1–6 run first on the test kit (breakouts; the SparkFun board has no
shunt, so read motor current at the bench supply), then per module on
Rev A.

0. Before any power: check the 5 V polarity and that 5 V, 3V3 and GND
   aren't shorted to each other. Measure the motor's phase resistance R and
   phase-to-stator resistance (must be open).
1. 3.3 V only: read the MT6701 over SSI (24-bit frames, CRC checked) while
   turning the motor by hand.
2. Add 5 V on the bench supply with a current limit (~300 mA): open-loop
   spin at low voltage limit. With `NSTDBY` low and a PWM pin high, VIO
   stays below 0.4 V (no back-powering).
3. Closed-loop FOC; store calibration (lessons.md #4). Measure Kt. Store R
   per knob and scale duty by the measured VS. Read motor current at the
   supply.
4. Haptics: detents, smooth, end stops; then the press switch (Rev A). Reseat the
   motor plug reversed and confirm the direction check catches it.
5. Standby/wake cycling: confirm ≤ 5 mA in standby on the power meter.
6. Loop timing for the full board: run 1 real and 4 dummy FOC loops (all 15
   PWM outputs, 5 sensor reads) on the RP2350B. Target ≥ 2–5 kHz per
   motor, with FOC on core 1 running from RAM. Initialize every driver
   before enabling any (SimpleFOC's `syncSlices()` resets all slices on each
   driver init).

## Lite module (D22, D23)

The lite module carries a push encoder instead of the motor channel: the
haptic module's outline, pads, holes, base and cover, no tongue, motor,
driver or sensor. Untested.

| Ref | Part | Package | LCSC | Notes |
|---|---|---|---|---|
| ENC1 | Bourns PEC11R-4215F-S0024 (24 detents) **or** PEC11R-4015F-S0024 (smooth) | THT, vertical, 6 mm flatted shaft, 15 mm | C143790 / C143789 (5,249 / 3,748 in JLC stock, 2026-10-19) | Chosen when ordering. JLC hand-solders it (Economic). Leads trimmed to ≤ 1.2 mm: the backplane is 2.5 mm under the module |
| R1, R2 | 10 kΩ | 0402 | (basic) | A and B pull-ups to 3V3 |
| R3, R4 | 10 kΩ | 0402 | (basic) | Series, A and B to the RP2350B |
| C1, C2 | 10 nF | 0402 | (basic) | A and B to GND at the RP2350B (Bourns' suggested filter, ~0.1 ms) |
| D1, D2 | 1N4148W | SOD-123 | (basic) | D1: push switch in the key matrix, as on the haptic module. D2: module ID (`COL_k` to `ROW_IDB`) |

**Netlist (per knob)**
- ENC1 C (common) → GND. A → R1 to 3V3 → R3 → `ENC_A` pad (the slot's
  `PWM_U`), C1 to GND. Same for B (R2, R4, C2) on `PWM_V`. U and V of a
  slot are consecutive GPIOs, read by a PIO quadrature program (24 pulses
  per turn; no CPU load, nothing missed while flash writes). R3/R4 also
  limit the current if the slot is ever driven as PWM.
- ENC1 switch pins: one to `COL_k`, the other through D1 to `ROW_PRESS`,
  as on the haptic module ([wiring.md](wiring.md)).
- D2 from `COL_k` to `ROW_IDB`: firmware reads the slot as lite at power-up
  and reports it ([protocol.md](protocol.md)).
- VMOT, NSTDBY, PWM_W and the SSI pads: not connected.
- Mounting tabs: soldered to GND pads.

**Knob height.** The knob is the haptic knob's cap with a 9 mm stem down
through the cover's hub hole. Its D-bore seats on the shaft tip, 9 mm
of shaft inside (the 7 mm flat fully in), so the cap sits 1 mm above the
plate like the haptic knob. `assembly.py --check` checks the top matches
within 0.05 mm, and that a full press (0.5 mm switch travel) clears the
cover and the bushing. The shaft length is ±0.5 mm and the body ±0.3 mm:
measure the first encoders, set `ENC_*` in `cad/params.py` and reprint
the knobs.

**Bring-up:** the encoder needs no prototype board. Check the PIO
quadrature reader and the switch on the WeAct RP2350B bench with an EC11
on a breadboard (same pinout); the lite module is first built on Rev A.

## Blank

One printed part (`cad/out/blank_cover.stl`): the cover with no hub hole,
flush with the plate, its posts down to the backplane, held by the same two
screws. Its front wall stops above the free pogo pins, so nothing presses
them. The slot reads empty (no ID diode).
