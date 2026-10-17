# Wiring and power

How the boards connect, where power comes from, and how the cables are held.
The builder solders and crimps nothing: JLC fits every board-mounted
connector, and every cable is bought ready-made and plugged in. Pinouts of
Waveshare's board are from its schematic
([ESP32-S3-Touch-LCD-7B-Schematic.pdf](https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-7B/ESP32-S3-Touch-LCD-7B-Schematic.pdf),
read 2026-10-17) and its STEP model. Untested, like everything else in this
repo.

## Overview

```
 PC ──USB-C (back wall)──► USB board: CH334F USB 2.0 hub, reads the port's current offer
                            ├─ hub port 1 ── JST-GH 8-pin cable ──► knob board: RP2350B native USB
                            │                (USB D+/D−, 5 V ×2, GND ×2, CC sense ×2)
                            └─ hub port 2 ── USB-C socket ── 100 mm USB-C cable ──► Waveshare 7B native USB
                                                                       (5 V for the display board too)

 knob board (RP2350B) ◄── 12-pin FFC ── frame PCB (21 key switches + diodes)
        ├──── JST-SH 6-pin cable ────► touch band (touch controller, I²C)
        └──── 3-pin plug ×5 ─────────► 2204 motors
```

The PC sees two USB devices behind a hub: the display board (ESP32-S3:
images, display settings) and the knob board (RP2350B: keys, knobs, touch,
haptics). The host software pairs them ([protocol.md](protocol.md)). Each
chip updates over its own USB connection; there's no link between the two
chips inside the case.

![Cabling, top view with the display and top plate removed](../cad/out/cabling.png)

## Where things go (and why)

**USB board in the back-left corner.** The knob board runs across the front
and the display board fills the middle, so the free space is a 34 × 75 mm bay
beside the display board's left edge (under the panel, 10 mm tall) and an
8.5 mm strip behind it. The USB board's main part sits in the bay; a narrow
arm runs along the back wall to the external socket. Options considered:

| | Option | Verdict |
|---|---|---|
| a | **Small USB board at the back** (external USB-C, hub, current sensing), cabled to the display board and the knob board | **Chosen.** The external socket is ours, so it can be clamped to the wall and its CC pins read directly. It sits next to the display board's USB port, so that cable is the shortest stock length (100 mm). One more board in the same JLC panel |
| b | Hub on the knob board, panel-mount USB-C extension from the back wall | Two USB-C cables crossing the case, and the extension's own socket and wiring are a third-party part: cheap ones often don't carry the CC wire through, which would lose current sensing (and C-to-C cables might not get 5 V at all). Extensions aren't allowed by the USB-C spec |
| c | Hub on the knob board, a plain "port board" at the back | Still needs a 2 A cable plus the CC lines from the back to the front, the same harness as (a), and a longer display cable |
| c' | USB board standing upright against the back wall | 8.5 mm behind the display board isn't enough for the board plus plugs going into it |

**External port 16 mm left of center**, not dead center: the center of the
back wall has the two pinholes for the display board's BOOT and RESET
buttons. The opening is 3 mm from the nearest pinhole, and a plugged-in cable
still leaves the pinholes free (checked in the model).

