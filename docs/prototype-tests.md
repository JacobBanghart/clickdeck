# Prototype tests (go/no-go)

What the 2-key + 1-knob prototype (on the real 7B, with the Rev 0.5 test
board; [parts.md](parts.md)) has to show before the full build. The
targets are starting points, not specs. Adjust them once there's hardware to
feel, and record the results here.

Tools: USB power meter between the computer and the board, the calipers, a
phone slow-motion video for timing, a kitchen scale (0.1 g) for press
force, a thermocouple or IR thermometer, and a logic analyzer (a cheap
8-channel one is enough).

## Knob

| Test | How | Pass |
|---|---|---|
| Motor on arrival | Spin each motor by hand, unpowered. Measure phase resistance R, phase-to-stator resistance, thread depth and lead length | At least one motor feels smooth (gate for Order 2). Phase-to-stator is open |
| Clicky mode | Set 24 and 48 clicks per turn; turn slowly and fast | Clicks feel distinct and even, none skipped at normal speed |
| Smooth mode | Zero torque, driver in standby; turn slowly by hand | No noticeable cogging (bumps). If it fails, try the second motor or SparkFun ROB-20441 |
| End stops | Bounded 0–100; push past each end | Firm stop, springs back, no buzzing; eases off after a few seconds of pushing |
| Current at rest | Power meter, knob untouched | Driver asleep; ≤ 5 mA above the board's idle current |
| Current while clicking | Spin through detents on a 1.5 A C-to-C port | Peak motor current ≤ ~0.8 A; VBUS at the meter stays ≥ 4.75 V |
| Default port | Same on a 500 mA port and an A-to-C cable | Haptics nearly off (faint detents only), no resets, the configurator shows why |
| Current at an end stop | Lean on the stop for 30 s | Driver case < 70 °C; the firmware time limit keeps current within the budget |
| Standby back-power | `NSTDBY` low, one PWM pin high | VIO stays below 0.4 V |
| Wake latency | Turn from rest | No dead zone or delay you can feel before the first click |
| Hinge, before ordering | Saw a tongue into scrap FR-4 with the planned neck; load its tip on the kitchen scale | Record the force for 0.15 mm of travel; size the Rev 0 hinge from it |
| Press feel | Kitchen scale under the knob; tune the hinge perforations and the set-screw striker | Clicks at roughly 150–400 g, one clear click, no rocking |
| Press while turning | Turn hard without pressing; push sideways on the knob rim | No accidental press events (if sideways force clicks, plan a parallel-guided flexure) |
| Calibration | Store, power-cycle 10× | Knob never twitches at power-on; angle and direction stay correct |
| Plug reversed | Reseat the motor plug the other way, power up | Direction check catches it and recalibrates; the motor never runs away |
| Sensor fault | Pull the sensor's DO line while the motor holds a detent | Firmware drops `NSTDBY` within one loop |
| Loop timing | RP2350B running 1 real + 4 dummy FOC loops, 15 PWM outputs, 5 sensor reads | ≥ 2 kHz per motor (aim for 5 kHz) |
| Noise | Listen up close in a quiet room | No audible whine or buzz at rest or while turning |

## Keys

