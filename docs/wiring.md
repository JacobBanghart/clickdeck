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
                            ├─ hub port 1 ── JST-GH 8-pin cable ──► backplane: RP2350B native USB
                            │                (USB D+/D−, 5 V ×2, GND ×2, CC sense ×2)
                            └─ hub port 2 ── USB-C socket ── 100 mm USB-C cable ──► Waveshare 7B native USB
                                                                       (5 V for the display board too)

 backplane (RP2350B) ◄── 12-pin FFC ── frame PCB (21 key switches + diodes)
        ├┄┄┄┄ JST-SH 6-pin cable ┄┄┄┄► touch band (optional add-on, off by default, D24)
        ├──── 18 pogo pins ×5 slots ─► knob modules (haptic: driver, sensor, motor; lite: encoder) or blanks
        └┄┄┄┄ HY2.0 3-pin lead (optional) ┄┄► Waveshare 7B J8 (GPIO6): page, wake
```

**Knob slots (D23):** the knobs are modules. Each of the five slots takes a
haptic module (DRV8311H driver, MT6701, press switch, its motor plugged in), a
lite module (push encoder) or a blank. Modules have no MCU; they connect
to the backplane through the slot connector (below) and nothing else. The
haptic module's motor plugs into a header on the module itself.

The PC sees two USB devices behind a hub: the display board (ESP32-S3:
images, display settings) and the backplane (RP2350B: keys, knobs, touch,
haptics). The web configurator and the optional daemon pair them
([protocol.md](protocol.md)). Each chip updates over its own USB
connection. The only link between the chips inside the case is the
optional one-wire lead (see "Link to the display board").

![Cabling, top view with the display and top plate removed](../cad/out/cabling.png)

## Where things go (and why)

**USB board in the back-left corner.** The backplane runs across the front
and the display board fills the middle, so the free space is a 34 × 75 mm bay
beside the display board's left edge (under the panel, 10 mm tall) and an
8.5 mm strip behind it. The USB board's main part sits in the bay; a narrow
arm runs along the back wall to the external socket. Options considered:

| | Option | Verdict |
|---|---|---|
| a | **Small USB board at the back** (external USB-C, hub, current sensing), cabled to the display board and the backplane | **Chosen.** The external socket is ours, so it can be clamped to the wall and its CC pins read directly. It sits next to the display board's USB port, so that cable is the shortest stock length (100 mm). One more board in the same JLC panel |
| b | Hub on the backplane, panel-mount USB-C extension from the back wall | Two USB-C cables crossing the case, and the extension's own socket and wiring are a third-party part: cheap ones often don't carry the CC wire through, which would lose current sensing (and C-to-C cables might not get 5 V at all). Extensions aren't allowed by the USB-C spec |
| c | Hub on the backplane, a plain "port board" at the back | Still needs a 2 A cable plus the CC lines from the back to the front, the same harness as (a), and a longer display cable |
| c' | USB board standing upright against the back wall | 8.5 mm behind the display board isn't enough for the board plus plugs going into it |

**External port 16 mm left of center**, not dead center: the center of the
back wall has the two pinholes for the display board's BOOT and RESET
buttons. The opening is 3 mm from the nearest pinhole, and a plugged-in cable
still leaves the pinholes free (checked in the model). A third pinhole, in
the case floor under the backplane's left end (11 mm from the left edge,
30.5 mm from the front), reaches the backplane's BOOTSEL button, so both
chips can be put into their bootloaders from outside; lift the slab off
the stand to use it ([recovery.md](recovery.md); pictures in
[assembly.md](assembly.md)).

**Display board cable.** Waveshare's board has two USB-C ports on its left
edge (facing left, about 26 mm in from the panel frame's left edge, from the
STEP model): the native USB port, 36 mm from the board's back edge, and the
USB-to-UART port 15 mm in front of it. The schematic confirms Type_C2
("USB") is native (Type_C2 → R65/R66 → U9 → GPIO19/20); its position comes
from Waveshare's PCB view: **check the silkscreen on the real board.** The
port's center is only 12.8 mm above the case bottom and 9.0 mm below the
glass (the board sits 2.7 mm above the floor, with no floor pocket), so the cable's
display end is a **90° side-exit plug** (cable leaves sideways in the plane
of the plug's wide face, here toward the front). USB-C is reversible, so a
"left-angle" plug flipped over is a "right-angle" one; "up/down-angle" plugs
don't fit. The cable loops forward through the bay (bend radius 10 mm) and
comes back into the USB board's socket with a straight plug. The model sizes
the loop for a 100 mm cable; 95–110 mm cables fit (the loop takes up the
difference).

**Keys and touch at the right end of the backplane.** The left end is taken
by the USB link and the loop, so the key FFC runs from a ZIF connector on top
of the frame PCB's right edge, down the 1 mm gap between the panel and the
right wall, into a ZIF connector on the backplane's right end. The touch
band (optional, off by default, D24) has its connector at its right end,
right of slot 4, facing right so the plug stays clear of the slot's
opening; its cable drops along the right wall to a top-entry header beside
the ZIF. Without the band that header is a footprint only.

**Knob slots across the front.** The backplane runs under the five slots
with a slot connector (18 pogo pins) under each module's front border; the
modules drop in from the top (D23, below). Each haptic module carries its
own motor plug, on an upright header on its front border, and the spare
motor lead coils in front of the bell inside the module. See "Motors"
below.

## Display board facts (from the schematic and STEP model)

- **Native USB-C ("USB", Type_C2):** VBUS goes straight to the board's 5 V
  rail. The CC pins have fixed 5.1 kΩ pull-downs, so the display board
  itself can't tell how much current is offered. It doesn't need to: the USB
  board does.
- **Back-feed:** the same 5V net is also fed from the UART port (Type_C1,
  through the Q10 ideal diode) and from a battery on J3 (through a boost
  converter). Anything that powers the 5V net shows up on the native port's
  VBUS and goes back into our USB board. The USB board blocks it (see
  "Power"), but still: **never fit a battery to J3, and unplug the back
  cable before using the UART port.**
- **USB/CAN mux:** GPIO19/20 reach Type_C2 through an FSUSB42 mux (U9),
  selected by expander pin EXIO5 with a 10 kΩ pull-down (low = USB). The
  display firmware must **never drive EXIO5 high**, or USB disappears. An
  ESP32 reset doesn't reset the CH32V003 expander, so recovery from that is
  "unplug for 10 s, hold BOOT, plug in" ([recovery.md](recovery.md)).
- **Port position:** center 1.22 mm below the board's underside, face flush
  with the board's left edge (STEP; an earlier figure of 2.97 mm was wrong).
- **J8 GPIO6 (HY2.0 3-pin: 3V3, GND, GPIO6):** the optional link from the
  backplane (see "Link to the display board").
- **H3 UART2, J9 POWER, H1 I2C (HY2.0):** not used. The UART1/UART2 slide
  switch position doesn't matter.
- **I/O expander:** a CH32V003 with a PWM output for the backlight, so
  brightness is adjustable. Which dimming resistors are fitted is unknown
  until a real board is probed.
- **Board power:** 350 mA at 5 V (Waveshare's figure; unmeasured).

## Power

### Path

```
 PC VBUS ─► USB board ─┬─ TVS (clamps < 6 V) + 2 × 22 µF ─ CH334F (its own 3.3 V regulator, 22 µF on VDD33)
                       ├─ TPS259470A eFuse (~1 A) ─► display board port VBUS (always on)
                       └─ TPS259470A eFuse (~1.8 A) ─► JST-GH pins 2+7 ─► backplane:
                              ├─ AMS1117-3.3 regulator (logic, direct)
                              └─ TPS259470A eFuse, soft start ─► motors (enabled by firmware after reading CC)
