# Open questions and risks

Things that are unverified or decided "for now". Each has how and when it
gets answered. Strike items through (or delete them) once answered, and
record the answer in the doc it affects.

Status: ❓ open · ⚠️ risk to watch · ✅ answered

## Answer before the knob board design

| | Question | How we answer it | Affects |
|---|---|---|---|
| ✅ | Is the 7B's 3-pin sensor connector GPIO6? **Yes**: J8 = 3V3, GND, GPIO6 (schematic, 2026-10-17). Now used by the optional one-wire link from the knob board (D5) | — | [wiring.md](wiring.md) |
| ✅ | Does the TMC6300 have built-in break-before-make, so one inverter can derive its low-side inputs (3-PWM plan A)? **Yes** (datasheet: "Internal break-before-make (BBM) logic ensures that no cross-conduction occurs"). Catch: in standby no input may be high, so the inverter is powered from the standby pin ([knob-module.md](knob-module.md)). Still verify: on the test kit with inverted PWM outputs, then on Rev A | — | Driver choice |
| ✅ | TMC6300 sourcing (D2). LCSC had 59 TMC6300-LA-T (C5274455) at $5.93 on 2026-10-17; DigiKey lists ~4,100 at ~$2.44. **Answer:** source it through JLC Global Sourcing or consign it from DigiKey; reserve the Rev A quantity (10 per build) in JLC's parts library once the test kit passes. Keep the DRV8316 fallback drawn | Check JLC stock right before each order | Driver choice, cost |
| ✅ | MT6701 package (D2). **Answer:** **MT6701CT-STD**, SOP-8 (JLC C3003196), not the QFN-16 MT6701QT. JLC's stock is separate from LCSC's | Confirm JLC stock on layout day; the package sets the magnet gap | Knob board, `params.py` |
| ❓ | Mitoot 2204's real bolt pattern, height and KV (sellers disagree) | Calipers when the motor arrives | Knob board holes, `params.py` |
| ✅ | ~~Can an RP2350B bootloader update reliably over the UART link from the ESP32-S3?~~ Not needed: the RP2350B now has its own USB connection through the internal hub and updates with its built-in UF2 bootloader (2026-10-17) | — | Knob board flashing ([plan.md](plan.md)) |
| ✅ | Can we read the PC's USB-C current offer? **Yes, now**: the 7B can't (fixed 5.1 kΩ CC pull-downs), but the external port moved to our USB board, whose CC lines go to two RP2350B ADC pins. Motor budget 500 mA / 1.0 A / 1.5 A for default / 1.5 A / 3 A ports, brownout guard kept ([wiring.md](wiring.md)) | — | Power budget |
| ⚠️ | Hub chip: **CH334F** (LCSC C5187527) 8,489 in stock, $0.63 (checked 2026-10-17). Its crystal-free mode isn't on by default on some packages, so the board fits a 12 MHz crystal (0 Ω link to try crystal-free). Still to confirm in its datasheet row: MTT and integrated terminations. Fallback: FE1.1s (C9359, SSOP-28, needs a 12 MHz crystal) | Check stock before ordering; datasheet; keep the FE1.1s footprint option in mind | USB board |
| ❓ | 2204 motor lead: length and plug. One listing mentions ~30 cm with a 3-pin servo-style (Futaba/JR, 2.54 mm) plug; the knob board has matching 1×3 headers. A 30 cm lead coils 6.6 mm high in the 11.1 mm under the panel | Measure length and diameter on arrival; if the plug differs, change the header (JLC fits it, still no soldering) | Knob board headers, `MOTOR_*` in `params.py` |
| ❓ | Where is the 7B's native USB-C port? The schematic confirms it's Type_C2 ("USB": Type_C2 → R65/R66 → U9 → GPIO19/20). The model puts it 36 mm from the board's back edge, from Waveshare's PCB view | Silkscreen on the real board, then close this | Display cable route |
| ❓ | Mid-mount USB-C socket (C2894902): LCSC lists it as SMD-only, so the through-hole shell legs the strain relief relies on are unverified. Also how far it sticks out past the board edge, footprint | Get the HC-TYPE-C-16P-CB1.6 drawing; adjust `USB_C_SOCKET`/the board edge so the face lines up with the inside of the back wall; if it has no real legs, pick a mid-mount part that does | USB board, strain relief |
| ⚠️ | B3U-1000P (LCSC C231329): 110,060 in stock at $0.19 (5+) with no lifecycle flag on 2026-10-17 (an older check saw "not recommended for new designs"). Operating force spreads 1.01–1.99 N. Same-size (3 × 2.5 mm) alternatives on LCSC: XKB TS-3025-B-A-B (C2885149, 160 gf, 1.5 mm tall), plus Hanxia, SAMZO, Zhongdi and G-Switch parts (2026-10-17) | Feel a few alternatives on the desk next to the rev C frame PCB's B3Us; check pad layouts | Key switches |
| ✅ | Real thickness of the 7B. **From Waveshare's STEP model**: panel 6.2 mm; the board sits on 2.5 mm bosses, with the frame back 3.7 mm behind the glass; the connector row 16.1 mm below the glass. The deepest part under the board is the microSD socket (5.0 mm). In the model the board sits 2.7 mm above the floor, with no floor pocket. The native USB-C port center is 1.22 mm below the board's underside: 12.8 mm above the case bottom, 9.0 mm below the glass | Confirm with calipers on a real board | Case (`params.py`) |
| ❓ | The only STEP is the touch SKU. The non-touch 31727 may have a bare polarizer instead of cover glass, so its front profile and `PANEL_T` are unmeasured. Which backlight dimming resistors are fitted is unknown. Waveshare revises boards | On the first 7B: measure `PANEL_T` and the front lip, probe EN/FB while sweeping brightness, record the silkscreen revision against the STEP. Buy two 7Bs if the budget allows | Key stack, case, brightness |

