# Open questions and risks

Things that are unverified or decided "for now". Each has how and when it
gets answered. Strike items through (or delete them) once answered, and
record the answer in the doc it affects.

Status: ❓ open · ⚠️ risk to watch · ✅ answered

## Answer before the knob board design

| | Question | How we answer it | Affects |
|---|---|---|---|
| ❓ | Is the 7B's 3-pin sensor connector GPIO6? (Inferred from a forum post, not from Waveshare's pin tables) | Waveshare 7B schematic, or a multimeter on the real board | Knob board reset line ([pcb.md](pcb.md)) |
| ❓ | Does the TMC6300 have built-in break-before-make, so one inverter can derive its low-side inputs (3-PWM plan A)? | TMC6300 datasheet; then test on the Rev 0 knob module | Driver choice, RP2350B pin budget |
| ⚠️ | TMC6300 stock at JLC (an "extended" part, seen out of stock) | Check the JLC parts library right before each order | Plan A vs DRV8316 plan B |
| ❓ | Mitoot 2204's real bolt pattern, height and KV (sellers disagree) | Calipers when the motor arrives | Knob board holes, `params.py` |
| ❓ | Can an RP2350B bootloader update reliably over the UART link from the ESP32-S3? | Prototype firmware | Knob board flashing ([plan.md](plan.md)) |
| ❓ | Read the USB-C current advertisement on the display board, or on our own board? | Waveshare 7B schematic (CC line wiring) | Power budget |

## Answered by the prototype

Pass/fail criteria for each are in [prototype-tests.md](prototype-tests.md).

| | Question | Affects |
|---|---|---|
| ⚠️ | Is the B3U's 0.15 mm travel a satisfying click, or too short? | Key switch choice |
| ⚠️ | Does a press anywhere on the cap, including the far corner, click cleanly without tilting? | Cap, tab and guide design |
| ⚠️ | Is the 2204's cogging noticeable in smooth mode? | Motor choice (fallback: SparkFun ROB-20441) |
| ❓ | Knob current at rest, while clicking, at an end stop | Power budget numbers |
| ❓ | Does the hinged tongue give a good press feel (force, travel, no wobble when turning)? | Tongue size and hinge width in `params.py` |
| ❓ | Does the touch band work reliably through 3 mm acrylic (and later 2 mm printed plastic)? | Touch band design |
| ❓ | How long does one key image take over USB? | Protocol (compression, framing) |

## Answer before the full build

| | Question | How we answer it | Affects |
|---|---|---|---|
| ❓ | Is a full-screen redraw at 1024×600 fast enough on the ESP32-S3? | Test on a 7B board | Firmware design |
| ❓ | Touch band controller part (must be in LCSC stock) | Pick from the JLC parts library | Touch band PCB |
| ❓ | OpenDeck device plugin: interface and whether an MIT plugin is OK next to the GPL-3.0 app | Read OpenDeck's plugin docs | Host software, licensing |
| ❓ | Case printing: does the stand print well on a home printer, and what does JLC3DP charge? | Slice the STLs; get a JLC3DP quote | Cost estimate |
| ❓ | Real costs: JLC quotes for the panelized PCBs with assembly | Upload the real Gerbers/BOM | Cost estimate |

## Decided for now, revisit later

- **21 keys (7×3).** 24 keys (8×3) fit on the same board; 32 needs a bigger
  screen or moving the knob displays.
- **IPS LCD, not OLED.** OLED looks better under clear caps but static icons
  risk burn-in. Could be trialled on the prototype with a 2.4" OLED.
- **UART link to the knob board.** Fallback: a USB hub chip on the knob
  board so each chip gets its own USB connection.
- **Printed knobs (`KNOB_STYLE = "integrated"`).** The `shaft_adapter`
  style takes any 6 mm D-shaft knob.
