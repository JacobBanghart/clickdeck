# Shorts and electrical-safety review

**Summary.** Nothing in the design routes a high-current rail where a normal assembly puts it straight onto ground. The worst risks are a reversed or mirrored JST-GH link cable, which puts raw VBUS onto RP2350B ADC pins that aren't 5 V tolerant, and the display board's 5 V rail feeding back through an always-on SY6280 into the hub and the PC. The VBUS branch to the knob board also has no current limit at all. The FFC is well designed: it carries no power and has GND on both ends, so a flipped cable is harmless.

Method: read docs/wiring.md, knob-module.md, pcb.md, assembly.md, bom.md and cad/params.py/model.py. Measured clearances in `model.full_device()` with `distance_to`. Ran `kicad-cli pcb drc` on proto-frame (0 violations). Read the Waveshare 7B schematic and loaded its STEP (801 solids). Checked the SY6280, TMC6300 and RP2350 datasheets and summaries.

## Blocker

### B1. Reversed or mirrored JST-GH link cable puts VBUS onto RP2350B ADC pins
- **Short path:** USB-board GH pins 1–2 (VBUS, PC-sourced, no limit) → cable reversed (n↔9−n) → knob-board pins 8/7 (CC2/CC1 sense) → RP2350B GPIO40–47 ADC pins. The only part on those lines at the knob board is the 100 nF filter cap. The 10 kΩ series resistors sit on the *USB-board* side, so they don't protect this path.
- **Evidence:** pinout `1 VBUS · 2 VBUS · 3 GND · 4 D− · 5 D+ · 6 GND · 7 CC1 · 8 CC2` (docs/wiring.md:162). The 10 kΩ is on the USB board (wiring.md:116, pcb.md:69). The analog inputs must be GPIO40–47 (wiring.md:260). RP2350's ADC-capable pins are not 5 V tolerant, and the digital pins are tolerant only while IOVDD is up ([cctalk quoting datasheet §14.8](https://classiccmp.org/mailman3/hyperkitty/list/cctalk@classiccmp.org/message/KQSLPKCY7ZRZ2JKE26ZVVPDONBWQNQRM/)). If the cable is reversed, the knob board is unpowered: its VBUS pins see only the CC lines through 10 kΩ. So 5 V back-powers the chip through the ADC clamp diodes.
- **How:** in assembly. The two side-entry headers face each other (USB board faces forward, knob board faces back; wiring.md table). Whether a "same direction" cable gives pin 1→1 depends on how each footprint is rotated and on the S-bend. AliExpress sells both cable directions, and the knob board isn't laid out yet.
- **Cheapest check:** before the first power-up, with the cable plugged in, measure continuity from USB-board GH pin 1 to knob-board GH pin 1.
- **Fix [no-decision]:** use a reversal-safe palindromic pinout: `1 GND · 2 VBUS · 3 CC1 · 4 D− · 5 D+ · 6 CC2 · 7 VBUS · 8 GND`. Reversed, this only swaps D+/D− (no enumeration, no damage) and CC1/CC2. Also add 10–22 kΩ in series at the knob-board ADC end, plus a clamp to 3V3.

## High

