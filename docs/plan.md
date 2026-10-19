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
- **Works standalone:** set up once in a web configurator, everything
  stored on the device. Optional host software for live integrations
  (Linux first).
- Knobs also **press to click**, like Stream Deck dials.
- A **touch band** under the knob displays for taps and swipes.
- Simple to build: case printable at home (256 mm bed), one JLC order.
  Cost isn't a design driver (a single build costs more than a Stream
  Deck + XL; [cost.md](cost.md)), but the numbers stay honest.

**Explicitly not wanted**
- Hall-effect switches.
- Huge SmartKnob-sized knobs; aim for something closer to the MX Master
  MagSpeed wheel in size.

## Architecture

```
 PC: web configurator (browser, setup) · optional daemon (live integrations) · or nothing
   │  single USB-C cable, into the back wall
   ▼
 USB board: USB 2.0 hub (CH334F), reads the port's current offer (CC pins)
   ├── USB ──► knob board: RP2350B (USB device 1)
   │             ├── USB HID (keyboard + media) + WebUSB data channel → keymap, macros, knob settings
   │             ├── optional 1-wire link ──► display board GPIO6 (page, wake)
   │             ├── 5 knobs: MT6701 sensor + motor driver + press switch each
   │             ├── 21-key matrix (frame PCB, switches only)
   │             └── I²C ──► touch band (under the top plate)
   └── USB ──► ESP32-S3 + 7" display board (USB device 2; bought: Waveshare ESP32-S3-LCD-7B, 1024×600)
                 ├── WebUSB data channel → pages, images, display settings (~0.5 MB/s)
                 └── drives the LCD   → all key images + knob display areas
```

The host sees two USB devices behind a hub; the software pairs them
([protocol.md](protocol.md)). Inside the case every link is a bought cable
plugged into a connector JLC fits: no soldering or crimping
([wiring.md](wiring.md)).

### Software: web configurator, optional daemon
VIA-style: a **web configurator** (a static page using WebUSB, WebHID and
Web Serial; Chromium browsers only) is the main tool. It sets the key
layout and pages, HID shortcuts and macros, knob feel, images and
brightness, and updates the firmware of both chips. Everything is stored
on the device, so clickdeck works on any computer with no software
installed.

A small optional **host daemon** (`clickdeckd`) adds live integrations:
changing images, showing app state (mic muted, volume), running scripts.
OpenDeck or Companion Satellite thin clients are possible later, on top of
it. Details: [configurator.md](configurator.md).

Linux needs a udev rule (`uaccess`) so the browser can open the devices.

### Why a bulk channel for images
HID on full-speed USB is limited to ~64 KB/s (64-byte reports, one 120×120
key image ≈ 0.5 s), so WebHID is too slow. Each chip has a vendor bulk
interface that the browser reaches through WebUSB. Plan on about 0.5 MB/s
(Espressif's figure for its USB stack): one raw key takes ~85 ms, a raw
full page ~1.8 s. So RLE/JPEG is the default, not an option. Also: upload
icons once and reference them by CRC; redraw only the parts of the screen
that changed. Target: a full page in under 300 ms.

### Keys: Elgato style
One LCD panel under a **frame-shaped PCB** (square window cut out per key).
A clear resin cap sits in each window; a tab on the cap presses a micro
switch mounted on the PCB strip between windows.

The frame PCB must not rest on the glass, and the glass must not be the
cap's stop (design review B1–B3, decision D8):
- **More frame support:** 14 M2 screws hold the frame PCB: 5 pan-head
  along the back and left edges (off the glass) and 9 countersunk, flush
  with the PCB's underside, over the glass (4 between the knob windows, 3
  on the right margin, 2 at strip crossings x = ±33 mm between key rows 2
  and 3).
- **Cap down-stop:** caps and frame PCB sit 0.8 mm above the glass
  (`GLASS_GAP`; the image sits ~0.6 mm deeper than with the old 0.2 mm).
  Rails under each cap's side lips and lugs at its back corners stop on the
  frame PCB after 0.5 mm of travel, past the B3U's worst-case 0.35 mm. 0.1
  and 0.2 mm shim washers tune the stack. `cad/keystack.py` checks that the
  worst cap drop (0.52 mm) plus the frame's flex (0.046 mm/N worst, down
  from 4.2 mm/N) leaves at least 0.1 mm to the glass at a 3 N press.
- **Second switch:** the prototype frame PCB has a second switch footprint
  per key. The 5-point force test decides whether the full build needs two
  switches per key.

