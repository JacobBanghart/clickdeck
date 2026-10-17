# Sourcing, cost and prototype plan: adversarial review

Reviewer: red team (independent; no other review read). Checked 2026-10-17. Read-only, apart from this file.

**Summary.**
1. The MT6701 (5 per device, plus 1 in the prototype) is out of stock at LCSC today. TMC6300-LA-T stock is 59, not the 200 the docs say. Both orders depend on these two chips.
2. Every cost table leaves out US import duty. JLC charges about 35% DDP and AliExpress charges extra too, so a single build probably costs about $375–575, above the $350 Stream Deck + XL at almost every point in the range.
3. The prototype does not test the parts the expensive order adds that are new and most likely to fail (RP2350B board, hub, 7B display, touch IC, connectors). It also needs soldering, and it buys about $40 of parts that get thrown away, which contradicts the "no throwaway" and "no soldering" claims.

## Blocker

### B1. MT6701QT-STD is out of stock
- **Claim attacked:** bom.md:27 and knob-module.md:22 list C2913974 with no stock caveat. parts.md:262 says to "confirm both chips are in LCSC stock" but open-questions.md tracks only the TMC6300 and CH334F.
- **Evidence:** LCSC C2913974 shows **"Out of stock"** with a reference price of $1.92 at 1+ (https://www.lcsc.com/product-detail/C2913974.html, 2026-10-17). JLC lists it as Extended, and its page shows no stock (https://jlcpcb.com/partdetail/C2913974). Older LCSC snapshots show 444 and 3,784 units, so stock swings a lot.
- **Consequence:** Order 2 (prototype knob module) and the full panel can't be assembled as specified. Without the sensor there is no knob.
- **Cheapest confirm:** Search "MT6701" in JLC's parts library (JLC stock is separate from LCSC stock). Check the SOP-8 MT6701CT-STD-R (C3003196, https://jlcpcb.com/partdetail/MT6701CT-STD-R/C3003196) and whether JLC's pre-order or global sourcing can supply it, and with what lead time.
- **Fix:** [no-decision] Add MT6701 to open-questions.md as a ⚠️ stock risk, and list a pin-compatible alternate in the BOM. [decision] Choose a second-source sensor, such as an AS5600/AS5047-class part or the CT variant, and give it a footprint option.

## High

### H1. US import duty is missing from every total
- **Claim attacked:** cost.md:145 has "Shipping, 2 orders $15–35" and no duty line. README:43–46 gives totals and the + XL comparison.
- **Evidence:** JLC's US tariff FAQ says US individuals must ship DDP, with a total tariff of "about 35%~92.5%", not refunded in that band (https://jlcpcb.com/help/article/us-tariff-policy-faq, updated 2026-09-09). A May 2026 user report and the JLCCNC table both put PCB/SMT at 35%. Since de minimis ended, AliExpress orders also carry import charges, either at checkout or collected by the carrier.
- **Consequence:** The JLC part of a build is about $185–270 (cost.md:136–142), so duty adds about $65–95 there and roughly $10–30 on the AliExpress/Waveshare side. The single build becomes about $375–575, or about $410–650 with the case printed by JLC3DP. The prototype gets the same increase on each of its three orders.
- **Cheapest confirm:** Get a JLC cart quote with a US address. The DDP line appears before payment.
- **Fix:** [no-decision] Add a "US import duty (~35% JLC, varies on AliExpress)" row to cost.md, parts.md and README, and restate the totals.

### H2. TMC6300 stock is about 59 and the documented price is 2.4× a Western distributor's
- **Claim attacked:** bom.md:26, knob-module.md:21 and open-questions.md:77 say "200 in stock". cost.md:181 says the driver is "the biggest lever" and that a *different chip* is the fix.
- **Evidence:** LCSC C5274455 shows **59 in stock** with $5.93/1, $5.12/10, $4.64/30 (https://www.lcsc.com/product-detail/C5274455.html, 2026-10-17). DigiKey lists the same MPN at about 4,117 in stock and $2.44/1 (https://www.digikey.com/en/products/detail/analog-devices-inc-maxim-integrated/TMC6300-LA-T/12090904, cached, undated).
- **Consequence:** One build needs 10 chips (2 assembled boards), so LCSC stock covers 5 builds. One group-of-5 order (25 chips) would take nearly half of it. The "~$26" for drivers in README:52 is really about $51 per single build, because the spare board also gets 5.
- **Cheapest confirm:** Get a JLC quote that uses Global Sourcing (DigiKey/Mouser) for C5274455 and compare landed cost and lead time.
- **Fix:** [no-decision] Correct the stock figure and the $51 per single build. [decision] Use JLC Global Sourcing or consigned parts from DigiKey instead of LCSC stock.

### H3. The prototype knob-module order is about 2× its quoted $30–45
- **Claim attacked:** cost.md:170 and parts.md:241, 260–261 give "$30–45 with economy shipping".
- **Evidence:** JLC price page (https://jlcpcb.com/help/article/pcb-assembly-price, updated 2026-09-09):
  - Economic setup $8.18, stencil $1.53, $3.07 per extended part, $3.58 hand-solder fee plus a per-joint charge, and $8.21 panel fee when there is more than one design.
  - Standard **double-side** setup is $51.12 plus a $16.42 stencil.
- **What this order needs:**
  - Extended parts (×$3.07): TMC6300, MT6701, SN74LVC3G04, B3U, and probably the RA header.
  - knob-module.md:24 puts SW1 on the **bottom side**, so the board is double-sided.
  - J1, J2 and J3 are THT (knob-module.md:33–35).
  - Parts for 2 boards: about $18.
- **Arithmetic:**
  - PCB about $4 + $8.18 + $1.53 + about $15 extended + $18 parts + $3.58 THT + about $15 shipping ≈ $65.
  - With 35% DDP that is about $85–90.
  - If bottom-side placement forces Standard tier, it is about $140.
- **Consequence:** The prototype total is about $160–280, not $120–200 (cost.md:161). Development cost goes up by the same amount.
- **Cheapest confirm:** Upload a placeholder BOM/CPL with SW1 on the bottom and read the tier JLC chooses. JLC's site disagrees with itself on whether Economic does both sides.
- **Fix:** [no-decision] Re-quote, and include duty. [decision] Move SW1 to the top on the prototype and hand-fit it, or put it on a separate small switch board.

### H4. The prototype doesn't test the parts that make the full order risky
- **Claim attacked:** parts.md:3, 243–244 say the knob module "proves the design that gets repeated 5×". open-questions.md:88–100 and plan.md stage 5 say go/no-go comes before the full build.
- **Evidence:** These meet for the first time in the full JLC panel:
  - RP2350B custom circuit: QFN-80, flash, crystal, USB, BOOTSEL. The prototype uses a core board (parts.md:210).
  - CH334F hub and CC sensing.
  - Touch controller, which isn't chosen yet (bom.md:38, open-questions.md:121). The prototype uses an MPR121 breakout.
  - ZIF/FFC, JST-GH and JST-SH (parts.md:220–223).
  - The $34 Waveshare 7B and its 1024×600 redraw speed (open-questions.md:120, "Test on a 7B board"), which is never bought for the prototype.
- **Consequence:** One wrong footprint or strap on the RP2350B means re-spinning the whole 4-board panel. That costs setup, about 17 extended-part fees (about $52), parts for 2 more boards (including 10 TMC6300 at about $51), shipping and 35% duty, so about $150–250. cost.md:163 budgets "One PCB redo $30–60".
- **Cheapest confirm:** List every circuit in the full panel that no prototype board exercises.
- **Fix:** [no-decision] Raise the redo line to about $150–250. [decision] Add a cheap "Rev 0.5" order to the prototype: a small RP2350B + CH334F + touch IC + connector test board on the same panel as the knob module (marginal cost about $15–25 because of the shared setup), and buy the 7B now instead of the 2.4" screen.

## Medium

### M1. Extended-part fees are under-counted
- **Claim attacked:** cost.md:139 and open-questions.md:114 count about 5 extended types, all on the USB board.
- **Evidence:** The extended parts on the whole panel, from bom.md:25–46, are probably:
  - RP2350B (Extended, https://jlcpcb.com/partdetail/RaspberryPi-RP2350B/C42415655), QSPI flash, crystal
  - TMC6300, MT6701, LVC3G04, B3U, RA header
  - SM08B-GHS, FPC ZIF, BM06B, SM06B
  - touch IC, CH334F, 2 USB-C sockets, SY6280, load switch, 470 µF bulk cap

  That is about 17–19 types × $3.07 ≈ $52–58 per order, plus THT hand-solder for the USB-C shell legs and the 1×3 headers.
- **Consequence:** The low ends of cost.md's board rows (knob board $105) don't cover fees plus 2× parts. That is about $72–82 for parts alone (cost.md:136) plus about $40 of knob-board extended fees and setup.
- **Fix:** [no-decision] Count extended parts from the BOM. Consider the RP2354B (C39843328), which has on-chip flash and removes one extended part. [decision] Swap in basic-library parts where possible.

### M2. "No throwaway parts" and "no soldering" are false for the prototype
- **Claim attacked:** parts.md:3. README:51 and bom.md:9 also say "solders nothing".
- **Evidence:**
  - Thrown away after the prototype: ESP32-S3 devkit, 2.4" display, RP2350B core board, USB hub, breadboard, 6×6 switches, MPR121 and copper tape (parts.md:196–210), about $30–50. The Rev 0 module itself is a separate PCB that isn't reused.
  - Soldering: J1, J2 and J3 are THT with no LCSC number (knob-module.md:33–35), the 6-PWM fallback uses solder jumpers JP1–3 (:32), and breakouts usually ship with loose headers.
  - Missing: a soldering iron and a 5 V bench supply. knob-module.md:35 and parts.md:234 say to power the motor "straight from the supply", but no supply is listed.
- **Fix:** [no-decision] Reword both claims. Add an iron, solder and a 5 V/3 A supply (or USB-C PD trigger) to Order 1 at about $15–30.

### M3. Shipping is under-counted: it is 3–4 orders, not 2
- **Claim attacked:** cost.md:128, 145 and bom.md:63 say "Two orders".
- **Evidence:** Waveshare is its own store. "AliExpress (search the spec)" for the motors, magnets, 4 cable types and hardware means several separate sellers. JLC3DP prints only ship with the PCBs if they are combined at checkout. The prototype has 3 orders plus a laser-cut vendor (parts.md:274).
- **Fix:** [no-decision] Budget per seller and add duty.

### M4. No lead times and a serial schedule
- **Claim attacked:** parts.md:291–298 and plan.md:159–175 give no durations.
- **Evidence:** The chain is serial: Order 1 (AliExpress, 1–3 weeks) → measure motor → layout → JLC Order 2 (about 1 week build + 1 week DHL/customs) → stage 3 → Order 3 (2–3 weeks) → go/no-go → full panel (2–3 weeks, longer if MT6701/TMC6300 need pre-order).
- **Consequence:** At least 10–14 weeks. Stock seen at decision time (59 TMC6300, 0 MT6701) won't hold until the full order.
- **Fix:** [no-decision] Add durations. [decision] Buy and hold the full-build TMC6300 and MT6701 in JLC's parts library (pre-order) as soon as the knob module passes.

### M5. The Stream Deck + XL comparison is tilted
- **Claim attacked:** README:35–36 says "about the same or less". cost.md:177–179.
- **Evidence:** The + XL is $349.99 (Videoguys, Sweetwater listings) with **36 keys, 6 dials and a 161 mm touch strip**. clickdeck has 21 keys and 5 knobs. Per key the + XL is about $9.70, against about $18–27 for clickdeck once duty is included. The comparison also leaves out the first builder's development cost ($450–710 in cost.md:157, more after H3/H4), warranty and labor.
- **Fix:** [no-decision] State the totals with duty and the key/knob counts in the README table, and say plainly "costs more".

## Low

- **L1. Stale B3U stock note:** open-questions.md:85 says "~33k in stock, NRND". LCSC now shows 110,060, $0.19/5, and no lifecycle flag on the page (https://www.lcsc.com/product-detail/C231329.html). bom.md:35 "~$8" for 21 is really about $3. Also, buying B3U on AliExpress (parts.md:200, $0.30–0.60) costs more than genuine LCSC parts and risks fakes.
- **L2. README:52 is wrong:** it calls the five drivers "the biggest cost after the display". The motors ($40–60) and the JLC fees are both bigger.
- **L3. Prototype motors aren't reused:** the 2 motors from the prototype aren't subtracted from the full-build 5 (bom.md:70), even though "no throwaway" is the stated goal.
- **L4. Waveshare price:** $33.99 is the low end of a $33.99–38.99 range on waveshare.com, and the cheapest variant isn't clearly 31727. Third-party stock of 31727 shows out-of-stock at Grobotronics.
- **L5. Group-of-5 claim:** "nobody pays for a spare board" (cost.md:152) ignores the domestic re-shipping of 4 kits and splitting the duty.

## What I could not verify
- Live JLC parts-library stock for MT6701, TMC6300 and RP2350B (the pages don't render stock without login or JS).
- Whether JLC Economic currently accepts bottom-side or double-sided placement (official pages conflict).
- The exact DDP rate JLC would apply to this order, JLC3DP clear-resin pricing and its duty rate.
- DigiKey's live TMC6300 price (cached figure only).
- AliExpress listing prices and plugs for the 2204 motor and cables, the exact cheapest SKU on waveshare.com, and the SendCutSend/Ponoko minimum charges.
