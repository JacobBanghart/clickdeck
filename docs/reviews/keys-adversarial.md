# Keys: adversarial review

**Summary.**
1. As modeled, the full 21-key build very likely won't click. The cap bottom sits only 0.05 mm above the LCD at the switch's nominal travel. The frame PCB hangs from one edge and bends about 0.3–11 mm per N, so the cap (or the PCB) lands on the glass before the B3U trips.
2. Each cap rests on one switch, 10.75 mm off-center. That makes it a lever that pivots on the LCD: the far half of the key needs 3–10 N or never clicks, and the cap edge grinds on the polarizer inside the image.
3. The 2-key prototype can't reveal either problem: it's stiffer, it's supported on both sides, and with the documented 3 mm standoffs it has a different stack. Several fixes are cheap and need no decision. The support and stabilization fixes need decisions.

All geometry comes from `cad/model.py` and `cad/params.py`. Stack values come from `make_stack()`: glass 19.55, PCB 19.75–21.35, switch top 22.95, flange 23.25–24.45, plate underside 24.65, cap 19.75–28.15 (8.4 mm tall; 9.4 mm on the prototype).
B3U datasheet: Omron A162-E1-07, https://omronfs.omron.com/en_US/ecb/products/pdf/en-b3u.pdf. It gives OF "1.50 ± 0.49 N", RF "0.2 N min.", pretravel "0.15 +0.2/−0.1 mm", height "1.6 +0.15/−0.10", plunger "1.5 dia.", durability "200,000 operations min." and "Washing: Not possible".

---

## Blocker

### B1. The cap bottoms out on the LCD before the switch trips
- **Assumption attacked:** `GLASS_GAP = 0.2` (params.py:31) is enough room for a 0.15 mm-travel switch.
- **Evidence:**
  - `key_cap()` sets `cap_bot = st.pcb_bot` (model.py:141), so the cap bottom is 0.2 mm above the glass. Cap-to-glass gap = 0.2 − (PCB deflection δ) − (switch travel). At nominal travel that leaves 0.05 mm with δ = 0.
  - The datasheet pretravel goes up to **0.35 mm**, which is more than the whole 0.2 mm gap even with a rigid PCB.
  - The frame PCB is screwed only along its back edge and left side (model.py:651–655). The front edge (knob side) and the right edge, where the ZIF is, hang free over the glass.
  - I ran a grillage estimate of the real strip lattice (FR4, E = 20 GPa, G = 4 GPa, 1.6 mm, measured strip widths 3.6–9.8 mm, pinned at the 5 screws). Deflection per N:

    | Point | Deflection |
    |---|---|
    | Back-row center | 0.31 mm/N |
    | Middle row | 0.98 mm/N |
    | Front-row center | 2.0 mm/N |
    | Front-right key | 4.7 mm/N |
    | Front-right corner (ZIF) | 7.5 mm/N |

  - At 1.5 N that is 0.5–7 mm, versus the 0.2 mm gap. Even 3× stiffer than estimated is still at least 10× too soft. Self-weight (21 g PCB plus caps, at 42° tilt) is probably enough to lay the front-right area on the glass at rest.
- **Failure scenario:** On a press, the PCB moves down by δ and the cap moves down by δ + travel. So the cap always reaches the glass first, and does so at about 0.1 N, long before the 1.01–1.99 N click. Front-row keys go dead or feel mushy and inconsistent. Where the PCB rests on the glass at rest, the key has zero travel. `check_key_fit()` (model.py:121) only checks in-plane fit, so it reports no warnings.
- **Cheapest test:** First, a free CAD check: set `GLASS_GAP` = 0.2, add 0.35 mm pretravel, and see the negative margin. Then for about $5: a 1.6 mm FR4 offcut with an 18.4 mm window, held only on one edge 90 mm away. Load it with 150 g and measure the drop with a feeler gauge.
- **Fix:**
  - Shorten the cap so its bottom ends at or above the PCB top. That gives ≥1.8 mm to the glass, costs nothing, and the image is unaffected. [no-decision]
  - Give the frame PCB a defined support near every switch row:
    - (a) Bosses on the top plate between the knob windows and along the right edge, using heat-stake pins or screws from above, or
    - (b) deliberately seat the PCB on the glass using 0.2 mm PET/PSA pads on the strip undersides. This puts key loads into the LCD.

    [decision]

