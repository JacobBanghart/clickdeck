# Open questions and risks

Things that are unverified or decided "for now". Each has how and when it
gets answered. Strike items through (or delete them) once answered, and
record the answer in the doc it affects.

Status: ❓ open · ⚠️ risk to watch · ✅ answered

## Answer before the knob board design

| | Question | How we answer it | Affects |
|---|---|---|---|
| ✅ | Is the 7B's 3-pin sensor connector GPIO6? **Yes**: J8 = 3V3, GND, GPIO6 (schematic, 2026-10-17). No longer used (the internal UART link and reset line are gone) | — | [wiring.md](wiring.md) |
| ✅ | Does the TMC6300 have built-in break-before-make, so one inverter can derive its low-side inputs (3-PWM plan A)? **Yes** (datasheet: "Internal break-before-make (BBM) logic ensures that no cross-conduction occurs"). Catch: in standby no input may be high, so the inverter is powered from the standby pin ([knob-module.md](knob-module.md)). Still verify on the Rev 0 module | — | Driver choice |
| ⚠️ | TMC6300 stock and price. Checked 2026-10-17: TMC6300-LA (C5196961) out of stock; **TMC6300-LA-T (C5274455) 59 in stock at LCSC, $5.93 each ($5.12 at 10+)**; DigiKey lists ~4,100 at ~$2.44. One build uses 10 (JLC assembles 2 boards). Where to source it: owner decision D2 in [design-review.md](design-review.md) | Check JLC stock right before each order. Keep the DRV8316 fallback drawn (needs 4.5 V min) | Driver choice, cost |
| ⚠️ | MT6701 stock and package. The SOP-8 part is **MT6701CT-STD** (JLC C3003196); the MT6701QT (C2913974) is a 3×3 QFN-16 and was out of stock at LCSC on 2026-10-17. JLC's stock is separate from LCSC's. Second source: owner decision D2 | Search JLC's parts library on layout day and draw the package it stocks; the package sets the magnet gap | Knob board, `params.py` |
| ❓ | Mitoot 2204's real bolt pattern, height and KV (sellers disagree) | Calipers when the motor arrives | Knob board holes, `params.py` |
| ✅ | ~~Can an RP2350B bootloader update reliably over the UART link from the ESP32-S3?~~ Not needed: the RP2350B now has its own USB connection through the internal hub and updates with its built-in UF2 bootloader (2026-10-17) | — | Knob board flashing ([plan.md](plan.md)) |
| ✅ | Can we read the PC's USB-C current offer? **Yes, now**: the 7B can't (fixed 5.1 kΩ CC pull-downs), but the external port moved to our USB board, whose CC lines go to two RP2350B ADC pins. Motor budget 500 mA / 1.0 A / 1.5 A for default / 1.5 A / 3 A ports, brownout guard kept ([wiring.md](wiring.md)) | — | Power budget |
| ⚠️ | Hub chip: **CH334F** (LCSC C5187527) 8,489 in stock, $0.63 (checked 2026-10-17). Its crystal-free mode isn't on by default on some packages, so the board fits a 12 MHz crystal (0 Ω link to try crystal-free). Still to confirm in its datasheet row: MTT and integrated terminations. Fallback: FE1.1s (C9359, SSOP-28, needs a 12 MHz crystal) | Check stock before ordering; datasheet; keep the FE1.1s footprint option in mind | USB board |
| ❓ | 2204 motor lead: length and plug. One listing mentions ~30 cm with a 3-pin servo-style (Futaba/JR, 2.54 mm) plug; the knob board has matching 1×3 headers. A 30 cm lead just fits as a coil under the panel (6.6 of 6.7 mm); longer won't | Measure length and diameter on arrival; if the plug differs, change the header (JLC fits it, still no soldering) | Knob board headers, `MOTOR_*` in `params.py` |
| ❓ | Where is the 7B's native USB-C port? The schematic confirms it's Type_C2 ("USB": Type_C2 → R65/R66 → U9 → GPIO19/20). The model puts it 36 mm from the board's back edge, from Waveshare's PCB view | Silkscreen on the real board, then close this | Display cable route |
| ❓ | Mid-mount USB-C socket (C2894902): LCSC lists it as SMD-only, so the through-hole shell legs the strain relief relies on are unverified. Also how far it sticks out past the board edge, footprint | Get the HC-TYPE-C-16P-CB1.6 drawing; adjust `USB_C_SOCKET`/the board edge so the face lines up with the inside of the back wall; if it has no real legs, pick a mid-mount part that does | USB board, strain relief |
| ⚠️ | B3U-1000P (LCSC C231329): 110,060 in stock at $0.19 (5+) with no lifecycle flag on 2026-10-17 (an older check saw "not recommended for new designs"). Operating force spreads 1.01–1.99 N. Same-size (3 × 2.5 mm) alternatives on LCSC: XKB TS-3025-B-A-B (C2885149, 160 gf, 1.5 mm tall), plus Hanxia, SAMZO, Zhongdi and G-Switch parts (2026-10-17) | Order a few alternatives with the prototype and compare the click; buy extra B3U and sort by feel; check pad layouts | Key switches |
| ✅ | Real thickness of the 7B. **From Waveshare's STEP model**: panel 6.2 mm; the board sits on 2.5 mm bosses, with the frame back 3.7 mm behind the glass; the connector row 16.1 mm below the glass. The deepest part under the board is the microSD socket (5.0 mm). The model now uses these; the connector row gets a 1 mm floor pocket (1.5 mm clearance). The USB-C port center is 1.22 mm below the board's underside (about 11.05 mm below the glass), not the 2.97 mm in `USB_BELOW_PCB` (measured from the wrong face) | Confirm with calipers on a real board | Case (`params.py`) |
| ❓ | The only STEP is the touch SKU. The non-touch 31727 may have a bare polarizer instead of cover glass, so its front profile and `PANEL_T` are unmeasured. Which backlight dimming resistors are fitted is unknown. Waveshare revises boards | On the first 7B: measure `PANEL_T` and the front lip, probe EN/FB while sweeping brightness, record the silkscreen revision against the STEP. Buy two 7Bs if the budget allows | Key stack, case, brightness |