Laser-cut acrylic caps are out:
sheet tolerance alone is larger than the key stack's budget. The cap has
0.2 mm of free play; an optional foam or silicone ring on the flange stops
rattle. Caps come in one standard clear finish for now; revisit the look
once real caps are in hand.

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
  enabled. The test kit times 1 real and 4 dummy loops first.
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
(U-shaped slot, hinged at the back). An arm on the printed motor spacer
reaches forward over the slot to a B3U switch on the board's fixed front
border (top side); pressing the knob flexes the tongue down and an M2×3 set
screw in the arm presses the switch. A plain 8 × 1.6 mm FR-4 neck is likely several
times too stiff (design review H3, decision D10), so:
1. First a $0 test: saw a tongue into scrap FR-4 and load it on the kitchen
   scale.
2. Rev A's knob board gets a **tunable hinge** (perforations that can be
   drilled or cut out) and an adjustable **set-screw striker** per switch,
   so each knob's press gap is set on the bench, with the top plate off.
   Rev A is the first real hinge (the Rev 0 knob module was dropped).
3. If sideways force on the knob causes false clicks (the cap top is far
   above the hinge), the next revision moves to a parallel-guided flexure.

**Knob board floorplan** (D16, D6): each driver sits on the 19 mm back
strip next to its motor header, off the tongues, so only sensor traces
cross each hinge. Before the full order, floorplan the board with real
footprints (RP2350B QFN-80, TMC6300, connectors). Motor current is
measured on the test kit at the bench supply and the USB power meter (the
Rev 0 module and its shunt footprints were dropped). The knob board is
**top-side only** (D6, shown feasible in the model), so JLC's cheaper
single-side assembly fits everything. It needs SMD right-angle motor
headers (part not chosen; THT is the fallback) and a reverse-mount BOOTSEL
switch.

### Power budget
One USB-C cable feeds the display board, its backlight and 5 motors. One
SmartKnob motor alone draws ~0.7–1 A peak at 5 V. But a motor only draws
real current while it's pushing back on a hand: an untouched knob sits at a
detent center and needs no torque. So the budget is about **one motor's
worth (about 0.8–1.5 A, set by the port; below)**, enforced by a firmware arbiter:

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

**Power policy (D9): full haptics need a USB-C port that offers 1.5 A or
more, over a C-to-C cable.** The USB board reads the host port's
advertised USB-C current (CC pins, polled all the time) and the knob board
sets the motor budget from it:
- Default USB power (500 mA, or any A-to-C cable): haptics nearly off. The
  display, hub and logic already use about 0.5 A, so the motors only get
  faint detents and ticks. The configurator says why.
- 1.5 A port: about 0.8 A for the motors until real current is measured.
- 3 A port: 1.5 A (capped by the internal cable).

Until the knob board has read CC and been configured over USB, the motors
stay off and the backlight starts low. An optional USB-PD sink footprint
(CH224-class, not fitted by default) on the USB board could ask a PD
charger for 5 V at 3 A. A brownout guard on the 5 V input backs it all up
(it trips on a drop from idle, not a fixed 4.6 V). Details:
[wiring.md](wiring.md); see also [lessons.md](lessons.md) #2.

### Firmware updates and recovery
Both chips update from the web configurator over the single USB cable,
each over its own USB connection through the hub, through its ROM
bootloader: the ESP32-S3 with esptool-js over Web Serial, the RP2350B
through its UF2 bootloader over WebUSB (drag and drop of a UF2 works too).
No OTA slots and no custom bootloader: the ROM bootloader can't be
overwritten, so a failed update can always be retried. Trust is VIA-style
(D17): the browser's device picker is the confirmation, with no pinhole or
knob hold by default. An optional lock (stored on the device) brings back
a 3 s knob hold for reflashes and keymap changes. Bootloaders stay unlocked.

Three pinholes reach the display board's BOOT and RESET (back wall) and the
knob board's BOOTSEL (case floor, under the knob board's left end; lift the
slab off the stand to reach it). Settings live in flash that firmware updates don't
erase; holding the top-left key while plugging in resets them. Step by
step: [recovery.md](recovery.md).

