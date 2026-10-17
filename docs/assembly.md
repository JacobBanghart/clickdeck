# Assembly and service guide

> [!CAUTION]
> **Generated from the CAD model; nothing here has been built.** The pictures and
> checks come from `cad/assembly.py`, so they show the design as modeled, not a
> verified build. Expect the first real assembly to find problems the model can't.

![Assembly animation](../cad/out/assembly/assembly.gif)

Sharper version: [assembly.mp4](../cad/out/assembly/assembly.mp4).

## Build checks

Run on every build of this guide (`.venv/bin/python cad/assembly.py --check`).

| Check | Result |
|---|---|
| Parts don't overlap in the finished device | ✅ no overlaps |
| Every screw reachable with a straight screwdriver at its step | ✅ 23 of 23 screws reachable |
| Every plug slides straight into its socket at its step (plug bodies modeled at full size: USB-C overmold 12.5×6.5 mm) | ✅ 14 of 14 plugs |
| Cables clear every part (motor bells included); bends ≥ 10 mm on the USB-C cable; plate cables reach with the plate lifted 40 mm | ✅ all clear |
| Service: top plate, then display, then knob board lift straight out | ✅ all three lift out |
| A paperclip reaches BOOT and RESET through the back wall | ✅ both reachable |

## Hardware

| Part | Qty | Used in step |
|---|---|---|
| M2x6 self-tapping | 4 | 2. Screw in the USB board |
| M2x5 self-tapping | 6 | 4. Screw the knob board into the tray; plug in the USB link |
| M3x14 machine | 4 | 5. Mount the display; plug in its USB cable |
| M2x5 self-tapping | 5 | 6. Build the top plate (on the bench) |
| M3x10 self-tapping | 4 | 7. Close the case |
| Motor mounting screws (usually supplied with the 2204; check length vs the 1.6 mm board) | 5 sets | 3. Build the knob board (on the bench) |
| Hook-and-loop cable ties, ~10 mm wide (strap each motor lead coil through its two slots) | 5 | 3. Build the knob board (on the bench) |
| Magnets 8×1.5 mm (tray) | 4 | 1. Print the case; fit magnets and front feet |
| Magnets 8×3 mm (stand) | 4 | 9. Put it on the stand |
| Rubber feet 10×1.5 mm | 6 | 1. Print the case; fit magnets and front feet, 9. Put it on the stand |
| Epoxy | — | knob hubs, magnets |

Self-tapping screws go into printed plastic: drive them slowly and stop when snug.
Panel screws thread into the display's metal tabs (check the thread on the real
board; the drawing says M3).

### Cables

All bought ready-made and plugged in: nothing to solder or crimp. The length to buy
is the shortest common stock length that covers the modeled route (plug tip to plug
tip, plugs included) and, for the two cables to the top plate, the reach with the
plate lifted. The display cable's loop is sized for 100 mm; 95-110 mm cables fit.

| Cable | Connects | Buy | Route in the model | Step |
|---|---|---|---|---|
| USB-C to USB-C, USB 2.0 (3 A), one 90° side-exit end + one straight end | display board USB port ↔ USB board | **100 mm** | 97 mm | 5. Mount the display; plug in its USB cable |
| JST-GH 1.25 mm 8-pin, plugs both ends, pin 1 to pin 1 ("same direction") | USB board ↔ knob board | **100 mm** | 74 mm | 4. Screw the knob board into the tray; plug in the USB link |
| FFC, 12-pin, 1.0 mm pitch, contacts on opposite sides (type B) | frame PCB ↔ knob board | **80 mm** | 22 mm; 67 mm with the plate lifted 40 mm | 6. Build the top plate (on the bench) |
| JST-SH 1.0 mm 6-pin, plugs both ends, pin 1 to pin 1 | touch band ↔ knob board | **100 mm** | 30 mm; 67 mm with the plate lifted 40 mm | 6. Build the top plate (on the bench) |
| Motor leads (on the motors) | motor ↔ knob board header | 300 mm assumed | ~37 mm routed; the rest coils on the back strip (6.6 mm high, 6.7 mm room) | 3. Build the knob board (on the bench) |

Pinouts and the strain-relief measures: [wiring.md](wiring.md). Every part with
sources: [bom.md](bom.md).

## Assembly

### 1. Print the case; fit magnets and front feet

