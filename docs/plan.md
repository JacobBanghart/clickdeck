# Plan

## Goals

**Final device**
- At least 20 keys, each showing its own image (Elgato Stream Deck look).
- Keys use **micro switches** (mouse/controller-style click), not rubber domes.
- At least 5 knobs, each with a display area right next to it.
- Knobs: **clicky vs. smooth switchable in software** (hard requirement).
  Adjustable detent count/strength and end stops are nice-to-have.
  Full force feedback is not required.
- **USB only.** Must not show up as a monitor.
- Custom host software / integrations (Linux first).

**Explicitly not wanted**
- Hall-effect switches.
- Huge SmartKnob-sized knobs; aim for something closer to the MX Master
  MagSpeed wheel in size.

## Architecture

```
 PC (custom host software, Python first)
   │  single USB cable
   ▼
 ESP32-S3 (main MCU, native USB)
   ├── USB HID interface   → key presses + knob events (no driver needed)
   ├── USB CDC/bulk channel → images and commands from the PC (~1 MB/s)
   ├── drives one LCD panel  → all key images + knob display areas
   └── link (UART/I²C) → knob controller(s) in the full build
```

### Why two USB interfaces
HID on the ESP32-S3's full-speed USB is limited to ~64 KB/s (one 120×120 key
image ≈ 0.5 s). The CDC/bulk channel does ~1 MB/s (<50 ms per key).
Optimizations: upload icons once and reference them by ID; send only the parts
of the screen that changed; optionally JPEG + on-device decode.

### Keys: Elgato style
One LCD panel under a **frame-shaped PCB** (square window cut out per key).
A clear cap (3–5 mm clear resin/acrylic) sits in each window; a tab on the
cap presses a micro switch mounted on the PCB strip between windows. Guides
in the case stop the cap from tilting.

```
      ┌──────────────┐  ← clear cap (the image shows through it)
   ┌──┤              ├──┐  ← tab reaches past the window edge
 ══╧══╧══            ══╧══  ← PCB with a window cut out per key
  [sw]                      ← micro switch under the tab
 ───────────────────────────  ← one LCD panel
```

Knobs sit just past the panel edge; each knob's "display" is an area of
the same panel.

Full build target: 7" 800×480 RGB panel. Layout (from the CAD model):
**7×3 = 21 keys at 22 mm pitch** (~93×93 px per key, about Stream Deck XL
density) plus a ~20 mm strip below the keys for the 5 knob displays.
(5×4 at 30 mm doesn't fit: the panel's active area is only ~86 mm tall.)
Likely an ESP32-S3 + 7" panel board (Waveshare/Sunton style).

Switches: **Omron B3U-1000P** (3.0 × 2.5 mm SMD tactile). The strip
between keys is 3.6 mm, so 13 mm mouse switches don't fit.

### Knobs
Small brushless gimbal motor + magnetic angle sensor + low-voltage driver,
run with the SimpleFOC library. Software modes: clicky (detent count/
strength), smooth (free or light drag), end stops.
Driver must work from USB 5 V: TMC6300 (2–11 V). **Not** the SimpleFOC
Mini / DRV8313, which needs 8–30 V.
Full build: the motors likely run on separate RP2040(s) because the display
uses most of the ESP32-S3's pins. Not decided yet.

## Stages (test board: 2 keys + 1 knob)

1. **Images over USB:** a Python script sends an image to a key area on the
   2" screen.
2. **Switches:** a press sends an HID event; the PC reacts by changing that
   key's image.
3. **Knob:** on the Rev 0 knob module (MT6701 + TMC6300); SimpleFOC closed loop; clicky/smooth/stops switched by a
   command from the PC.
4. **Mechanics:** frame + clear cap + tab + guides; adjust until a press
   anywhere on the key clicks cleanly. No 3D printer → order prints
   (JLC3DP clear resin) and/or laser-cut acrylic.
5. **Decide go/no-go:** if the knob and cap feel are both good → full
   20-key/5-knob design.

Software: PlatformIO + Arduino-ESP32 core (TinyUSB, SimpleFOC) on the device;
Python + `pyserial` + `hidapi` on the PC. Keep the host integration layer
behind an abstraction so it carries over to the full build.