### USB protocol
Follows lessons from Stream32's documented protocol
([lessons.md](lessons.md) #11–16): versioned hello with feature flags,
images stored by CRC so reconnects resend nothing, the device reports key
size in pixels, binary framing with RLE/JPEG, pages stored on the device
plus temporary live-state overlays, separate key-down/key-up events, and
keys that send their stored shortcuts with no host software.

**Offline pages and screen wake (D5):** the two chips only meet over USB
through the host. An optional one-wire link from the knob board to the
display board's GPIO6 connector carries page switches and activity, so
pages change and the screen blanks and wakes with no host. The knob board
has the footprint now; fitting the lead is optional. Without the link and
without a host, the display never idle-blanks
([protocol.md](protocol.md)).

### Touch band
A thin capacitive sensor PCB under the top plate, just below the knob
displays: tap or swipe on the plate surface, like the + XL's touch strip.
(Touching the display glass itself doesn't work: it sits ~7 mm below the top
surface because of the key stack.) The knobs moved forward 4 mm to make the
band 11.2 mm tall (model). It sits close to the motor bells, so it has a
grounded guard trace, hatched ground on the bottom layer, and firmware
ignores touches for 300 ms around knob motion or a press
([pcb.md](pcb.md)). The realistic touch test (full-length band, motor
running, panel lit) happens on Rev A, the first build with a running motor
under a printed plate. If it fails, the band gets one revision with the
knobs further forward (D11), or is dropped (it's optional, D12).

Touch controller (D12): **AT42QT2120** (Microchip, SOIC-20; LCSC C614938,
$1.89, 69 in stock on 2026-10-17, not marked end-of-life; Farnell and RS also stock it). It replaces the
discontinued MPR121. Its built-in slider uses only 3 channels (too coarse
over ~155 mm), so all 12 channels run as separate electrodes and firmware
works out the position from their signal levels. The band is a
nice-to-have and unplugs; if the part can't be sourced, the band is
dropped, not the build (`TOUCH_BAR = False` in `cad/params.py` removes the
band, its cable and the knob board's SH header from the model).

### Case material
The case holds about 2.3 W in a closed box, and the 7B is rated 0–65 °C.
Print it in **PETG** (not PLA), with 4 walls and ≥ 25% infill at the
bosses. Screws that get undone for service go into **M3 heat-set inserts**
(4.0 mm hole × 5.7 mm) in the top plate's 8 mm posts, with M3×6 machine
screws, not self-tapped plastic threads (D14). Log temperatures
for 2 h at full brightness on the first build.

## Stages (prototype: 2 keys on the 7B + a knob test stand, then Rev A)

Plan changed 2026-10-18 (D3). Final parts are bought early, tested on the
bench and reused in the full build: the Waveshare 7B, six 2204 motors (5 +
1 spare), the magnets and the display cable. A throwaway test kit covers
the rest: a SparkFun TMC6300 breakout, an MT6701 breakout, a WeAct RP2350B
core board and a CH334F hub module (these two stay as the firmware dev
bench), a printed knob test stand, and one custom PCB, the rev C 2-key
frame PCB on the real 7B. No custom knob or controller board before the
full build. Parts and costs: [parts.md](parts.md), [cost.md](cost.md).

**Prototype (test kit):**

1. **Images over USB:** the display firmware (ESP-IDF) shows images sent
   over its WebUSB bulk interface on the 7B. Measure throughput and the
   flash-write glitch early.
2. **Two devices, one hub:** the 7B and the core board behind the CH334F
   module; the configurator pairs them. A stored keymap works with no
   software running; a "host" key changes its own image.
3. **Knob:** the 2204 on the printed test stand over the MT6701 breakout,
   driven by the SparkFun TMC6300 from the core board. SimpleFOC closed
   loop; clicky/smooth/stops set from the PC; current, standby and wake;
   1 real + 4 dummy FOC loops for timing. Each low side runs from an
   inverted PWM output, as the knob board's inverter will.
4. **Keys:** the two top-left keys on the rev C frame PCB + clear caps on
   the 7B; adjust until a press anywhere on the key clicks cleanly, and
   compare one switch per key with two. Caps are JLC3DP clear resin
   prints; the plates are laser-cut acrylic.
5. **Hinge (free):** a tongue sawn into scrap FR-4, loaded on the kitchen
   scale (D10).
6. **Decide go/no-go:** if the knob and cap feel are both good → Rev A.

**Rev A (the full build):** first test of everything the kit can't
show: the hinge and press feel, the motor mount fit, our RP2350B, hub,
CC sensing and touch circuits, the connectors and cables, and the touch
band next to a running motor ([prototype-tests.md](prototype-tests.md)).
Plan on one revision of whichever board fails, and order only that board,
not the whole panel ([cost.md](cost.md)).

Software: on the ESP32-S3, **ESP-IDF 5.x** (esp_lcd + esp_tinyusb; the
7B's RGB panel needs sdkconfig options a precompiled Arduino core can't
set: [protocol.md](protocol.md)). On the RP2350B, **arduino-pico +
SimpleFOC**, pinned. The web configurator in TypeScript; the optional
daemon with a Python library. Pin every version and build in CI.