### H1. Display board's 5 V backfeeds the hub, the knob board and the PC's VBUS
- **Short path:** display 5 V rail → its native USB-C VBUS (wired directly, TVS only) → cable → USB-board SY6280 OUT → IN (the switch is enabled, so it conducts both ways) → hub VBUS → upstream USB-C VBUS pin and GH VBUS.
- **Evidence:** Waveshare schematic, "USB" block: Type_C2 VBUS is tied straight to the `5V` net. The same `5V` net is fed by the UART port through the Q10 AO3401 ideal diode and by the CS8501 boost converter from the J3 battery header ([schematic](https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-7B/ESP32-S3-Touch-LCD-7B-Schematic.pdf)). The SY6280 is "always on" (wiring.md:98). It blocks reverse current only while it is shut down ([SY6280 datasheet](https://olimex.com/Products/Components/IC/SY6280/resources/SY6280AAC.PDF)).
- **How:** in use or bring-up. A builder debugs the display through its UART port with the back cable unplugged, or fits a LiPo to J3 (the 7B supports a battery). The device then drives VBUS out of its upstream port, which a sink must never do, and powers the motors from a laptop's UART port. Two hosts fight if a second cable is plugged in.
- **Cheapest check:** power the display through the UART port only, then measure the back-wall USB-C VBUS pin.
- **Fix [no-decision]:** fit a reverse-blocking part at the display port: an ideal-diode switch, or a load switch with true reverse-current blocking, in place of the SY6280. Add a note in assembly.md: "never fit a battery to J3; unplug the back cable before using the UART port."

### H2. VBUS branch to the knob board has no fuse or current limit
- **Short path:** PC VBUS → USB-board trace → 2 JST-GH contacts / ~28 AWG wires → knob board. A short anywhere on this path (pinched cable, knob-board load switch failed short, bulk cap failed short) is limited only by the PC port.
- **Evidence:** the power path shows a current limit (SY6280) only on the display branch (wiring.md:96–100). The knob-board load switch is "part TBD" (bom.md:34). Plain load switches usually have no current limit. GH contacts are rated about 1 A each (wiring.md "Cap from the cable"). Chargers and powered hubs that offer 3 A often trip only well above that.
- **How:** in use: cable pinched under the display or a knob-board fault.
- **Cheapest check:** at schematic review, confirm that every VBUS consumer sits behind a limiter.
- **Fix [no-decision]:** put a 2 A-class eFuse or current-limited switch at the GH branch on the USB board, or at least a 1.5–2 A PTC. Choose a current-limited load switch with short protection on the knob board too.

### H3. Rev 0 knob-module power pads are unpolarized, and J1 puts 3V3 next to GND on a loose pin header
- **Short path:** bench supply reversed on J2 → TMC6300 VS reversed (bridge body diodes conduct, 22 µF ceramic caps reverse-biased). Separately, a Dupont jumper shifted one pin on J1 shorts dev-board 3V3 (pin 1) to GND (pin 2), or drives PWM_U into GND. A bench supply set above about 11 V exceeds the TMC6300's VS range.
- **Evidence:** knob-module.md:36 ("2 pads, large") and :45; J1 pinout at :74. The bring-up current limit of about 300 mA helps (knob-module.md "Bring-up order"), but only from step 2 onward.
- **How:** at the bench, the most likely place for a first-board mistake.
- **Fix [no-decision]:** fit a polarized two-pin connector (JST-VH/XT30) with large +/− silkscreen. Add a reverse-polarity P-FET or a Schottky in series, plus an SMBJ6.0A TVS across VS. Use a shrouded 2×7 header or a keyed JST-GH for J1, or move GND to pins 1 and 14 so 3V3 never sits next to GND.

## Medium

### M1. Motor mounting screws can reach into the stator windings
- **Short path:** an over-long screw pierces the winding enamel → motor phase (switching 0–5 V) to stator/screw → board copper around the hole (plated hole, pour or nearby pads near the MT6701).
- **Evidence:** "check length vs the 1.6 mm board" (assembly.md:34, bom.md:96). Gimbal-motor screws are sized for thicker mounts, so on a 1.6 mm board the same screw goes about 1–2 mm deeper. The TMC6300 has short-to-GND/VS detection that shuts the bridges off and sets DIAG ([SparkFun TMC6300 docs](https://docs.sparkfun.com/SparkFun_Three_Phase_Motor_Driver-TMC6300/single_page)). That makes the fault survivable, but the motor is ruined.
- **Cheapest check:** on arrival, measure thread depth to the windings. Before fitting, measure phase-to-stator resistance (should be open).
- **Fix [no-decision]:** state the maximum screw length (board + base thread depth − 0.5 mm). Make the motor holes NPTH with a 1 mm copper keep-out and no pour under the motor base.

### M2. Spare touch cable and FFC fold beside a spinning motor bell
- **Path:** about 70 mm of spare JST-SH (3V3/GND/I²C) and about 58 mm of spare FFC fold "into the gap by the right wall" (assembly.md:111). Knob 4's bell is 1.53 mm from the touch plug and 3.3 mm from the modeled cable (measured). Insulation rubbed through on a 28–32 AWG wire touches the bell. The bell is grounded through the bearing and stator if the mount holes are tied to GND, so that becomes a 3V3-to-GND short.
- **Fix [no-decision]:** add a printed fence or clip between motor 4 and the right-end connectors. Buy the shortest cables that still reach the 40 mm service lift (67 mm needed, so 70–80 mm rather than 100 mm).

### M3. Tray magnets sit right under the knob board
- **Path:** tray magnets at (±40, −46.1) are under the knob board's back strip. There is only 1.65 mm between the floor and the board's underside, and the right-angle motor-header tails (phase U/V/W) protrude there. A dropped M2 screw or a steel fragment gets pulled in and held across adjacent pins or pads.
- **Evidence:** `info['magnets']` and the stack (floor top 3.0, knob board underside 4.65).
- **Fix [no-decision]:** move the magnets out from under the knob board's footprint, or ask JLC to trim header tails flush and keep exposed bottom-side pads away from (±40, −46). Add a step to the assembly guide: "shake out and inspect before closing."

### M4. Touch cable reversal, and "NC" pins tied to GND by a copper pour
- **Path:** `1 3V3 · 2 GND · 3 SDA · 4 SCL · 5 INT · 6 NC` (wiring.md:169). Reversed, knob 3V3 lands on band pin 6. If either board's NC pad joins a GND pour, the touch controller is reverse-powered, and its substrate diode shorts 3V3 to GND. The headers are top-entry on one board and side-entry underside on the other, so they have the same mirror ambiguity as B1.
- **Fix [no-decision]:** leave pin 6 unconnected and not poured on both boards, or use a palindromic pinout `GND·3V3·SDA·SCL·3V3·GND`. Specify a PTC or a 10 Ω series resistor on the 3V3 feed.

## Low

- **L1. Frame PCB 0.2 mm over the glass and the panel's metal rim** (GLASS_GAP, params.py:31; measured 0.200 mm). The board is screwed only along its back and left edges, so key presses push its free edges down onto the panel. Untented vias or bottom-side pads then touch the rim, and a row or column can short to the display's GND. The keys misbehave but nothing is damaged. **Fix [no-decision]:** tent all vias, keep the bottom layer to traces under soldermask, put all diodes on the top side, and add Kapton over the rim.
- **L2. Motor bell 0.8 mm from the touch band and 1.0 mm from the panel frame** (measured; MOTOR_D 27.85 is an estimate). The top plate, 0.3 mm above the motor, limits tilt, so the bell can't rub when the case is closed. It can rub during bench calibration with no plate fitted. Measure the real bell diameter.
- **L3. Motor header is unshrouded and can be fitted offset by one pin.** Any orientation is safe (wiring.md:171), and offset leaves one phase open, which does no damage. A half-pulled plug leaves live phase pins exposed beside the coiled leads.
- **L4. Hot-plugging the JST-GH:** its contacts aren't staggered, so VBUS can make before GND and the return current flows through D± or CC. Add "PC unplugged" to assembly steps 4 and 7.
- **L5. Proto-frame through-hole wire pads** (TP1–3 at x = ±23.98) sit 0.2 mm above the 2.4" glass. Solder tails press on the glass, which risks cracks, not shorts. DRC is clean (0.2 mm clearance, 0.3 mm to edges). Copper is only 0.3 mm from the window edges (params.py:26), which is close to the board-cutting tolerance; 0.5 mm would be safer.
- **L6. Knob-board USB test pads:** recovering through them while the GH link is plugged in connects two VBUS sources. Label them "unplug GH first."

## Connector table

| Connector | Pinout | Keyed? | Can a misplug short a rail? |
|---|---|---|---|
| Back-wall USB-C (mid-mount, USB board) | std; CC 5.1 kΩ Rd | yes | No. Shell to GND; TVS + USBLC6 |
| USB-board USB-C → display (TYPE-C-31-M-12) | std; 56 kΩ Rp; VBUS via SY6280 | yes | No short, but backfeed (H1) |
| Display native USB-C (Type_C2) | VBUS = 5 V rail directly | yes | Backfeed source (H1) |
| Display UART USB-C (Type_C1) | via ideal diode | yes | Plugging the internal cable into it is harmless; host plugged in here backfeeds through Type_C2 |
| JST-GH 8p ×2 | 1 VBUS 2 VBUS 3 GND 4 D− 5 D+ 6 GND 7 CC1 8 CC2 | yes | **Yes, reversed cable puts VBUS on ADC pins (B1)**; VBUS sits next to GND at pins 2–3 |
| ZIF 12p ×2 (FFC) | 1 GND · 2–8 cols · 9–11 rows · 12 GND | yes (flip-lock) | No. A type A/B mix-up only remaps the matrix |
| JST-SH 6p ×2 | 1 3V3 2 GND 3 SDA 4 SCL 5 INT 6 NC | yes | Yes if reversed and NC is poured to GND (M4) |
| Motor 1×3 2.54 ×5 | U V W | no | No (any orientation; offset leaves one phase open) |
| Knob USB test pads + BOOTSEL | VBUS/D±/GND | n/a | Backfeed if used with GH plugged in (L6) |
| Display J9 POWER, H1, H3, J8 (HY2.0, unused) | 5 V/GND etc. | yes | No (nothing plugged in) |
| Display J3 battery (MX1.25) | VBAT/GND | weak | Fitting a battery causes backfeed (H1); battery polarity is a known MX1.25/PH trap |
| Rev 0 J2 | 5 V, GND pads | **no** | **Yes, reversed polarity (H3)** |
| Rev 0 J1 1×14 | 1 3V3 2 GND 3 PWM_U … | **no** | **Yes, an offset Dupont shorts 3V3 to GND (H3)** |
| Rev 0 J3 1×3 | U V W | no | No |
| Proto frame TP1–3 | K1, GND, K2 | n/a | No (no rail) |

## What I could not verify

- Whether the 7B's metal back frame, M3 tabs and USB shells are tied to GND, and where the panel's backlight/AVDD/VGH ribbon runs: the STEP contains no ribbon solid. If the ribbon wraps the front edge of the panel, it sits in the 1.0 mm gap beside the motor bells.
- How far the M3 panel screws reach: their tips go 2.95 mm above the panel's back plane, and the tab construction isn't visible in the STEP.
- The real 2204's thread depth, lead insulation and bell diameter.
- How the GH and SH footprints will be rotated, since the knob board, USB board and touch band aren't laid out yet.
- The SY6280's exact reverse-blocking condition: I read secondary summaries, not the full datasheet table. The same goes for the exact FT marking of RP2350 GPIO40–47.
- I didn't run `cad/assembly.py --check`. All clearances above come from direct `distance_to` measurements.
