# Touch band: adversarial review

**Summary.** I expect the band to fail, and the likeliest cause is false touches from the hand turning a knob. The knob rims are 5 mm from the band, and each motor's bell, driven by PWM, sits 0.8 mm from the electrode edge. The prototype test can't reveal this: its band is 26 mm long, made of copper tape on 3 mm cast acrylic, with no 7" panel and one motor. The controller isn't chosen, and the MPR121 used for testing has been discontinued since 2019. Two parts of the stack decide how well touches come through the plate, the plate material and the adhesive, and the docs don't specify either.

Geometry used below is from `model.full_layout()` and `make_stack()`, read-only. The band runs from y −41.3 to −52.5 (11.2 mm tall) and is about 155 mm long. The motor bell tops are at z 24.35, which is 0.3 mm below the plate (plate_bot 24.65). The knob rims (Ø19) reach y −57.7. The panel's front border runs from y −42.8 to −52.3, so it sits directly under the band, with the glass at z 19.55.

## Blocker

### B1. Turning a knob registers as a touch on the band
- **Assumption attacked:** a band sitting between the knobs and their displays can tell a deliberate tap from a hand gripping a knob (`docs/prototype-tests.md:43`).
- **Evidence:**
  - The band's bottom edge is `motor_edge + TOUCH_BAR_MARGIN` (`cad/model.py:448`, `cad/params.py:116`), which puts it 0.8 mm from the Ø27.85 bell.
  - The bell top is 0.3 mm below the plate (`cad/params.py:119`), so the bell and the 0.8 mm band PCB overlap in height.
  - The knob rim is 5.2 mm from the band. The knob stands 15 mm tall, 1 mm above the plate (`cad/params.py:96-102`).
  - On a 42° slab, the fingertips gripping a knob sit on its upslope side, which is the band side.
  - The bell is bonded to the knob hub, so a finger on the knob couples to the bell (`docs/assembly.md:81`).
- **Failure scenario:** turning knob 3 makes the band report a touch at about 0.5 and swipe events whenever a fingertip moves. Haptic detents then make it jitter.
- **Cheapest test:** stick a 26 × 10 mm piece of copper tape 0.8 mm from a running 2204 under 2 mm of plastic, with a printed Ø19 knob 5 mm away. Log MPR121 baseline minus filtered data while gripping and turning the knob. If the delta goes past the touch threshold, B1 is confirmed.
- **Fix:**
  - [no-decision] Add a driven shield or a hatched-ground guard trace along the motor-side edge.
  - [no-decision] In firmware, ignore the band for 300 ms around knob motion or press events.
  - [decision] Make the band taller by moving the knobs further forward (more than 4 mm), or move the band above the windows.

## High

### H1. The prototype can't validate the design
- **Assumption attacked:** step 3b (`docs/plan.md:169`) answers the question in `docs/open-questions.md:37`.
- **Evidence:**
  - The prototype band is `touch_bar(st, L, win[0], …)` (`cad/model.py:1152`). That is 26 mm wide with one knob position, but the test asks for "each of the knob-display positions" and "swipe left and right" (`docs/prototype-tests.md:41-42`).
  - The prototype plate is 3 mm cast acrylic (`cad/params.py:161`). Cast acrylic is solid and flat, and copper tape sticks to it with no air gap.
  - The real build is a 2 mm printed plate of unspecified material (`docs/bom.md:58`), with an FR-4 board that has a ground pour and traces on its back.
  - The prototype has none of the main noise sources: 5 motors, the 7" panel and the backlight boost.
- **Failure scenario:** the prototype passes, and the full build then fails because of B1, H2 and H3.
- **Cheapest test:** before the full order, build the test strip at full length (155 mm, 10–12 segments) under an offcut of the real printed plate. Mount it over a running 7" panel with two motors spinning.
- **Fix:** [no-decision] Rewrite the touch section of prototype-tests.md to use a full-length strip, the real plate material and the noise sources running.

