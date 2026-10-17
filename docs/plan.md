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
   │  single USB-C cable, into the back wall
   ▼
 USB board: USB 2.0 hub (CH334F), reads the port's current offer (CC pins)
   ├── USB ──► knob board: RP2350B (USB device 1)
   │             ├── USB HID + data channel → keys, knob turns/presses, touch; knob settings
   │             ├── 5 knobs: MT6701 sensor + motor driver + press switch each
   │             ├── 21-key matrix (frame PCB, switches only)
   │             └── I²C ──► touch band (under the top plate)
   └── USB ──► ESP32-S3 + 7" display board (USB device 2; bought: Waveshare ESP32-S3-LCD-7B, 1024×600)
                 ├── USB data channel → images and display commands from the PC (~0.5 MB/s)
                 └── drives the LCD   → all key images + knob display areas
```

The host sees two USB devices behind a hub and pairs them
([protocol.md](protocol.md)). Inside the case every link is a bought cable
plugged into a connector JLC fits: no soldering or crimping
([wiring.md](wiring.md)).

### Host software: OpenDeck
[OpenDeck](https://github.com/nekename/OpenDeck) is an open-source app (Linux,
Windows, macOS) that runs Stream Deck plugins. It officially supports Elgato
hardware, and other vendors' devices through plugins. A **clickdeck device
plugin** gives builders much of the Stream Deck plugin library without
writing integrations. Plugins that rely on Elgato-only features may not
work. Knob feel (detents, stops, haptic ticks) needs clickdeck-specific
settings on top. A small Python library talks to the device directly for
custom scripts.

### Why a data channel for images
HID on full-speed USB is limited to ~64 KB/s (one 120×120 key
image ≈ 0.5 s). A CDC channel on the ESP32-S3 does about 0.5 MB/s
(Espressif's figure): one raw key takes ~85 ms, a raw full page ~1.8 s. So
RLE/JPEG is the default, not an option. Also: upload icons once and
reference them by ID; redraw only the parts of the screen that changed.
Target: a full page in under 300 ms.

### Keys: Elgato style
One LCD panel under a **frame-shaped PCB** (square window cut out per key).
A clear resin cap sits in each window; a tab on the cap presses a micro
switch mounted on the PCB strip between windows. What stops the cap from
tilting, and how the frame PCB is supported, is still open
([open-questions.md](open-questions.md)). Laser-cut acrylic caps are out:
sheet tolerance alone is larger than the key stack's budget. The cap has
0.2 mm of free play; an optional foam or silicone ring on the flange stops
rattle.

```
      ┌──────────────┐  ← clear cap (the image shows through it)
   ┌──┤              ├──┐  ← tab reaches past the window edge
 ══╧══╧══            ══╧══  ← PCB with a window cut out per key
  [sw]                      ← micro switch under the tab
 ───────────────────────────  ← one LCD panel