Print the tray, top plate and stand (all fit a 256 mm bed). Glue the four tray magnets into the pockets underneath (check polarity against the stand's magnets first) and stick the two rubber feet near the front edge.

![Print the case; fit magnets and front feet](../cad/out/assembly/step1_tray.png)

### 2. Screw in the USB board

Lower the USB board into the back-left corner, external USB-C socket first: the socket's face sits flush behind the opening in the back wall, the board's arm rests against the printed backstop, and its edge touches the back wall. Drive the four M2 screws into the floor bosses (two of them either side of the socket).

![Screw in the USB board](../cad/out/assembly/step2_usb_board.png)

![Screw in the USB board](../cad/out/assembly/step2_usb_board_screws.png)

### 3. Build the knob board (on the bench)

Glue a diametric magnet to the bottom end of each motor shaft. Screw each motor's base to its tongue on the knob board, centered over the MT6701, with its lead pointing back. Bond a printed hub to the top of each motor bell (epoxy, or M2 screws if the bell has holes). Plug each motor's 3-pin plug onto the header behind its tongue (any way round: the firmware finds the phase order), coil the spare lead flat on the back strip and strap it through the two slots with a hook-and-loop tie. Keep the lead clear of the bell. Calibrate each knob now, before it's buried in the case.

![Build the knob board (on the bench)](../cad/out/assembly/step3_knob_sub.png)

### 4. Screw the knob board into the tray; plug in the USB link

Lower the knob board in with its back strip resting on the floor ribs, and screw it down along its front edge into the floor bosses (self-tapping, don't overtighten). Plug the JST-GH cable into the knob board's back-left corner and into the USB board (both click), and press it into its floor clip.

![Screw the knob board into the tray; plug in the USB link](../cad/out/assembly/step4_knob_board.png)

![Screw the knob board into the tray; plug in the USB link](../cad/out/assembly/step4_knob_board_screws.png)

### 5. Mount the display; plug in its USB cable

Lay the panel face up on its four posts, then turn the tray on its side and drive the four M3 screws up from underneath into the panel's tabs. Plug the right-angle end of the USB-C cable into the display board's USB port (the one nearer the back; the cable points forward), loop it round in the bay and plug the straight end into the USB board. Press the cable into its two floor clips, clear of the knob board.

![Mount the display; plug in its USB cable](../cad/out/assembly/step5_display.png)

![Mount the display; plug in its USB cable](../cad/out/assembly/step5_display_screws.png)

### 6. Build the top plate (on the bench)

Lay the top plate face down. Drop the clear caps into their holes, tabs toward the front edge. Plug the key cable (FFC) into the frame PCB's ZIF connector (flip the latch up, slide the cable in, latch down) before screwing the frame PCB onto the plate's bosses (switches facing the caps). Stick the touch band under the plate below the knob display windows and plug the touch cable into it.

![Build the top plate (on the bench)](../cad/out/assembly/step6_top_plate_sub.png)

![Build the top plate (on the bench)](../cad/out/assembly/step6_top_plate_sub_screws.png)

### 7. Close the case

Hold the top plate above the tray (its cables reach with the plate ~40 mm up). Plug the key cable into the knob board's ZIF connector at its right end and the touch cable into the header beside it; the spare cable folds into the gap by the right wall. Lower the top plate over the knob hubs, then drive the four M3 screws up from underneath into its posts.

![Close the case](../cad/out/assembly/step7_close.png)

![Close the case](../cad/out/assembly/step7_close_screws.png)

### 8. Press on the knob caps

Press each knob cap onto its hub. They pull straight off for service.

![Press on the knob caps](../cad/out/assembly/step8_knobs.png)

### 9. Put it on the stand

Glue the stand's magnets in (opposite polarity to the tray's) and stick its four feet on. The slab snaps onto the stand with the magnets.

![Put it on the stand](../cad/out/assembly/step9_stand.png)

### 10. Plug it in

Plug a USB-C cable from the computer into the port in the back wall. A C-to-C cable lets the device see how much current the port offers; an A-to-C cable works too, with weaker haptics (500 mA budget).

![Plug it in](../cad/out/assembly/step10_plug_in.png)

## Service

### Open the case

1. Pull the slab off the stand (magnets).
2. Pull the five knob caps straight up.
3. Undo the four M3 screws under the tray (the top plate's posts).
4. Lift the top plate straight up, with the caps, frame PCB and touch band on it.
   Its two cables reach 40 mm; at that height unplug them at the knob
   board's right end (flip the ZIF latch up to free the key cable; pull the touch
   plug straight up).

![Top plate lifted off](../cad/out/assembly/service_open.png)

### Swap a key cap or switch

With the top plate off and face down, undo the frame PCB's screws, lift the PCB
and replace the cap or switch.

### Recover the display board's firmware

No need to open the case: press BOOT (hold) and RESET through the two small holes
in the back wall with a paperclip, then flash over USB.

![Back wall pinholes](../cad/out/assembly/service_pinholes.png)

### Recover the knob board's firmware

The knob board has its own USB connection through the hub, so the host app reboots
it into the RP2350B's built-in bootloader and copies a UF2 file. If the firmware is
too broken for that, open the case, hold the BOOTSEL button on the knob board and
unplug/replug the USB cable at the back: it shows up as a USB drive.

### Replace a motor or the knob board

Open the case. Unplug the USB-C cable at the display board, remove the display
(four M3 screws from underneath), unplug the JST-GH cable at the knob board (press
the latch), then undo the knob board's screws along its front edge and lift it out.
Its back strip sits under the display, which is why the display comes out first.
A motor unplugs from its header; cut its hook-and-loop tie free.