## Answered by the prototype

Pass/fail criteria for each are in [prototype-tests.md](prototype-tests.md).

| | Question | Affects |
|---|---|---|
| ⚠️ | Is the B3U's 0.15 mm travel a satisfying click, or too short? | Key switch choice |
| ⚠️ | Does a press anywhere on the cap, including the far corner, click cleanly without tilting? | Cap, tab and frame support (owner decision D8) |
| ⚠️ | Is the 2204's cogging noticeable in smooth mode? | Motor choice (fallback: SparkFun ROB-20441) |
| ❓ | Knob current at rest, while clicking, at an end stop | Power budget numbers |
| ❓ | Does the hinged tongue give a good press feel (force, travel, no wobble when turning)? | Tongue size and hinge width in `params.py` (the hinge is likely too stiff: owner decision D10) |
| ❓ | Does the touch band work through the printed plate, next to a running motor and a lit panel, with no false touches from a hand on a knob? | Touch band design |
| ❓ | How fast do images go over USB? (Plan on ~0.5 MB/s; target a full page < 300 ms) | Protocol (compression, framing) |
| ❓ | Can the RP2350B run 5 FOC loops at ≥ 2–5 kHz each? | Knob firmware |

## Answer before the full build

Cabling (new with the internal hub; [wiring.md](wiring.md)):