```

- **One switch part for all three:** the TPS259470ARPWR eFuse (LCSC
  C3662799). Its back-to-back FETs block reverse current while it's on.
  RILM sets the current limit (3.32 kΩ ≈ 1.0 A, 1.65 kΩ ≈ 2.0 A, ±10%
  above 1 A). A cap on dVdt sets the turn-on slew. It runs from 2.7 V to
  23 V (28 V absolute max). QFN-10, 2 × 2 mm, 0.45 mm pitch.
- **Display board port:** a downstream USB-C socket with 56 kΩ pull-ups on
  CC1/CC2 (default USB power, per spec) and VBUS through an eFuse with
  **true reverse-current blocking**. The SY6280 first picked here only
  blocked reverse current while disabled. This switch is always on, so the
  7B's 5 V rail could have driven the PC's VBUS (see "Back-feed" above).
  RILM 3.32 kΩ (~1 A). Delay its enable with an RC so the 7B's ≥ 120 µF
  doesn't charge at the same moment as the backplane. A short in that
  cable can't take down the rest.
- **Backplane branch:** its own eFuse on the USB board, RILM ~1.87 kΩ
  (~1.8 A), blocking reverse current while on. A pinched GH cable or a
  shorted bulk cap can't go straight to the PC port.
- **Input protection:** the VBUS TVS needs a 5–5.5 V standoff and a clamp
  voltage below 6 V at the expected surge. The eFuses take 28 V, but the
  CH334F sits straight on VBUS (check its absolute max). An ordinary 5 V
  TVS clamps near 9 V and doesn't qualify. Name the part in the BOM. Put
  2 × 22 µF basic ceramics (C45783) at the input. Keep a 22–47 µF polymer
  footprint, and fit it only if the hot-plug test shows ringing.
- **Backplane input:** logic (AMS1117-3.3 regulator, sensors, RP2350B)
  runs straight from the input. The third eFuse (soft start set by its
  dVdt cap) feeds only the motor rail, and firmware
  enables it after reading the CC offer, and only when a slot has a haptic
  module, so charging the ~470 µF bulk doesn't sag the PC's port. The
  rail reaches each slot on two VMOT pogo pins; 2 × 22 µF at each driver,
  on the module, for motor current spikes.
- **Hub supply:** the CH334 datasheet warns of low-voltage resets under
  dynamic load. Put 22 µF on its VDD33 (or feed it from its own LDO behind a
  diode), so motor dips don't reset the hub.
- **Voltage monitoring:** the RP2350B measures its 5 V input through a
  divider on an ADC pin.

### Power by slot configuration (D23)

The motor budget scales with the number of haptic modules: the firmware
shares the port's budget (table below) among the haptic slots, and the
1.5 A+ C-to-C policy (D9) stays for full haptics. Each MT6701 adds
10–14 mA of logic current; with no haptic module the motor rail stays off.
A device with only lite modules and blanks draws about 0.46 A (display
board 350 mA, hub ~50 mA, backplane ~60 mA), so it runs on any USB port,
including a default 500 mA port or an A-to-C cable. The CC sense lines
are still read and reported in `STATUS`, but nothing waits on them then.

| Haptic modules | Logic, whole device | Motor budget | Port |
|---|---|---|---|
| 0 (lite or blank only) | ~0.46 A | none | any, A-to-C fine |
| 1–2 | ~0.48 A | port-limited, one knob active at a time gets it all | 1.5 A+ C-to-C for full haptics |
| 5 | ~0.52 A | same, shared when several turn at once | 1.5 A+ C-to-C for full haptics |

### Reading the PC's current offer

The USB board's upstream socket has the standard 5.1 kΩ pull-downs on CC1
and CC2. Both CC lines also go through 10 kΩ resistors to the JST-GH cable
(pins 3 and 6), then through another 10–22 kΩ at the backplane, on to two
RP2350B ADC pins, with 100 nF to ground at the backplane (a slow filter;
the ADC reads DC). The knob-end resistors protect the ADC pins if 5 V ever
lands on a CC pin. Firmware disables the digital input buffers on those
pins (RP2350 erratum E9). One SRV05-4-P-T7 ESD array on the USB board
covers CC1/CC2 as well as D±. Whichever CC line the cable
connects sits at (USB Type-C spec, voltage across the 5.1 kΩ):

| PC advertises | CC voltage | Motor budget (default) |
|---|---|---|
| Default USB power (or an A-to-C cable) | 0.25–0.61 V | Haptics nearly off: faint detents and ticks only |
| 1.5 A | 0.70–1.16 V | ~0.8 A (until real current is measured) |
| 3.0 A | 1.31–2.04 V | 1.5 A |

- **Policy (design review D9): full haptics need a C-to-C cable from a
  port offering 1.5 A or more.** The rest of the device already uses about
  0.5 A: display board 350 mA, hub ~50 mA, backplane logic ~120 mA (each
  MT6701 draws 10–14 mA). So on a default 500 mA port (or any A-to-C
  cable) there's next to nothing left for motors, and the configurator
  tells the user why the knobs feel weak.
- **Start-up:** the motor rail stays off and the backlight starts low until
  the backplane has read CC and been configured over USB. Firmware polls
  CC all the time, so a cable change takes effect at once.
- **Optional PD sink:** a footprint on the USB board for a CH224-class
  USB-PD sink, not fitted by default, so a PD charger can be asked for 5 V
  at 3 A when its CC advertisement says less.
- **Cap from the cable:** the JST-GH link carries 5 V on two contacts rated
  1 A each (JST's rating at 26 AWG; buy a 26 AWG cable, since cheap ones are
  28–30 AWG), so the backplane takes at most ~1.8 A whatever the PC offers
  (motor budget ≤ 1.5 A). The knob branch's switch on the USB board enforces
  this in hardware.
- **Brownout guard:** a legal 3 A port can deliver only 4.2–4.4 V at the
  backplane (4.75 V at the source minus cable, contact and switch drops),
  so a fixed 4.6 V threshold would trip on good ports. Instead, trip when
  the 5 V input falls more than ~300 mV below its idle value, with an
  absolute floor near 4.2–4.3 V, using a fast comparator. On a trip the
  firmware cuts motor current right away and lowers the budget; it recovers
  with hysteresis, and every trip is logged in `STATUS`.
- **User setting:** can lower the budget, or raise it for a port known to
  supply more than it advertises (within the cable cap).
- The arbiter from [plan.md](plan.md) (wake on movement, one active knob
  gets the budget, two split it) works inside this budget.

## Connectors

All on the boards, fitted by JLC. Part numbers: [bom.md](bom.md).

| Board | Connector | Mates with | Notes |
|---|---|---|---|
| USB board | USB-C, mid-mount (sinks into the board), through-hole shell legs (unverified: LCSC lists C2894902 as SMD-only) | PC cable | External; see "Strain" |
| USB board | USB-C, top mount, 4 through-hole shell legs (TYPE-C-31-M-12) | Display cable, straight end | Faces forward |
| USB board | JST-GH 8-pin, side entry (HCTL HC-GH-8PWT, a GH clone; JST SM08B-GHS-TB is out of stock) | USB link cable | Faces forward; positive latch |
| Backplane | JST-GH 8-pin, side entry | USB link cable | Back-left corner, faces back |
| Backplane | Slot connector ×5: 18 SMD pogo pins each (C2988082) | Pads under each module | Under each slot's front; pinout in "Slot connector" below (D23) |
| Haptic module | 1×3 2.54 mm vertical SMD header (HX PZ2.54-1x3P TP-YQ, C41417360) | Motor plug | On the module's front border, plug upright. Keyed plugs: check against the motor's |
| Backplane | 12-pin 1.0 mm flip-lock ZIF | Key FFC | Right end, on a small tab. Series resistors and three SRV05-4-P-T7 arrays on the key lines |
| Backplane | JST-SH 6-pin, top entry (BM06B-SRSS-TB) | Touch cable | Right end, front. One SRV05-4-P-T7 on SDA/SCL. Footprint only by default; fitted with the touch band (D24) |
| Backplane | HY2.0 3-pin, footprint always, fitting optional | Link lead to the 7B's J8 | GPIO6 link (see below) |
| Backplane | BOOTSEL button: reverse-mount tact switch (part not chosen), plunger through the board, reached through a pinhole in the case floor | — | Recovery ([recovery.md](recovery.md)) |
| Backplane | USB test pads | — | Bench recovery only. Silkscreen "unplug GH first" (the pads would back-feed with the cable in) |
| Frame PCB | 12-pin 1.0 mm flip-lock ZIF, top side | Key FFC | Right edge; the frame PCB's edge is about 1.2 mm inside the panel's metal edge (model) |
| Touch band (optional) | JST-SH 6-pin, side entry (SM06B-SRSS-TB), underside | Touch cable | Right end, past the last motor |

### Pinouts

**USB link, JST-GH 8-pin** (cable wired pin 1 to pin 1):
`1 GND · 2 VBUS · 3 CC1 sense · 4 D− · 5 D+ · 6 CC2 sense · 7 VBUS · 8 GND`.
The order is mirror-symmetric: a reversed cable (sold next to straight
ones) only swaps D+/D− (no enumeration, no damage) and CC1/CC2. GND on the
outer pins keeps VBUS off the edge pins, which touch first when a plug goes
in at an angle. GH contacts aren't staggered, so unplug the PC before
plugging or unplugging this cable. Check pin-1-to-pin-1 continuity on a new
cable before first power-up. USB full speed (12 Mbit/s) over ~100 mm of
unshielded wire is fine; JST-GH carrying USB is the drone-controller
(Pixhawk) convention. Route D+/D− as a pair on both boards.

**Upstream is high speed.** The CH334F talks 480 Mbit/s to the PC; only the
two downstream legs are full speed. See "USB board connections" for the
routing rule.

**Keys, 12-pin FFC:** `1 GND · 2–8 columns 1–7 · 9–11 rows 1–3 · 12 GND`.

**Touch, JST-SH 6-pin:** `1 GND · 2 3V3 · 3 SDA · 4 SCL · 5 3V3 · 6 GND`.
Mirror-symmetric, so a reversed cable only swaps SDA and SCL and can't
reverse-power the touch chip. There's no interrupt line: firmware polls the
controller. I²C pull-ups sit on the backplane; the band has a ferrite bead
plus 10 µF on its 3V3.

**Link to the display board, HY2.0 3-pin** (matches the 7B's J8:
`3V3 · GND · GPIO6`): only GND and the signal connect on the backplane.
Its 3V3 pin is left open, so the two boards' 3.3 V rails never meet. A
spare RP2350B pin sends a one-way UART to the ESP32-S3's GPIO6 through a
1 kΩ series resistor: page switches, activity (wake), the 3 s knob-hold
confirmation and settings reset ([protocol.md](protocol.md)). The
backplane always has the footprint; fitting the connector and buying the lead
is optional. Without it, the device still works standalone, but pages
don't change images and the display never idle-blanks without a host.

**Motors, 1×3 header:** phases U, V, W. The plug goes on either way round,
which changes the phase order. Calibration finds the order once; at the
first wake after power-up the firmware runs a small open-loop direction check and throws
away the stored calibration if it no longer matches.

### Cables

Bought ready-made; lengths from the model (`cad/assembly.py`, table in
[assembly.md](assembly.md)):

| Cable | Buy | Why that length |
|---|---|---|
| USB-C to USB-C, USB 2.0, one 90° side-exit plug + one straight plug | 100 mm | Loop sized for it (route 98 mm) |
| JST-GH 1.25 mm 8-pin, both ends, pin 1 to pin 1, 26 AWG | 100 mm | Route 73 mm, the rest as a gentle S. Check pin-1-to-pin-1 continuity on arrival |
| FFC 12-pin 1.0 mm, contacts on opposite sides (type B): LCSC C80646 | 100 mm | Top plate lifts 40 mm with it plugged in (needs 74 mm). LCSC stocks 100 mm, not 80 (D24); the extra ~20 mm folds with the rest of the spare in the gap by the right wall (check on Rev A) |
| JST-SH 1.0 mm 6-pin, both ends, pin 1 to pin 1 (touch band only) | 80 mm | Same (needs 75 mm). A longer spare folds against knob 4's bell |
| HY2.0 3-pin, both ends (optional link) | 50 mm | Backplane to the 7B's J8 (route 27 mm) |

**FFC contact side:** with top-contact ZIF connectors on the top of both
boards as modeled, the cable's contacts end up on opposite sides (type B).
If the ZIF picked has bottom contacts on one board, it flips to type A:
check before ordering.

## Strain and service

**External socket.** Plugging in, yanking or levering the PC cable must not
load solder joints:
- The socket is a **mid-mount** part with **through-hole shell legs**
  (unverified: LCSC lists C2894902 as SMD-only, so get its drawing; if it
  has no real THT legs, pick a mid-mount part that does), and its face sits flush with the inside of the back wall. The plug's overmold
  seats 2.5 mm deep into a 13 × 7 mm opening in the wall, so a sideways pull
  levers the plug against the case, not the socket. (Most cables'
  overmolds are 10.5–12.5 × 5.5–6.5 mm and seat fully; a bigger one stops
  at the wall.)
- **Push-in:** the USB board's arm rests against a printed backstop rib on
  the floor right behind the socket.
- **Pull-out:** the board's edge sits against the back wall.
- **Screws:** two M2×6 screws either side of the socket, two more in the
  main part of the board, into printed bosses.

**Internal USB-C.** The USB board's socket has four through-hole shell legs.
The cable is pressed into two printed clips on the tray floor, so tugging the
loop doesn't pull on either socket. Bends stay at 10 mm radius or more, and
the loop stays off the backplane and away from the motors (checked).

**Latches.** JST-GH and the ZIF connectors latch. JST-SH holds by friction
only; it's the short touch cable, which nothing pulls on once the case is
closed.

**Clips.** Three push-in clips printed with the tray (two for the
display cable, one for the USB link).

**Motors.** The 2204 lead (~30 cm with a 3-pin servo-style plug per one
listing; **verify on arrival**) leaves the motor base forward, under the
bell, and plugs into the upright 1×3 header on its module's front border.
The rest coils flat in the 7.4 × 3.8 × 13 mm space right of the plug, in
front of the bell and behind the cover's front wall, clear of the spinning
bell (model). A 30 cm lead may not fit there: measure it on arrival, and
ask the seller for a short lead if it doesn't (open question).

**Service loops.** The top plate lifts 40 mm with the key cable (and the
touch cable, if fitted) still plugged in (checked), which is enough to reach
the ZIF latch and the touch plug at the backplane's right end. The display board's USB cable and
the USB link unplug before the display or the backplane come out (guide in
[assembly.md](assembly.md)).

**Plug insertion.** Every plug has a straight path into its socket at the
step that connects it (checked in the model, like the screwdriver access).

## Key matrix

- **7 columns × 6 rows:** rows 1–3 are the 21 keys on the frame PCB. Row 4
  is the knob presses: slot k's press switch (haptic: the B3U; lite: the
  encoder's push switch) sits between column k and row 4, on the module.
  Rows 5 and 6 are the **module-ID rows** (below). Rows 4–6 reach every
  slot on the slot connector; columns 1–5 go one per slot.
- **One diode per switch** (SOD-123, e.g. 1N4148W) so any combination of
  keys can be held at once (needed for held modifiers and push-to-talk):
  21 on the frame PCB, 2 on each module (press and ID).
- **Module ID (D23):** each module ties its column to one ID row through a
  diode, a "switch" that's always closed: haptic → row 5 (ID A), lite →
  row 6 (ID B). A blank or an empty slot has neither, a future module type
  can have both. The firmware scans the ID rows at power-up and knows each
  slot's type; a haptic ID must also come with a valid MT6701 frame (CRC)
  before the slot's motor is enabled. Two GPIOs cover all five slots;
  an ADC resistor per slot would have needed five of the eight ADC pins
  and two more GPIOs than there are.
- **ESD:** the cap gaps leave ~5.6 mm air paths to the B3U terminals, and
  the lines run 100 mm of FFC to bare GPIO. The frame PCB has a GND guard
  ring around each window; the backplane has series resistors and three
  SRV05-4-P-T7 arrays at the ZIF.

## Slot connector (D23)

Every slot has the same 18-contact connector, whatever goes in it:
upright SMD pogo pins on the backplane's top side (BAT WIRELESS
BWCD-L3W2.0H1.0, LCSC C2988082: 3.0 mm tall, 1.0 mm stroke, ~1 N, 1.5 A,
10,000 cycles) press ENIG pads on the module PCB's underside. Pads aren't
parts, so both boards stay top-side only (D6). The module's printed base is
2.5 mm thick, which sets the pins' working height (0.5 mm in, ±0.25 mm
before a pin bottoms or lifts off); the pads are 1.8 mm across, so a
printed carrier can sit ±0.4 mm off and still mate.

Three rows of six at 3.0 × 2.5 mm, under the module's front border, front
row first, left to right as seen from above:

| Row | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| A (front) | GND | VMOT | VMOT | GND | 3V3 | GND |
| B | PWM_U / ENC_A | PWM_V / ENC_B | PWM_W | NSTDBY | SSI_DO | SSI_CLK |
| C | SSI_CS | COL_k | ROW_PRESS | ROW_IDA | ROW_IDB | nFAULT |

- **VMOT:** the eFuse-protected motor rail, two pins (1.5 A each). Lite
  modules and blanks leave it unconnected.
- **PWM_U/V/W, NSTDBY:** per slot. On a haptic module PWM_U/V/W drive the
  DRV8311H's INHA/B/C and NSTDBY its nSLEEP and INLA/B/C (3x PWM, D24). The
  10 kΩ pull-downs (RP2350 erratum E9) sit on the haptic module, next to its
  driver, so a lite module's lines aren't loaded.
- **nFAULT (C6, D24):** the haptic module's driver fault output, open
  drain. Bussed across the five slots to one GPIO with one 10 kΩ pull-up
  on the backplane (wired-OR, no diodes). Lite modules and blanks leave it
  unconnected.
- **ENC_A/B reuse PWM_U/V.** U and V of a slot are GPIO 2m and 2m+1 (one
  PWM slice, so they share a frequency; and consecutive, as the PIO
  quadrature reader needs). On a lite slot the firmware sets them as
  inputs. That's safe both ways: the lite module has 10 kΩ in series on A
  and B, so a slot misread as haptic drives at most 0.33 mA into a closed
  encoder contact; a haptic module misread as lite sees inputs, its
  pull-downs keep NSTDBY and the PWM lines low, and the driver sleeps with
  its outputs in Hi-Z (re-checked for the DRV8311H, D24).
- **SSI:** CLK and CS are shared by all slots (bussed on the backplane);
  each slot has its own data line, read together by PIO. Pull-downs on
  the data lines keep empty and lite slots at a known level.
- **COL_k, ROW_PRESS, ROW_IDA, ROW_IDB:** the key matrix (above).
- **Keying:** the module can't go in turned round: two key pins of
  different sizes (2.0 and 1.4 mm) under its base drop into matching
  holes in the backplane, and the pinout has GND at both ends of the power
  row. **No hot-plugging:** unplug USB before swapping a module (the pins
  aren't staggered, and the slot types are read at power-up).

## RP2350B pin budget (48 GPIO)

| Use | Pins |
|---|---|
| Per slot: PWM U, V, W (lite: encoder A, B on U, V), NSTDBY, SSI data; × 5 | 25 |
| SSI clock + chip select, shared | 2 |
| Key matrix: 7 columns + rows 1–3 (keys), row 4 (knob presses), rows 5–6 (module ID) | 13 |
| I²C to the optional touch band (polled, no interrupt; kept free without it) | 2 |
| 5 V monitor (ADC) | 1 |
| CC1/CC2 current-offer sense (ADC) | 2 |
| Link to the display board (UART TX, optional lead) | 1 |
| **Total** | **46 of 48** |

Two spare: one for the five drivers' nFAULT lines (open drain, wired-OR
through slot contact C6, D24), one free. The old single knob board used 45 (with a board-ID
strap); the slots add the second ID row and drop the strap. Nothing is
muxed.

USB, RUN and the SWD debug pins are separate pins on the RP2350B and don't
count against the 48.
Constraints for the schematic: each motor's 3 PWM signals should share one
PWM frequency; GPIO n and n+16 share a PWM channel, so map the 15 PWM
signals to 15 distinct channels in the schematic, with each slot's U and V
on one slice (2m, 2m+1); the three analog inputs need GPIO40–47. 10 kΩ
pull-downs on every `NSTDBY` and PWM net, on the haptic modules (RP2350
erratum E9; see [knob-module.md](knob-module.md)).

## Frame PCB connections

- 21 B3U switches + 21 diodes, 7 columns × 3 rows.
- GND guard ring around each key window.
- One 12-pin flip-lock ZIF connector (1.0 mm pitch) on the top side at the
  right edge.
- Nothing else: no chips.

## Touch band connections

Optional add-on, off by default (D24): `TOUCH_BAR = True` in
`cad/params.py` adds it to the model and the BOM.

- Touch controller **AT42QT2120** (SOIC-20, LCSC C614938) + 12 electrodes,
  1–10 kΩ in series with each electrode next to the chip. All 12 channels
  run as keys; firmware interpolates the position (the chip's own slider
  uses only 3 channels, too coarse for the band).
- JST-SH 6-pin, side entry, on the underside at the right end.

## USB board connections

- CH334F hub (QFN-24), USB ESD protection (one SRV05-4-P-T7 covering D±
  and CC), TVS (see "Input protection").
- **Crystal:** a 12 MHz crystal (C9002, basic) on XI/XO (load caps are
  built in), fitted, plus a 0 Ω link that can ground XI for crystal-free
  mode. The CH334
  datasheet says crystal-free mode isn't on by default on some package
  forms, and JLC can't confirm it at ordering.
- **Power strap:** PSELF strapped low (bus-powered), with a 0 Ω option to
  flip it. Both firmwares declare bMaxPower ≤ 100 mA, since Linux gives each
  port of a bus-powered hub only 100 mA and refuses configurations above
  it.
- **Placement:** the hub sits next to the external socket, so the
  480 Mbit/s upstream pair is under 15 mm: a 90 Ω coplanar pair with no
  vias, over unbroken ground, with the SRV05-4 at the socket. The
  long runs are the full-speed downstream legs.
- Confirm in the CH334F's datasheet row: MTT (one translator per port) and
  integrated terminations.
- Upstream: external USB-C (CC1/CC2 5.1 kΩ to GND, sensed through 10 kΩ).
  Shell to GND at the socket.
- Optional USB-PD sink (CH224-class) footprint on the upstream CC lines,
  not fitted by default (power policy above).
- Downstream port 1: JST-GH 8-pin to the backplane (VBUS through its own
  ~1.8 A eFuse). Port 2: USB-C to the display board (56 kΩ CC pull-ups,
  VBUS through a ~1 A eFuse). Ports 3–4
  unused (test pads).
