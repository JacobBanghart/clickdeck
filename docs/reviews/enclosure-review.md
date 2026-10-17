# Enclosure and assembly design review

**Verdict: GO WITH CHANGES.** The architecture works: a screwed tray and plate, a magnetic wedge stand, plug-in cabling and top-down service.
Several vertical clearances (0.05–0.3 mm) can't be held by printed parts. The frame PCB is supported on only two edges. Both affect the PCB outlines, so fix them before the JLC order.
The stand collides with the tray's front feet, the knob-window covers have nothing holding them and aren't in the BOM, and the knob caps have no way to transmit torque. All of these are cheap to fix in `params.py`/`model.py`.

Scope: tray, top plate, stand, fasteners, magnets and feet, USB board mount, print fit, thermal, stability, the assembly and service sequence, and `cad/assembly.py --check`. I re-ran the check (0 problems) and probed the geometry in Python.

## Strengths

- **Clean service architecture.** Everything mounts upward from one tray, and the plate lifts off over the knob hubs with its cables still plugged in. Firmware can be recovered through pinholes without opening the case (`docs/assembly.md:135-174`).
- **The external USB-C port is properly strain-relieved.** The plug overmold seats in a 14×8 mm pocket in the back wall. A printed backstop takes insertion force, and the board edge against the wall takes extraction force (`cad/model.py:776-781`).
- **Stability margin is large.** Tip-over needs 13.2 N on a top-row key (`cad/out/summary.md:20`). I re-ran it with the stand at 0.35 and 0.2 g/cm³ (realistic infill) and still got 11.3 N and 10.2 N, against a ~3 N press.
- **The 42° tilt is inside the 40–45° target.** All parts fit a 256 mm bed. The tray prints floor-down and the plate face-down, which gives a good visible surface.
- **The automated checks are a real asset.** Interference, screwdriver access, plug insertion, cable reach and lift-out are each checked per step. Few hobby designs have this.
- **The BOM is generated from the model**, so screw and cable lengths stay in sync with the CAD.

## Issues

### Blocker

**B1. The vertical clearance stacks can't be held by FDM parts.** [no-decision]
- Gaps in `cad/params.py`:
  - knob press switch to tray floor: `KNOB_PRESS_GAP = 0.05` (line 82)
  - motor bell to plate underside: `MOTOR_TO_PLATE = 0.3` (line 119)
  - frame PCB to LCD glass: `GLASS_GAP = 0.2` (line 31)
- Each gap closes through 4–6 printed or estimated dimensions:
  - floor
  - 21.65 mm plate posts
  - 10.35 mm panel posts
  - bosses
  - `MOTOR_H` (EST; sellers disagree, `docs/open-questions.md`)
  - `PANEL_T`
- Typical FDM Z accuracy is ±0.1–0.2 mm per feature, plus warp across a 178 mm floor.
- Likely results:
  - some knob press switches held permanently pressed or never reached
  - motor bells rubbing the plate, especially when someone presses the touch band right above the motors
  - the frame PCB clamped onto the glass
- JLC3DP doesn't fix this: SLA is ±0.2 mm and MJF ±0.3 mm ([JLC3DP capabilities](https://jlc3dp.com/capabilities/3d-printing-service)).
- **Recommendation:**
  - Give each knob press switch an adjustable striker: an M2 set screw threaded up through the floor and set during calibration.
  - Raise `MOTOR_TO_PLATE` to ≥0.8 mm. Absorb it in `KNOB_GAP` or a slightly taller hub.
  - Decide deliberately whether the frame PCB lands on the glass border (see H1) or clears it by ≥0.5 mm.
  - Add a clearance check to `build.py` (minimum gap per mating pair).

### High

**H1. The frame PCB hangs from only its back and left edges.** [no-decision; changes PCB outline]
- Screws are only at y=47.8 (×3) and x=−82.5 (×2) (`cad/model.py:276-280`). The 170×96 mm lattice (3.6 mm webs) is cantilevered toward the front-right keys.
- A rough beam estimate gives >0.5 mm deflection at the B3U's ~1.5 N actuation force. The switch travel is 0.15 mm.
- So the front-right keys will bottom the PCB on the LCD glass before they click. That puts load on the LCD (pressure marks) and makes the feel vary from key to key.
- The 2-key prototype can't reveal this.
- **Recommendation:** add support at the front and right edges. Options:
  - thin spacers that land on the panel's inactive glass border (9.5 mm front, ~8.8 mm right)
  - plate-side bosses with low-head fasteners or heat-staked pins