### B2. The single off-center switch makes the cap a lever that pivots on the glass
- **Assumption attacked:** "Guides in the case stop the cap from tilting" (plan.md). The prototype test "Corners… every press clicks" (prototype-tests.md:32).
- **Evidence:**
  - The nub sits at `SW_DY = −10.75` mm (model.py:117) and is the cap's only downward support. Lips only stop upward motion.
  - The guide is the plate hole plus the PCB window, 6.9 mm tall with 0.2 mm clearance per side. That allows 3.3° of tilt.
  - The far edge, 19.75 mm from the nub, reaches the glass after only 0.58°. So the glass becomes the fulcrum, not the guide.
  - Force at the nub = F × d / 19.75, where d is the distance from the far edge. To reach 1.5 N (worst case 1.99 N) you need:
    - Pressing over the nub: 1.5 N
    - Pressing the center (d = 9): **3.3 N (4.4 N worst)**
    - Pressing 4 mm from the far edge: **7.4 N (9.8 N)**
    - Pressing the far edge: **never**
  - Tightening the guide instead doesn't fix it. To keep the far edge off a 0.2 mm gap, the clearance would have to be <0.035 mm. With an 18 mm offset and a 6.9 mm guide, μ ≈ 0.3–0.5 puts it in the drawer-binding regime (guide length < 2μ × offset), so it would stick.
- **Failure scenario:** The key feels heavy and position-dependent, and the back third is dead. On every off-center press, 0.5–0.8 of the force goes through the cap's sharp bottom edge (only the top edges are filleted, model.py:143) onto the LCD, inside the visible image.
- **Cheapest test:** On the prototype, use the kitchen-scale method at 5 points along the key's axis. A paper strip under the far edge shows whether the glass is the contact.
- **Fix:** A real mechanism. Options:
  - A wire stabilizer or rocker in the strip
  - A living-hinge cap hinged at the far edge, which accepts a 1–2× force gradient
  - Two switches per key, in parallel, at diagonal corners

  All of these change cost or look. [decision]

## High

### H1. The prototype's documented standoffs give the wrong stack
- **Evidence:** hardware/README.md:30 says "3 mm M2 standoffs". The model needs `plate_bot − pcb_top` = **3.3 mm**. With 3.0 mm standoffs, the PCB sits 0.3 mm higher: the lips (0.2 gap) hit the plate and the switch is held 0.1 mm down. Pretravel is 0.05–0.35, so some switches will read permanently pressed. The glass gap also becomes 0.5 mm, which hides B1.
- **Test:** Assemble one key dry and check with a multimeter whether it reads open at rest.
- **Fix:** Specify 3 mm standoffs plus 0.3 mm shims, and keep a 0.1/0.2 mm shim kit so the stack can be tuned. [no-decision]

### H2. The vertical tolerance budget is ±0.4 mm against 0.2 mm gaps, with zero preload
- **Evidence:**
  - The nub just touches the plunger (`sw_top = flange_bot − NUB_H`, model.py:105–106).
  - The lip gap is 0.2 mm (`CAP_TO_PLATE`, params.py:21).
  - Contributors: switch height +0.15/−0.10 and pretravel +0.2/−0.1 (datasheet), printed bosses 3.3 mm (±0.1–0.2), SLA flange and nub (±0.1), PCB thickness ±10% (±0.16, which moves the cap-to-glass gap 1:1).
  - The glass gap chain runs through two printed post stacks: 21.65 mm for the plate and 10.35 mm for the panel, plus the 6.2 mm panel thickness taken from STEP, not measured. Its RSS is about ±0.4 mm.
- **Failure scenario:** Too tall: the switch is preloaded or stuck on, and screwing the plate down clamps the PCB onto the glass. Too short: the cap rattles over 0.2–0.55 mm of vertical play and gives a dead zone before the click.
- **Test:** Caliper 10 B3Us (height) and 3 SLA caps (flange-to-nub) when they arrive, then compute the actual stack.
- **Fix:** Make the gaps adjustable with shims at the frame bosses. Set the vertical stack from the switch, not the motor (`make_stack` derives everything from the motor height, model.py:96–112). [no-decision]

### H3. Two keys don't scale to 21
- **Evidence:**
  - The prototype frame is 54 × 42 mm, held at 4 points on **both** sides (`FRAME_MOUNT_Y`). Each switch is ~2 mm from solid material below the knob window (proto_frame_pcb.json).
  - The full frame is 170 × 96 mm, held at back and left only, with deflections up to 7.5 mm/N (B1).
- **Failure scenario:** The prototype passes "Corners/Click feel" and then the full build fails.
- **Test:** Add a third prototype frame cut to a full-device front-right corner (3 keys + ZIF corner, same unsupported edges).
- **Fix:** As above, or fix the full-device support first. [no-decision]

## Medium

### M1. Thick clear caps: side-wall mirror images and print clarity
- **Evidence:**
  - The cap is 8.4 mm tall (9.4 on the prototype), driven by the motor height, not the optics.
  - At 45° viewing, the refraction angle in resin (n ≈ 1.5) is 28°. The line of sight shifts 8.4 × tan 28° + 0.2 = **4.7 mm**, which is 26% of the 18 mm cap. That band hits the polished side walls and shows a total-internal-reflection mirror strip.
  - SLA clear resin has layer lines and support marks on its faces unless sanded and clear-coated.
