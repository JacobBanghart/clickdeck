# Display integration: adversarial review

**Summary**
1. The LCD will act as the backstop for the whole key matrix. The frame PCB is held only along its back and left edges, and it and the caps sit 0.2 mm above the glass, so every key press pushes on the panel.
2. The M3x14 panel screws reach about 0.45 mm past the tab's threaded boss and into the LCD module's back plate (Waveshare STEP). Storing images to flash, as protocol.md plans, stops the RGB LCD while the flash is written, according to ESP-IDF's own docs.
3. The depths taken from the STEP model mostly check out against the file. The weak points are mechanical loading, screw length, and firmware/flash interaction, not the dimensions themselves.

Sources: Waveshare schematic (https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-7B/ESP32-S3-Touch-LCD-7B-Schematic.pdf), drawing and STEP `ESP32-S3-Touch-LCD-7B-20251025` (from the wiki zip), ESP-IDF RGB LCD docs (https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/lcd/rgb_lcd.html), and the Waveshare wiki (https://docs.waveshare.com/ESP32-S3-Touch-LCD-7B).

---

## Blocker

### B1. The LCD glass is the structural support for 21 keys
- **Assumption attacked:** the frame PCB "hangs from the top plate" and stays 0.2 mm off the glass (`cad/params.py:31` `GLASS_GAP = 0.2`). Cap bottoms sit at the same height (`cad/model.py:139` `cap_bot = st.pcb_bot`).
- **Evidence:**
  - The frame PCB screws are only at the back edge (y = py1+2.5) and the left edge (`cad/model.py:651-655`, "only where there's no glass under the head"). The right and front edges are free.
  - The front-row switch is at y ≈ −23 mm, about 71 mm from the back screw line. The far-right key is about 148 mm from the left screws.
  - Cantilever estimate for one 3.6 × 1.6 mm FR-4 web (E ≈ 20 GPa, I ≈ 1.2 mm⁴): F = 1.5 N (B3U actuation force) over 70 mm gives δ ≈ FL³/3EI ≈ 7 mm. Even if every web in the lattice shares the load, deflection is still in the mm range, far beyond 0.2 mm.
  - Behind the glass the LCD is not backed. In the STEP model, the module's back plate is at y = −5.2 and the bracket floor at −7.2, a 2 mm void, and the bracket only touches the posts at the four tabs.
  - Stack tolerances also exceed 0.2 mm before any load: PCB 1.6 ± 0.16 mm, FDM post height ±0.1–0.2 mm, B3U height, and plate post height.
- **Failure scenario:** every press, and every far-corner press of a tilting cap, bottoms out on the polarizer. IPS ripple or pooling appears under the key on each press. Over time this leaves pressure mura, polarizer scuffs from the cap edges, and, in the worst case, cracked glass when someone slaps a key. Clicks feel mushy because the glass, not the B3U, sets the end of travel. Nominal tolerances alone may already preload the panel when the case is closed.
- **Cheapest test:** on the prototype, put a 0.2 mm feeler gauge (or carbon paper) between the frame PCB and the 2.4" glass, press the front-right key with about 10 N, and look for marking or ripple. Alternatively, run FEA or hang a 1 kg weight on a frame-PCB offcut.
- **Fix [decision]:** support the frame PCB in the middle of its span. For example, add printed ribs or posts from the tray up through the gaps between the panel and the board edges along the front and right, so they reach the frame PCB's border. Or switch to a stiffer frame (aluminium, or a 2.0 mm PCB with a steel stiffener). Also give the caps a hard stop on the top plate or the frame, not on the glass, and raise `GLASS_GAP` to at least 0.8 mm. More gap means more parallax, which is the trade-off.

## High

### H1. The panel screws run into the LCD's back plate
- **Assumption attacked:** M3x14 machine screws "thread into the display's metal tabs" (`docs/assembly.md:31,229`). Screw length comes from `std_length(panel_z0 + 2.5 - cb)` (`cad/model.py:834`).
- **Evidence:** in the STEP model, each tab is 0.5 mm sheet (y −7.7 to −7.2). On its inner side sits a clinched boss, Ø3.5 mm with a Ø2.5 mm bore (M3 tap size), whose top is at y = −6.0. So the tabs are threaded, with about 1.7 mm of engagement. The LCD module's back is at y = −5.2. The model puts the screw head at z = 2.3 with length 14, so the tip is at z = 16.3, which is 2.95 mm above the tab underside, at y ≈ −4.75. That is 0.45 mm past the LCD back. Even the unrounded target of +2.5 mm just touches it.
- **Failure scenario:** the screw tip either stops on the backlight's back plate before the head seats, leaving the panel loose and rattling, or keeps going and dents the light-guide stack. The dent shows as a bright or dark spot near each corner. The assembly check doesn't catch it because the panel is modeled as a solid box that the screw is meant to enter.
- **Cheapest test:** on the real board, put a depth gauge or a pin through a tab hole from below and measure to the first hard surface. It should read about 2.5 mm.
- **Fix [no-decision]:** pick the length so the tip ends inside the boss (≤ 1.6 mm above the tab underside). With the current 2.3 mm counterbore that means M3x12 (tip at +0.95 mm, under 2 threads engaged). Better: make the counterbore 1.0 mm shallower and use M3x12 for about +1.95 mm. Add a "screw tip vs. target's far side" check to `assembly.py`.

### H2. Saving images to flash stops the LCD
- **Assumption attacked:** "images persist in flash keyed by CRC32" (`docs/protocol.md:369-372`), with pages and settings also stored in flash (`docs/protocol.md:423`).
- **Evidence:** ESP-IDF RGB LCD docs: "the LCD **CANNOT** function if the external memory cache is disabled, such as during OTA or NVS writes to the main flash." They also say a missed bounce-buffer switch "results in a screen shift" that can stay.
- **Failure scenario:** every page upload or new icon writes to flash. The display shows glitches, a permanent horizontal shift until reboot, or flicker during each sector erase (tens of ms each). The `DISPLAY` brightness setting is also persisted, so it triggers this too.
- **Cheapest test:** on a 7B, run Waveshare's RGB demo while a loop writes NVS. Watch for shift or flicker.
- **Fix [no-decision]:** framebuffer in PSRAM, bounce buffers in internal SRAM, and `CONFIG_SPIRAM_XIP_FROM_PSRAM` (which ESP-IDF recommends). Batch flash writes and do them while the screen is blanked or idle. Keep the image cache in PSRAM and write to flash lazily.

## Medium

### M1. Full-screen updates and redraw speed
- **Assumption attacked:** ~1 MB/s USB and "fine for mostly static images" (`docs/plan.md:57,86-89`).
- **Evidence:** one 1024×600 RGB565 frame is 1.23 MB. RGB scanout at about 30 MHz PCLK reads about 60 MB/s from octal PSRAM, and CPU drawing competes for the same bus. ESP-IDF warns "a high pixel clock might cause LCD peripheral starvation, leading to display corruption." TinyUSB CDC at full speed realistically moves about 0.6–0.9 MB/s.
- **Failure scenario:** a raw full-screen update (wallpaper, page change with non-RLE art) takes about 1.5–2 s. Animated or live keys plus JPEG decode cause tearing unless two framebuffers are used (2.5 MB of the 8 MB PSRAM).
- **Cheapest test:** the open-questions redraw test, plus a measurement of CDC throughput on the 7B.
- **Fix [no-decision]:** `num_fbs = 2` with VSYNC swaps, dirty-rect only, and JPEG for photographic art. Specify the target as fps per key, not per screen.

### M2. The STEP depths come from the touch SKU
- **Assumption attacked:** "depths taken from Waveshare's STEP model" (`cad/params.py:39`).
- **Evidence:** the only STEP in the zip is `ESP32-S3-Touch-LCD-7B`. Its drawing says "TP+LCD=5.00", with a 193×110.8 lens on top. I traced the repo's 6.2 mm to the LCD module's top face at y = −1.5, which is under the touch stack, so for a bare module it is internally consistent. But the non-touch SKU 31727 may use a different module front, for example a metal bezel lip. On the touch model, the polarizer is 0.15 mm below the rim.
- **Failure scenario:** any front lip above about 0.2 mm runs straight into the frame PCB (see B1).
- **Cheapest test:** calipers from the tab underside to the highest point of the front of a 31727.
- **Fix [no-decision]:** measure, then set `PANEL_T`.

### M3. Backlight dimming depends on unknown resistor population and the expander firmware
- **Assumption attacked:** "CH32V003 with a PWM output for the backlight" (`docs/wiring.md:88-89`).
- **Evidence:** the schematic's dashed optional block offers two routes:
  - EXIO_PWM → R52 "NC/0R" → AP3032 EN, which is PWM on enable.
  - EXIO_PWM → R49 "0R/NC" + R50 "10k/NC" + C34 "100NF/NC" + R51 "68K/NC" → AP3032 FB, which is analog dimming by injecting a filtered PWM into the feedback node.

  EN is also DISP/EXIO2, with R21 "4.7K/NC" as a pull-up to 5 V. Which parts are fitted on SKU 31727 is not shown. The LED current is about 78 mA (0.2 V across 5.1 Ω ∥ 5.1 Ω).
- **Failure scenario:** with FB injection, the range may not reach dark, and brightness drifts with the CH32's 3V3. PWM frequency and resolution are fixed by Waveshare's closed CH32 firmware. If R21 is fitted, the backlight comes on full at power-up before the ESP32 runs.
- **Cheapest test:** sweep brightness on a 31727 and probe TP3 and EN.
- **Fix [no-decision]:** confirm and document. If EN is PWM, set "brightness 0" to switch DISP off.

### M4. BOOT/RESET pinholes are placed from a photo, and may push the wrong way
- **Assumption attacked:** `DISPLAY_BUTTONS` "EST from photo" (`cad/params.py:155-156`). The pinholes sit 1 mm below the board underside and push horizontally (`cad/model.py:784-787`).
- **Evidence:** the drawing shows small parts on the board's back edge, but neither the drawing nor the STEP clearly gives the buttons' positions or which way they press. If they are top-actuated SMD tact switches, a paperclip pushed horizontally can't press them. The wall is about 8.5 mm from the board edge.
- **Failure scenario:** the firmware can't be recovered without opening the case. That matters because a bad build can also drive USB_SEL (EXIO5) high, which switches native USB to CAN through FSUSB42 U9.
- **Cheapest test:** photograph the board edge and press the buttons with a paperclip horizontally.
- **Fix [no-decision]:** measure. If they are top-actuated, add a printed lever or a removable floor plug.

## Low

### L1. The display board's power path isn't "straight to 5 V"
`docs/wiring.md:80-81` says VBUS goes straight to the 5 V rail. The schematic shows Type_C2 VBUS passing through an AO3401 with an MMBT3906 pair (an ideal-diode OR with the UART port), and a CS8501 battery boost. This is harmless, but the wording is wrong. **[no-decision]** Fix the doc.

### L2. Which port is native: half answered
The schematic shows Type_C2 → USBH → R65/R66 → U9 HSD1 → GPIO19/20, and Type_C1 → CH343P. U9's SEL has a 10 kΩ pull-down (R117), so it defaults to USB. The physical location of each port still needs the silkscreen. **[no-decision]**

### L3. Orientation
The FPC (thick border) faces the knobs, which matches the drawing. The scan direction is set by resistor options on L/R and U/D (J1 pins 39/40), not in software. The host can pre-rotate images at no cost, so this is low risk. **[no-decision]** Report rotation in `HELLO_ACK`.

### L4. Thermal and ESD
The board draws about 1.75 W (350 mA at 5 V) in a sealed, unvented case, with the board facing down 3 mm above the floor. The cap gaps (0.2 mm) give an ESD path to the bezel and bracket. **[no-decision]** Log the temperature after 2 h on the first build, and do a 4 kV contact test on a cap edge.

---

## What I could not verify
- Which parts are fitted for the backlight options, and the CH32V003 register map, on SKU 31727.
- The non-touch module's front profile and thickness. Only the touch STEP and drawing exist.
- BOOT/RESET part type, actuation direction, and position. They are not identifiable in the STEP.
- Which physical USB-C port is Type_C2, and the board revision printed on current stock.
- Waveshare's default PCLK, and real CDC throughput on this board. My deflection figure is a hand estimate, not FEA.