## Answered by the prototype (test kit) or first on Rev A

Pass/fail criteria for each are in [prototype-tests.md](prototype-tests.md).
Since 2026-10-18 the prototype is a test kit of bought breakouts plus the
rev C frame PCB; questions about our own boards (hinge, touch, CC sensing,
connectors) are first answered on Rev A.

| | Question | Affects |
|---|---|---|
| ⚠️ | Is the B3U's 0.15 mm travel a satisfying click, or too short? | Key switch choice |
| ⚠️ | Does a press anywhere on the cap, including the far corners, click cleanly? Does the cap slide freely in its 0.05 mm guide? One switch or two per key? | Cap, guide, tab, frame support and down-stop (D8) |
| ⚠️ | Is the 2204's cogging noticeable in smooth mode? | Motor choice (fallback: SparkFun ROB-20441) |
| ❓ | Knob current at rest, while clicking, at an end stop | Power budget numbers |
| ❓ | **Rev A.** Does the hinged tongue give a good press feel (force, travel, no wobble when turning), and does side force cause false clicks? | Hinge perforations and striker setting; parallel flexure if side force clicks (D10) |
| ❓ | **Rev A.** Does the touch band work through the printed plate, next to a running motor and a lit panel, with no false touches from a hand on a knob? With the AT42QT2120, is the interpolated position within ±5%? | Touch band design; knobs move forward if it fails (D11) |
| ❓ | How fast do images go over USB? (Plan on ~0.5 MB/s; target a full page < 300 ms) | Protocol (compression, framing) |
| ❓ | Can the RP2350B run 5 FOC loops at ≥ 2–5 kHz each? | Knob firmware |
| ❓ | Does the MT6701 breakout read all 14 bits over SSI on the RP2350B (SPI mode, last-bit clock edge, CRC)? See the notes in [parts.md](parts.md) | Sensor driver, knob board |
| ❓ | Does the motor fit and center on the stand's deck as on the knob board (bolt pattern, magnet gap)? The board's own fit is first checked on Rev A | `MOTOR_*` in `params.py` |
| ⚠️ | Rev A is the first build of the knob board, USB board and touch band. Which board needs its one planned revision? | [cost.md](cost.md) (single-board respin costs) |

## Answer before the full build

Cabling (new with the internal hub; [wiring.md](wiring.md)):

