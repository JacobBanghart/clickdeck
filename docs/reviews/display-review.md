# Display integration review: Waveshare ESP32-S3-LCD-7B

Reviewer: senior HW/FW design review (standard, not red-team), 2026-10-17. I used the repo plus Waveshare's schematic, drawing and STEP (`ESP32-S3-Touch-LCD-7B_Drawing.zip`, dated 2025-10-25), which I probed in build123d. `cad/assembly.py --check` passes (0 problems).

## Verdict

**Go with changes.** The board is the right choice and most of the mechanical numbers match Waveshare's STEP file.
Two things should be fixed before ordering: the panel screws are too long for the space behind the M3 tabs, and the plan to store images in flash will cause RGB "drift" on the ESP32-S3.
Buy one 7B now and test it, because the 2.4" SPI prototype tests none of the 7B-specific risks.

## Strengths

- **Board choice.** The 7B costs $33.99 and is current at Waveshare (SKU 31727, no touch). It has an N16R8 module, a native USB-C port and dimmable backlight, and it beats building an RGB panel driver from scratch. Dimming works because the schematic shows the AP3032 backlight driver's EN pin reachable from the CH32V003 `EXIO_PWM` output.
- **Clean split of roles.** The ESP32-S3 only draws the screen, and each chip gets its own USB connection through the hub ([plan.md:86-89](../plan.md)). Wi-Fi and BT can stay off.
- **Depths and mounting points mostly match the STEP:**
  - Board face 6.2 mm below the glass, and the connector row 16.1 mm below it.
  - M3 tabs 126.2 mm apart, 18.31/13.64 mm from the frame edges. The tab holes are Ø2.5 mm, consistent with tapped M3.
  - The native port really is the one 35.7 mm from the back edge. Waveshare's PCB view labels Type_C2 "USB", nearer the BOOT/RESET edge, so open-questions.md:379 can be closed.
- **USB-C power handling.** CC handling is correct. The 7B has fixed 5.1 kΩ pull-downs and the hub port has 56 kΩ pull-ups ([wiring.md:258-283](../wiring.md)).
- **Protocol design.** Caching images by CRC, RLE, the device reporting key size in pixels, and keeping overlays in RAM are good choices.

## Issues

### High

**H1. Panel screws hit the panel's back sheet.** [no-decision]
- *Evidence:* Each screw is sized to reach 2.5 mm past the tab face ([model.py:834](../../cad/model.py)), which rounds up to M3x14 ([assembly.md:31](../assembly.md)).
  - The head seats at z = 2.3, so the tip ends at 16.3, which is 2.95 mm past the tab face (z 13.35).
  - In the STEP, the tab face is at Y = -7.7 and the frame's main back sheet is at Y = -5.2, only 2.5 mm above it. The thread engagement is about 1.7 mm.
  - So each screw goes about 0.45 mm into the back of the LCD. That bows the frame and the backlight, causing pressure marks or a cracked LGP.
  - The overlap check misses this because the screw counts as threading into its target part.
- *Recommendation:* Size the screws so the tip ends 1.6-2.2 mm past the tab face. For example, use M3x12 and raise the counterbore floor by about 1 mm, or change the post height. Add a check that screw tips stay clear of the panel's back sheet.

**H2. Writing images to flash will make the RGB panel drift, and the planned toolchain can't fix it.** [decision]
- *Evidence:*
  - [protocol.md:89-93](../protocol.md) writes every new image and page to flash.
  - Espressif's LCD FAQ says flash writes disable PSRAM access, and the panel shifts unless code runs from PSRAM (XIP) and bounce buffers are used. A PCLK too high for PSRAM bandwidth causes the same drift. ([esp-faq LCD](https://docs.espressif.com/projects/esp-faq/en/latest/software-framework/peripherals/lcd.html))
  - Waveshare's own Arduino setup needs a patched "esp32-XIP-3.1.1" core, plus 120 MHz octal PSRAM and 120 MHz QIO flash ([wiki](https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-7B)).
  - [plan.md:176](../plan.md) assumes stock PlatformIO + Arduino-ESP32.