```

Knobs sit just past the panel edge; each knob's "display" is an area of
the same panel.

Full build target: Waveshare **ESP32-S3-LCD-7B** (non-touch, SKU 31727,
$33.99), 7" 1024×600 RGB panel with **adjustable backlight**. Chosen over
the original ESP32-S3-LCD-7 (800×480): same price and pinout, but the
original's backlight is on/off only (CH422G expander pin) without a wire
mod. Layout (from the CAD model): **7×3 = 21 keys at 22 mm pitch** (146 px
pitch; about 120×120 px visible under each cap) plus a ~20 mm strip below the keys for the 5 knob displays.
(5×4 at 30 mm doesn't fit: the panel's active area is only ~86 mm tall.)

The display board only draws the screen; it needs none of its free pins.
Keys, knobs and touch go to the RP2350B, which has its own USB connection
through the hub. 1024×600 is more work for the ESP32-S3 than 800×480; fine
for mostly static key images, but test full-screen redraw speed early.

Switches: **Omron B3U-1000P** (3.0 × 2.5 mm SMD tactile). The strip
between keys is 3.6 mm, so 13 mm mouse switches don't fit.

### Knobs
Small brushless gimbal motor + magnetic angle sensor + low-voltage driver,
run with the SimpleFOC library. Software modes: clicky (detent count/
strength), smooth (free or light drag), end stops, haptic ticks.
Driver must work from USB 5 V: TMC6300 (2–11 V). **Not** the SimpleFOC
Mini / DRV8313, which needs 8–30 V.

Firmware notes:
- Five FOC loops on one RP2350B are unproven. FOC runs on core 1 from RAM,
  targeting ≥ 2–5 kHz per motor; all drivers are initialized before any is
  enabled. Rev 0 times 1 real and 4 dummy loops first.
- The 2204 has 84 cogging steps per turn, which don't line up with 24 or 48
  detents. Each knob gets a cogging feed-forward table from calibration.
- On wake, the detent grid re-anchors at the current angle, so the knob
  doesn't snap.
- In free smooth mode the driver stays in standby (3-PWM shorts the windings
  at zero torque, which drags) and wakes only for effects.

All five knobs share **one knob board** run by an **RP2350B**. Each motor is
driven with 3 PWM signals (the TMC6300 needs 6, so an inverter derives the
low sides; DRV8316 is the fallback). Details in [pcb.md](pcb.md).

**Press to click:** each knob sits on a tongue cut into the knob board
(U-shaped slot, hinged at the back). Pressing the knob flexes the tongue onto
a B3U switch underneath.

### Power budget
One USB-C cable feeds the display board, its backlight and 5 motors. One
SmartKnob motor alone draws ~0.7–1 A peak at 5 V. But a motor only draws
real current while it's pushing back on a hand: an untouched knob sits at a
detent center and needs no torque. So the budget is about **one motor's
worth (~1 A)**, enforced by a firmware arbiter:

- **Wake on movement.** All angle sensors stay on (10–14 mA each). A
  knob's driver wakes when it moves more than a fraction of a degree
  (well under 1 ms, too fast to feel) and goes back to standby after
  1–2 s without movement.
- **Share the budget.** One active knob gets the full current limit; if
  two move at once, each gets half (they feel slightly weaker for that
  moment instead of browning out).
- **Time-limit end stops.** Pushing against a stop is the only sustained
  full-torque case; ease off if someone leans on it.
- **Queue haptic notifications** so pulses never overlap. Calibrate knobs
  one at a time.

The USB board reads the host port's advertised USB-C current (CC pins) and
the knob board sets the motor budget from it: 500 mA for default USB power
(or an A-to-C cable), 1.0 A for a 1.5 A port, 1.5 A for a 3 A port (capped by
the internal cable). A brownout guard on the 5 V input backs it up (it trips
on a drop from idle, not a fixed 4.6 V). Details:
[wiring.md](wiring.md); see also [lessons.md](lessons.md) #2.

### Firmware updates
Both chips update over the single USB cable, no extra tools, each over its
own USB connection through the hub: the ESP32-S3 with esptool (or the
host app), the RP2350B by rebooting into its built-in bootloader and
copying a UF2 file (drag and drop works too). No custom bootloader. If the
RP2350B firmware is broken, a BOOTSEL button on the knob board recovers it.
Bootloaders stay unlocked.
Knob calibration and display settings live in flash storage that firmware
updates don't erase.

### USB protocol
Follows lessons from Stream32's documented protocol
([lessons.md](lessons.md) #11–16): versioned hello with feature flags,
image cache by CRC so reconnects resend nothing, the device reports key
size in pixels, binary framing with RLE/JPEG, saved pages that persist
plus temporary live-state overlays, separate key-down/key-up events, and a
plain HID keyboard mode that needs no host software.

### Touch band
A thin capacitive sensor PCB under the top plate, just below the knob
displays: tap or swipe on the plate surface, like the + XL's touch strip.
(Touching the display glass itself doesn't work: it sits ~7 mm below the top
surface because of the key stack.) The knobs moved forward 4 mm to make the
band 11.2 mm tall (model). It sits close to the motor bells, so it has a
grounded guard trace and firmware ignores touches for 300 ms around knob
motion or a press ([pcb.md](pcb.md)).

### Case material
The case holds about 2.3 W in a closed box, and the 7B is rated 0–65 °C.
Print it in PETG or ASA (not PLA), with 4 walls and ≥ 25% infill at the
bosses. Log temperatures for 2 h at full brightness on the first build.

## Stages (test board: 2 keys + 1 knob)

1. **Images over USB:** a Python script sends an image to a key area on the
   2.4" screen.
2. **Switches:** a press sends an HID event; the PC reacts by changing that
   key's image.
3. **Knob:** on the Rev 0 knob module (MT6701 + TMC6300 + press switch on
   a tongue); SimpleFOC closed loop; clicky/smooth/stops switched by a
   command from the PC. Also test: the press feel (tongue stiffness), and
   driving the TMC6300 with 3 PWM signals + inverter.
3b. **Touch band:** a full-length, 10–12-segment strip under an offcut of
   the printed plate, with the motor running and the panel lit
   ([prototype-tests.md](prototype-tests.md)).
4. **Mechanics:** frame + clear cap + tab; adjust until a press anywhere
   on the key clicks cleanly. Caps are JLC3DP clear resin prints; the
   prototype plates are laser-cut acrylic.
5. **Decide go/no-go:** if the knob and cap feel are both good → full
   20-key/5-knob design.

Software: on the RP2350B, the arduino-pico core + SimpleFOC (or pico-sdk);
on the ESP32-S3, a toolchain that can set ESP-IDF sdkconfig options (the
7B's RGB panel needs them: [protocol.md](protocol.md)); Python with
`pyserial` and `hidapi` on the PC. Pin every version and build in CI. Keep the host
integration layer behind an abstraction so it carries over to the full
build.