- Do this before the frame PCB outline goes to JLC.

**H2. The tray's front feet collide with the stand.** [no-decision]
- `foot_front_0/1` (y=oy0+7, 1.5 mm proud, `cad/model.py:805-808`) overlap the stand by 83 mm³ each in the tilted model. The stand starts 6 mm behind the front edge (`params.py:127`).
- Result: the slab rides 1.5 mm off the stand face, the front magnets lose most of their pull, and the slab can rock.
- In the tilted model the feet also sit 0.22 mm above the desk, so the bare tray edge is what actually touches the desk.
- **Recommendation:**
  - Delete the tray feet, or move them onto the front face.
  - Put a rubber bumper strip along the front-bottom edge.
  - Run the interference check on the tilted model too (see H6).

**H3. The knob-window covers have nothing to sit on and aren't in the BOM.**
- `knob_windows()` (`cad/model.py:432-437`) makes five 2 mm clear covers, 0.1 mm smaller than the plate cut-outs and flush with the plate, with no ledge or lip.
- Nothing is under them except the panel, 5 mm down. They will fall in.
- They're missing from `docs/bom.md`, the STL exports and step 6 of `docs/assembly.md`.
- **Recommendation:**
  - Add a 0.8–1 mm ledge in the plate, or a flange on the cover.
  - Export an STL and add the covers to the BOM and step 6.
  - Simpler alternative: one clear SLA strip glued under the plate. [decision: look]

**H4. The knob cap–hub interface can't transmit torque.**
- The hub is a plain Ø10 cylinder. The cap bore is Ø10.2 (`cad/model.py:238-244`).
- A clearance fit with no flat or ribs means the cap spins on the hub, then falls off. The guide says caps "press on" (`docs/assembly.md:119`).
- **Recommendation:**
  - Give the hub a D-flat or spline.
  - Add 3 crush ribs in the cap bore, tuned with a test print.
  - Keep the straight pull-off.

**H5. The key-cap clearance is at or below printing tolerance.**
- `CAP_CLEAR = 0.2` per side (`params.py:12`), between an SLA cap (±0.2) and an FDM or SLA plate hole.
- FDM holes print undersize, and elephant's foot lands on the visible face-down top surface.
- Caps that bind give missed or sticky keys.
- **Recommendation:**
  - Add a `HOLE_COMP` parameter.
  - Print a 3×1 test coupon of plate holes with real caps before the full plate.
  - Do the same for the 8.2 mm magnet pockets (`model.py:800`, `:1060`).

**H6. The checks test the flat assembly only, with zero-clearance acceptance.**
- `assembly.py:885` builds `full_device(tilt=False)`, so the stand, its magnets and the feet are never interference-checked. That is how H2 got through.
- Overlap counts only above 0.01 mm³ (`assembly.py:194`), so touching or 0.05 mm-gap parts pass.
- Not checked at all:
  - minimum clearances
  - support or retention of loose parts (H3)
  - torque paths (H4)
  - printability (walls, overhangs, holes)
  - holding loose parts while the tray is inverted
- The "✅" table in `docs/assembly.md:16-23` reads as stronger than it is.
- **Recommendation:**
  - Run interference on the tilted model.
  - Add a minimum-gap table per mating pair.
  - Add a "floating part" check: every part touches a support.
  - Reword the table as "model checks".

### Medium

**M1. Self-tapping screws in the service path will strip.** [decision: cost/part]
- The four M3 plate screws and five M2 frame-PCB screws are undone on every service. Plastic threads typically survive about 5–10 cycles.
- The M2 bosses are Ø4.5 with a Ø1.7 pilot, about 1.4 mm walls (`params.py:143-145`), which splits easily.
- **Recommendation:**
  - Use M3 heat-set inserts in the plate posts (Ø7 already fits).
  - Grow the M2 bosses to Ø5.5, or use inserts.
  - Specify the screw type (e.g. ST2.2/ST2.9 or "PT" thread-forming pan-head) instead of "M3 self-tapping".