- *Recommendation:* Decide on ESP-IDF 5.x for the display firmware (or Arduino as an IDF component), with:
  - `SPIRAM_XIP_FROM_PSRAM` and a bounce buffer of 10 lines or more
  - PCLK at 30 MHz or below
  - `LCD_RGB_RESTART_IN_VSYNC` as a backstop

  Use plain `esp_lcd` blits; LVGL isn't needed for blitting tiles. Batch flash writes after a page upload finishes.

**H3. The prototype tests nothing about the 7B.** [decision]
- *Evidence:* The prototype uses an N16R8 devkit and a 2.4" SPI screen ([parts.md:13-14](../parts.md)). The 1024×600 redraw speed is deferred to the full build ([open-questions.md:416](../open-questions.md)), and prototype-tests.md has no 7B tests.
- *What goes untested:* RGB/PSRAM drift while flash is written and USB traffic is streaming, the EXIO5 USB/CAN mux, PWM dimming through the CH32V003, CDC throughput while the panel is scanning, heat, and fit.
- *Recommendation:* Buy the 7B with the prototype order (about $34) and add a "7B bring-up" section to prototype-tests.md (see Actions).

**H4. Caps and the frame PCB sit only 0.2 mm above the glass.** [decision]
- *Evidence:* `GLASS_GAP = 0.2` ([params.py:31](../../cad/params.py)). That gap is smaller than the stacked tolerances:
  - printed post height: ±0.2 mm
  - PCB thickness: ±0.16 mm
  - glass-to-tab distance: unverified
  - cap tilt at the far corner when pressed
- *Risk:* A resin cap or the PCB pressing on the glass causes mura or scratches.
- *Recommendation:* Use 0.5-0.8 mm, or add printed spacers/shims, and accept the small extra parallax. Check the gap with feeler gauges on the first build.

### Medium

**M1. The EXIO5 USB/CAN mux is not documented anywhere in the repo.** [no-decision]
- *Evidence:* The schematic shows an FSUSB42 (U9) switching GPIO19/20 between the native USB-C port and the CAN transceiver, controlled by USB_SEL (EXIO5) on the CH32V003. The wiki says "low = USB". wiring.md:256-268 doesn't mention it.
- *Risk:* Recovery with BOOT through the pinhole only works over the native port, because the UART port isn't cabled. Resetting the ESP32 doesn't reset the CH32V003, so a bad USB_SEL state survives a pinhole reset.
- *Recommendation:* Document that firmware must never drive EXIO5 high, and that recovery is "unplug, hold BOOT, plug in". Test ROM download over the native port on the real board.

**M2. The USB port height and board offset in `params.py` disagree with the STEP.** [no-decision]
- *Evidence* ([params.py:49-60](../../cad/params.py)):
  - Port center: the STEP puts it 1.22 mm below the board underside, not `USB_BELOW_PCB = 2.97`. That value was apparently measured from the board's top face, so the modeled port and plug sit 1.75 mm too deep, and "USB-C 12.8 mm below the glass" ([open-questions.md:382](../open-questions.md)) is really 11.05 mm.
  - `DISPLAY_PCB_LEFT`: 26.0 mm in the STEP, not 27.2.
  - `DISPLAY_PCB_BACK`: 0.2 mm in the STEP, not 0.5.
- *Effect:* The display-cable loop, the clip heights and the bay width are checked against the wrong geometry.
- *Recommendation:* Correct the values and rerun `--check`.

**M3. The floor pocket is in the wrong place.** [no-decision]
- *Evidence:* The model centers the six-connector row 40 mm from the back edge and makes it 44 mm long ([model.py:639](../../cad/model.py)), so the pocket covers 17-63 mm from the back edge. In the STEP the row runs 23.3-70.1 mm.
- *Effect:* The H3 connector's last ~7 mm has no pocket under it, leaving only 0.45 mm of clearance to the floor (conn_bot 3.45 vs floor 3.0).
- *Recommendation:* Use center 46.7 mm and length 47 mm.

**M4. The BOOT/RESET pinholes are marginal.** [no-decision]
- *Evidence:*
  - The STEP buttons sit 59.2/48.1 mm from the board's USB edge, against 58.4/47.5 (EST) in [params.py:156](../../cad/params.py). Together with the 1.2 mm board-offset error, the x error is 0.4-0.6 mm.
  - Hole height: `pin_z = dpcb_bot - 1.0`, but the real button center is 0.3 mm below the underside, so the model is 0.7 mm low.
  - The holes are Ø2 mm, with about 8 mm of unguided travel behind the wall.
