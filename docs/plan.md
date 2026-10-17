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
- Knobs also **press to click**, like Stream Deck dials.
- A **touch band** under the knob displays for taps and swipes.
- Cheap to build: case printable at home (256 mm bed), one JLC order.

**Explicitly not wanted**
- Hall-effect switches.
- Huge SmartKnob-sized knobs; aim for something closer to the MX Master
  MagSpeed wheel in size.

## Architecture

```
 PC: OpenDeck + clickdeck device plugin (or the Python library directly)
   │  single USB cable
   ▼
 ESP32-S3 + 7" display board (bought: Waveshare ESP32-S3-LCD-7)
   ├── USB HID interface    → key presses, knob turns/presses, touch
   ├── USB CDC/bulk channel → images and commands from the PC (~1 MB/s)
   ├── drives the LCD       → all key images + knob display areas
   └── UART ──► knob board: RP2350B
                 ├── 5 knobs: MT6701 sensor + motor driver + press switch each
                 ├── 21-key matrix (frame PCB, switches only)
                 └── I²C ──► touch band (under the top plate)
```

### Host software: OpenDeck
[OpenDeck](https://github.com/nekename/OpenDeck) is an open-source app (Linux,
Windows, macOS) that runs Stream Deck plugins. It officially supports Elgato
hardware, and other vendors' devices through plugins. A **clickdeck device
plugin** gives builders much of the Stream Deck plugin library without
writing integrations. Plugins that rely on Elgato-only features may not
work. Knob feel (detents, stops, haptic ticks) needs clickdeck-specific
settings on top. A small Python library talks to the device directly for
custom scripts.

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
strength), smooth (free or light drag), end stops, haptic ticks.
Driver must work from USB 5 V: TMC6300 (2–11 V). **Not** the SimpleFOC
Mini / DRV8313, which needs 8–30 V.

All five knobs share **one knob board** run by an **RP2350B**. Each motor is
driven with 3 PWM signals (the TMC6300 needs 6, so an inverter derives the
low sides; DRV8316 is the fallback). Details in [pcb.md](pcb.md).

**Press to click:** each knob sits on a tongue cut into the knob board
(U-shaped slot, hinged at the back). Pressing the knob flexes the tongue onto
a B3U switch underneath.

### Power budget
One USB-C cable feeds the display board, its backlight and 5 motors. One
SmartKnob motor alone draws ~0.7–1 A peak at 5 V, so the firmware caps total
motor current, motors use only the torque a detent needs, and the device
assumes the current the host advertises on USB-C (1.5 A or 3 A), falling
back to a low limit. Requires a C-to-C cable. See
[lessons.md](lessons.md) #2.

### Firmware updates
Both chips update over the single USB cable, no extra tools: the ESP32-S3
through its native USB, and the RP2350B through the ESP32-S3 (its RUN and
boot pins, or SWD, are wired to the ESP32-S3). Bootloaders stay unlocked.
Knob calibration and display settings live in flash storage that firmware
updates don't erase.

### USB protocol
Follows lessons from Stream32's documented protocol
([lessons.md](lessons.md) #11–16): versioned hello with feature flags,
image cache by CRC so reconnects resend nothing, the device reports key
size in pixels, binary framing with RLE/JPEG, saved pages that work offline
plus temporary live-state overlays, separate key-down/key-up events, and a
plain HID keyboard mode that needs no host software.

### Touch band
A thin capacitive sensor PCB under the top plate, just below the knob
displays: tap or swipe on the plate surface, like the + XL's touch strip.
(Touching the display glass itself doesn't work: it sits ~7 mm below the top
surface because of the key stack.) The knobs moved forward 4 mm to make the
band 10 mm tall.

## Stages (test board: 2 keys + 1 knob)

1. **Images over USB:** a Python script sends an image to a key area on the
   2" screen.
2. **Switches:** a press sends an HID event; the PC reacts by changing that
   key's image.
3. **Knob:** on the Rev 0 knob module (MT6701 + TMC6300 + press switch on
   a tongue); SimpleFOC closed loop; clicky/smooth/stops switched by a
   command from the PC. Also test: the press feel (tongue stiffness), and
   driving the TMC6300 with 3 PWM signals + inverter.
3b. **Touch band:** tap and swipe through the 3 mm acrylic top plate.
4. **Mechanics:** frame + clear cap + tab + guides; adjust until a press
   anywhere on the key clicks cleanly. No 3D printer → order prints
   (JLC3DP clear resin) and/or laser-cut acrylic.
5. **Decide go/no-go:** if the knob and cap feel are both good → full
   20-key/5-knob design.

Software: PlatformIO + Arduino-ESP32 core (TinyUSB, SimpleFOC) on the device;
Python + `pyserial` + `hidapi` on the PC. Keep the host integration layer
behind an abstraction so it carries over to the full build.
