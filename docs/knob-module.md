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

- **Haptic module:** module PCB with the MT6701 sensor, the DRV8311H
  driver in 3x PWM mode (D24; the TMC6300 is the fallback), B3U press
  switch and the motor's header; the 2204 motor and the sensor sit on a
  hinged tongue. Below: parts, netlist, design notes.
- **Lite module** (D22): the same PCB outline and pads with a Bourns PEC11R
  push encoder. At the end.
- **Blank:** one printed cover, flush with the plate. No electronics.

The knob was first meant to be tested on a standalone Rev 0 module
(dropped 2026-10-18, D3): it's first tested on bought breakouts (SparkFun
TMC6300 + an MT6701 board on a printed test stand; [parts.md](parts.md)),
and the DRV8311H on the small driver bench board next to it
(`hardware/driver-bench/`, D24).

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

Driver changed 2026-10-19 (D24): the **DRV8311H** replaces the TMC6300 and
its SN74LVC3G04 inverter. In 3x PWM mode it takes the three PWM signals the
slot already carries, so the inverter goes, and it's in JLC's stock (no
Global Sourcing). Nobody is known to run it with SimpleFOC yet, so it's
tested on the driver bench board before Rev A ([prototype-tests.md](prototype-tests.md)).

| Ref | Part | Package | LCSC | Notes |
|---|---|---|---|---|
| J0 | 18 ENIG pads (slot connector) | — | — | Under the front border, 3 × 6 at 3.0 × 2.5 mm, 1.8 mm across; pinout in [wiring.md](wiring.md). The pogo pins (C2988082) are on the backplane |
| D2, D3 | 1N4148W | SOD-123 | (basic) | D2: press switch into the key matrix (COL_k to ROW_PRESS). D3: module ID (COL_k to ROW_IDA) |
| U1 | DRV8311HRRWR (TI) | WQFN-24 3 × 3 mm, 0.4 mm pitch, exposed pad | C5218862 (7,399 in JLC stock, $0.95 at 500, 2026-10-19; LCSC's own stock is separate, 405) | Extended part, JLC assembles it. 3–20 V (UVLO 2.6 V falling), 5 A peak, 210 mΩ high + low side, nSLEEP, internal pull-downs on every logic input, 3.3 V / 100 mA LDO (AVDD), three current-sense amplifiers (unused). Hardware variant **H**: pins set the mode. **Fallback:** TMC6300-LA-T (C5274455): another footprint (QFN-20) and the inverter back, so a module-board respin. Its stock has dropped (DigiKey 343, LCSC 163, 2026-10-19) |
| U2 | MT6701CT-STD | SOP-8 | C3003196 (JLC, extended; check JLC stock on layout day) | Magnetic angle sensor, SSI mode. Not the MT6701**QT** (C2913974): that's a 3×3 QFN-16, and it was out of stock at LCSC on 2026-10-17. The package sets the sensor height and so the magnet gap |
| SW1 | B3U-1000P | SMD | C231329 | Press switch, **top side**, on the module's fixed front border in front of the tongue. An arm on the printed motor spacer reaches over the slot; an M2×3 set screw in the arm is the adjustable striker |
| C1, C2 | 22 µF 25 V X5R | 0805 | C45783 (basic) | VM bulk, at U1 (the datasheet asks ≥ 10 µF; 2 × 22 µF derate to ~10–12 µF at 5 V) |
| C3 | 220 µF 10 V electrolytic | footprint only | — | Optional extra bulk; fit if motor current dips the 5 V |
| C4 | 100 nF | 0402 | (basic) | VM and VIN_AVDD (pins 8 and 7, side by side), at the pins |
| C5 | 100 nF 16 V X7R | 0402 | (basic) | Charge pump: CP to VM |
| C6 | 1 µF 6.3 V+ X5R | 0402 | (basic) | AVDD to AGND (0.7–7 µF for ≤ 25 mA) |
| C7 | 100 nF | 0402 | (basic) | CSAREF to AGND |
| C8 | 100 nF + 1 µF | 0402 | (basic) | U2 VDD |
| R1 | 10 kΩ | 0402 | (basic) | U2 CSN pull-up (keeps the sensor idle when unwired) |
| R2–R5 | 10 kΩ | 0402 | (basic) | Pull-downs on `NSTDBY`, `PWM_U`, `PWM_V`, `PWM_W`, so the driver stays asleep with its outputs off during reset, BOOTSEL or a crash (RP2350 erratum E9 makes the internal pull-downs unreliable; the driver's own 200–300 kΩ pull-downs are a second line) |
| J3 | 1×3 pin header, 2.54 mm, vertical SMD (HX PZ2.54-1x3P TP-YQ) | SMD | C41417360 (47,856 in JLC stock, $0.039, 2026-10-19) | Motor phases A, B, C, on the front border; the plug stands upright and the spare lead coils beside it. Matches the 3-pin servo-style plug one 2204 listing shows; if the motor arrives with bare wires or another plug, change the header |

Gone with the TMC6300: the SN74LVC3G04 inverter (C139324), the 1 kΩ series
resistors on the high-side inputs, the BRUV/BRW ground links and the
1.8VOUT and VIO capacitors. The bench-module rows (J1, J2, Q1, the TVS, the
jumpers, the shunts) went with the Rev 0 module (D3); the driver bench
board ([hardware/README.md](../hardware/README.md)) is the bench version now.

LCSC numbers were looked up on 2026-10-17 (driver 2026-10-19); "basic"
parts avoid JLC's extended-part fee. Confirm everything in JLC's parts
library when ordering.

## Netlist

Pin numbers are the DRV8311H's (WQFN-24, datasheet SLVSFN2B). Slot pads
per [wiring.md](wiring.md).

**Power**
- `VMOT` (pads A2, A3: the backplane's eFuse-protected motor rail) → U1 VM
  (8) and VIN_AVDD (7), C1–C4. The driver's LDO runs from the motor rail,
  so the driver is fully off while the rail is off.
- `+3V3` (pad A5) → U2 VDD, R1, C8.
- `GND` (pads A1, A4, A6): everything, plus U1 PGND (9), AGND (16) and the
  exposed pad (thermal: stitch vias under it).

**Driver (U1, DRV8311H)**
- INHA (15), INHB (14), INHC (13) ← `PWM_U`, `PWM_V`, `PWM_W` (pads B1–B3);
  R3–R5 pull-downs.
- nSLEEP (24) and INLA (18), INLB (19), INLC (20) ← `NSTDBY` (pad B4), all
  four tied; R2 pull-down. High: awake, each half-bridge follows its INHx
  (high or low). Low: asleep, and INLx low puts every phase in Hi-Z.
- MODE (23) → AVDD: **3x PWM** and the lower overcurrent level (5 A typ,
  3.4 A min). SLEW (22) → AVDD: fastest slew (230 V/µs at 12 V), shortest
  dead time (≤ 710 ns). GAIN (21) → AGND.
- AVDD (17) → C6. CSAREF (2) → AVDD, C7. SOA/SOB/SOC (5, 4, 3): not
  connected (a test pad each, for a scope).
- CP (6) → C5 → VM.
- OUTA/OUTB/OUTC (10–12) → J3 (motor).
- nFAULT (1) → pad C6 (`nFAULT`): open drain, bussed across the five slots
  on the backplane with one 10 kΩ pull-up to 3V3 (wired-OR, no diodes).

**Sensor (U2, MT6701)**
- `MODE` pin tied **high** (to VDD) for I²C/SSI (breakout boards often
  default to ABZ, lessons.md #5).
- SSI: `CSN` ← `SSI_CS` (R1 pull-up), `CLK` ← `SSI_CLK`, `DO` → `SSI_DO`.
  Read the full 24-bit frame and check its CRC.
- ABZ/UVW/PWM outputs unused (leave open or per datasheet).
- Centered exactly under the motor shaft; the board's motor holes set the
  magnet position.

**Press switch (SW1) and ID**
- SW1 from `COL_k`, through D2 to `ROW_PRESS`. D3 from `COL_k` to
  `ROW_IDA` (module ID; [wiring.md](wiring.md)).

## Design notes

- **3x PWM is safe:** in 3x mode each INHx sets its half-bridge high or
  low, and the driver inserts its own dead time (a handshake between the
  high and low side), so one PWM line per phase can't short the
  half-bridge. That's SimpleFOC's `BLDCDriver3PWM` with `NSTDBY` as the
  enable pin.
- **Sleep:** `NSTDBY` low puts the driver to sleep (1.5 µA) and its
  outputs in Hi-Z (INLx low), so the motor turns freely: smooth mode with
  no drag. The logic inputs are rated to 6 V with no logic supply pin, so
  there's no back-powering path like the TMC6300's (no inverter trick, no
  series resistors). Firmware still drives `PWM_x` low before sleep and
  stops the motor first.
- **Wake and idle current:** the driver takes 1–3 ms to wake (tWAKE) and
  draws 7–13 mA from VM while awake, even at zero duty. Firmware sleeps
  idle drivers and wakes one before an effect; the test kit checks the
  wake latency by feel.
- **Reset and fault states:** R2–R5 hold `NSTDBY` and the PWM nets low
  while the MCU is in reset, in BOOTSEL or crashed. A watchdog drops
  `NSTDBY`. On the full board, specify RP2350B stepping A4 (erratum E9 is
  fixed there).
- **Faults:** overcurrent (5 A level), overtemperature and undervoltage
  turn the outputs off and pull `nFAULT` low; the hardware variant retries
  by itself after ~5 ms. The five nFAULT pins share one GPIO (the spare
  one in the pin budget). Firmware ignores it while a driver wakes,
  drops every `NSTDBY` on a fault, then wakes the haptic slots one at a
  time to find which one faults. Untested: whether an unpowered DRV8311's
  nFAULT pin loads the pulled-up line while the motor rail is off
  (V: measure on the bench board).
- **Supply caps** per the datasheet's table 8-1: VM ≥ 10 µF bulk plus
  100 nF, VIN_AVDD 100 nF (it shares VM's bulk here), CP 100 nF to VM,
  AVDD 0.7–7 µF, CSAREF 100 nF. Keep the VM/PGND loop tight; stitching
  vias under the exposed pad (RθJA 42.6 °C/W).
- **Assembly:** WQFN-24 at 0.4 mm pitch, the same as the RP2350B's QFN-80,
  so it stays inside JLC's Economic assembly limit (D6). Same 3 × 3 mm
  body as the TMC6300; it sits where the TMC6300 did on the front border,
  and the module outline doesn't change.
- **Tongue:** the motor and U2 are on the tongue; U1, SW1, J3 and the
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
- **Misread slots** (re-checked for D24): a **lite module read as haptic**
  gets PWM on its encoder lines through its 10 kΩ series resistors (≤ 0.33
  mA into a closed contact) and `NSTDBY` high into an unconnected pad;
  there's no MT6701 frame, so the motor rail stays off for that slot
  anyway. A **haptic module read as lite** sees its `PWM_U/V` set as
  inputs and `NSTDBY` undriven: R2 holds nSLEEP and INLx low, so the
  driver sleeps with its outputs in Hi-Z, even with the motor rail on for
  the other slots.

## Bring-up order

Steps 1–6 run first on the test kit (the SparkFun TMC6300 breakout and the
driver bench board's DRV8311H and SS6343M channels; read motor current at
the bench supply), then per module on Rev A.

0. Before any power: check the 5 V polarity and that 5 V, 3V3 and GND
   aren't shorted to each other. Measure the motor's phase resistance R and
   phase-to-stator resistance (must be open).
1. 3.3 V only: read the MT6701 over SSI (24-bit frames, CRC checked) while
   turning the motor by hand.
2. Add 5 V on the bench supply with a current limit (~300 mA): open-loop
   spin at low voltage limit. With `NSTDBY` (or the bench board's enable)
   low and a PWM pin high, the outputs stay off (the motor turns freely) and
   the driver draws < 0.1 mA.
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
- VMOT, NSTDBY, PWM_W, nFAULT and the SSI pads: not connected.
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