- *Recommendation:* Use the STEP numbers. Make the holes Ø3 mm or slots, or add a printed guide tube.

**M5. Heat is unassessed.** [no-decision]
- *Evidence:* The board alone draws about 1.75 W (350 mA at 5 V), sealed under the panel in a printed tray next to the motor drivers. The rated range is 0-65 °C. Espressif treats 120 MHz octal PSRAM as experimental and temperature-sensitive.
- *Recommendation:* Log the board temperature at full brightness in the closed case for 2 hours. If it runs hot, use 80 MHz PSRAM. Use PETG/ASA rather than PLA for the tray.

**M6. The image throughput figure is optimistic.** [no-decision]
- *Evidence:* "~1 MB/s, <50 ms per key" ([plan.md:56-57](../plan.md)). TinyUSB CDC on a full-speed S3, behind a shared hub, with the panel scanning, usually gets 0.5-0.9 MB/s.
- *Effect:* One raw 146×146 RGB565 key is 42.6 KB, which takes 50-85 ms. A first sync of a full raw page (0.9 MB) takes 1-2 s.
- *Recommendation:* Keep RLE/JPEG as the default and measure on the 7B.

### Low

- **L1. Documentation errors.** [no-decision]
  - The board is not "screwed flat on the frame". It sits on 2.5 mm bosses, and the frame back is only 3.7 mm behind the glass.
  - "Deepest part: USB-C" is wrong. The deepest part is the microSD socket, 5.0 mm (the value is right, the label isn't).
  - VBUS doesn't go "straight" to 5 V. It goes through a P-FET ideal-diode OR stage (Q5) ([wiring.md:258](../wiring.md)).
  - "~146 px per key" is the key pitch. The visible area under an 18 mm cap is about 120 px.
- **L2. The brightness command isn't documented.** The CH32V003 expander runs Waveshare firmware, and the wiki gives no brightness command. Take it from Waveshare's demo code, and check the PWM frequency for flicker or audible whine. [no-decision]
- **L3. Single source, and the board may be revised.** Port and button positions are tied to one PCB revision; Waveshare has revised similar boards before (the 4" needed a Rev 3). Buy two boards, and record the revision/date silkscreen against the STEP. [decision]

## Missing

- A 7B bring-up test plan with pass/fail numbers, covering drift, throughput, dimming, recovery and heat.
- Any mention of USB_SEL/EXIO5, or of the XIP-PSRAM/bounce-buffer sdkconfig.
- A screw-tip clearance check in `assembly.py`, plus a written tolerance stack for the glass gap.
- A firmware memory plan:
  - a 1.2 MB framebuffer, or 2.4 MB double-buffered, in PSRAM
  - SRAM for the bounce buffer next to the TinyUSB buffers
  - a partition layout for the image cache in flash
- A plan for idle blanking that turns off both the backlight and the RGB scan, to save power and heat.

## Actions before ordering (in order)

1. Fix the panel screw length and add the tip-clearance check (H1).
2. Correct `USB_BELOW_PCB`, `DISPLAY_PCB_LEFT/BACK`, the connector-row position and the button positions from the STEP. Enlarge the pinholes, then rerun `assembly.py --check` (M2-M4).
3. Raise `GLASS_GAP` or add shims, and write down the tolerance stack (H4).
4. Buy a 7B now, ideally two, and run these bring-up tests:
   - a 1024×600 full-screen blit at 30 MHz PCLK, while USB CDC streams and flash is being written, with no drift allowed
   - key-image time over CDC through a CH334F-class hub
   - PWM dimming 0-100%
   - ROM recovery over the native port with BOOT held
   - default state of EXIO5
   - 2-hour temperature at full brightness in a closed box
   - measuring the ports, buttons and tabs with calipers against the STEP
5. Decide the display firmware toolchain (ESP-IDF with XIP-PSRAM) and pin it in CI (H2).
6. Update wiring.md, open-questions.md and plan.md with the corrected facts (L1, M1, M6).