**Display board cable.** Waveshare's board has two USB-C ports on its left
edge (facing left, about 27 mm in from the panel frame's left edge, from the
STEP model): the native USB port, 36 mm from the board's back edge, and the
USB-to-UART port 15 mm in front of it. Which is which comes from the earlier
estimate: **check the silkscreen ("USB") on the real board.** The port is
only 8.8 mm above the floor with the panel 4.6 mm above it, so the cable's
display end is a **90° side-exit plug** (cable leaves sideways in the plane
of the plug's wide face, here toward the front). USB-C is reversible, so a
"left-angle" plug flipped over is a "right-angle" one; "up/down-angle" plugs
don't fit. The cable loops forward through the bay (bend radius 10 mm) and
comes back into the USB board's socket with a straight plug. The model sizes
the loop for a 100 mm cable; 95–110 mm cables fit (the loop takes up the
difference).

**Keys and touch at the right end of the knob board.** The left end is taken
by the USB link and the loop, so the key FFC runs from a ZIF connector on top
of the frame PCB's right edge, down the 1 mm gap between the panel and the
right wall, into a ZIF connector on the knob board's right end. The touch
band's connector sits at its right end, just past the last motor; its cable
drops to a top-entry header beside the ZIF.

**Motor plugs behind each tongue**, pointing left, with the spare lead
coiled flat on the back strip and strapped through two slots. See
"Motors" below.

## Display board facts (from the schematic and STEP model)

- **Native USB-C ("USB", Type_C2):** VBUS goes straight to the board's 5 V
  rail. The CC pins have fixed 5.1 kΩ pull-downs, so the display board
  itself can't tell how much current is offered. It doesn't need to: the USB
  board does.
- **Port position:** center 2.97 mm below the board's underside, face flush
  with the board's left edge (STEP).
- **H3 UART2, J8 GPIO6, J9 POWER, H1 I2C (HY2.0):** no longer used. The
  UART1/UART2 slide switch position doesn't matter.
- **I/O expander:** a CH32V003 with a PWM output for the backlight, so
  brightness is adjustable.
- **Board power:** 350 mA at 5 V (Waveshare's figure).

## Power

### Path

```
 PC VBUS ─► USB board ─┬─ TVS ─ CH334F (its own 3.3 V regulator)
                       ├─ SY6280 current-limited switch ─► display board port VBUS (always on)
                       └─ JST-GH pins 1+2 ─► knob board: soft-start load switch ─► motors, 3.3 V regulator
```

- **Display board port:** a downstream USB-C socket with 56 kΩ pull-ups on
  CC1/CC2 (default USB power, per spec) and VBUS through a current-limited
  switch (SY6280, ~1 A; check the exact limit), so a short in that cable
  can't take down the rest.
- **Knob board input:** a load switch with a controlled rise time (soft
  start, part TBD from JLC stock), so charging its capacitors doesn't sag
  the PC's port; ~470 µF bulk plus 10 µF at each driver for motor current
  spikes.
- **Voltage monitoring:** the RP2350B measures its 5 V input through a
  divider on an ADC pin.

### Reading the PC's current offer

The USB board's upstream socket has the standard 5.1 kΩ pull-downs on CC1
and CC2. Both CC lines also go through 10 kΩ resistors to the JST-GH cable
(pins 7 and 8) and on to two RP2350B ADC pins, with 100 nF to ground at the
knob board (a slow filter; the ADC reads DC). Whichever CC line the cable
connects sits at (USB Type-C spec, voltage across the 5.1 kΩ):

| PC advertises | CC voltage | Motor budget (default) |
|---|---|---|
| Default USB power (or an A-to-C cable) | 0.25–0.61 V | 500 mA |
| 1.5 A | 0.70–1.16 V | 1.0 A |
| 3.0 A | 1.31–2.04 V | 1.5 A |

- The defaults keep the whole device under the offer: display board 350 mA
  + hub ~50 mA + knob board logic ~60 mA + motors. With default USB power the
  total (~1 A) goes past the USB 2.0 500 mA figure, as the earlier plan
  already did; most ports allow it, and the brownout guard catches the ones
  that don't.
- **Cap from the cable:** the JST-GH link carries 5 V on two contacts rated
  1 A each, so the knob board takes at most ~1.8 A whatever the PC offers
  (motor budget ≤ 1.5 A).
- **Brownout guard:** if the 5 V input drops below ~4.6 V under load, the
  firmware cuts motor current right away and lowers the budget.
- **User setting:** can lower the budget, or raise it for a port known to
  supply more than it advertises (within the cable cap).
- The arbiter from [plan.md](plan.md) (wake on movement, one active knob
  gets the budget, two split it) works inside this budget.

## Connectors

All on the boards, fitted by JLC. Part numbers: [bom.md](bom.md).

| Board | Connector | Mates with | Notes |
|---|---|---|---|
| USB board | USB-C, mid-mount (sinks into the board), through-hole shell legs | PC cable | External; see "Strain" |
| USB board | USB-C, top mount, 4 through-hole shell legs (TYPE-C-31-M-12) | Display cable, straight end | Faces forward |
| USB board | JST-GH 8-pin, side entry (SM08B-GHS-TB) | USB link cable | Faces forward; positive latch |
| Knob board | JST-GH 8-pin, side entry | USB link cable | Back-left corner, faces back |
| Knob board | 1×3 2.54 mm right-angle header ×5 | Motor plugs | Behind each tongue, pins point left |
| Knob board | 12-pin 1.0 mm flip-lock ZIF | Key FFC | Right end, on a small tab |
| Knob board | JST-SH 6-pin, top entry (BM06B-SRSS-TB) | Touch cable | Right end, front |
| Knob board | USB test pads + BOOTSEL button | — | Recovery only |
| Frame PCB | 12-pin 1.0 mm flip-lock ZIF, top side | Key FFC | Right edge; the frame PCB reaches 4.6 mm past the panel there |
| Touch band | JST-SH 6-pin, side entry (SM06B-SRSS-TB), underside | Touch cable | Right end, past the last motor |

### Pinouts

**USB link, JST-GH 8-pin** (cable wired pin 1 to pin 1):
`1 VBUS · 2 VBUS · 3 GND · 4 D− · 5 D+ · 6 GND · 7 CC1 sense · 8 CC2 sense`.
USB full speed (12 Mbit/s) over ~100 mm of unshielded wire is fine; JST-GH
carrying USB is the drone-controller (Pixhawk) convention. Route D+/D− as a
pair on both boards.

**Keys, 12-pin FFC:** `1 GND · 2–8 columns 1–7 · 9–11 rows 1–3 · 12 GND`.

**Touch, JST-SH 6-pin:** `1 3V3 · 2 GND · 3 SDA · 4 SCL · 5 INT · 6 NC`.

**Motors, 1×3 header:** phases U, V, W. The plug goes on either way round:
the firmware's calibration finds the phase order and direction.

### Cables

Bought ready-made; lengths from the model (`cad/assembly.py`, table in
[assembly.md](assembly.md)):

| Cable | Buy | Why that length |
|---|---|---|
| USB-C to USB-C, USB 2.0, one 90° side-exit plug + one straight plug | 100 mm | Loop sized for it (route 97 mm) |
| JST-GH 1.25 mm 8-pin, both ends, pin 1 to pin 1 | 100 mm | Route 74 mm, the rest as a gentle S |
| FFC 12-pin 1.0 mm, contacts on opposite sides (type B) | 80 mm | Top plate lifts 40 mm with it plugged in (needs 67 mm) |
| JST-SH 1.0 mm 6-pin, both ends, pin 1 to pin 1 | 100 mm | Same (needs 67 mm) |

**FFC contact side:** with top-contact ZIF connectors on the top of both
boards as modeled, the cable's contacts end up on opposite sides (type B).
If the ZIF picked has bottom contacts on one board, it flips to type A:
check before ordering.

## Strain and service

**External socket.** Plugging in, yanking or levering the PC cable must not
load solder joints:
- The socket is a **mid-mount** part with **through-hole shell legs**, and
  its face sits flush with the inside of the back wall. The plug's overmold
  seats 2.5 mm deep into a 14 × 8 mm opening in the wall, so a sideways pull
  levers the plug against the case, not the socket. (Overmolds up to
  ~13.5 × 7.5 mm seat fully; most cables are 10.5–12.5 × 5.5–6.5 mm.)
- **Push-in:** the USB board's arm rests against a printed backstop rib on
  the floor right behind the socket.
- **Pull-out:** the board's edge sits against the back wall.
- **Screws:** two M2 screws either side of the socket, two more in the main
  part of the board, into printed bosses.

**Internal USB-C.** The USB board's socket has four through-hole shell legs.
The cable is pressed into two printed clips on the tray floor, so tugging the
loop doesn't pull on either socket. Bends stay at 10 mm radius or more, and
the loop stays off the knob board and away from the motors (checked).

**Latches.** JST-GH and the ZIF connectors latch. JST-SH holds by friction
only; it's the short touch cable, which nothing pulls on once the case is
closed.

**Clips and ties.** Three push-in clips printed with the tray (two for the
display cable, one for the USB link). Motor leads: hook-and-loop ties
through slots in the knob board.

**Motors.** The 2204 lead (~30 cm with a 3-pin servo-style plug per one
listing; **verify on arrival**) leaves the motor base under the bell, runs
back over the hinge to the back strip, and plugs into the header behind its
tongue. The rest coils flat on the back strip (24 × 5 mm, 3 layers) under
the panel and is strapped through two slots, clear of the spinning bell. A
30 cm lead fills the 6.7 mm under the panel (6.6 mm coil): longer leads
don't fit, shorter ones are easier.

**Service loops.** The top plate lifts 40 mm with the key and touch cables
still plugged in (checked), which is enough to reach the ZIF latch and the
touch plug at the knob board's right end. The display board's USB cable and
the USB link unplug before the display or the knob board come out (guide in
[assembly.md](assembly.md)).

**Plug insertion.** Every plug has a straight path into its socket at the
step that connects it (checked in the model, like the screwdriver access).

## Key matrix

- **7 columns × 4 rows = 28 positions:** rows 1–3 are the 21 keys on the
  frame PCB; row 4 is the 5 knob press switches on the knob board (sharing
  the column lines).
- **One diode per switch** (SOD-123, e.g. 1N4148W) so any combination of
  keys can be held at once (needed for held modifiers and push-to-talk).

## RP2350B pin budget (48 GPIO)

| Use | Pins |
|---|---|
| Motor PWM, 3 per motor × 5 | 15 |
| Motor driver standby (TMC6300 VIO), one per motor so each sleeps independently | 5 |
| MT6701 sensors: shared clock + data, 5 chip selects | 7 |
| Key matrix, 7 columns + 4 rows (includes knob presses) | 11 |
| I²C to touch band + interrupt | 3 |
| 5 V monitor (ADC) | 1 |
| CC1/CC2 current-offer sense (ADC) | 2 |
| **Total** | **44 of 48** |

USB, RUN and the SWD debug pins are separate pins on the RP2350B and don't
count against the 48. The UART pins the old internal link used are free.
Constraints for the schematic: each motor's 3 PWM signals should share one
PWM frequency; the three analog inputs need GPIO40–47.

## Frame PCB connections

- 21 B3U switches + 21 diodes, 7 columns × 3 rows.
- One 12-pin flip-lock ZIF connector (1.0 mm pitch) on the top side at the
  right edge.
- Nothing else: no chips.

## Touch band connections

- Touch controller (part TBD from JLC stock) + slider electrodes.
- JST-SH 6-pin, side entry, on the underside at the right end.

## USB board connections

- CH334F hub (QFN-24, no crystal), USB ESD protection, TVS.
- Upstream: external USB-C (CC1/CC2 5.1 kΩ to GND, sensed through 10 kΩ).
- Downstream port 1: JST-GH 8-pin to the knob board. Port 2: USB-C to the
  display board (56 kΩ CC pull-ups, VBUS through SY6280). Ports 3–4 unused
  (test pads).
