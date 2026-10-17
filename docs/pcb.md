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
boards, all connectors fitted by JLC (cabling: [wiring.md](wiring.md)):

| Board | What's on it | Outline |
|---|---|---|
| **Knob board** | RP2350B, 5× MT6701 sensors, 5× motor drivers, 5× B3U press switches, 5× motor headers, JST-GH (USB link), ZIF (keys), JST-SH (touch) | `full_knob_board_outline.dxf` |
| **Frame PCB** | 21× B3U key switches around the key windows, ZIF connector for the key cable. No chips | `full_frame_pcb_outline.dxf` |
| **Touch band** | Capacitive touch electrodes + touch controller, glued under the top plate below the knob displays | strip, ~160 × 11 mm |
| **USB board** | CH334F USB 2.0 hub, external USB-C (mid-mount), USB-C to the display board, JST-GH to the knob board, current-offer sensing (CC), power switch, ESD | L-shape, back-left corner: `full_usb_board_outline.dxf` |

### Knob board
- One PCB for all five knobs. Each knob sits on a **tongue**: a U-shaped
  slot cuts it free on three sides, and the uncut neck at the back is the
  hinge. Pressing the knob flexes the tongue ~0.15 mm onto a **B3U switch on
  the underside** of its front tip, which presses against the case floor.
  The MT6701 rides on the tongue, so it stays aligned with the motor's
  magnet.
- **Microcontroller: RP2350B** (48 GPIO, 24 PWM channels). An RP2040 isn't
  enough: 16 PWM channels, 30 GPIO.
- **Motor drivers: 3 PWM signals per motor** (15 total).
  - Plan A: TMC6300 (2–11 V, ideal on USB 5 V) with an inverter deriving
    each low-side input from its high-side input. Check the datasheet for
    built-in break-before-make (shoot-through protection), and test on the
    prototype.
  - Plan B: DRV8316 in its native 3x PWM mode. Its 4.5 V minimum is close
    to USB 5 V under motor load, so it's the fallback.
- **Driver stock:** JLC lists the TMC6300 as an "extended" part and has
  shown it out of stock. Check before ordering; keep the DRV8316 fallback
  drawn in the schematic.
- **Sensor:** MT6701 in SSI mode (mode pin strapped on the board).
- **Motor mount:** holes fit more than one motor (2204 patterns plus a
  fallback motor), since specific motors go out of stock.
- **USB and flashing:** the RP2350B's native USB goes to the USB board's
  hub over the JST-GH cable (5 V and GND on two contacts each). Firmware
  updates use the RP2350's built-in UF2 bootloader; a BOOTSEL button and USB
  test pads are the recovery path.
- **Power:** the two CC sense lines from the USB board go to ADC pins, so
  firmware sets the motor budget from the PC's advertised current
  ([wiring.md](wiring.md)).
- **Motor connectors:** a right-angle 1×3 2.54 mm header behind each
  tongue, plus two slots per knob for a strap around the coiled lead.
- Pin budget: 44 of 48 GPIO ([wiring.md](wiring.md)).

### Frame PCB
- Board outline with key and knob-display windows from the CAD model.
- B3U switches on the strips between windows, placed for the cap tabs.
- Only switches (and diodes if the matrix needs them) and a connector.

### USB board
- CH334F hub (QFN-24, internal clock, no crystal). Port 1 → JST-GH to the
  knob board; port 2 → USB-C socket to the display board; ports 3–4 to test
  pads. Fallback hub: FE1.1s (needs a 12 MHz crystal).
- External socket: a mid-mount (sink) 16-pin USB-C with through-hole shell
  legs; its face lines up with the inside of the back wall. Four M2 holes,
  two right beside the socket. Keep the arm's rear edge straight: it bears
  on a printed backstop.
- Upstream CC1/CC2: 5.1 kΩ to GND, plus 10 kΩ out to the JST-GH cable for
  sensing. Downstream USB-C: 56 kΩ CC pull-ups, VBUS through a
  current-limited switch.
- Board top is 7.1 mm above the floor and the panel sits at 13.35 mm, so
  parts on top stay under ~3.5 mm (a top-mount USB-C is 3.3 mm).

### Touch band
- Thin PCB, ~160 × 11 mm, interleaved electrodes for a slider; it reaches
  past the last motor on the right, where its JST-SH connector sits.
- Touch controller on the band (exact part TBD, must be in LCSC stock),
  I²C to the knob board.
- Senses through the 2 mm top plate.

### Order everything from JLC at once
Put the frame PCB, knob board, touch band and USB board in **one panel**
(JLC accepts multiple designs panelized with mouse bites), so there's one
PCB order and one assembly setup fee. One panel means one thickness: the
touch band was planned at 0.8 mm, so either make it 1.6 mm like the rest
(check it still senses through the plate) or order it separately. Add the 3D prints (caps, knobs,
case if you don't print it yourself) to the same JLC order so it ships
together.

## Prototype boards

### Rev 0: knob module
One tongue of the knob board: MT6701, motor driver, B3U press switch, same
tongue/hinge geometry. Outline: `proto_knob_module_outline.dxf`. It tests the
knob feel, the press, and Plan A (TMC6300 + inverter) driven by the ESP32-S3
dev board. Netlist, parts and design notes: [knob-module.md](knob-module.md).

### Rev A: prototype frame PCB
Two key windows + one knob-display window, B3U switches. **Generated** from
the CAD: see [hardware/README.md](../hardware/README.md) (DRC clean,
untested).

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