| | Question | How we answer it | Affects |
|---|---|---|---|
| ✅ | **Offline page switching (D5).** **Answer:** an HY2.0 footprint on the knob board now for a one-wire link to the 7B's GPIO6 (J8), fitting optional. It carries page switches, activity, the knob-hold confirmation and settings reset. Without the link and without a host, the display never idle-blanks | Test with a jumper from the core board to J8 (kit), then the HY2.0 lead on Rev A | [protocol.md](protocol.md), [wiring.md](wiring.md) |
| ❓ | Real USB-C plug sizes: the model uses 12.5 × 6.5 mm overmolds, 22 mm straight and 13 mm right-angle. The display end must be a side-exit (left/right) 90° plug, not up/down | Measure the cable that arrives; rerun `cad/assembly.py --check` with its sizes | Display cable, `USB_PLUG_*` |
| ❓ | Is a 100 mm USB-C cable really ~100 mm plug tip to plug tip? (Sellers measure differently.) The loop takes 95–110 mm | Measure | Display cable |
| ❓ | JST-GH carries 5 V on two 1 A contacts (26 AWG cable): knob board capped at ~1.8 A. Enough? | Prototype current measurements | Power budget |
| ✅ | Power on default 500 mA ports (D9). **Answer:** full haptics need a 1.5 A+ port over C-to-C; on default ports haptics are nearly off; ~0.8 A motor budget on 1.5 A ports until measured; optional PD sink footprint ([wiring.md](wiring.md)) | Measure real motor current on the test kit, then on Rev A | Power budget |
| ❓ | FFC contact side: type B (opposite sides) assumes top-contact ZIFs on both boards | ZIF datasheet | Key cable order |
| ❓ | One JLC panel means one board thickness, but the touch band was planned at 0.8 mm | Rev A: the band is 1.6 mm in the panel; if it can't sense through the plate, its one revision is ordered separately at 0.8 mm | Touch band, cost |
| ⚠️ | Extended-part fees: the whole panel has 19 extended part types after the basic/preferred swaps ($3.07 each per order at JLC; counted 2026-10-17, list in cost.md; was 24), not ~5. Cost isn't a design driver (D1), but [cost.md](cost.md) includes these and US import duty | Count from the BOM with JLC's BOM tool; get a real JLC cart quote with a US address | Cost |
| ✅ | Can the knob board be top-side only (D6)? **Yes, in the model:** each press switch sits on the top side of the fixed 5 mm front border and an arm on the printed motor spacer presses it (an M2×3 set screw in the arm is the striker); the drivers moved to the back strip, so only sensor traces cross the hinges. Still to pick: SMD right-angle motor headers (THT fallback) and a reverse-mount BOOTSEL tact switch (fallback: a plain one on the bottom, the only bottom part) | Floorplan with real footprints before the full order | Knob board, assembly cost ([pcb.md](pcb.md)) |

Everything else:

| | Question | How we answer it | Affects |
|---|---|---|---|
| ❓ | Is a full-screen redraw at 1024×600 fast enough on the ESP32-S3? | Test on a 7B board | Firmware design |
| ✅ | Touch band controller (D12). **Answer:** **AT42QT2120-SUR** (SOIC-20, LCSC C614938, $1.89, 69 in stock on 2026-10-17; extended part at JLC). The MPR121 is dropped (discontinued, NXP PCN16772). Its slider is only 3 channels, so all 12 channels run as keys and firmware interpolates the position | Check JLC stock on quote day; if it's gone, drop the touch band rather than pay for an alternative (`TOUCH_BAR = False` in `cad/params.py`) | Touch band PCB |
| ✅ | Host software (D4). **Answer:** a VIA-style web configurator (WebUSB/WebHID/Web Serial, Chromium) is the main tool, settings stored on the device; an optional daemon for live integrations. OpenDeck/Companion Satellite clients maybe later ([configurator.md](configurator.md)) | — | Host software |
| ❓ | Image throughput over the WebUSB vendor bulk interface on the 7B (plan ~0.5 MB/s) | Measure on the prototype | Protocol |
| ✅ | Display reflash confirmation without the GPIO6 link. **Answer (D17 changed):** no confirmation by default, so no pinhole. Only with the optional lock on and no link does a display-only reflash need the BOOT pinhole | — | [protocol.md](protocol.md), [recovery.md](recovery.md), [configurator.md](configurator.md) |
| ❓ | Case printing: does the stand print well on a home printer, and what does JLC3DP charge? | Slice the STLs; get a JLC3DP quote | Cost estimate |
| ❓ | Real costs: JLC quotes for the panelized PCBs with assembly | Upload the real Gerbers/BOM | Cost estimate |

## Lite tier (D22)

| | Question | How we answer it | Affects |
|---|---|---|---|
| ❓ | Encoder part: Bourns PEC11R-4215F-S0024 (C143790, 5,485 in JLC stock) detented / PEC11R-4015F-S0024 (C143789, 3,748) smooth, 2026-10-19. Body height (6.5 mm), shaft length (15 mm) and flat (7 mm) are from the Bourns drawing; tolerance ±0.3/±0.5 mm moves the knob | Buy a few of each with the next AliExpress/LCSC order; calipers; set `ENC_*` in `cad/params.py` and rerun `assembly.py --check` | Lite knob height, `knob_lite.stl` |
| ❓ | Knob height: the lite knob seats on the shaft tip, 1 mm above the plate, 0.5 mm when pressed. Is that enough with a real part, and does the stem through the 11 mm hub hole wobble or rub? | Print `knob_lite.stl` on a real encoder under a plate offcut | Lite knob, plate hole (shared) |
| ❓ | Does JLC fit the through-hole encoders under Economic assembly at the quoted ~$0.0173 per joint, and trim the leads to ≤ 1.2 mm (2 mm under the board to the floor)? | JLC quote with the lite BOM; ask about lead trimming | Lite cost, tray clearance |
| ❓ | Encoder feel: the PEC11R's 24 detents and 0.5 mm, ~6 N push. Is the press too stiff next to the B3U keys? An Alps EC11 (e.g. EC11E15244B2, C470754, 30 detents; V: push switch, press force) is the alternative | Feel both on the desk | Lite encoder choice |
| ❓ | SMD option: Alps EC11J1525402 (C209762, 1,666 in stock) has a push switch but only with detents; no stocked SMD part without detents. Worth a second footprint? | Only if THT assembly is a problem on the quote | Lite board |
| ❓ | PIO quadrature with the RC filter (10 kΩ, 10 nF): no missed steps when spun fast, no bounce at the detents | WeAct RP2350B bench with an EC11 on a breadboard | Lite firmware |