| Test | How | Pass |
|---|---|---|
| Rest state | Assemble one key dry; multimeter across the switch | Open at rest (the stack doesn't pre-press the switch) |
| Gap | Feeler gauge or calipers: cap bottom to glass | Record it (model: 0.8 mm); must be > 0 under every key |
| Down-stop | Press each cap at 3 N, then harder, with witness film on the glass | The cap's rails and lugs stop on the frame PCB after ~0.5 mm, past the switch's click; no mark on the film |
| Click feel | Press each key 50× | Crisp click every time; decide whether 0.15 mm travel feels good or too short |
| Actuation force | Kitchen scale at 5 points per cap: center, 4 edges (including the far edge from the switch) | Every point clicks; the far edge needs ≤ 2× the center force |
| Glass load | Witness film (or carbon paper) on the glass, press 10 N on each cap | No mark on the glass |
| Missed events | 500 presses per key, logic analyzer on the switch and the USB events | 0 missed or doubled events |
| Rattle | Shake the prototype; tap keys lightly | No rattle you'd notice in use (if it fails, try a foam or silicone ring on the flange) |
| One switch vs two | Same 5-point force test on a cap with one switch (SW1/SW2, one-nub cap) and one with two (SW3/SW4 wired too, two-nub cap) on the rev C frame PCB | Decides whether the full build uses two switches per key |
| Image | Look through the cap from straight on and at 45° | Image looks like it's on the key surface; edges and gaps acceptable |
| Down and up events | Hold a key 3 s | Separate key-down and key-up events (push-to-talk works) |

## Touch band

Setup: a full-length strip of 10–12 copper-tape segments (13–15 mm pitch,
half-width ends) under an offcut of the printed top plate, read by the
AT42QT2120 on the Rev 0.5 board (all channels as keys, position
interpolated in firmware), with the motor running next to it and the panel
lit. Guard trace, hatched ground and the 300 ms lockout in place. If it
fails, the knobs move further forward (D11). Not a short strip on acrylic: that
can't show the motor and panel interference.

| Test | How | Pass |
|---|---|---|
| Tap | Tap each of the knob-display positions 20× | 20/20 detected, no ghost taps |
| Position | Tap at marked points along the band | Within ±5% of the band length |
| Latency | Slow-motion video of a tap and the host's event | < 50 ms |
| Swipe | Swipe left and right along the band | Direction and position tracked smoothly |
| Hand nearby | 10 min of normal knob use (turning, pressing, hand resting on the plate) | 0 false touches |

## USB and display

| Test | How | Pass |
|---|---|---|
| Image speed | Send a full page of key images (compressed) | Shows in under 300 ms. Record the raw throughput (plan: ~0.5 MB/s) |
| Flash-write glitch | On a 7B: full-screen redraws while images stream over USB and the cache is written to flash | No flicker, no lasting image shift |
| Reconnect | Unplug and replug | Keys reappear without resending images (cache works) |
| Standalone | Set keys, a macro and knob feel in the configurator; close it; plug into another computer with no software | Keys, macros and knob feel all work; the display shows the stored page; no key stays held |
| Idle | Leave untouched: with the daemon running, with the GPIO6 link and no host, and with neither | Blanks and wakes on touch, key or knob in the first two cases; never blanks in the third |
| Offline pages | Link fitted, no host: press a page-switch key | Images, keymap and knob feel all change together |
| Two devices, one hub | Knob board (RP2350B) and display (ESP32-S3) behind the Rev 0.5 hub; replug in a different port | The configurator pairs them every time; images and events land on the right device |
| Browsers and OSes | Configurator in Chrome and Edge on Linux (with the udev rule), Windows and macOS | Both devices open; no driver installs |
| Power descriptors | `lsusb -v`, `lsusb -t`, `dmesg` on Linux | Both devices declare ≤ 100 mA; no "insufficient available bus power" |
| Connectors | Rev 0.5: JST-GH link, FFC + ZIF to the frame PCB, JST-SH to the touch strip | All work; footprints and pin 1 match the bought cables |

## Firmware stress

| Test | How | Pass |
|---|---|---|
| Replug | Unplug and replug 50× | Enumerates every time; no stuck keys, no lost settings |
| Sleep and resume | Suspend and wake the PC 10× | Screen blanks and motors sleep in suspend; no stored HID shortcut fires on resume |
| Flash while running | `SAVE` / `PERSIST` while knobs turn and images stream | No FOC glitch you can feel, no display glitch |
| Brownout | Pull VBUS down with a load or a long thin cable | Motors cut, the device stays enumerated, the trip shows in `STATUS` |
| Fuzz | Send malformed and random frames to both data channels for 10 min | No crash or hang; bad frames get `ERROR` |
| Confirm hold | Send a keymap change and a bootloader request; don't hold, then hold a knob 3 s | Nothing changes without the hold; both apply after it. Without the GPIO6 link the display's bootloader request stays refused (`not-confirmed`) and the configurator asks for the BOOT pinhole |

## Updates and recovery

Steps in [recovery.md](recovery.md).

| Test | How | Pass |
|---|---|---|
| Web update | Update both chips from the configurator 10× | Every update succeeds; settings survive |
| Interrupted update | Pull the cable halfway through each chip's update | The retry succeeds from the configurator |
| Pinholes | Start each chip's bootloader with BOOT (back wall) and BOOTSEL (case floor, slab lifted off the stand); flash from there | Both work with the case closed |
| EXIO5 stuck | Test firmware drives EXIO5 high; then unplug 10 s | USB is gone until the power-off, then back |
| Settings reset | Hold the top-left key while plugging in | Defaults back, firmware and knob calibration kept |
| Corrupt settings | Corrupt the stored settings block (test build) | Boots defaults; the old block is kept until the next save |
| Factory restore | "Restore factory firmware" in the configurator | Both chips back on the release builds |

## Power and USB bring-up (first full-build boards)

In order; stop at the first failure. "PC unplugged" means exactly that:
the JST-GH contacts aren't staggered.

1. Bare boards: check for shorts between VBUS, 3V3 and GND.
2. Power from a current-limited bench supply (~300 mA) first.
3. CC readings with 0.5 / 1.5 / 3 A sources, in both cable orientations.
4. PC unplugged: check the JST-GH cable pin 1 to pin 1, then plug it in.
5. `lsusb -t`: the hub at 480M, both devices at 12M on separate ports; no
   power rejections in `dmesg`. Repeat on Windows and macOS.
6. Scope VBUS inrush at hot-plug.
7. PC unplugged: plug in a reversed GH cable, then power up. Nothing gets
   hot; the knob board doesn't enumerate; no damage after the straight
   cable goes back.
8. Electronic-load sweep of each motor budget for 10 min on real laptop
   ports.
9. Short the display port's output: the switch limits, the hub and knob
   board stay up.
10. Stream images while knob HID traffic runs at the same time.
11. Sleep and wake the PC.
12. Pull the external cable sideways and axially, about 30 N; ESD at the
    external port if a gun is available.

## First full build

- Log the case and 7B temperatures for 2 h at full brightness.
- Measure the 7B: `PANEL_T`, the front lip, its current at full
  brightness, and record the board's silkscreen revision. Probe the
  backlight EN/FB while sweeping brightness.

## Decision

- **Go:** knob feel (clicky, smooth, stops, press) and key click both pass,
  and current numbers fit the power budget.
- **Adjust and retest:** a mechanical part fails (cap, tongue, motor) but
  the approach works. Change `params.py`, reorder that part.
- **Rethink:** smooth mode cogs with every motor tried, or the key click
  can't be made to feel good.