### H2. Air gaps from an unspecified plate material and adhesive
- **Assumption attacked:** "stick the touch band under the plate" (`docs/assembly.md:103`) gives good coupling.
- **Evidence:**
  - The BOM lists no adhesive. Its only adhesive items are feet and magnets (`docs/bom.md:94`).
  - The plate has posts and bosses on its underside (`cad/model.py:861-868`), so it prints face-down. That leaves the band's mounting face as the last printed top layer, which tends to pillow, and a 155 mm part can bow.
  - A 1.6 mm FR-4 strip won't conform to a bowed plate.
  - Infineon, recommending nonconductive adhesive film: it "increases sensitivity by eliminating the air gap between the overlay and the sensor pads" (https://community.infineon.com/t5/CAPSENSE-MagSense/CapSense-Capacitive-Sensing-Design-Considerations/td-p/162166).
  - An air gap reduces sensitivity "due to the fact that air has a much lower dielectric constant than most overlay materials" (https://www.embedded.com/?p=4421859).
- **Failure scenario:** sensitivity varies along the band, so position is non-linear and one end goes dead. Changes in humidity or heat lift the tape.
- **Cheapest test:** with a feeler gauge and a straightedge, measure how flat a printed plate's underside is under the band. Compare per-segment deltas with 0.1 mm and 0.3 mm shims.
- **Fix:**
  - [no-decision] Specify a thin acrylic transfer adhesive such as 3M 467MP, at 100% coverage.
  - [no-decision] Print the band area at 100% infill with no ironing gap, and add a recess so the band can't bow.
  - [decision] Specify the plate material: PETG, PLA or JLC resin.

### H3. Noise from motor PWM and the display directly under the band
- **Assumption attacked:** the band is in a quiet spot.
- **Evidence:**
  - Each bell is the outer rotor of a winding switched by PWM through 3 phases (`docs/pcb.md:32`). The bells are 0.8 mm from the electrode.
  - The panel's front border (estimated, `cad/params.py:41`) is directly under the band and 4.3 mm below the board's underside. That border usually carries the gate/source fan-out.
  - The backlight boost is on the same panel (`docs/plan.md:79`).
  - The MPR121 has no frequency hopping. Its charge/discharge measurement is synchronous with its sample period.
- **Failure scenario:** during haptic detents, baseline tracking drifts or fires spurious touches. Swipe position jitters with backlight brightness.
- **Cheapest test:** for each segment, log the 0.5 s standard deviation of raw counts with motors off, then on, at 0/50/100% backlight.
- **Fix:**
  - [no-decision] Put a solid or hatched ground on the band's bottom layer as a shield toward the panel.
  - [no-decision] Pick a controller with spread-spectrum or frequency hopping.
  - [no-decision] Stagger the band's sampling between PWM edges if the controller allows it.

### H4. No controller exists yet, and the obvious choices don't fit
- **Assumption attacked:** an LCSC part can be "picked from the library" later (`docs/open-questions.md:59`, `docs/bom.md:38`).
- **Evidence:**
  - NXP has discontinued the MPR121 (PCN16772; longevity ended in 2019) and offers no replacement (https://forum.seeedstudio.com/t/mpr121-end-of-life/263331). Prototype breakouts are therefore old stock or clones, and the full build can't reuse that tuning.
  - The MPR121 has no slider engine, so position interpolation would have to be written for the RP2350.
  - The AT42QT2120 drops to "1 to 9 keys if wheel or slider option enabled" (https://www.mouser.in/new/microchip/atmelat42qt2120). Its slider is built from 3 channels, which over 155 mm gives roughly 50 mm per electrode. That is too coarse for linear position.
- **Failure scenario:** the schematic is blocked, or a part gets substituted late without tuning.
- **Cheapest test:** search the JLC parts library for slider-capable controllers before layout, and record stock and the extended-part fee.
- **Fix:** [decision] Choose one:
  - RP2350 PIO self-cap sensing on about 10 GPIO. The pin budget leaves 4 free (`docs/wiring.md:253`), so this needs an expander.
  - A 12-channel controller with 10 discrete segments and host-side interpolation.
  - An Azoteq/Infineon slider controller, if JLC stocks one.

## Medium

### M1. Panel thickness conflict: 0.8 mm planned, 1.6 mm in the panel
- **Assumption attacked:** the band can share the 1.6 mm panel with the other boards (`docs/bom.md:19` against `cad/params.py:115`).
- **Evidence:**
  - At 1.6 mm, the band's underside and its side-entry SH header (2.9 mm tall, `cad/params.py:194`) drop 0.8 mm. `assembly.py --check` only verifies the 0.8 mm case (0 problems).
  - The stiffer board makes H2 worse.
  - The thickness itself barely matters electrically, because the electrodes are on the top copper and the FR-4 sits behind them.
- **Cheapest test:** set TOUCH_BAR_T to 1.6 in a scratch copy and rerun `--check`.
- **Fix:** [decision] Use 1.6 mm with a full-coverage adhesive and a printed recess, or order the band as a separate 0.8 mm board, which is about $5 more.

### M2. Users can't see where the band is
- **Assumption attacked:** users will tap the band and not the display.
- **Evidence:** the band is hidden under the opaque plate. On the + XL, the touch strip *is* the display. The band's top edge is 0.8 mm below the clear knob windows (`cad/model.py:447`).
- **Failure scenario:** users tap the knob display, and that registers only weakly or not at all.
- **Fix:** [no-decision] Add a printed groove or texture over the band. [decision] Extend the electrodes up under the window edges.

### M3. No ESD path or series resistors
- **Evidence:**
  - `docs/wiring.md:169,269-272` lists only the controller and electrodes. ESD/TVS parts appear only on the USB board (`docs/bom.md:45`).
  - The window inserts leave a seam 0.8 mm from the band (`cad/model.py:434`), giving a discharge a short path through the gap.
- **Fix:** [no-decision] Add 1–10 kΩ series resistors on each electrode near the controller, and TVS diodes on the SH cable at the knob board.

## Low

### L1. Moisture
A damp palm resting while the knob turns makes B1 worse. The design has no driven shield for liquid tolerance. [no-decision] Fold this into the shield in H3.

### L2. Is swiping on a 10 mm band at 42° feasible?
The 11.2 mm height comfortably fits a fingertip, and the 2 mm overlay is well below the segment pitch. Azoteq's rule is that pitch "must be larger than the overlay thickness" (https://www.azoteq.com/images/stories/pdf/azd076_how_to_design_touch_electrode_for_non_uniform_and_curved_surfaces_3d_touchpads.pdf). The real risk is the knuckles. A swipe has to pass under the 16 mm-tall knobs that stand 5 mm in front of the band, which leads back to B1.

## What I could not verify
- LCSC/JLC stock for the AT42QT2120, CY8CMBR3116, IQS7211 and CAP1214. The LCSC search wasn't reachable.
- The exact overlay and air-gap figures in Microchip AN2934 and Infineon AN85951. I couldn't extract text from the PDFs, so I used secondary quotes.
- What the panel's front border actually holds, and the PWM frequency planned for the TMC6300 drive.
- The real 2204 bell sizes (marked EST in `cad/params.py:70`).
- The permittivity of the chosen plate material.
- Whether the side-entry SH header clears everything with a 1.6 mm band. I didn't modify params to check.
