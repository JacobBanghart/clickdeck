# PCB plan

## Tools
- **KiCad 9** (free, runs natively on Linux). Schematic → layout → Gerbers.
- Footprints: `easyeda2kicad` pulls LCSC/JLC part footprints so assembly
  parts match what JLC stocks.
- Board outlines come from the CAD model: `cad/out/*_outline.dxf`
  (KiCad: File → Import → Graphics, layer Edge.Cuts).

## Boards in the full build

The ESP32-S3 + 7" display is a bought board (Waveshare ESP32-S3-LCD-7B), so
it isn't designed here. It only draws the screen. Everything else is on four
base boards in one panel, plus one small board per knob module type (D23),
all connectors fitted by JLC (cabling: [wiring.md](wiring.md)):

| Board | What's on it | Outline |
|---|---|---|
| **Backplane** | RP2350B and its support parts, the motor-rail eFuse and bulk cap, JST-GH (USB link), ZIF (keys), JST-SH (touch), HY2.0 footprint, BOOTSEL, CC sense, and a slot connector (18 pogo pins) under each of the 5 knob slots | `full_backplane_outline.dxf` |
| **Frame PCB** | 21× B3U key switches around the key windows, ZIF connector for the key cable. No chips | `full_frame_pcb_outline.dxf` |
| **Touch band** | Capacitive touch electrodes + touch controller, glued under the top plate below the knob displays | strip, ~155 × 11 mm |
| **USB board** | CH334F USB 2.0 hub, external USB-C (mid-mount), USB-C to the display board, JST-GH to the backplane, current-offer sensing (CC), two reverse-blocking eFuses (TPS259470A), ESD (SRV05-4-P-T7) | L-shape, back-left corner: `full_usb_board_outline.dxf` |
| **Haptic module** (per knob) | TMC6300, SN74LVC3G04 inverter, MT6701 on a hinged tongue, B3U press switch, motor header, ID diode; ENIG pads underneath for the slot connector | `module_haptic_pcb_outline.dxf`, 28.4 × 30.5 mm |
| **Lite module** (per knob) | Bourns PEC11R push encoder (THT), RC filter, ID diode; the same outline and pads, no tongue | `module_lite_pcb_outline.dxf` |

### Backplane
- The old knob board's outline, mounting and connectors (GH at the
  back-left corner, ZIF tab and SH header at the right end, HY2.0 on the
  back edge, BOOTSEL over the floor pinhole), with the knobs taken off. It
  sits 1 mm above the floor on bosses and ribs, with no parts under it.
