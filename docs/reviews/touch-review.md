# Touch band design review

**Verdict: go with changes.**
The band is cheap ($5–10, `docs/cost.md:27`), plugs in separately and can be left out, so it can't stop the rest of the build. The concept is sound.
Before ordering, though, pick a controller (one is in stock), turn the 0.8 vs 1.6 mm question into a layout rule, fix one clash in the model, and add the real noise sources to the prototype test.

## Strengths
- **Easy to drop.** The band only connects through a 6-pin JST-SH plug (`docs/wiring.md:169`). If it fails, unplug it and the device still works.
- **Room was planned for it.** The knobs moved forward so the band fits (`cad/model.py:392-396`). The model gives it 11.2 mm of height (`cad/out/summary.md:11`) and warns if it drops below 5 mm (`cad/model.py:450`).
- **Firmware has what it needs.** The RP2350B reads both the touch band and the knobs (`docs/protocol.md:15`), so it can tell a touch on the band from a hand on a knob. The protocol already has a `touch-band` feature flag and a `TOUCH` event type (`docs/protocol.md:71,107`).
- **Testing starts cheap.** The plan tests an MPR121 breakout with copper tape first (`docs/parts.md:21`), before paying for a PCB.
- **Docs explain why.** The plan says why touching the display glass won't work: it sits about 7 mm below the top surface (`docs/plan.md:155`).

## Issues