- **Test:** Order one cap now (~$3) and view a printed key image through it at 0/30/45°.
- **Fix:** Frost or paint the cap sides (bead-blast) and polish or coat the top and bottom faces [decision: look]. Specify black solder mask so the window edges don't glow [no-decision].

### M2. ESD path straight onto the matrix
- **Evidence:**
  - The caps are insulators with 0.2 mm gaps. The air path from a finger at the hole edge to the B3U terminals is about 5.6 mm (2 mm plate + 3.3 mm + 0.3 mm keep-out, `SW_EDGE_MARGIN`). An 8–15 kV IEC 61000-4-2 air discharge can arc across that.
  - The datasheet: "Models with ground terminals are available for protection against static electricity". The design uses B3U-1000P, which has no ground terminal.
  - The only ESD protection listed is on the USB board (wiring.md:276). The matrix lines run 80 mm of FFC to bare RP2350B GPIO.
- **Test:** A piezo lighter spark at a cap edge while the prototype logs keys and resets.
- **Fix:** A top-layer GND guard ring around each window and series resistors plus a TVS array at the knob-board ZIF [no-decision]. B3U-1100P (with ground terminal) is an option if JLC stocks it [decision].

### M3. Nub-to-plunger registration
- **Evidence:**
  - The nub is 1.5 mm across, the same as the 1.5 mm plunger. The model draws the plunger as 1.2 mm (`switch()`, model.py:159).
  - Error sources: cap play ±0.2, plus a 0.2 mm gravity bias toward the front at 42° tilt, plus M2 in 2.2 mm holes (±0.1), printed bosses (±0.15) and the datasheet default "±0.2 mm" on dimensions. Worst case is about 0.5 mm off-center.
  - The lever motion from B2 adds sliding.
- **Failure scenario:** Side load on the plunger, an uneven click, and nub wear over the B3U's 200k cycles.
- **Fix:** A 2.0 mm domed nub, or locating pins for the frame PCB instead of screw-hole location alone. [no-decision]

### M4. The laser-cut acrylic cap route can't make this cap
- **Evidence:** parts.md:99 offers 3/5 mm cast acrylic. The cap needs a 0.3 × 1.5 mm nub, a 1.2 mm flange and an 8.4–9.4 mm body. Cast sheet thickness tolerance (typically ±10%) alone is more than the 0.2 mm budgets.
- **Fix:** Use SLA (or machined) caps only, or redesign for stacked sheets with a separately glued nub. [no-decision]

## Low

### L1. Key FFC and ZIF location
- **Evidence:**
  - wiring.md:156 says the frame PCB "reaches 4.6 mm past the panel". In the model the frame edge is x = 84.5, which is **1.2 mm inside** the panel's metal edge at 85.7.
  - The FFC drops through 0.5 mm clearances on each side, past the sheet-metal edge.
  - The frame's ZIF is on its most compliant corner (7.5 mm/N), so FFC stiffness pushes that corner around.
- **Fix:** Correct the doc, add a support at the ZIF, and add a kapton strip on the panel edge. [no-decision]

### L2. Force spread and durability
- **Evidence:** OF 1.01–1.99 N between switches (±33%), on top of the lever effect. 200k cycles is fine for normal use, but a mute key pressed 100 times a day uses up 36k a year. Release force (0.2 N min) is well above cap friction (~0.01 N), so the keys will return.
- **Fix:** Buy 30 switches and sort them by feel. Run the planned alternative-switch comparison. [no-decision]

### L3. Matrix
- **Evidence:** One diode per switch (wiring.md:241) prevents ghosting. Sharing the knob-press row with the key columns is fine.
- **Risk:** Placing 21 SOD-123s (1.1–1.35 mm tall) on 3.6 mm strips. They must stay top-side (the bottom side has 0.2 mm to the glass) and out from under the tab and lips, which have only 1.9 mm of headroom minus up to 0.35 mm of travel.
- **Fix:** Place the diodes in the strip zones away from the tab and lips, and run a CAD clearance check. [no-decision]

---

## What I could not verify
- Real FR4 lattice stiffness. The grillage is approximate: plate action, the top plate's own flex and solder-mask stiffening are ignored. The conclusion holds unless it's more than 10× too soft.
- Whether the Waveshare 7B front is a cover glass or a bare polarizer. This decides how fast B2 scratches the image.
- How much an IPS panel ripples under 2–4 N line loads.
- JLC3DP clear-resin dimensional tolerance and as-printed clarity.
- Whether B3U-1100P and the ZIF part are in stock at LCSC.
- The full frame PCB routing: it hasn't been laid out (hardware/README.md).
- The measured 7B panel thickness: the 6.2 mm comes from STEP only.
