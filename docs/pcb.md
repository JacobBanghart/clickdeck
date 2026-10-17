# PCB plan

## Tools
- **KiCad 9** (free, runs natively on Linux). Schematic → layout → Gerbers.
- Footprints: `easyeda2kicad` pulls LCSC/JLC part footprints so assembly
  parts match what JLC stocks.
- Board outlines come from the CAD model: `cad/out/*_outline.dxf`
  (KiCad: File → Import → Graphics, layer Edge.Cuts).

## Boards in the full build

The ESP32-S3 + 7" display is a bought board (Waveshare ESP32-S3-LCD-7B), so
it isn't designed here. It handles USB and draws the screen. Everything
else is on three boards:

| Board | What's on it | Outline |
|---|---|---|
| **Knob board** | RP2350B, 5× MT6701 sensors, 5× motor drivers, 5× B3U press switches, connector to the display board | `full_knob_board_outline.dxf` |
| **Frame PCB** | 21× B3U key switches around the key windows, cable to the knob board. No chips | `full_frame_pcb_outline.dxf` |
| **Touch band** | Capacitive touch electrodes + touch controller, glued under the top plate below the knob displays | strip, ~150 × 10 mm |

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
- **Link and flashing:** UART to the display board's UART connector
  (GPIO43/44); RP2350B RUN to its sensor connector (likely GPIO6). Firmware
  updates go over that UART via a small bootloader on the RP2350B. Add
  USB test pads plus a BOOTSEL button as the recovery path.
- **Power:** read the USB-C current advertisement (CC lines) or get it
  from the display board, so firmware can set the motor current budget.
- Pin budget (approx.): 15 PWM, 2 sensor bus + 5 chip selects, 5 press
  switches, 10 for the 7×3 key matrix, 2 UART to the display board, a
  driver enable, I²C to the touch band. About 42 of 48.

### Frame PCB
- Board outline with key and knob-display windows from the CAD model.
- B3U switches on the strips between windows, placed for the cap tabs.
- Only switches (and diodes if the matrix needs them) and a connector.

### Touch band
- Thin (0.8 mm) PCB, ~150 × 10 mm, interleaved electrodes for a slider.
- Touch controller on the band (exact part TBD, must be in LCSC stock),
  I²C to the knob board.
- Senses through the 2 mm top plate.

### Order everything from JLC at once
Put the frame PCB, knob board and touch band in **one panel**
(JLC accepts multiple designs panelized with mouse bites), so there's one
PCB order and one assembly setup fee. Add the 3D prints (caps, knobs,
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
