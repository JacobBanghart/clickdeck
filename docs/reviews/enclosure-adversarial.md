# Enclosure and assembly: adversarial review

**Summary**
1. The key stack leaves 0.05 mm of margin: the cap stops 0.2 mm above the glass and the switch needs 0.15 mm of travel. The frame PCB hangs off only its back and left edges, so with FDM layer steps, it can't hold that margin and the far keys will hit the glass before they click.
2. Parts of the enclosure that are modeled are missing from the build: the knob windows have no file, no BOM line and nothing holding them in. The panel screws go 2.95 mm into the panel, and the interference check hides this on purpose.
3. Stability, heat and service rest on numbers nobody has checked: the stand's density, the "3 N" key press, front feet that don't reach the desk, no case material named anywhere, and the panel loose on its posts while it's screwed from below.

Geometry comes from `model.full_device()` (run 2026-10-17). `assembly.py --check` reports 0 problems, and none of the findings below would trip it.

## Blocker

### B1. A 0.05 mm budget between the cap and the glass decides whether keys click at all
- **Assumption attacked:** that `GLASS_GAP = 0.2` (cad/params.py:31) is enough clearance for the cap.
- **Evidence:**
  - `key_cap()` starts the cap body at `st.pcb_bot` (cad/model.py:141), so the cap bottom and the frame PCB bottom both sit 0.2 mm above the glass (stack: glass 19.55, pcb_bot 19.75).
  - The B3U needs 0.15 mm of travel at 1.53 N (params.py:23; [Digi-Key B3U listing](https://www.digikey.com/en/products/detail/omron-electronics-inc-emc-div/B3U-1000P-B/1811777)). That leaves 0.05 mm for everything else.
  - The frame PCB is screwed only along its back edge (y = 47.8) and its left edge (x = −82.5) (model.py:651-652). The front-right key switch (≈66, −23) is about 100 mm from the nearest screw. The PCB there is a lattice of 3.6 mm webs (22 mm pitch, 18.4 mm windows).
  - Hand calculation, treating it as a cantilever of 8 FR-4 webs (E ≈ 20 GPa, I ≈ 9.8 mm⁴, L ≈ 71 mm, P = 1.53 N): δ ≈ PL³/3EI ≈ 0.9 mm. Even ten times stiffer, that is still more than 0.05 mm.
  - Height tolerances add up in the same direction:
    - The printed heights (panel posts 10.35 mm, plate posts 21.65 mm, frame bosses 3.3 mm) are not multiples of a 0.2 mm layer, so each prints about ±0.1 mm off.
    - The 1.6 mm PCB is ±10% (±0.16 mm).
    - `PANEL_T` is an estimate; the 2 mm plate is screwed only at its corners.
- **Failure scenario:** the PCB and cap sag about 0.05 mm, the cap bottom lands on the glass, and the switch never reaches its actuation point. The result is dead or mushy keys, worst at the front-right.
  - Off-center presses rock the cap about its nub onto the glass; dust ≥0.05 mm under a cap does the same.
- **Cheapest test:** print the tray and top plate and screw on a bare 1.6 mm FR-4 board cut from `full_frame_pcb_outline.dxf`. Then:
  - measure the PCB-to-glass gap with feeler gauges at all 21 keys, on a panel (or a dummy of the same height);
  - hang 150 g on the front-right switch spot and measure again.
- **Fix:**
  - [no-decision] Add frame-PCB mounting points on the right margin (there's ~3 mm free to `ix1`) and along the front strip between the knob windows. Add a check that compares stack tolerance against the gap.
  - [decision] Raise the cap-to-glass gap to ≥0.6 mm and make the cap's down-stop the PCB or plate, not the glass. This costs about 0.4 mm more image depth/parallax.

## High

### H1. Panel screws go 2.95 mm into the panel, and the check is blind to it
- **Evidence:**
  - M3x14 screws start at z = 2.3 (from the counterbore), so the tip is at 16.3. The panel back is at 13.35 (probe of `screw_panel_*` against `panel7_module`).
  - `check_interference` skips every (screw, target) pair (cad/assembly.py:182-188), so any length passes.
  - Whether the tabs are tapped is unverified (assembly.md:42 says so).
- **Failure scenario:** the screw tip punctures the backlight or diffuser stack, or bottoms out and lifts the panel off its posts, which shifts the glass height in B1.
- **Test:** measure tab thickness, thread and what sits behind the tab on the real 7B.
- **Fix:** [no-decision] Add a "tip protrudes ≤ tab thickness" check and size the screw to the measured tab (probably M3x12 or shorter).

### H2. The knob windows exist only in the render
- **Evidence:**
  - `knob_windows()` (model.py:432) makes five clear inserts that fit flush in the 2 mm plate with a 0.1 mm gap per side and no ledge.
  - No STL is exported (build.py:84-99 exports only the tray, plate, stand, cap and knob). They aren't in bom.md, and no assembly step installs them.
  - `knobN_hub` also has no STL.
- **Failure scenario:** if a builder leaves them out, there are five open 26×15 mm holes over the display and touch band. If they're improvised, a flush insert with nothing behind it falls into the case at the first press.
- **Fix:** [no-decision] Add a 0.8 mm ledge or under-lip, export the STLs, and add a BOM line and an assembly step. [decision] Alternatively, a single clear strip bonded under the plate.

### H3. The assembly steps assume three hands
- **Evidence:**
  - Step 5: "Lay the panel face up on its four posts, then turn the tray on its side and drive the four M3 screws up from underneath". Nothing locates the ~190 g panel (density 1.9 × 100 cm³), so on its side it slides off 8 mm posts.
  - Step 7: the plate is loose, the screws go in from below, and the knob caps aren't on yet. Inverting the case therefore rests ~0.56 kg on five epoxied hubs that stick up 7 mm (`hub_top = plate_top + 1 + 6`), loading the motor bearings and press tongues.
  - `check_access` only sweeps a 5 mm straight shaft along the screw axis (model.py:492). It has no gravity, hands, driver handle diameter or fixture.
- **Fix:** [no-decision]
  - Print locating pins or bosses on the panel posts and stops on the plate perimeter.
  - Put the "case on its back" step on a printed cradle, or fit the knob caps before closing.

## Medium

### M1. The knob press gap of 0.05 mm is smaller than one printed layer
- `KNOB_PRESS_GAP = 0.05` (params.py:258). The knob-board bosses are 1.65 mm tall (floor 3.0 to 4.65), which prints as 1.6 or 1.8 at 0.2 mm layers.
- At 1.6 mm, all five press switches are preloaded by the front-edge screws: always clicked, or a hair trigger. At 1.8 mm, travel is 0.2 mm larger.
- Test: print the tray and measure boss and rib heights with calipers.
- Fix: [no-decision] Make that height a multiple of the layer height and design for ≥0.2 mm, so the tongue takes up the gap.

### M2. The stability margin rests on guessed densities and a soft press
- stability.py:429 gives the 852 cm³ stand 0.6 g/cm³, which is 511 g, 48% of the 1068 g total. A 15% infill, 2-wall print is more like 0.25–0.3 g/cm³ (~240 g).
- Rerunning `stability.check` with 0.3 and 0.2 gives 813 and 727 g. The top-key tip force drops from 13.2 N to **11.0 and 10.2 N**, against a firm jab of 5–10 N, not 3 N.
- The USB plug sits 98–117 mm high, pointing up and back. About **4 N** of horizontal pull there tips the device backward.
- The tilted model puts the "front feet" 0.22 mm above the desk (`foot_front_0` min z). The front contact is the bare PLA bottom edge.
- With the slab parallel to the stand face, holding position needs μ ≈ 1.1 at that edge unless magnet friction carries the shear. That makes the magnets structural, not just locating.
  - USB-C extraction is 8–20 N (Type-C spec, from memory) against an estimated ~10 N of magnet shear friction, so unplugging the cable drags the slab up off the stand.
- Test: weigh the stand; luggage-scale push on the top key.
- Fix:
  - [no-decision] Move the front feet to the lower edge (an angled pad or a chamfer). Add a lip on the stand that catches the slab's bottom edge.
  - [decision] Add a steel weight in the stand (cost) or a wider/deeper stand (size).

### M3. No case material is named; heat and creep are not assessed
- `grep -i "PLA|PETG|ASA" docs/` finds nothing, so most builders will print PLA (Tg ≈ 55–60 °C, typical; not verified per grade).
- Steady dissipation is about 2.3 W (display 350 mA + hub + logic, wiring.md:127), with bursts up to ~10 W at the 1.5 A motor budget. It sits in a sealed box whose underside presses against the stand, with no vents.
- Estimate: ~0.05 m² of effective skin at h ≈ 7 W/m²K gives ~7 K average rise. Local spots (backlight LED edge, which sits on PLA posts; motors at the end-stop) will run hotter. A sunny desk adds more.
- The self-tapping threads are preloaded in PLA and creep faster when warm, so the plate loosens and rattles.
- Test: a 2 h thermocouple log on the panel frame, posts and motor at maximum backlight.
- Fix: [no-decision] State the material. [decision] PETG or ASA (warp and cost), or a vent slot pair.

### M4. Self-tapping joints are thin and are cycled at every service
- The M3 plate screws' heads bear on **0.7 mm** of floor (FLOOR 3 − counterbore 2.3, model.py:787-794). That is 3–4 layers, easy to pull through by overtightening.
- The frame-PCB M2x5 screws get 3.4 mm of engagement (~1.7d) in 5 mm bosses. They are removed for every cap or switch swap.
- The knob-board bosses have 1.4 mm walls.
- Load runs along the layers into 21.65 mm tall, 7 mm posts, and the plate is held twice: posts on the floor and plate on the wall tops, both at zero nominal gap.
- Test: drive and remove each joint 10× on a printed coupon, then torque it to failure.
- Fix: [no-decision] Make the floor web ≥1.2 mm, give the walls a deliberate 0.2 mm gap so the posts set the height. [decision] Heat-set inserts (≈$3, a soldering iron).

## Low
- **L1. Top plate STL orientation:** it's exported in assembly orientation (build.py:82). The 2 mm plate floats 21.6 mm above the bed on its posts, so a slicer will fill it with support unless the builder flips it. Fix: [no-decision] export it face-down.
- **L2. Dust, light and ESD paths:**
  - 0.2 mm cap gaps and a 0.5 mm annulus around each hub let dust onto the glass and motors.
  - The paperclip pinholes give a direct metal path to the ESP32 BOOT/RESET nets.
  - A sideways pull on the external USB-C overmold levers on a 2.5 mm PLA wall around a 14×8 mm opening.
  - Fix: [no-decision] felt or foam ring under each knob cap; ESD/TVS on BOOT/EN (or recessed buttons); a 3 mm wall boss around the port.
- **L3. Stand:** 852 cm³ is a ~10–15 h print. Fix: [decision] hollow or rib it.

## What I could not verify
- Real 7B tab thread and depth, and `PANEL_T`.
- B3U height tolerance.
- Magnet grade and actual pair pull.
- Desk friction coefficients.
- PLA Tg and creep for a specific filament.
- Actual dissipation of the panel and motors.
- Real FDM flatness of the plate.

All the numbers here are hand estimates or model probes, not measurements.