**M2. No material or print settings are specified.** [no-decision]
- Grep finds no PLA, PETG, ASA, wall-count or infill guidance.
- The display board draws 5 V × 350 mA ≈ 1.75 W ([Waveshare wiki](https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-7B)), plus the hub, MCU and motors, all in a sealed, unvented box.
- The bulk temperature rise is modest (~5–10 K), but PLA creeps under screw preload and softens near 55 °C (sunny desk, near a window).
- **Recommendation:**
  - Specify PETG or ASA, 4 walls, ≥25% infill around bosses, and print orientation per part.
  - Measure the internal temperature on the first build.

**M3. The stand is a solid 852 cm³ wedge.** [decision: cost/look]
- It is 511 of the 1068 g estimated mass. Expect a long print and lots of filament, and the JLC3DP "$10–25" (`docs/bom.md:58`) looks low for that much resin.
- Stability doesn't need the mass (still 10.2 N at 0.2 g/cm³).
- **Recommendation:**
  - Shell it (3 mm walls plus ribs) or make it an open frame.
  - Get a JLC3DP quote.

**M4. Assembly steps 5 and 7 need a third hand.** [no-decision]
- Step 5 tips the tray on its side while the 190 g panel sits loose on its posts.
- Step 7 holds the plate 40 mm up, operates a ZIF latch, then inverts the whole assembly with the plate unscrewed.
- **Recommendation:**
  - Add locating pins or bosses so the panel and plate can't slide.
  - Supply a printed prop that holds the plate at 40 mm.
  - Specify a raised build block so the from-below screws are driven with the tray upright.

### Low

- **L1. The plate is over-constrained.** It rests on both the wall tops and its own posts, which are separate printed dimensions. Make one of them the datum and relieve the other by 0.3 mm. There's also no lip registering the plate to the tray (visible seam). [decision: look]
- **L2. The magnet polarity wording is ambiguous.** "Opposite polarity to the tray's" (`assembly.md:125`) is unclear. Better: "stack each stand magnet on its mating tray magnet and mark the outward face".
- **L3. The tip-over calculation uses the wrong rear edge.** It uses the stand's bounding-box rear edge (`stability.py:258`) instead of the rear foot contact, about 3 mm inboard. The effect on the result is negligible.
- **L4. The USB cable leaves upward.** On the stand, the cable exits up and back at 42° and stands above the device (`cad/out/full_side.png`). Consider a right-angle cable in the BOM or an angled exit. [decision: look]
- **L5. The counterbores leave a thin skin.** The M3 counterbores leave 0.7 mm of floor under each screw head. This is fine in compression under the plate and panel posts, but watch for cracking if overtightened.

## Missing

- A tolerance and clearance budget (mating pairs, nominal gap, worst case).
- Material, print settings and orientation per part, and print test coupons (holes, magnet pockets, cap fit, hub fit).
- Knob-window covers in the BOM, the STL exports and step 6. Adhesive for the touch band is also not in the BOM.
- A support check for the frame PCB and plate deflection under a 5 N press.
- Thermal estimate or measurement plan, and vents if needed.
- Screw spec (thread-forming type, head style) and torque guidance.
- Flat-use story: whether the slab is meant to sit on a desk without the stand. Today it sits on only two front feet.

## Actions before ordering (in order)

1. Fix the frame PCB support (H1) and decide on the glass gap (B1). Both change the frame PCB outline, so do them before the JLC PCB order.
2. Fix the knob-board press striker and the motor-to-plate gap (B1). Confirm `MOTOR_H` with calipers on a real 2204 before freezing the tray.
3. Extend `assembly.py --check`: tilted-model interference, minimum gaps, floating-part check (H6). Then fix the feet–stand collision (H2).
4. Add retention for the knob-window covers and add them to the BOM (H3). Key the knob hub (H4).
5. Add hole compensation and print a coupon: cap holes, magnet pockets, hub fit, an M2/M3 boss with the chosen screws or inserts (H5, M1).
6. Specify PETG/ASA and print settings. Shell the stand and get a JLC3DP quote (M2, M3).
7. Add DFA aids: locating features, plate prop, build block (M4). Regenerate `docs/assembly.md` and `docs/bom.md`.
8. After the first build, measure the internal temperature, key feel across the grid, and knob drag. Feed the results back into `params.py`.