- **Slot connector (D23):** 18 upright SMD pogo pins per slot (BAT WIRELESS
  BWCD-L3W2.0H1.0, C2988082: 3.0 mm tall, 1.0 mm stroke, ~1 N, 1.5 A,
  10,000 cycles), 3 rows × 6 at 3.0 × 2.5 mm under each module's front
  border. They press ENIG pads on the module's underside, so the module
  needs no part on its bottom (D6). Pinout and the reasons in
  [wiring.md](wiring.md). Keep pours and other parts 0.6 mm clear of the
  pins (the module base's window). A tray rib supports the board under
  each pin field (5 × ~18 N).
- **Slot holes:** two 6.1 mm holes per slot for the tray's slot bosses
  (they carry the modules' screws and locate the backplane), and two key-pin
  holes (2.1 and 1.5 mm, NPTH) so a module only seats one way round.
- **Microcontroller: RP2350B** (48 GPIO, 24 PWM channels). An RP2040 isn't
  enough: 16 PWM channels, 30 GPIO. FOC for up to five motors runs here;
  the modules have no MCU.
- **Motor drive: 3 PWM signals per slot** (15 total) to the slot
  connector; each slot's U and V on one PWM slice (GPIO 2m, 2m+1), so a lite
  module's encoder can use them as a consecutive pair. Plan B for the driver
  is the DRV8316 in its native 3x PWM mode (on the haptic module).
- **Sensors:** one shared SSI CS and CLK, five separate data lines read
  together by PIO, with pull-downs.
- **Reset safety:** specify RP2350B stepping A4; the drivers' 10 kΩ
  pull-downs on `NSTDBY` and the PWM nets are on the haptic modules, plus a
  watchdog that drops `NSTDBY` (RP2350 erratum E9).
- **Module ID:** two extra key-matrix rows (ID A, ID B) reach every slot;
  each module's ID diode ties its column to one of them
  ([wiring.md](wiring.md)).
- **RP2350B support parts** (the RP2354B has on-chip flash and drops the
  flash; full list in [bom.md](bom.md)):
  - Flash: W25Q128JVSIQ (C97521, basic).
  - Crystal: X322512MSB4SI (C9002, basic, 20 pF load, 80 Ω ESR) with
    2 × 33 pF (C1562) and Raspberry Pi's 1 kΩ series resistor. That's
    2 × (20 − 3 pF stray). Raspberry Pi's reference is the ABM8-272-T3
    (10 pF, 50 Ω) with 2 × 15 pF. The C9002's higher ESR and load mean
    less drive margin, and Raspberry Pi asks for a start-up test over
    temperature with any other crystal. Rev A runs that test;
    if it fails, fit the ABM8 (same 3225 footprint) with 15 pF, or a
    smaller series resistor.
  - SMPS inductor: AOTA-B201610S3R3-101-T (C42411119). Raspberry Pi
    requires shielded, 3.3 µH ±20%, DCR ≤ 250 mΩ, Isat ≥ 1.5 A, and a
    polarity mark, placed the right way round. No stocked JLC part has the
    mark, so it stays (3 in stock, pre-order minimum 32, 2026-10-17).
  - Regulator: AMS1117-3.3 (C6186, basic, 1 A, ~1.1 V dropout), with
    22 µF on its output.
  - Motor-rail soft start: TPS259470ARPWR eFuse (C3662799), the same part
    as the USB board's two VBUS switches, to the slots' VMOT pins; enabled
    only when a haptic module is fitted.
- **USB and flashing:** the RP2350B's native USB goes to the USB board's
  hub over the JST-GH cable (5 V and GND on two contacts each). Firmware
  updates use the RP2350's built-in UF2 bootloader, from the web
  configurator. The BOOTSEL button is a reverse-mount tact switch on the
  board's left end; its plunger reaches through the board to a pinhole
  in the case floor ([recovery.md](recovery.md)). USB test pads are the
  bench fallback. Silkscreen "unplug GH first" by the pads.
- **Display link (D5):** an HY2.0 3-pin footprint for the optional
  one-wire link to the 7B's GPIO6 (J8), 3V3 pin left open, 1 kΩ in series
  ([wiring.md](wiring.md)). Footprint always; fitting optional.
- **Power:** the two CC sense lines from the USB board go to ADC pins
  through 10–22 kΩ series resistors, so firmware sets the motor budget from
  the PC's advertised current ([wiring.md](wiring.md)). The soft-start
  eFuse feeds the motor rail only.
- **ESD:** series resistors and SRV05-4-P-T7 arrays (C85364, preferred,
  no fee): three on the key lines at the ZIF, one on SDA/SCL at the
  JST-SH. Pin 5 to 3V3.
- **Top side only (D6):** every part on top; the reverse-mount BOOTSEL
  switch (part not chosen; a plain tact switch on the bottom side, the
  board's only bottom part, is the fallback).
- Pin budget: 46 of 48 GPIO ([wiring.md](wiring.md)). Map the 15 PWM
  signals to distinct PWM channels in the schematic.

### Knob modules (D23)
- **Haptic module:** a 28.4 × 30.5 mm board per knob. The motor and the
  MT6701 sit on a 22 mm tongue, cut free at the front and sides and held by
  two torsion necks near its back edge (the hinge, D10). The driver,
  inverter, the driver's 2 × 22 µF, the B3U press switch, the upright 1×3
  motor header (C41417360) and the ENIG pads are on the fixed front border,
  so only the sensor's traces cross a neck (D16). The spacer's arm and its
  set-screw striker press the B3U. Netlist and notes:
  [knob-module.md](knob-module.md).
- **Hinge (D10):** do the scrap-FR-4 test on the module's tongue first.
  The module is its own small design, so the neck width or a 1.0 mm board
  can change without touching the other boards.
- **Lite module:** the same outline, holes and pads, no tongue; a Bourns
  PEC11R-4215F-S0024 (detented) or PEC11R-4015F-S0024 (smooth), one
  footprint for both. Through-hole: JLC hand-solders it under Economic, so
  the board stays one-sided (D6). Leads trimmed to ≤ 1.2 mm (the backplane
  is 2.5 mm below).
- **Floorplan:** the front border (28.4 × 7.5 mm) is crowded: driver,
  inverter, switch, header, passives, and the 18 pads underneath. Do it
  with real footprints before ordering.
- **Motor mount:** holes fit more than one motor (2204 patterns plus a
  fallback), NPTH with a 1 mm copper keep-out; screw length rule in
  [knob-module.md](knob-module.md).
- **Ordering:** each module type is its own JLC design (5 PCBs made, at
  least 2 assembled), in the same order as the base panel or later. For
  the first build, two haptic modules is exactly JLC's assembly minimum
  ([cost.md](cost.md)).

### Frame PCB
- Board outline with key and knob-display windows from the CAD model.
- B3U switches on the strips between windows, placed for the cap tabs.
- Only switches, one diode per switch, and a connector.
- GND guard ring around each window (ESD), a ground pour under the touch
  band's area, and black solder mask so the window edges don't glow under
  the clear caps.
- Each 3.6 mm strip must hold a B3U, a row trace and a diode on the top
  side. Route one full row before the full order (consider SOD-523 diodes).

### USB board
- CH334F hub (QFN-24) with a fitted 12 MHz crystal (C9002) on XI/XO and a 0 Ω link
  that can ground XI (crystal-free mode isn't guaranteed on JLC's lot).
  PSELF strapped low (bus-powered) with a 0 Ω option; 22 µF on VDD33. Port
  1 → JST-GH to the backplane; port 2 → USB-C socket to the display board;
  ports 3–4 to test pads. Fallback hub: FE1.1s (also needs a 12 MHz
  crystal).
- Hub next to the external socket: the upstream link is 480 Mbit/s, so keep
  it under 15 mm as a 90 Ω coplanar pair, no vias, unbroken ground below,
  SRV05-4-P-T7 at the socket. It takes D+, D−, CC1 and CC2 on its four
  pins (3.5 pF typ, 5 pF max; the datasheet lists USB 2.0). It fits the
  USBLC6-2SC6 footprint, but its lines don't flow through: route each line
  to its own pad.
- External socket: a mid-mount (sink) 16-pin USB-C with through-hole shell
  legs; its face lines up with the inside of the back wall. Four M2 holes,
  two right beside the socket. Keep the arm's rear edge straight: it bears
  on a printed backstop.
- Upstream CC1/CC2: 5.1 kΩ to GND, plus 10 kΩ out to the JST-GH cable for
  sensing. Downstream USB-C: 56 kΩ CC pull-ups. Both downstream VBUS
  branches go through TPS259470A eFuses that block reverse current while
  on (RILM sets ~1 A display, ~1.8 A backplane). Input: 2 × 22 µF basic
  ceramics (C45783), plus an unfitted polymer footprint. VBUS TVS clamps
  below 6 V ([wiring.md](wiring.md)).
- Optional footprint for a CH224-class USB-PD sink on the upstream port,
  not fitted by default (power policy D9 in [plan.md](plan.md)).
- Board top is 7.1 mm above the case bottom (4.1 mm above the floor). The
  arm under the display board meets its bottom-side parts at 10.9 mm (the
  ESP32-S3 module), so parts on top stay under ~3.5 mm (a top-mount USB-C
  is 3.3 mm).

### Touch band
- Thin PCB, ~160 × 11 mm, 10–12 interleaved chevron segments at 13–15 mm
  pitch with half-width end segments, 1–10 kΩ in series with each
  electrode next to the chip. It reaches past the last motor on the right,
  where its JST-SH connector sits. Notch it around the frame PCB's ZIF (or
  stop it at x ≈ 79): at 1.6 mm thick it would sit 0.3 mm into the ZIF.
- Grounded guard trace along the motor-side edge, hatched ground (~25%) on
  the bottom layer. Firmware ignores touches for 300 ms around knob motion
  or a knob press.
- Touch controller on the band: **AT42QT2120** (SOIC-20, LCSC C614938,
  $1.89, 69 in stock on 2026-10-17), I²C to the backplane. All 12 channels
  as keys; firmware interpolates the position from their signal levels
  (the built-in slider is only 3 channels). The MPR121 is out: discontinued
  (NXP PCN16772).
- Senses through the 2 mm top plate. The band area of the plate is a
  sensing surface: 100% solid infill there, a flat recess, full-coverage
  3M 467MP/468MP transfer tape, and no carbon-fiber or metal-filled
  filament.

### Order everything from JLC at once
All boards are 2-layer FR-4 with an **ENIG** finish (owner decision).
ENIG pads are flat, which suits the 0.4 mm QFN-80 and QFN-20, and the
gold suits the modules' pogo contact pads. The module boards are their own
designs in the same order (above).

Put the frame PCB, backplane, touch band and USB board in **one panel**
(JLC accepts multiple designs panelized with mouse bites), so there's one
PCB order and one assembly setup fee. One panel means one thickness: the
touch band was planned at 0.8 mm, so either make it 1.6 mm like the rest
(check it still senses through the plate) or order it separately. Add the 3D prints (caps, knobs,
case if you don't print it yourself) to the same JLC order so it ships
together.

## Prototype boards

Plan changed 2026-10-18 (D3): the only custom PCB before the full build
is the rev C frame PCB. The knob runs on bought breakouts (SparkFun
TMC6300, an MT6701 board) on a printed test stand, and the controller and
hub on a WeAct RP2350B core board and a CH334F hub module
([parts.md](parts.md)). The Rev 0 knob module and the Rev 0.5 test board
are dropped: Rev A is the first build of the backplane, the knob modules,
the USB board and the touch band. Plan on one revision of whichever board fails, ordered alone
([cost.md](cost.md)). The knob channel's netlist stays in
[knob-module.md](knob-module.md).

### Rev C: prototype frame PCB
The full build's two top-left keys at the same place on the 7B, 58.3 ×
30.7 mm, four B3U footprints (SW1/SW2 under the keys, SW3/SW4 the optional
second switches for the D8 force test). Pan-head screws and pads sit off
the glass; over the glass it uses two countersunk M2 screws. **Generated** from the CAD: see
[hardware/README.md](../hardware/README.md) (untested).

It goes in one JLC order with the 2 + 2 caps and the knob test stand
prints (one shipping and duty charge).

## Workflow per board
1. Schematic in KiCad; run ERC.
2. Assign footprints; for JLC assembly, pick parts in LCSC stock
   ("basic" parts avoid extra fees).
3. Import the outline DXF, then place switches/connectors, then route.
4. Run DRC with JLCPCB's design rules.
5. Export Gerbers + drill files + BOM/CPL, upload to JLCPCB, check the
   preview.
6. Cross-check against the CAD model: window positions, switch heights, cap
   travel, tongue slots, mounting holes.

## Where AI helps
- Writing and reviewing schematics (pin assignments, strap pins, USB,
  decoupling).
- Checking KiCad files (plain text): ERC/DRC results, footprints, the
  netlist against the firmware's pin map.
- Code-CAD and firmware.

AI is weak at manual board routing; plan on routing in KiCad yourself.