### High
1. **No controller chosen, and the stock check is in an unplanned-for state** (`docs/bom.md:38`, `docs/open-questions.md:59`). I checked the JLCPCB parts library on 2026-10-17:

   | Part | LCSC number | Stock | Notes |
   |---|---|---|---|
   | MPR121QR2 | C91322 | 3003 | ~$2.70, extended part |
   | CY8CMBR3108-LQXIT | C462528 | 2410 | $0.73, but no slider support |
   | AT42QT2120-SUR | C614938 | 69 | built-in slider |
   | CAP1188-1-CP-TR | C2652057 | 121 | |
   | IQS7222A / IQS263 / IQS269A | – | 0 | |

   NXP has stopped making the MPR121; the rights went to Resurgent ([NXP forum](https://community.nxp.com/t5/Sensors/X-ray-issue/m-p/1527670)). For a few units, the existing stock is still enough.
   **Recommendation:** use the MPR121QR2 (C91322). It is the same chip the prototype tests, so prototype results carry over. Firmware reads its 12 electrodes and works out slider position from them. Keep the AT42QT2120 as the drop-in alternative. Recheck stock on the day you order. **[decision]**

2. **The 0.8 vs 1.6 mm question rests on a wrong assumption** (`docs/open-questions.md:51`, `docs/pcb.md:86`). The docs talk about sensing "through 1.6 mm board + 2 mm plate". In practice the electrodes go on the top copper layer, pressed against the plate, so the finger only senses through the 2 mm plate. A thicker board actually helps: it puts the bottom-layer ground farther from the electrodes, which means less stray capacitance.
   **Recommendation:** make the band 1.6 mm and put it in the shared panel. Electrodes go on the top layer. The chip and connector go on the bottom, at the right end. **[decision]**

3. **A 1.6 mm band would collide with the frame PCB's ZIF connector.** The band runs from x −75.9 to 84.5 at z 23.85–24.65. The ZIF connector sits at x 79.9–84.5, y −45.6 to −29.6, with its top at z 23.35. They overlap in plan view by 4.6 × 4.3 mm, with only 0.5 mm vertical gap (from a read-only bounding-box check of `full_device()`). A 1.6 mm band bottoms out at z 23.05, which is 0.3 mm into the ZIF. Even at 0.8 mm, the ZIF latch can't open without peeling the band off.
   **Recommendation:** cut a notch in the band's outline around the ZIF, or stop the band at x ≈ 79. Then run `cad/assembly.py --check` with `TOUCH_BAR_T = 1.6`. **[no-decision]**

4. **The noise sources are packed right around the band, and the test ignores them** (`docs/prototype-tests.md:37-43`).
   - The motor bells are 0.8 mm from the band's front edge and come up to 0.3 mm below the plate (`cad/params.py:116,119`). Their windings switch with PWM.
   - The 7" panel's bottom border, where the panel's driver lines run, is 4.3 mm below the band.
   - The knob caps are 5.3 mm away, so the fingers gripping a knob will rest over the band.

   **Recommendation:**
   - Put a grounded guard trace along the band's motor-side edge.
   - Fill the bottom layer with hatched ground (about 25%) under the electrodes.
   - Add a ground pour on the frame PCB under the band area.
   - In firmware, ignore touches for about 300 ms after a knob moves or is pressed.

   **[no-decision]**

### Medium
5. **No rules for the printed plate as a sensing surface** (`cad/params.py:130`, `docs/assembly.md:103`). Air gaps and voids in the plastic weaken and unevenly change sensitivity. Infineon's guidance is to bond the overlay with non-conductive adhesive film and keep the overlay at about 2 mm or less ([AN85951](https://www.infineon.com/assets/row/public/documents/30/42/infineon-an85951-psoc-4-psoc-6-capsense-design-guide-applicationnote-en.pdf)).
   **Recommendation:** document these rules:
   - Print the band area 100% solid.
   - No carbon-fibre, metal-filled or graphite filaments, and no nylon (it absorbs moisture).
   - Use full-coverage 3M 467MP/468MP transfer tape.
   - The underside must be flat where the band sits.

   **[no-decision]**

6. **The prototype test doesn't match the final build, and its pass criteria are vague.**
   - Copper tape on jumper leads: the leads pick up touches too.
   - It tests through 3 mm acrylic, not 2 mm printed plastic.
   - There is no motor running, no LCD, and no 100 mm cable.
   - "Smoothly" isn't measurable.

   **Recommendation:** add measurable pass criteria:
   - Position error ≤ ±5% of the band length.
   - Tap latency under 50 ms.
   - Zero false touches over 10 minutes of knob use with haptics on.
   - Run it with the laptop on battery and on its charger.
   - No baseline drift after an hour.

   Also test through a 2 mm printed coupon from the JLC3DP order in stage 4 (`docs/plan.md:170`). **[no-decision]**

7. **Electrode pattern isn't specified** (`docs/pcb.md:76`).
   **Recommendation:**
   - Use 10–12 interleaved chevron segments at about 13–15 mm pitch across x −74 to 74.
   - Make the end segments half-width.
   - Keep a 0.5 mm gap between segments and a gap to the ground hatch equal to the overlay thickness (about 2 mm).
   - Size segments so each has at least 75% of the largest segment's capacitance (AN85951).
   - Add 1–10 kΩ series resistors next to the chip.

   **[no-decision]**

8. **Gestures aren't fully defined** (`docs/protocol.md:107`). The + XL strip has a long press. The protocol also doesn't say which knob's area a tap landed in.
   **Recommendation:**
   - Add `long` and `segment` (which knob's area) to the `TOUCH` event.
   - Let the host set the thresholds.
   - Use the MPR121's own baseline tracking and debounce, plus a firmware step that recalibrates if a touch stays stuck.

   **[decision]**

### Low
9. **Cable pinout has no spare ground** (`docs/wiring.md:169`). Pin 6 is unused. Use it as a second GND, place the I²C and INT pull-ups on the knob board, and add a ferrite bead plus 10 µF capacitor on the band's 3V3 input. **[no-decision]**
10. **Band height and outline docs disagree.**
    - `docs/plan.md:157` says 10 mm; the model says 11.2 mm.
    - No band DXF is exported, though `docs/bom.md:19` says the outlines come from `cad/out/*.dxf`.
    - `docs/pcb.md:20` lists no outline file for the band.

    **[no-decision]**
11. **Cost is optimistic if the band is ordered separately** (`docs/cost.md:27`). The chip is an extended part (+$3), and a separate assembly order adds another setup fee. **[no-decision]**

## Missing
- A schematic for the band, an ESD plan, and a defined I²C address.
- Firmware notes: I²C clock speed, how the interrupt is handled, power-on calibration, and what to do if the band isn't fitted (report the `touch-band` feature as absent).
- A test with water drops or a damp finger.
- What happens if the plate is lifted while the device is powered (it should recalibrate).

## Actions before ordering
1. Choose the MPR121QR2 (C91322) and recheck stock that day.
2. Decide on a 1.6 mm band in the shared panel. Notch the outline around the frame ZIF and rerun `assembly.py --check`.
3. Run the copper-tape test again under realistic conditions:
   - motor running with haptics on,
   - LCD showing patterns,
   - 2 mm printed coupon,
   - 100 mm cable,
   - laptop on battery and on its charger,
   - measurable pass criteria (issue 6).
4. Lay out the guard trace, bottom ground hatch, chevron segments and series resistors. Ask for a ground pour on the frame PCB.
5. Write the plate print rules and adhesive spec into `assembly.md`.
6. Add `long` and `segment` to the `TOUCH` event, and export the band DXF.
