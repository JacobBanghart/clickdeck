# Design review: keys (caps, B3U switches, frame PCB, key matrix)

**Verdict: go with changes.** The prototype frame PCB is cheap and is the right way to learn about key feel, but it can't be ordered as it stands.
In the prototype, the mounting hardware and the wire pads sit over the 2.4" glass with a 0.2 mm gap. Fix that, and add a second switch position so the order can test the main risk.
The key concept has two unproven risks: a single switch at one edge of an 18 mm cap, and a vertical stack with 0.05 mm of margin above the LCD. The prototype has to answer both before the 21-key board is drawn.

## Strengths
- **One source of truth.** The board outline, windows, switch positions and holes come from the CAD (`cad/out/proto_frame_pcb.json`, read by `hardware/proto-frame/gen_pcb.py`), so the PCB can't drift away from the case. `check_key_fit()` (`cad/model.py:121`) guards the 3.6 mm strip, the reach of the tab and lip collisions.
- **DRC and outputs check out.** I reran `kicad-cli pcb drc` at every severity and got 0 violations. The CPL coordinates (SW1/SW2 at X 89/111, Y -103.39) match the F.Paste Gerber pads. The B3U body sits 0.3 mm from the key window, and its pads are 0.7 mm from it.
- **Full-device frame screws are placed only where no glass is under the head** (`cad/model.py:651`). That is good thinking, and the prototype should copy it.
- **Sound matrix and connector plan.** One diode per key gives full rollover, which push-to-talk and held modifiers need. The FFC has GND on both outer pins (`docs/wiring.md`, Pinouts). The knob presses share the columns. `assembly.py --check` passes with 0 problems, including the FFC length with the plate lifted (route 22 mm, 67 mm needed, 80 mm bought).
- The docs are candid about what is unverified, and the prototype tests already include corner presses and rattle.

## Issues

### Blocker
**B1. Prototype: screws and wire pads sit over the glass with a 0.2 mm gap.** The proto frame PCB (±26.98 × ±20.86 mm) lies entirely inside the 2.4" glass (±30.13 × ±21.36; model bounding boxes from `model.prototype()`). The four M2 holes at (±23.98, 8/−12) take standoffs from above (`model.py:1138`), so a screw head or nut ends up under the PCB, 1.3 mm or more tall in a 0.2 mm gap. The through-hole K1/K2/GND pads (`gen_pcb.py:126-131`) put solder and wire ends on the glass side. Either the PCB gets lifted, which wrecks the key stack, or the glass gets loaded.
*Fix:* widen the proto outline past the glass in X (to about ±36 mm). Put the holes and wire pads out there, and check what is on the module's header side. Alternatively use SMD wire pads on top plus adhesive mounting. **[no-decision]**

### High
**H1. One switch at one edge won't click for presses near the far edge.** The only support under the cap is the nub on the switch (`model.py:104-107`). A press near the far edge rotates the cap about the nub until the cap's bottom lands on the glass 0.2 mm below, and the switch never actuates. `docs/plan.md` says "Guides in the case stop the cap from tilting", but the model has no guides. There is only 0.2 mm clearance per side through the plate and the PCB window, over about 6.9 mm of height, which allows about 3° of tilt. The far edge needs only about 0.6° to reach the glass.
*Fix:* on this prototype order, add a second B3U footprint on the top strip above each key window (4.3 mm wide there, so it fits). Wire each one to its own pad, and order caps with a nub at both ends. Then test one switch, two switches, and a far-edge fulcrum variant. Choosing two switches per key in the full build changes cost (21 more switches) and strip routing. **[decision]**

