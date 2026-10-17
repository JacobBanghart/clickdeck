# Wiring and power

How the boards connect, and where power comes from. Pinouts of Waveshare's
board are from its schematic
([ESP32-S3-Touch-LCD-7B-Schematic.pdf](https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-7B/ESP32-S3-Touch-LCD-7B-Schematic.pdf),
read 2026-10-17). Untested, like everything else in this repo.

## Overview

```
 PC ──USB-C──► Waveshare ESP32-S3-LCD-7B ("display board")
                │  native USB port "USB" (Type_C2), via the tunnel in the left wall
                │
                ├─ J9  POWER 5V ───────────► knob board 5 V in (motors, logic)
                ├─ H3  UART2 ──────────────► knob board UART (events, haptic settings, firmware)
                ├─ J8  GPIO6 ──────────────► knob board RP2350B RUN (reset)
                │
 knob board (RP2350B) ◄── 12-pin FFC ── frame PCB (21 key switches + diodes)
        │
        └──── 6-pin cable ────► touch band (touch controller, I²C)
```

## Display board facts (from the schematic)

- **Native USB-C ("USB", Type_C2):** VBUS goes straight to the board's 5 V
  rail. The CC pins have fixed 5.1 kΩ pulldowns, so the board **can't tell
  how much current the PC offers** (500 mA, 1.5 A or 3 A).
- **J9 POWER (HY2.0 2P):** 1 = GND, 2 = 5V, straight off that 5 V rail.
  HY2.0 is 2.0 mm pitch, like JST PH (rated ~2 A).
- **H3 UART2 (HY2.0 4P):** 1 = 3V3, 2 = GND, 3 = EX_RXD (into the ESP32),
  4 = EX_TXD. It's GPIO43/44 through an analog switch; **slide switch SW1
  must select UART2** (otherwise the UART goes to the onboard USB-to-UART
  chip).
- **J8 GPIO (HY2.0 3P):** 1 = 3V3, 2 = GND, 3 = GPIO6.
- **H1 I2C (HY2.0 4P):** 1 = 3V3, 2 = GND, 3 = SDA, 4 = SCL (shared with
  touch and the I/O expander). Not used.
- **I/O expander:** a CH32V003 microcontroller with a PWM output for the
  backlight (`EXIO_PWM`), so brightness is adjustable.
- **Board power:** 350 mA at 5 V (Waveshare's figure).

## Power

### Path
PC → display board's native USB-C → its 5 V rail → **J9** → knob board.
No extra USB-C connector or hub. The motors draw from the same rail as the
ESP32-S3, so the knob board must not disturb it:

- **Soft start.** A load switch with a controlled rise time on the knob
  board's 5 V input, so charging its capacitors at power-on doesn't sag the
  rail and reset the ESP32-S3. (Part TBD from JLC stock.)
- **Bulk capacitance** on the knob board (~470 µF total plus 10 µF at each
  driver) to absorb motor current spikes.
- **Voltage monitoring.** The RP2350B measures its 5 V input through a
  divider on an ADC pin (GPIO40–47).

### Budget
Because the display board can't read the PC's USB-C current offer, the
firmware can't either. So:

- **Default motor budget: 500 mA total.** Enough for detents and stops on
  one knob at a time. (Display board 350 mA + knob board logic ~60 mA +
  motors stays under 1 A, safe on any USB-C port.)
- **A user setting** raises it for ports known to supply 1.5 A or 3 A.
- **Brownout guard:** if the 5 V input drops below ~4.6 V under load, the
  firmware cuts motor current right away and lowers the budget.
- The arbiter from [plan.md](plan.md) (wake on movement, one active knob
  gets the budget, two split it) works inside this budget.
- USB-A ports and A-to-C cables (500 mA) still work; haptics are weaker.

## Knob board connections

| Connector | Type | Pins | Goes to |
|---|---|---|---|
| Power in | HY2.0 2P | 1 GND, 2 5V | Display board J9 |
| Link | HY2.0 4P | 1 NC (don't connect 3V3), 2 GND, 3 TX → EX_RXD, 4 RX ← EX_TXD | Display board H3 |
| Reset | HY2.0 3P | 1 NC, 2 GND, 3 RUN ← GPIO6 | Display board J8 |
| Keys | 12-pin FFC, 1.0 mm | 7 columns, 4 rows, GND | Frame PCB |
| Touch | JST-SH 6P | 3V3, GND, SDA, SCL, INT, NC | Touch band |
| Recovery | Test pads + button | USB D+/D−, BOOTSEL | Bench only |
| Motors ×5 | Solder pads (3 each) | Phases U/V/W | 2204 motors |

Cables use the HY2.0-to-HY2.0 leads Waveshare ships, or crimped ones.
Lengths come from the CAD model (to do).

**RUN from GPIO6:** RP2350B RUN has an internal pull-up and is 3.3 V
logic, so GPIO6 can drive it directly (open-drain style). The ESP32-S3 can
reset the knob board, which the UART bootloader uses for firmware updates.

## Key matrix

- **7 columns × 4 rows = 28 positions:** rows 1–3 are the 21 keys on the
  frame PCB; row 4 is the 5 knob press switches on the knob board (sharing
  the column lines). That saves pins compared with wiring the knob presses
  separately.
- **One diode per switch** (SOD-123, e.g. 1N4148W) so any combination of
  keys can be held at once (needed for held modifiers and push-to-talk).

## RP2350B pin budget (48 GPIO)

| Use | Pins |
|---|---|
| Motor PWM, 3 per motor × 5 | 15 |
| Motor driver standby (TMC6300 VIO), one per motor so each sleeps independently | 5 |
| MT6701 sensors: shared clock + data, 5 chip selects | 7 |
| Key matrix, 7 columns + 4 rows (includes knob presses) | 11 |
| UART to display board | 2 |
| I²C to touch band + interrupt | 3 |
| 5 V monitor (ADC) | 1 |
| **Total** | **44 of 48** |

RUN, USB and the SWD debug pins are separate pins on the RP2350B and don't
count against the 48. Constraints for the schematic: each motor's 3 PWM
signals should share one PWM frequency (any slices work); the 5 V monitor
needs one of GPIO40–47.

## Frame PCB connections

- 21 B3U switches + 21 diodes, 7 columns × 3 rows.
- One 12-pin FFC connector (1.0 mm pitch) to the knob board.
- Nothing else: no chips.

## Touch band connections

- Touch controller (part TBD from JLC stock) + slider electrodes.
- JST-SH 6P to the knob board: 3V3, GND, SDA, SCL, INT.