## Decided for now, revisit later

- **21 keys (7×3).** 24 keys (8×3) fit on the same board; 32 needs a bigger
  single shared panel. Separate screens for keys or knobs are out (D19).
- **IPS LCD, not OLED.** OLED looks better under clear caps but static icons
  risk burn-in. Could be trialled later with a small OLED test screen.
- **Internal USB hub instead of a UART link** (decided 2026-10-17): the
  RP2350B and ESP32-S3 each get their own USB connection, so there's no
  custom bootloader and no hand-made leads. Cost: the software pairs two
  devices, and the chips only reach each other through the host or the
  optional GPIO6 link. Confirmed by the owner (D7).
- **Printed knobs (`KNOB_STYLE = "integrated"`).** The `shaft_adapter`
  style takes any 6 mm D-shaft knob.

## Owner decisions from the design review (answered 2026-10-17)

Options are in [design-review.md](design-review.md). ✅ All answered:

- ✅ D1 cost: not a design driver; numbers include import duty; a single
  build costs more than a + XL; get a real JLC quote ([cost.md](cost.md))
- ✅ D2 sourcing: MT6701CT SOP-8; TMC6300 via JLC Global Sourcing/DigiKey;
  reserve stock after the test kit passes
- ✅ D3 prototype (changed 2026-10-18): final parts bought early (7B, 6
  motors, magnets, cable); a throwaway test kit (SparkFun TMC6300 and
  MT6701 breakouts on a printed stand, WeAct RP2350B + CH334F module, the
  rev C frame PCB with 2 + 2 caps); Rev A is the first build of our own
  boards, with one single-board revision planned. Rev 0 and Rev 0.5
  dropped ([parts.md](parts.md))
- ✅ D4 software: web configurator first, optional daemon
  ([configurator.md](configurator.md))
- ✅ D5 offline pages: GPIO6 link footprint, optional fit; no idle blanking
  without a host
- ✅ D6 assembly: top-side only; shown feasible in the model (press switch on
  the front border, pressed by the motor spacer's arm)
- ✅ D7 internal hub: kept
- ✅ D8 key support (resolved 2026-10-18): 14 M2 frame screws (5 pan-head,
  9 countersunk), cap down-stop at 0.5 mm travel, 0.8 mm gap to the glass,
  0.1/0.2 mm shims; caps guided straight by the plate (no rocker, hinged or
  tilting caps); a second switch per key stays an option, with its
  footprint on the prototype, decided by the force test ([plan.md](plan.md))
- ✅ D9 power: 1.5 A+ C-to-C for full haptics ([wiring.md](wiring.md))
- ✅ D10 hinge: scrap-FR-4 test, tunable hinge + set-screw striker, parallel
  flexure if needed ([knob-module.md](knob-module.md))
- ✅ D11 touch vs motors: guard + hatch + 300 ms lockout, realistic test,
  move the knobs only if it fails
- ✅ D12 touch controller: AT42QT2120 (above)
- ✅ D13 toolchains: ESP-IDF 5.x for the display; pinned arduino-pico +
  SimpleFOC for the RP2350B
- ✅ D14 case: M3 heat-set inserts (4.0 mm hole × 5.7 mm) in 8 mm plate
  posts, M3×6 screws, PETG
- ✅ D15 look: one standard clear cap finish for now; revisit after seeing it
- ✅ D16 floorplan: drivers off the tongue (on the back strip next to each
  motor header), real-footprint floorplan first; no shunts on the knob board
  (Rev 0 was dropped; current is measured on the test kit)
- ✅ D17 security (changed 2026-10-18): VIA-style trust, the browser's device
  picker is the confirmation; optional on-device lock brings back the 3 s
  knob hold for reflash or keymap changes
- ✅ D18 updates: no OTA slots; the configurator flashes through each
  chip's ROM bootloader ([recovery.md](recovery.md))
- ✅ D19 displays (2026-10-18): one shared panel only; no screens per key or
  on the knobs
- ✅ D20 haptics (2026-10-18): core knob feel first; attention nudges and
  haptic notifications are an optional firmware module, off by default
- ✅ D21 look (2026-10-18): clickdeck's own look; comparisons with the + XL
  are fine
- ✅ D22 tiers (2026-10-19): a lite knob board with push encoders next to
  the haptic flagship; everything else shared; the display stays the 7B
