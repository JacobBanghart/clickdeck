# Lessons from related projects

Things other builders learned the hard way, from the code, docs and issue
trackers of related open-source projects (researched 2026-10-17). Each
lesson ends with what clickdeck does about it.

Sources and licenses:
- [Stream32](https://github.com/fadyfaheem/stream32) (MIT): ESP32-S3 touch
  decks on Waveshare boards, desktop app, documented USB protocol
- [eezbotfun 8-key macropad](https://github.com/eezbotfun/8-key-macropad)
  (MIT code; case files CC BY-NC): ESP32 HID macropad
- [Open Deck](https://github.com/joshr120/open-deck) (MIT): 4 keys under
  acrylic caps over one screen
- [SimpleFOC](https://github.com/simplefoc/Arduino-FOC) (MIT): motor control
  library we use
- [SmartKnob](https://github.com/scottbez1/smartknob) (Apache-2.0 for software
  and electronics, CC BY 4.0 for mechanical): haptic knob. Not MIT, but
  lessons from its issues are free to use; copied code needs its license
  and attribution kept.

## Knobs and motors

1. **The exact motor disappears.** SmartKnob's motor sold out, every
   alternative its author tried from the same seller had bad cogging, and
   the project stalled
   ([#16](https://github.com/scottbez1/smartknob/issues/16),
   [#27](https://github.com/scottbez1/smartknob/issues/27)). Cogging is
   the enemy of our "smooth" mode.
   → Describe the motor by spec (size, pole count, hollow shaft, low
   cogging), not by one link. Buy candidates from two sellers for the
   prototype and compare cogging by hand. Make the knob board's mounting
   holes fit more than one motor. Known-good fallback: SparkFun's
   SmartKnob motor ([ROB-20441](https://www.sparkfun.com/three-phase-brushless-gimbal-stabilizer-motor.html),
   ~$46, bigger than the 2204).

2. **USB power runs out.** One SmartKnob motor draws roughly 0.7–1 A peak at
   5 V; testers on weak USB ports or thin breadboard wires got unstable,
   noisy motors ([#32](https://github.com/scottbez1/smartknob/issues/32),
   [#113](https://github.com/scottbez1/smartknob/issues/113)).
   → clickdeck has 5 motors plus a 7" backlight on one USB-C cable. Motors
   only draw real current while pushing back on a hand, so drivers sleep
   until their knob moves and a firmware arbiter shares about one motor's
   worth of current (one active knob gets it all, two split it). See the
   power budget in [plan.md](plan.md). The device reads the host's
   advertised USB-C current (1.5 A or 3 A), falling back to a low limit.
   Require a C-to-C cable. On the prototype, power the motor with short,
   thick leads, not breadboard jumpers.

3. **The driver chip may not be in stock at the assembler.** SmartKnob
   builders found the TMC6300 missing from JLC's parts library
   ([#83](https://github.com/scottbez1/smartknob/issues/83)). JLC lists it
   today as an "extended" part, and one listing showed it
   [out of stock](https://jlcpcb.com/partdetail/TRINAMIC_MOTIONCONTROL-TMC6300LA/C5196961).
   → Check JLC stock before every order. Keep DRV8316 (plan B) footprint-
   compatible in the schematic, or pre-order parts through JLC's parts
   service.

4. **Auto-calibration at boot is fragile.** SimpleFOC's `initFOC` spins the
   motor at startup to find pole pairs and zero angle; with the MT6701 it
   has returned wrong values and burned extra power
   ([SimpleFOC #172](https://github.com/simplefoc/Arduino-FOC/issues/172)),
   and SmartKnob calibrations failed until the knob was nudged
   ([#126](https://github.com/scottbez1/smartknob/issues/126)).
   → Calibrate each knob once (hands off), store pole pairs, zero angle and
   direction in flash, and skip the boot-time spin. Also avoids the knobs
   twitching every time the device powers on.

5. **MT6701: use SSI, strap the mode pin.** Over I²C it reads jittery
   ([SimpleFOC #477](https://github.com/simplefoc/Arduino-FOC/issues/477));
   breakout boards default to ABZ/I²C mode and read garbage until the mode
   pin is pulled up for SSI
   ([SmartKnob #113](https://github.com/scottbez1/smartknob/issues/113)). The
   magnet must be diametric, centered and at the right distance.
   → SSI only, mode pin strapped on our PCB, magnet position set by the
   board's screw holes. On the prototype, check the breakout's mode pad.

6. **Press detection with strain gauges needs per-unit calibration**
   ([SmartKnob #48](https://github.com/scottbez1/smartknob/issues/48)).
   → Confirms the choice of a real switch under a hinged tongue.

## Firmware and toolchain

7. **Toolchain updates break motor code.** ESP-IDF 5.4 broke SimpleFOC's
   ESP32-S3 PWM driver; users lost days to version combinations
   ([SimpleFOC #462](https://github.com/simplefoc/Arduino-FOC/issues/462)).
   Open Deck users couldn't compile without the exact board package and
   libraries ([Open Deck #4](https://github.com/joshr120/open-deck/issues/4)).
   → Pin every version (PlatformIO platform, framework, libraries) in the
   repo and build firmware in CI, as Stream32 does. Publish binaries with
   SHA-256 hashes.

8. **Plan firmware updates over USB from day one.** eezbotfun's V1 could
   only update over Wi-Fi; USB updates needed new hardware
   ([#14](https://github.com/eezbotfun/8-key-macropad/issues/14)). Their
   locked bootloader drew complaints
   ([#12](https://github.com/eezbotfun/8-key-macropad/issues/12)).
   → The ESP32-S3 updates over its native USB. The RP2350B on the knob board
   has no USB connection of its own, so wire its RUN and boot-select (or
   SWD) pins to the ESP32-S3 so the main board can reflash it. Never lock
   the bootloader.

9. **Heavy artwork can lock up USB.** On eezbotfun's ESP32-S2, custom icons
   plus a background made the USB device stop responding until a firmware
   fix ([#16](https://github.com/eezbotfun/8-key-macropad/issues/16)).
   → Keep image buffers in PSRAM, give the USB task priority, and test with
   21 full-color keys early.

10. **Settings must survive firmware updates.** Stream32 keeps calibration,
    rotation and color settings in NVS, past the app partition.
    → Same for knob calibration and display settings.

## USB protocol (from Stream32's documented protocol)

11. **Handshake with versions and feature flags.** Every connection starts
    with hello messages carrying protocol version, firmware version, board
    ID, device ID and a list of supported features. New features are
    additive, so old firmware keeps working.
12. **Don't resend images the device already has.** The device reports which
    images it's missing (by CRC), so reconnecting streams nothing.
13. **The device reports its key size in pixels**; the host renders artwork
    at exactly that size.
14. **Raw images over slow links are slow.** Base64 RGB565 over serial took
    seconds per key; Stream32 added RLE compression (up to ~99% smaller for
    flat icons). → Binary framing on our USB bulk/CDC channel, with RLE or
    JPEG.
15. **Separate saved layouts from live updates.** Persisted pages for
    offline use (page navigation works with no host), plus temporary
    "live state" overlays in RAM that expire.
16. **Identify the device precisely.** Specific USB IDs and a stable serial
    number, so the host never grabs the wrong serial port.

## Displays

17. **The same display model ships with different panels.** Stream32 needed
    settings for color inversion, RGB/BGR order and mirroring
    ([#17](https://github.com/fadyfaheem/stream32/issues/17),
    [#20](https://github.com/fadyfaheem/stream32/issues/20)).
    → Firmware settings for all three. For the prototype's generic 2.4"
    screen, expect either ST7789 or ILI9341.
18. **Waveshare RGB boards may not dim.** Stream32 found the 4.3" board's
    backlight is on/off only (through an I/O expander), and the 4" Rev 3
    needed a hardware mod to power on automatically.
    → Check backlight dimming and power-on behavior of the 7" board before
    buying it in quantity; plan a PWM backlight mod if needed.
19. **Blank the screen when idle** (Stream32 defaults to 10 minutes, and
    blanks when the computer locks) to avoid burn-in.

## Keys and host software

20. **Send key-down and key-up separately.** eezbotfun sent a whole
    keystroke per press, which broke push-to-talk and held modifiers
    ([#17](https://github.com/eezbotfun/8-key-macropad/issues/17),
    [#2](https://github.com/eezbotfun/8-key-macropad/issues/2)).
    → Report press and release (and long-press) as separate events. A plain
    HID keyboard mode should work with no host software at all.
21. **Linux and macOS from the start.** eezbotfun's Windows-only app was the
    top request; it also crashed writing to its install folder
    ([#11](https://github.com/eezbotfun/8-key-macropad/issues/11),
    [#13](https://github.com/eezbotfun/8-key-macropad/issues/13)).
    → OpenDeck and the Python library are cross-platform; store settings in
    the user's config folder.
22. **Keys should show live state** (mic muted, which audio output) and
    profiles should import, export and clear
    ([Stream32 #27](https://github.com/fadyfaheem/stream32/issues/27),
    [eezbotfun #7](https://github.com/eezbotfun/8-key-macropad/issues/7),
    [#15](https://github.com/eezbotfun/8-key-macropad/issues/15)).
23. **Be careful running commands from the host.** Stream32 put shell-command
    status checks behind a developer-mode setting.
24. **Stream32 already speaks Bitfocus Companion's Satellite API**, a second
    host option alongside OpenDeck.

## Mechanics

25. **Caps without a CNC or printer.** Open Deck's caps are 4.5 mm acrylic,
    or 1.5 mm + 3 mm laser-cut layers glued with UV-curing glue.
    → A cheaper alternative to resin-printed caps for the prototype.

## Licensing notes

- OpenDeck (the app) is GPL-3.0. Its plugins run as separate programs, so a
  clickdeck plugin can likely stay MIT; check OpenDeck's plugin terms before
  publishing.
- Code copied from SmartKnob keeps its Apache-2.0 license and notice;
  mechanical files reused from it need CC BY attribution.
- eezbotfun's case files are CC BY-NC: don't copy them into this repo.
