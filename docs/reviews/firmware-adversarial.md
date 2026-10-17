# Firmware, protocol and host software: adversarial review

**Summary.** The OpenDeck path can't carry clickdeck's main feature: the device-plugin API sends only knob ticks and per-position images. It has no knob config, no haptics, no pages and no swipes.
Without a host, the device falls apart. The keys' fallback shortcuts don't match the images on screen, the screen blanks and can't be woken, and with the default Arduino descriptors Linux may refuse to configure the display behind the bus-powered hub.
Image throughput is about half what the plan assumes, and the "persist every image in flash" cache fights the ESP32-S3's RGB panel, which corrupts the picture during flash writes.

Reviewed: docs/protocol.md, plan.md, wiring.md, lessons.md, open-questions.md, prototype-tests.md (2026-10-17). No firmware exists yet. Every finding is about the plan.

---

## Blocker

### B1. OpenDeck's device-plugin API can't express knob feel, haptics, pages or swipes
- **Assumption attacked:** "A clickdeck device plugin gives builders much of the Stream Deck plugin library … Knob feel needs clickdeck-specific settings on top" (plan.md:45-53). Also "check when writing the plugin" (protocol.md:170-171).
- **Evidence:** `openaction` 2.8.0 `device_plugin` has exactly nine calls: `register_device(id, name, rows, columns, encoders, type)`, `key_down/up`, `encoder_down/up`, `encoder_change(device, position, ticks: i16)`, `touchscreen_press(device, position, x, y, hold)`, `rerender_images`, `unregister_device`. Inbound, it gets only `SetImageEvent{device, controller, position, image}` and `SetBrightnessEvent` (https://docs.rs/openaction/latest/openaction/device_plugin/index.html, https://docs.rs/openaction/latest/openaction/global_events/struct.SetImageEvent.html). OpenDeck: "Only Elgato hardware is officially supported" (https://github.com/nekename/OpenDeck).
- **Failure scenario:** A volume action from a stock plugin gets ticks and nothing else. There is no channel to tell the device "24 detents, end stops at the current volume". The device's `position`/`velocity` (protocol.md:105) are thrown away, and swipes (protocol.md:107) have no API call. OpenDeck owns the profiles and pages, so the plugin never learns a page number to send `LAYOUT` (protocol.md:83). Knob feel ends up as a global setting with no link to the action, which drops the hard requirement (plan.md:9).
- **Cheapest test:** Write a 50-line `openaction` device plugin that registers a 7×3 device with 5 encoders. Log every inbound event while switching pages and using a volume plugin.
- **Fix:** [decision] Pick one: (a) the Python app is the primary host and OpenDeck is a "basic mode"; (b) a companion clickdeck action plugin whose property inspector sets knob feel, sharing state with the device plugin over IPC; (c) upstream an API change to OpenDeck. Say this in the README now.

### B2. Linux rejects the display device (and maybe the inputs device) behind a bus-powered hub
- **Assumption attacked:** The CH334F hub passes both devices through transparently (wiring.md:14-18).
- **Evidence:** For a non-self-powered hub, Linux sets `hub->mA_per_port = unit_load; /* 7.2.1 */`, where `unit_load` is 100 mA for USB 2.0 (drivers/usb/core/hub.c, `hub_configure`). Any configuration with `usb_get_max_power > bus_mA` is "rejected … due to insufficient available bus power" (drivers/usb/core/generic.c). Arduino-ESP32 defaults to `usb_power_ma(500)` (cores/esp32/USB.cpp:137). The CH334 family's self- or bus-powered mode is set by I/O pins or an EEPROM, and no doc sets it (grep finds no "self-power" or "bMaxPower" anywhere in docs/).
- **Failure scenario:** The display enumerates but is never configured, so no ttyACM appears. The prototype test (prototype-tests.md:53) uses an external, likely self-powered hub and passes. The full build then fails.
- **Cheapest test:** Put any Arduino-ESP32 TinyUSB board behind a cheap bus-powered hub and check `dmesg` for "rejected 1 configuration".
- **Fix:** [no-decision] Strap the CH334F as self-powered (it is fed from VBUS anyway, and the motor budget logic already handles power). Set bMaxPower ≤100 mA on both firmwares as a second layer. Add both to pcb.md and protocol.md.

## High

### H1. Offline, the keys lie and the screen goes dark
- **Assumption attacked:** "Without the host app the keys still work as a keyboard … and the display shows its last saved page" (protocol.md:161-166). Lesson #15 promises "page navigation works with no host" (lessons.md:128-129).
- **Evidence:** `HID_MAP` is a single map per key (protocol.md:137), but images are saved per page (protocol.md:83, 92). `KNOB_CONFIG` is "stored per page" (protocol.md:115), yet the inputs device has no page concept and no link to the display. Wake is relayed by the app (protocol.md:139-141), and only the inputs device has a `PING` timeout (protocol.md:31-33).
- **Failure scenario:** The app crashes on page 3. The keys show page-3 icons such as "OBS: Start Stream" but send the page-agnostic fallback shortcuts. Most plugin actions have no keyboard equivalent at all. After the idle timeout the display blanks, and no key or knob can wake it. Overlays (mic-muted) stay up until the display somehow learns the host is gone, which isn't specified for a hung app. Separately, if a key is held in HID mode when `HELLO` arrives, the OS never gets the key-up unless firmware sends an empty report first.
- **Cheapest test:** On the prototype, kill the host process mid-session and walk through the offline experience for 15 minutes.
- **Fix:** [decision] Fit the 3-wire J8 link (open-questions.md:46). Then offline mode is coherent: the inputs device owns the page and the HID_MAP per page, and wakes the display. Or the display shows a dedicated "keyboard mode" page whenever the host is absent. [no-decision] Add `PING`/timeout to the display device, and release all HID keys on every mode switch.

### H2. Throughput is about half the plan's figure, and full-page changes take seconds
- **Assumption attacked:** "CDC/bulk channel on the ESP32-S3 does ~1 MB/s (<50 ms per key)" (plan.md:36, 56-57).
- **Evidence:** Espressif FAQ: ESP USB "can reach 500 KB/s at the maximum"; a forum measurement reached ~530 KB/s with a large FIFO (https://docs.espressif.com/projects/esp-faq/en/latest/software-framework/peripherals/usb.html, https://esp32.com/viewtopic.php?p=100435). The arithmetic: a 146×146 RGB565 key is 42.6 KB, about 85 ms. A full 21-key page is 895 KB, about 1.8 s. A 1024×600 frame is 1.23 MB, about 2.5 s.
- **Failure scenario:** OpenDeck sends a fresh PNG data URL per position on every page change and every state change. Stock plugin art (gradients, photos, anti-aliased text) defeats RLE. Paging becomes a visible 1-2 s wipe, and live tiles (clock, CPU meter) eat the link.
- **Cheapest test:** On a bare 7B with Arduino TinyUSB CDC, stream 1 MB from pyserial and time it. Also decode 21 real plugin PNGs with RLE and with JPEG and compare sizes.
- **Fix:** [no-decision] Make JPEG the default for photo-like art, measure the on-device decode, and change the 50 ms pass test (prototype-tests.md:49) to "full page < 300 ms". [decision] Vendor bulk with MS OS 2.0/WinUSB descriptors from day one if CDC can't reach the target.

### H3. The flash image cache corrupts the RGB display
- **Assumption attacked:** "images persist in flash keyed by CRC32" (protocol.md:89-92), and `PAIR` and settings are also written to flash.
- **Evidence:** ESP-IDF RGB LCD docs say that with bounce buffers "the LCD CANNOT function if the external memory cache is disabled", and they name NVS/OTA writes. With a PSRAM frame buffer, sharing the SPI bus with flash leads "to display corruption". A DMA shortfall gives "a permanently shifted image". The docs recommend `CONFIG_SPIRAM_XIP_FROM_PSRAM` (https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/lcd/rgb_lcd.html).
- **Failure scenario:** Every cache-miss image write makes the 1024×600 panel flicker or shift permanently. A plugin that updates every second also wears the flash. There is no eviction policy, and 16 MB holds about 18 raw pages.
- **Cheapest test:** On the 7B, write 64 KB to flash in a loop while showing a static test pattern.
- **Fix:** [no-decision] Enable XIP-from-PSRAM and RGB restart-in-vsync (both need IDF-level sdkconfig, see M1). Write the cache only when the host says "persist", lazily and batched. Specify LRU eviction. Treat anything the host updates more than once a minute as an overlay.

## Medium

### M1. The toolchain choice can't set the sdkconfig H3 needs
- **Evidence:** plan.md:176 picks "PlatformIO + Arduino-ESP32 core". Arduino-ESP32 ships precompiled IDF libraries. Upstream PlatformIO `espressif32` has lagged Arduino 3.x, which is what the community `pioarduino` fork exists for, and SimpleFOC already broke on IDF 5.4 (lessons.md #7). Arduino on RP2350 needs earlephilhower's core via a third-party PlatformIO platform.
- **Fix:** [decision] Use ESP-IDF (with esp_tinyusb and esp_lcd) for the display, and Arduino-pico or pico-sdk for the inputs device. Pin both.

### M2. SimpleFOC with 5 motors on one SPI bus is untested at this scale
- **Evidence:** `MagneticSensorMT6701SSI::readRawAngleSSI` does a `beginTransaction` and a 16-bit transfer per read, discards the MT6701's status/CRC bits, and carries the comment "check 40us delay between each read?" (simplefoc/Arduino-FOC-drivers, src/encoders/mt6701). `syncSlices()` disables and resets every PWM slice each time a driver is initialised (Arduino-FOC rp2040_mcu.cpp:90-96), so motor 5's init glitches motors 1-4. Each RP2350 PWM channel appears on two GPIOs, and 15 channels plus 3 fixed ADC pins (wiring.md:259-260) constrain the pinout.
- **Failure:** A noisy SSI read without a CRC check gives a wrong angle, which produces a torque kick. The loop rate per motor is unknown.
- **Test:** On a Pico 2, run 5 `BLDCMotor` instances with fake loads and 5 SSI reads, and toggle a GPIO per loop. Pass: ≥5 kHz per motor with the USB stack active.
- **Fix:** [no-decision] Read 24-bit SSI frames and check the CRC. Put FOC on core 1 and USB/matrix/I²C on core 0. Initialise all drivers before enabling any motor. Do the pin-to-slice map in the schematic.

### M3. The brownout guard may trip constantly and ratchet the budget down
- **Evidence:** It trips at "below ~4.6 V … and lowers the budget" (wiring.md:135-137). On a default port the total load is ~1 A, more than its 500 mA (wiring.md:127-131), with cable, JST-GH contact and load-switch drops in series.
- **Fix:** [no-decision] Add hysteresis and recover the budget over time, log trips in `STATUS`, and add a "detents survive a weak port" test.

### M4. Unauthenticated reflash and keymap writes make it a BadUSB-ready keyboard
- **Evidence:** "Bootloaders stay unlocked" (plan.md:140). `REBOOT_BOOTLOADER` and `HID_MAP` need no authentication (protocol.md:137, 151). On Linux any user in `dialout` can open the port, and so can a browser through WebSerial once the user grants it.
- **Failure:** Malware rewrites the RP2350 into an arbitrary keystroke injector that survives reinstalling the OS.
- **Fix:** [decision] Require a physical confirmation (hold a knob press for 3 s) before `REBOOT_BOOTLOADER` or a `HID_MAP` change. Keep the bootloader open.

## Low

- **L1. Port probing.** Until PIDs are assigned, development PIDs (protocol.md:26-30) collide with every Pico/ESP32 board, so the app may send `0xCD` frames into MicroPython REPLs or printer boards. Fix [no-decision]: apply for PIDs before the first release, and probe only ports whose USB product string matches. The framing also has no resync rule when 0xCD appears in a payload: specify "on a CRC fail, scan for the next magic and drop bytes".
- **L2. Pairing races.** The RP2350 enumerates well before the ESP32-S3 has initialised its panel, and esptool's download mode re-enumerates as 303A:1001 with a new COM port. Fix [no-decision]: the app treats a half pair as "connecting", not as a new device, and keys pairing off the hub location first.
- **L3. Recovery access.** The RP2350's BOOTSEL button is inside the case. Fix [no-decision]: use the RP2350 bootrom's A/B partitions with try-before-you-buy so a bad UF2 rolls back, or add a pinhole.

## What I could not verify

- Whether the CH334F's default strap is self- or bus-powered, and whether it's MTT or STT (I didn't get the datasheet pin table).
- arduino-pico's default bMaxPower (fetch failed), and the ESP32-S3 ROM download mode's bMaxPower.
- Real 7B pixel clock and PSRAM headroom while USB and the decoder run.
- Whether OpenDeck renders Stream Deck+ `setFeedback` layouts into the encoder image, and whether a sibling action plugin can share state with a device plugin.
- Whether OpenDeck's plugin licence terms constrain an MIT device plugin. The plugins run as separate processes, so I expect not, but I didn't check.
- Real MT6701 SSI noise with 5 sensors on a shared bus next to motor phase wiring.
