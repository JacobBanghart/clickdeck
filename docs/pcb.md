# PCB plan

## Tools
- **KiCad 9** (free, runs natively on Linux). Schematic → layout → Gerbers.
- Footprints: the Espressif KiCad library (ESP32-S3-WROOM-1), and
  `easyeda2kicad` to pull LCSC/JLC part footprints so assembly parts match
  what JLC stocks.
- Case and caps: code-based CAD (**build123d** or CadQuery). Parts are
  defined in Python, so they're easy to change and to iterate on with AI.

## Revisions

### Rev 0: knob module (first PCB)
The ~30 × 30 mm board that bolts to the 2204 motor: MT6701 sensor +
TMC6300 driver (JLC-assembled). See parts.md, Order 2. The design gets
reused 5× in the final build.

### Rev A: carrier board (after the breadboard + knob module work)
Same circuit as the breadboard, but on a real board with the real key
mechanics:
- The dev board plugs into headers (no fine-pitch soldering;
  modules can be reused).
- **Window cutout(s)** in the board outline (Edge.Cuts) over the display.
- Micro switch footprints on the strips between the windows, positioned for
  the cap tabs.
- Display connector, motor/encoder connector, mounting holes matching the
  case.
- Connector for the knob module (the small MT6701 knob PCB from
  parts.md, Order 2), which is designed and tested first.
- 2-layer, 5 boards from JLCPCB: a few dollars + shipping. All parts
  through-hole → you can hand-solder it.

Goal: prove the cap/tab/switch geometry and mounting on a real PCB.

### Rev B: everything on the board
- ESP32-S3-WROOM-1-N8R8 module soldered down, USB-C connector + ESD
  protection, 3.3 V regulator.
- **JLC PCBA** solders the surface-mount parts (LCSC parts); you
  hand-solder the switches and connectors.

### Rev C: full device
- 7" panel, 20 key windows, 5 knob areas.
- Knob controller(s) (RP2040 + TMC6300 per knob or per group), linked to the
  ESP32-S3.
- Case + clear caps ordered from JLC3DP in the same order.

## Workflow per revision
1. Schematic in KiCad; run ERC.
2. Assign footprints; for JLC assembly, pick parts that are in LCSC stock
   ("basic" parts avoid setup fees).
3. Lay out the board: board outline and window cutouts first (they come from
   the mechanical design), then place switches/connectors, then route.
4. Run DRC with JLCPCB's design rules.
5. Export Gerbers + drill files (+ BOM/CPL for assembly), upload to JLCPCB,
   check their preview.
6. Cross-check against the CAD model: window positions, switch heights, cap
   travel, mounting holes.

## Where AI helps
- Writing and reviewing the schematic (pin assignments, ESP32-S3 boot/strap
  pins, USB wiring, decoupling).
- Checking KiCad files (they're plain text): ERC/DRC results, footprint
  choices, the netlist against the firmware's pin map.
- Code-CAD for the case and caps, and firmware.

AI is weak at manual board routing; plan on routing in KiCad yourself
(Rev A is simple enough to route by hand).
