# Firmware, protocol and host software review

Reviewer role: senior embedded/systems engineer, standard design review. Scope: docs/protocol.md, plan.md, wiring.md, lessons.md, open-questions.md, prototype-tests.md, parts.md, knob-module.md, pcb.md. No firmware or host code exists yet, so this reviews a plan, not code. Reviewed 2026-10-17.

## Verdict

**Go with changes.** The architecture is sound and every firmware piece has a real library behind it.
Two things have to change before the prototype order: test the display firmware on the real 7B board, not the 2.4" SPI stand-in, and decide on the offline link between the two chips.
The protocol is a good v0 sketch, but it needs a framing and error-handling pass before anyone writes code against it.

## Strengths

- **Two USB devices behind a hub** (protocol.md:7-29) removes the custom bootloader and the UART relay. Each chip keeps its stock recovery path: UF2/BOOTSEL on the RP2350, and esptool plus the BOOT pinhole on the ESP32-S3 (wiring.md:48-51). That's the right trade for a hobby build.
- **The protocol borrows the right ideas from Stream32:** a hello with feature flags, a cache keyed by CRC, a device-reported pixel size, separate key-down and key-up events, overlays held in RAM, and HID fallback (lessons.md:395-416).
- **The knob firmware avoids SmartKnob's known traps:** calibration is stored instead of re-run at boot, the MT6701 uses SSI, and standby is sequenced to keep the inverter safe (lessons.md:339-356, knob-module.md:84-89).
- **Every firmware piece has a library behind it.** SimpleFOC has supported RP2350 since v2.3.5 (2025-07-28, PR #435, [releases](https://github.com/simplefoc/Arduino-FOC/releases)). TinyUSB does HID+CDC composite devices on both chips. ESP-IDF esp_lcd drives the RGB panel.
- **OpenDeck really has a device-plugin path.** A plugin registers a device with `rows`, `columns`, `encoders`, `touchpoints` and `infobars`, and receives `setImage` as data URIs, with encoder images pre-rendered as JPEG ([devices.rs](https://github.com/nekename/OpenDeck/blob/main/src-tauri/src/events/inbound/devices.rs), [outbound/devices.rs](https://github.com/nekename/OpenDeck/blob/main/src-tauri/src/events/outbound/devices.rs), `DeviceInfo` in [shared.rs](https://github.com/nekename/OpenDeck/blob/main/src-tauri/src/shared.rs)).
- **Pass/fail tests are written before the hardware exists** (prototype-tests.md).

## Issues

### Blocker

**B1. The prototype doesn't exercise the riskiest display firmware.** The prototype display is a 2.4" SPI ST7789 (parts.md:151). The real board drives a 1024×600 RGB panel from a PSRAM framebuffer. ESP-IDF says "the LCD CANNOT function if the external memory cache is disabled, such as during OTA or NVS writes to the main flash", and that EDMA and the CPU split PSRAM bandwidth ([esp_lcd RGB docs](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/lcd/rgb_lcd.html)). The plan writes every image and layout to flash (protocol.md:89-93, 143), so the screen will glitch or drift each time the cache is written unless bounce buffers and `CONFIG_SPIRAM_XIP_FROM_PSRAM` are used. Those are sdkconfig options, which the precompiled Arduino-ESP32 core in plan.md:347 can't easily change.
→ Add the $34 7B to Order 1 and use it for stages 1-2. Build the display firmware on ESP-IDF (esp_lcd + esp_tinyusb), not Arduino. Add a test: write to flash while the screen is static and look for glitches. **[decision]**

### High

**H1. With no host, the screen blanks and never wakes.** Idle blanking runs on the display chip, and only the host can wake it (protocol.md:139-141). Without the app, the stored idle timeout blanks the screen and a key press can't bring it back. Offline page switching is broken the same way (protocol.md:161-166). Both have one cause: the chips can't reach each other.
→ Before the knob board layout, decide on a one-way link from the RP2350 to the 7B's J8 GPIO6 (open-questions.md:13). A one-wire UART carrying `wake` and `page N` is enough. If the link is rejected, the firmware must turn off idle blanking whenever no host is connected. **[decision]**

**H2. Five FOC loops on one RP2350 are untested.** The SimpleFOC forum only discusses 2 to 4 motors on an RP2350 ([thread](https://community.simplefoc.com/t/rp2350-support-raspberry-pico-2/5607)). Each loop also needs an MT6701 SSI read. The prototype has one knob (plan.md:330), so loop rate under five-motor load is never measured.
→ The prototype firmware should run 5 loops: 1 real motor plus 4 dummy sensor reads and PWM writes. Measure the per-motor loop rate and aim for ≥2 kHz. Plan for PIO/DMA sensor reads and splitting the loops across both cores. **[no-decision]**

**H3. Flash writes during motor control will stall the knobs.** `KNOB_CONFIG` is "applied immediately, stored per page" (protocol.md:115). RP2350 flash writes stall execute-in-place on both cores, so the FOC loop freezes while a write runs. Every page switch would also wear the flash and, given B1, glitch the display.
→ Keep per-page configs and layouts in RAM; the host resends them on each page switch. Write to flash only on an explicit `SAVE`, and only when the motors are asleep. Put the FOC loop in RAM (`__not_in_flash_func`). **[no-decision]**

**H4. Framing and error handling are underspecified.** A single 0xCD magic byte can also appear inside payloads (protocol.md:57). No resync rule, NAK, retry, timeout or error-code table is defined. `PING`, `ERROR` and `REBOOT_BOOTLOADER` are mentioned but never specified. `seq` has no direction rule for unsolicited events. `HELLO` has no rule for a major-version mismatch.
→ Use COBS (or SLIP) framing with a CRC over the whole frame. Define ERROR codes, a per-chunk NAK with retransmit, a minimum and maximum version range, separate seq spaces per direction, and a `PING` for the display device too (overlay expiry at protocol.md:87 depends on it). **[no-decision]**

### Medium

**M1. Pairing on first contact is chicken-and-egg.** Hub topology works on Linux, but on Windows and macOS it needs per-OS code (protocol.md:40-43). The pairing-ID fallback only works once the devices are already paired.
→ Add an interactive pairing step: the display shows a code and the user presses a key. Use topology only to suggest a match. **[no-decision]**

**M2. Updating the ESP32 means a PID switch and esptool on the user's machine.** When the app is in ROM download mode, the device re-enumerates as USB-Serial-JTAG with a different identity (protocol.md:148-150).
→ Add in-app OTA over the data channel, using esp_ota with an A/B layout and rollback (this depends on B1's XIP fix). Keep esptool and the BOOT pinhole for recovery. **[decision]**

**M3. Linux CDC handling isn't covered.** ModemManager probes new ttyACM devices, and the user needs permissions to access them. Nothing in the docs mentions either.
→ Ship a udev rule that sets `ID_MM_DEVICE_IGNORE=1` and grants access through `uaccess`. **[no-decision]**

**M4. The power budget assumes far more than a default USB port gives.** On a default port the whole device draws about 1 A (wiring.md:127-131).
→ On a default port, the firmware should set the motor budget near zero (haptics off or weak) and say so in `STATUS`. **[decision]**

**M5. Smooth mode with complementary 3-PWM drive adds drag.** At zero torque, all three phases sit at the same voltage, which shorts the windings through the bridge and brakes the motor through back-EMF.
→ In free-smooth mode, keep the driver in standby. Wake it only for friction, stops or haptic effects. Test this on Rev 0. **[no-decision]**

**M6. Knob event rate isn't defined.** In smooth mode, `KNOB` events (protocol.md:105) could flood the host.
→ Coalesce events to ≤200 Hz, send detent events per step, and add a timestamp. **[no-decision]**

### Low

- **L1.** The official PlatformIO raspberrypi platform only has `pico` and `nanorp2040connect` boards. RP2350 needs the earlephilhower core through the maxgerhardt platform. Pin the versions (lessons.md:364-371). **[no-decision]**
- **L2.** RP2350 A2 silicon has erratum E9 (GPIO input leakage), which the A3/A4 steppings fix ([CNX](https://www.cnx-software.com/2025/page/51/?amp=1)). The WeAct boards may still carry A2. Use external or pull-up matrix polarity, and order A4 from JLC. **[no-decision]**
- **L3.** "Boot keyboard + consumer control" (protocol.md:22) needs two HID interfaces, because boot protocol doesn't allow report IDs. **[no-decision]**
- **L4.** The cache has no eviction or garbage-collection policy and no flash budget. A 146×146 RGB565 key is 42.6 KB raw. **[no-decision]**

## Host software

- **OpenDeck plugin.** OpenDeck is GPL-3.0. Plugins are separate processes that talk to it over WebSocket, so an MIT plugin is reasonable (aggregation), but it hasn't been confirmed. OpenDeck has no API for detent or haptic settings, so knob feel needs clickdeck-specific actions. Touch-band swipes aren't in the `touchscreen_press` model, which only carries a position.
- **Companion Satellite.** It's a better fit for knobs and per-control bitmaps. The advanced `LAYOUT_MANIFEST` allows per-control bitmap sizes, encoders, and signed `KEY-ROTATE` steps ([Satellite API](https://companion.free/for-developers/Satellite-API)). It's a line-based TCP protocol, easy to drive from Python.
- **Recommendation:** build one host core ("clickdeckd") that owns pairing, the image cache, overlays and knob config. The Python library, a Satellite client and a thin OpenDeck plugin all sit on it, so the protocol is implemented once, not twice. **[decision]**

## Documentation accuracy

- **Which board runs the knob is inconsistent.** knob-module.md:4 and pcb.md:204 say the knob module runs from the ESP32-S3 dev board; parts.md:164-173 says RP2350B.
- **plan.md:347** lists "Arduino-ESP32 core (TinyUSB, SimpleFOC)", but the knob firmware runs on the RP2350.
- **plan.md:332-335**, stage 2: "a press sends an HID event". In host mode, events go over CDC (protocol.md:31-33).
- **protocol.md:115**, "stored per page": the inputs device has no concept of pages.
- **plan.md:229**, "send only the parts of the screen that changed": this isn't in the protocol. Neither is a `LAYOUT` entry for the knob display areas.
- **plan.md:228**, "~1 MB/s": this is near the full-speed USB bulk ceiling, not a measured figure. A raw 146×146 key needs about 850 KB/s to land in 50 ms.

## Missing

- **No firmware tests in prototype-tests.md** for:
  - plugging and unplugging repeatedly
  - host sleep and resume (the 3 s fallback can fire stored HID shortcuts on resume)
  - flash writes while the display or motors are running
  - brownout behavior
  - a malformed-frame fuzz test
- **No shared codec.** There should be one C framing library for both firmwares, with a Python twin and golden test vectors.
- **No CI**, even though lessons.md:369 promises it.
- **No watchdog or fault policy** for the motors: what happens on a `DIAG` fault, a sensor dropout, or a USB stall.

## Suggested firmware milestones (prototype)

1. **M0, no hardware:** pinned toolchains (ESP-IDF + esp_tinyusb; arduino-pico + SimpleFOC 2.4.0), CI, protocol v0.1 (COBS, errors, PING), a C codec plus a Python codec, and unit and fuzz tests.
2. **M1, 7B display:** RGB panel with bounce buffers and XIP from PSRAM, CDC throughput, RLE blit, the flash-write glitch test, cache and layout.
3. **M2, inputs:** a composite HID+CDC device on the RP2350 board, key scan, HELLO/PING mode switch, HID fallback.
4. **M3, host core:** pairing (topology plus interactive), cache, overlays, a reconnect soak test.
5. **M4, knob:** open loop, then closed loop, stored calibration, all modes, standby and wake, the power arbiter, and the 5-loop timing test.
6. **M5:** touch band on the MPR121, then the update paths (UF2 reboot, ESP OTA with rollback).
7. **M6:** a thin OpenDeck plugin and a Satellite client.

## Actions first

1. Add the Waveshare 7B to Order 1 and retarget stages 1-2 to it (B1).
2. Decide on the J8 link to the RP2350, or on offline-no-blank behavior, before the knob board layout (H1).
3. Revise protocol.md: framing, errors, PING, RAM-versus-flash persistence (H3, H4).
4. Make M0 the first deliverable, with the shared codec and CI.
5. Fix the documentation inconsistencies listed above.
6. Add the 5-loop timing test and the firmware stress tests to prototype-tests.md.