| | Question | How we answer it | Affects |
|---|---|---|---|
| ⚠️ | **Offline page switching:** with no host app, a "go to page N" key can't change the images, because the two chips only meet through the host. Owner decision D5 in [design-review.md](design-review.md) | Decide if it matters. If it does: a 3-wire HY2.0 lead from the 7B's GPIO6 connector (J8) to a header on the knob board, carrying the page number (still plug-in) | [protocol.md](protocol.md) |
| ❓ | Real USB-C plug sizes: the model uses 12.5 × 6.5 mm overmolds, 22 mm straight and 13 mm right-angle. The display end must be a side-exit (left/right) 90° plug, not up/down | Measure the cable that arrives; rerun `cad/assembly.py --check` with its sizes | Display cable, `USB_PLUG_*` |
| ❓ | Is a 100 mm USB-C cable really ~100 mm plug tip to plug tip? (Sellers measure differently.) The loop takes 95–110 mm | Measure | Display cable |
| ❓ | JST-GH carries 5 V on two 1 A contacts (26 AWG cable): knob board capped at ~1.8 A. Enough? | Prototype current measurements | Power budget |
| ❓ | Power on default 500 mA ports: the device draws about 1 A, and the budget text in [wiring.md](wiring.md) contradicts itself. Owner decision D9 | — | Power budget |
| ❓ | FFC contact side: type B (opposite sides) assumes top-contact ZIFs on both boards | ZIF datasheet | Key cable order |
| ❓ | One JLC panel means one board thickness, but the touch band was planned at 0.8 mm | Test sensing through 1.6 mm board + 2 mm plate on the prototype, or order the band separately | Touch band, cost |
| ❓ | Extended-part fees: the whole panel has roughly 17–19 extended part types ($3 each per order at JLC), not ~5. Bottom-side and THT parts may need Standard double-sided assembly. Cost presentation and assembly route: owner decisions D1 and D6 | Count from the BOM with JLC's BOM tool; prefer basic parts where they exist | Cost |

Everything else:

| | Question | How we answer it | Affects |
|---|---|---|---|
| ❓ | Is a full-screen redraw at 1024×600 fast enough on the ESP32-S3? | Test on a 7B board | Firmware design |
| ❓ | Touch band controller part (must be in JLC stock). The MPR121 is discontinued (NXP PCN16772); distributor stock remains. Owner decision D12 | Pick from the JLC parts library | Touch band PCB |
| ❓ | OpenDeck device plugin: interface and whether an MIT plugin is OK next to the GPL-3.0 app. Its device-plugin API can't carry knob feel, pages or swipes: owner decision D4 | Read OpenDeck's plugin docs | Host software, licensing |
| ❓ | Case printing: does the stand print well on a home printer, and what does JLC3DP charge? | Slice the STLs; get a JLC3DP quote | Cost estimate |
| ❓ | Real costs: JLC quotes for the panelized PCBs with assembly | Upload the real Gerbers/BOM | Cost estimate |

## Decided for now, revisit later

- **21 keys (7×3).** 24 keys (8×3) fit on the same board; 32 needs a bigger
  screen or moving the knob displays.
- **IPS LCD, not OLED.** OLED looks better under clear caps but static icons
  risk burn-in. Could be trialled on the prototype with a 2.4" OLED.
- **Internal USB hub instead of a UART link** (decided 2026-10-17): the
  RP2350B and ESP32-S3 each get their own USB connection, so there's no
  custom bootloader and no hand-made leads. Cost: the host pairs two
  devices, and the chips can't reach each other without the host (below).
- **Printed knobs (`KNOB_STYLE = "integrated"`).** The `shaft_adapter`
  style takes any 6 mm D-shaft knob.

## Owner decisions from the design review

Open choices from [design-review.md](design-review.md); options and
recommendations are there. Not decided here.

- D1 cost and import duty · D2 TMC6300/MT6701 sourcing · D3 prototype scope
- D4 host software · D5 offline page switching and screen wake · D6
  double-sided assembly · D7 internal hub
- D8 key support (frame PCB support, cap down-stop, second switch) · D9
  power on default 500 mA ports · D10 knob press hinge
- D11 touch band vs motor bells · D12 touch controller · D13 display
  firmware toolchain (the RGB panel needs ESP-IDF sdkconfig options)
- D14 case fasteners and material · D15 look items · D16 knob-board
  floorplan (driver on or off the tongue) · D17 reflash/keymap security ·
  D18 ESP32 update path