**H2. The vertical stack has about 0.05 mm of margin, and the LCD is the overtravel stop.** The B3U travels 0.15 mm ([JLC C231329](https://jlcpcb.com/partdetail/B3U-1000P/C231329)) and the cap's bottom is 0.2 mm above the glass (`params.py:29`). The tolerances add up to far more than 0.05 mm:
- PCB thickness, ±0.16 mm
- standoffs
- cast acrylic, often ±0.3 mm
- switch height
- the SLA cap

A hard press drives the cap and the frame PCB onto the panel. The non-touch 7B (SKU 31727, 164 × 97 mm) lists tempered glass only for the touch version ([Waveshare](https://docs.waveshare.com/ESP32-S3-Touch-LCD-7B)), so the cap may be pressing on a bare polarizer: scratches and pressure marks.
*Fix:*
- Give the cap a hard stop on the PCB or plate, not on the glass.
- Raise `GLASS_GAP` to at least 0.5 mm, or add a clear PET or glass protector.
- Make the stack adjustable with shims.
- Confirm whether the 7B has a cover glass.

**[decision]** (cap height, look, and possibly a cover-sheet part)

**H3. The full frame PCB is unsupported at the front and right.** Its screws are only at the back edge and the left side (`model.py:654-655`). The board is a lattice of 3.6 mm strips over about 165 mm. Key forces of about 1.5 N, more on a hard press, will flex the front-right area toward the glass and soften the click. This is not a prototype blocker.
*Fix:* add support at the front and right, for example spacers onto the panel's 9.5 mm front border, a screw near the ZIF tab, or pads at strip intersections outside the windows. Check the deflection before the full build. **[decision]**

### Medium
**M1. Window corners against cap corners.** The windows are drawn with sharp corners (Edge.Cuts gerber). The cap's vertical edges are sharp too, since only the top edges get a fillet (`model.py:143`). JLC mills internal corners to about R0.5 ([JLC blog](https://jlcpcb.com/blog/rounded-corners-pcb-design), [TechOverflow](https://techoverflow.net/2023/04/12/jlcpcb-which-milling-tool-radius-is-used-for-internal-cutouts)). With 0.2 mm clearance, R0.5 leaves 0.08 mm at the corner, and anything above about R0.68 binds the cap.
*Fix:* draw R0.5 window corners explicitly and give the cap's vertical edges R1.0. **[no-decision]**

**M2. Prototype standoffs are non-standard lengths, and the docs disagree with the model.** The model needs:
- M2 3.3 mm (`pcb_top` 21.35 to `plate_bot` 24.65), while `hardware/README.md:30` says "3 mm". A 0.3 mm error closes the 0.2 mm flange gap and pre-loads the switch.
- M3 21.65 mm
- display standoffs 12.45 mm

`docs/parts.md:91` gives no lengths.
*Fix:* round to stock lengths, then fix the difference with shims. List the lengths in parts.md. **[no-decision]**

**M3. Cap optics.** The caps are 8.4 mm tall in the full device and 9.4 mm in the prototype, because the motor height sets the plate height. `plan.md` says "3–5 mm". A tall clear block acts like a light pipe: at 45° the image shifts and the side walls reflect it. SLA "clear" resin also needs a print orientation that keeps supports off the faces you look through, plus polishing or clear-coating.
*Fix:* order a few cap variants: polished, frosted sides, and a thinner top window. Specify the print orientation. **[decision]**

**M4. Rattle.** The cap has 0.2 mm of free vertical play (`CAP_TO_PLATE`) and 0.2 mm sideways. Nothing preloads it, and the B3U can't be preloaded.
*Fix:* plan a thin foam or silicone ring on the flange as an option. **[decision]**

**M5. The prototype doesn't test the full frame PCB's risks.** It has no diodes, no ZIF and no FFC, and none of the routing density. In the full board, each 3.6 mm strip has to hold a B3U plus a row trace and an SOD-123 diode, about 3.7 mm long with its pads, which is not proven.
*Fix:* either add a ZIF, two diodes and a row/column net to the proto PCB (cents of parts plus an FFC breakout), or route one full-size row before the full order. Consider SOD-523 diodes. **[decision]**

**M6. The key tests aren't measurable enough** (`docs/prototype-tests.md`, Keys).
*Fix:* add these tests:
- actuation force by position (center, near edge, far edge, corners), using the 0.1 g scale; pass if the far edge needs ≤2× the center force
- a feeler gauge or witness film check that the cap and PCB never touch the glass at a 10 N press
- the measured glass gap
- 0 missed or double events in 500 presses, checked on a logic analyzer

**[no-decision]**

### Low
- **L1. CPL rotation.** SW1 is placed at 180°. The B3U has no polarity, so 0° and 180° are both fine; only a 90° offset between KiCad's footprint (pads on X at ±1.7 mm) and JLC's model would matter. Check it in JLC's preview, and set the aux origin for cleaner CPL coordinates. **[no-decision]**
- **L2. Matrix firmware and ESD are not specified.** Nothing gives the diode direction, the scan direction or the debounce time. The matrix lines run about 80 mm of FFC straight into RP2350B GPIO.
  *Fix:* write them down (for example, 5 ms debounce that reports immediately on the first edge). Add 0402 series-resistor or ESD-array footprints on the knob board. **[no-decision]**
- **L3. B3U-1000P supply and life.** LCSC marks it "not recommended for new designs" (`docs/open-questions.md`), and listings show 200k cycles. Footprint-compatible alternatives are already planned; order a few with the prototype. **[decision]**
- **L4. Doc inconsistencies.**
  - `docs/pcb.md` says "diodes if the matrix needs them", while `docs/wiring.md` says one per switch.
  - `plan.md` mentions "guides in the case" and "3–5 mm" caps.
  - `hardware/README.md` says "3 mm" standoffs (see M2).

  **[no-decision]**
- **L5. Abrasion.** The milled FR4 window edge is one of the two cap guides, and it is abrasive. Let the plate hole be the tight guide and open the PCB window by about 0.2 mm. **[no-decision]**

## Missing
- A schematic or netlist for the 21-key frame PCB (diode orientation, FFC mapping), and a routing check of one strip.
- A cap drawing with tolerances, print orientation and surface finish. A force and position spec for the key ("clicks anywhere at ≤ X gf").
- A confirmed answer on whether the 7B has a cover glass, and a decision on what the cap's overtravel stops against.
- The ZIF contact side (`docs/bom.md` "V") and the matching FFC type A or B. This is already open.
- Frame PCB support points and a deflection estimate for the full build.

## Actions before ordering (in order)
1. Move the proto frame PCB's mounting holes and wire pads outside the glass outline (B1). Then re-export and re-run DRC.
2. Add a second B3U footprint on the far strip for each key (H1). Order caps with a nub at both ends, plus a fulcrum variant.
3. Rework the vertical stack: add a cap hard stop away from the glass, raise the gap or add a protector, and plan for shims. Fix the standoff lengths and the README (H2, M2).
4. Draw the window corners at R0.5 and round the cap's vertical edges to R1.0 (M1).
5. Add the measurable key tests from M6 to `docs/prototype-tests.md`.
6. Check B3U rotation and placement in JLC's preview, and order a few alternative switches (L1, L3).
7. Optional: add the ZIF and diodes to the proto board (M5).
8. After the prototype, before the 21-key board: decide on frame support, the diode package and the routing (H3, M5), and specify debounce and ESD (L2).
