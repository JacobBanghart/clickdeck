# Sourcing options for the four boards

Research from 2026-10-17. Nothing here is a live quote. Where a price isn't
published, it says **needs a quote**. All totals are for one finished
device, US address, own 3D printer, duty included, and compare against the
current estimate in [cost.md](cost.md): **~$475–735**.

The four boards (sizes from `cad/out/full_*_outline.dxf`, bounding boxes):

| Board | Size | Parts |
|---|---|---|
| Frame PCB | 169.5 × 95.6 mm | 21 B3U, 21 diodes, ZIF |
| Knob board | 164.4 × 57.8 mm | RP2350B (QFN-80, 0.4 mm), 5 TMC6300, 5 MT6701, connectors, ~1,800 joints across all boards |
| Touch band | 155.3 × 11.2 mm | AT42QT2120, SH header |
| USB board | 81.0 × 33.3 mm (L-shape) | CH334F, 2 USB-C, power switches |

Total board area ~301 cm² (46.7 sq in) per set. All top-side SMT, 2-layer.

## Recommendation (ranked)

How the totals are built: the non-board part of the build (display,
motors, caps, hardware, case, their shipping and duty) stays ~$200–300.
Only the "boards, landed" part changes between routes. Today that part is
~$275–430 (JLC $205–320 plus 35% duty).

| Rank | Route | Boards, landed | Single build | Confidence |
|---|---|---|---|---|
| 1 | **JLC, optimized** (Economic, 5 fewer extended types, stocked parts, HASL if yield allows) | ~$245–360 | **~$440–660** | Good: JLC publishes its fees |
| 2 | **Group buy of 5 at JLC, optimized** | ~$95–145 per device | **~$270–420 each** | Good |
| 3 | NextPCB Rev 0 (free assembly up to $500 on the first order) | ~$150–330 | ~$350–630 | Low: terms unverified, panel must be split (design change) |
| 4 | Elecrow / PCBWay / Seeed (min 1 assembled, no per-type fee) | ~$200–490 | ~$400–790 | Low: needs a quote |
| 5 | Aisler (Germany, ~10% US duty) | ~$350–540 | ~$550–840 | Medium on boards, assembly needs a quote |
| — | Self-assembly, designer only (JLC bare boards + stencil + hot plate) | ~$170–310 incl. tools | ~$370–610 (~$310–520 with tools owned) | Good on price, but it's soldering |
| — | Module approach (WeAct RP2350B, hub module, driver modules) | about the same or worse | no saving | Doesn't fit the knob board |
| — | OSH Park, Eurocircuits, MacroFab | more | more | See below |

**Short version:** stay with JLC, apply the levers already listed in
cost.md, and get one real cart quote. That saves ~$35–75. The only big
saving is the group buy. A one-off NextPCB Rev 0 order could be cheaper
for one build, but only if the free-assembly offer is real for this BOM and
the panel is split. No route makes a single build cheap: duty and parts
dominate.

## 1. JLC, optimized

### Economic PCBA eligibility

| Requirement | This BOM | OK? |
|---|---|---|
| Finest IC pitch 0.4 mm (Standard: 0.35 mm) | RP2350B and TMC6300 at 0.4 mm | Yes, at the limit |
| Smallest package 0402 | 0402 passives | Yes |
| 2, 4 or 6 layers | 2 | Yes |
| Panel ≤ 250 × 250 mm, mouse bites (no V-cut for PCBA) | ~180 × 160 mm, mouse bites | Yes |
| Single side | All top side (D6), BOOTSEL must stay reverse-mount on top | Yes |
| Quantity 2–50 | 2 (single) or 5 (group) | Yes |

Sources: [JLC assembly capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities),
[JLC prototype assembly](https://jlcpcb.com/solutions/pcb-prototype-assembly) (both read 2026-10-17).

### Fees that apply (JLC pricing page, updated 2026-09-09)

[jlcpcb.com/help/article/pcb-assembly-price](https://jlcpcb.com/help/article/pcb-assembly-price)

| Fee | Economic | Note |
|---|---|---|
| Setup | $8.18 | |
| Panel fee (more than one design in a panel) | $8.21 | Applies here. cost.md counts it in fabrication; check the quote |
| Stencil | $1.53 | 90% duty on stencils is a few cents here |
| Hand-solder labor | $3.58 per order | USB-C shell legs |
| Extended part loading | $3.07 per type | Preferred extended parts are free |
| SMT per joint | $0.0016 | ~$3 per set |
| Large size (PCB area over 650 cm²) | $57.46 | Two 180 × 160 mm panels are ~576 cm². A 180 × 180 panel would be 648 cm². **Keep the panel ≤ ~320 cm² or check the quote.** Five panels (group buy) likely pay it |
| X-ray | $1.64 per piece | Only if requested or required for the QFN; check the quote |

### Levers and estimate

| Item | Today | Optimized |
|---|---|---|
| Fabrication, 5 panels | $30–70 | $30–70 (HASL takes the low end) |
| Setup, panel, stencil, hand solder | $14–38 | $21–22 (Economic, panel fee included) |
| Extended types | 24 × $3.07 = ~$74 | 19 × $3.07 = ~$58 |
| Parts, 2 sets | $90–115 | $75–100 (no pre-order minimums) |
| Placement, Global Sourcing extras | $4–16 | $4–16 |
| **Boards, before duty** | **$205–320** | **~$180–265** |
| Duty 35% | $72–112 | $63–93 |
| **Boards, landed** | **~$275–430** | **~$245–360** |

The five swaps are in cost.md's levers: basic 12 MHz crystal, SRV05-4-P-T7
for the ESD parts, one shared switch part, basic 22 µF instead of the
polymer cap, basic regulator. The in-stock swaps replace the SM08B-GHS-TB
(0 in stock, minimum 19) and the AOTA inductor (minimum 32). These are
schematic choices; they don't change features.

Not done here, because they cut features or are owner calls: dropping the
touch band (D12) saves 3 more types (~$9) and the AT42QT2120.

Caveat: the Economic per-type fee and JLC's Global Sourcing rules were not
re-confirmed for TMC6300 under Economic. The cart decides.

## 2. Other Chinese assemblers

All ship from China, so the same US duty applies: ~35% today (JLC's FAQ,
[us-tariff-policy-faq](https://jlcpcb.com/help/article/us-tariff-policy-faq),
updated 2026-03-25). It may rise to ~37.5% (see section 3).

| Service | Min assembled | Per-type fee | Published fees | Parts | Estimate, boards landed |
|---|---|---|---|---|---|
| **PCBWay** | 1 ("yes, even 1 piece", if you pay setup) | None published | "$29 for 20 pcs" promo (assembly labor only); stencil free or $10–15 | Bought for you; one user report of ~2× markup on parts | **Needs a quote.** Guess $235–490 |
| **Seeed Fusion** | 1 | None published | Older articles: $25 setup + $0.01–0.30 per component. Old "free assembly up to 5 PCBA" promo, no 2026 date | OPL library (cheaper, faster) | **Needs a quote** |
| **NextPCB Rev 0** | 5 or 10 | None published | **Free assembly on the first Rev 0 order, up to $500** (launched 2026-05-13) | HQ Online stock only | ~$150–330 if the offer applies |
| **Elecrow** | 1 | None published | $10 engineering fee (old), $12 stencil; "0 soldering fees for ≤10 pcs" promo with no year | Bought for you; one-time fee for hard parts | **Needs a quote.** Guess $200–325 |
| **AllPCB** | — | — | Free PCBA promo is for companies only, boards ≤ 100 × 150 mm | — | Doesn't qualify (frame and knob boards are too wide) |

Notes:

- **The real advantage of PCBWay, Seeed and Elecrow** is assembling one set
  with no per-type fee. JLC's overhead for that is ~$58–74 of type fees plus
  the spare set's parts (~$45–55). That's ~$100–130 they could undercut.
  But their parts come from Western distributors with markup, not LCSC
  stock, so the parts line is likely higher. Only a quote settles it.
- **NextPCB Rev 0 limits:** board 50 × 50 to 150 × 250 mm, single design
  only, 5 or 10 assembled, in-stock parts only. The 180 × 160 panel doesn't
  fit (one side must be ≤ 150 mm). Frame + knob board stacked is
  95.6 + 57.8 = 153 mm, so even a 150 × 250 panel can't hold all four.
  It would need two orders (only the first is free) or a split panel.
  **Design change** (owner decision). 5 assembled sets suits a group buy.
- PCBWay may count a multi-design panel as several designs; ask.

Sources: [PCBWay PCBA page](https://www.pcbway.com/pcb-assembly.html) (read 2026-10-17);
[PCBWay Q&A on 1-piece orders](https://www.pcbway.com/blog/PCB_Basic_Information/PCBWay_Q_A_003___Common_Questions_for_PCBA_Ordering_01.html);
[user report, ~2× parts markup](https://forum.contextualelectronics.com/t/pcbway-assembly-service-my-experience/2541) (2020);
[Seeed Fusion page](https://www.seeedstudio.com/fusion_pcb.html), [Seeed wiki](https://wiki.seeedstudio.com/Service_for_Fusion_PCB/) (updated 2026-09-16: PCBA from 1 piece, no fees listed);
[Seeed free-assembly article](https://radiolocman.com/review/article.html?di=589341) (undated);
[NextPCB Rev 0 launch, CNX](https://www.cnx-software.com/2026/05/13/nextpcb-officially-launches-rev-0-pcba-an-automated-no-touch-prototype-assembly-service-built-for-speed-and-predictability/) (2026-05-13, sponsored);
[NextPCB Rev 0 page](https://www.nextpcb.com/rev0-pcba) (limits, read via search 2026-10-17);
[Elecrow PCBA](https://www.elecrow.com/pcb-assembly.html), [Elecrow promo](https://elecrow.com/blog/elecrow-special-pcba-promotion-0-soldering-fees-for-pcba-sample-orders-of-10pcs-or-below.html) (undated);
[AllPCB free proto terms](https://www.allpcb.com/activity/PCBAFreeProto) (no year).

## 3. Non-China options and US tariffs

### Tariffs (as of 2026-10-17)

| Origin | Duty on PCBs / PCBA | Note |
|---|---|---|
| China | ~35–37.5% | 12.5% Section 301 base layer (replaced Section 122 on 2026-07-24) + 25% Section 301. JLC's DDP rate is 35%. **Bare 2-layer boards** have had an exclusion from the 25% (HTS 9903.88.69) that **expires 2026-11-09** unless renewed. Assembled boards never had it |
| EU (Aisler, Eurocircuits) | ~10% | New Section 301 layer tops goods up to 10% total; MFN on PCBs is 0 |
| Taiwan | ~10% | Base layer, per one guide; verify |
| US-made | 0 | |

IEEPA tariffs ended 2026-02-24 after the Supreme Court ruling. Rates are
still moving (the new layer is being challenged in court). Sources:
[AtlasPCB, exclusion expiry](https://www.atlaspcb.com/news/news-pcb-tariff-section-301-exclusion-expiry-november-2026/) (2026-08-21);
[tariffstool, China electronics](https://www.tariffstool.com/guides/tariff-on-electronics-from-china-2026) (updated 2026-10-09);
[Section 122 out, 301 in](https://borderbuddy.com/trade-tariff-news/section-122-is-out-section-301-is-in);
[Cleary Gottlieb on the new 301 tariffs](https://www.clearygottlieb.com/news-and-insights/publication-listing/trump-administration-imposes-new-section-301-tariffs-on-60-trading-partners).
These are secondary sources, not CBP notices.

### Services

| Service | What it costs here | Verdict |
|---|---|---|
| **OSH Park** (US, ENIG, free shipping) | $5/sq in, sets of 3: 46.7 sq in → **~$235 for 3 bare sets**, no assembly | 4–6× JLC's bare boards. Only worth it for the touch band or USB board alone |
| **OSH Stencils** (US) | Priced by area; current price **needs a quote** (old posts: from $5–10) | Fine for self-assembly, no duty |
| **Aisler** (Germany) | Boards: €12 + €0.097/cm² × 3 (ENIG) = **~€100 ($115) for 3 sets**. Stencil €5 + €0.095/cm² ≈ €34. Assembly from 1 board, fee per task: **needs a quote**. Free shipping | ~$350–540 landed with a guessed €80–200 assembly fee. Not cheaper, but low duty and Western parts |
| **Eurocircuits** (Belgium) | PCB Proto assembly 1–5 boards, stencil included, online calculator only | **Needs a quote**; historically above Aisler |
| **MacroFab** (US, Houston) | No minimum; instant quote only. A 2018 user quote: ~$170 for one 110 × 60 mm board with ~80 parts | **Needs a quote**; likely well over $500 for ~1,000 parts |
| **Tempo Automation** | — | Closed (Chapter 7, 2023-12) |

Sources: [OSH Park services](https://docs.oshpark.com/services/);
[OSH Stencils pricing, 2016](https://www.adafruitdaily.com/2016/06/29/osh-stencils-pcb-solder-paste-stencil-maker-founded-by-do-it-yourself-engineers/);
[Aisler pricing post](https://community.aisler.net/t/our-simple-pricing/102) (2023-08-27, verify at checkout);
[Aisler assembly](https://aisler.net/products/assembly);
[Eurocircuits PCB Proto](https://www.eurocircuits.com/pcb-assembly-proto/);
[MacroFab prototyping](https://macrofab.com/prototyping);
[2018 MacroFab quote](https://lists.febo.com/pipermail/time-nuts/2018-January/108570.html);
[Tempo closure](https://evertiq.com/news/54167).

## 4. Module approach

| Module | Price | Fit | Saving |
|---|---|---|---|
| **WeAct RP2350B core board** | ~$4.21 + shipping (Feb 2025) | Exposes all 48 GPIO on two 30-pin headers (GP23 has the user button, GP25 the LED; still usable). 44 needed, so pins are OK. But it's **41.4 × 41.1 mm**: the knob board's back strip is 19 mm, so the board must grow. With headers and its own USB-C it's well over the ~6 mm parts room. Through-hole headers need hand soldering or JLC THT, and JLC would need the module consigned | Removes 3 extended types (RP2350B, crystal, inductor, ~$9) and ~$3 of parts per set. Adds ~$9 for 2 modules plus header parts. **About zero, and it doesn't fit** |
| **CH334F hub module** (Adafruit 5997) | $4.95 | 31.6 × 20.4 × 4.8 mm fits the 34 × 75 mm bay (10 mm tall). But the USB board still has to carry the socket, CC sensing, both reverse-blocking switches, TVS and ESD. The module's ports are solder pads, so it adds wiring | Removes 1 type (CH334F, ~$3) and ~$1 of parts. **Net loss.** Replacing the whole USB board with a bought hub loses current sensing and back-feed protection (wiring.md option a vs b) |
| **TMC6300 driver modules** | SparkFun ROB-21867 $17.95; Trinamic TMC6300-BOB ~CHF 16 | 2–11 V, fine electrically. 5 of them = ~$90 against ~$12 of chips. Header-mounted, too tall and too big for the 19 mm strip. **No cheap AliExpress TMC6300 module found.** SimpleFOC Mini (DRV8313, ~$6–10) needs **8 V minimum**, so it can't run from USB 5 V | Loss |
| MT6701 encoder boards | — | Must sit on each tongue under the magnet; a module adds wiring across the hinge | Not worth it |

**Verdict:** modules don't help. The custom circuits are cheap in parts;
the cost is JLC's per-type fees, the spare set and duty. A module only
removes a few types and adds soldering and size.

Sources: [CNX on WeAct RP2350B](https://www.cnx-software.com/2025/02/03/tiny-weact-rp2350b-core-board-exposes-all-48-i-os-from-the-raspberry-pi-rp2350b-microcontroller/) (2025-02-03);
[Zephyr board page](https://docs.zephyrproject.org/latest/boards/weact/rp2350b_core/doc/index.html);
[Adafruit 5997](https://www.adafruit.com/product/5997);
[SparkFun TMC6300](https://www.sparkfun.com/sparkfun-brushless-motor-driver-3-phase-tmc6300.html);
[Farnell TMC6300-BOB](https://ch.farnell.com/en-CH/trinamic-analog-devices/tmc6300-bob/breakout-board-pms-bldc-motor/dp/3416040);
[SimpleFOC Mini](https://docs.simplefoc.com/simplefocmini) (all read 2026-10-17).

## 5. Self-assembly (designer's own prototype only)

The project rule is no soldering for builders. This is only for the
owner's own boards.

| Item | ~Cost |
|---|---|
| Bare PCBs from JLC (same panel, 5 copies), 35% duty | $40–95 |
| Stencil: JLC framed/frameless (90% duty) or OSH Stencils (US, no duty, needs a quote) | $10–40 |
| Parts for 1 set + spares from DigiKey/LCSC (US distributor: no duty to you; TMC6300 $2.44) | $55–80 |
| 200 × 200 mm hot plate (the frame PCB is 170 × 96 mm) | $45–65 |
| Solder paste, flux, tweezers, wick (iron is already on the prototype list) | $20–30 |
| **Boards, landed, incl. tools** | **~$170–310** (tools ~$65–95 of that, reusable) |

That makes a designer's build ~$370–610, or ~$310–520 if the tools are
already owned. Risks: the RP2350B QFN-80 and TMC6300 QFN at 0.4 mm are hard
by hand (bridges under the pad, no X-ray). A hot plate does one side well,
which fits D6. The frame PCB (switches, diodes, ZIF only) is the easy one.
A middle path: JLC assembles only the knob board's chips, the owner does
the frame PCB. That doesn't save much, because the type fees stay.

Source: [200 × 200 mm hot plates](https://embeddedcomputing.com/technology/open-source/budget-pcb-hotplate-options-large-medium-small); listings ~$45–65 (2026-10-17).

## 6. Group buy of 5 (JLC Economic, optimized)

One order, 5 panels made and 5 assembled. Fixed costs are paid once.

| Item | Order total |
|---|---|
| Fabrication, 5 panels | $30–70 |
| Setup, panel fee, stencil, hand solder | ~$22 |
| Extended types (19) | ~$58 |
| Large-size fee (5 panels ≈ 1,440 cm²), if it applies | $0–57 |
| Parts, 5 sets (minimums absorbed) | $225–290 |
| Placement, Global Sourcing extras | $15–35 |
| **Before duty** | **~$350–530** |
| Duty 35% | $120–185 |
| **Per device, boards landed** | **~$95–145** |

Per device total: ~$95–145 boards + ~$175–275 for the rest (shared
shipping, bulk hardware packs) = **~$270–420 each**. cost.md has
$275–520; the lower top end comes from the swaps above.

Options for the group:

- **One spare:** make 10 panels, assemble 6. Adds ~$20–40 of fabrication
  and one set of parts (~$45–60), split five ways (~$15 each). Worth it:
  with 5 assembled there is no spare if one board fails.
- **NextPCB Rev 0** takes exactly 5 or 10 assembled, and the free assembly
  (up to $500) would cover the whole group's assembly. But it's one design
  per order, boards ≤ 150 × 250 mm, so the panel must be split into two
  orders and only the first is free. Get a quote with the split panel.
- Order before 2026-11-09 doesn't help much: JLC already charges 35% on
  assembled boards; the expiring exclusion is for bare boards.

## Owner decisions this raises

1. **Basic/preferred swaps and stocked substitutes** (crystal load caps,
   ESD part, shared switch part, polymer cap, regulator, GH header,
   inductor). Schematic choices, no feature loss. Saves ~$35–75 per build.
2. **Panel size:** keep the assembled area under JLC's 650 cm² large-size
   threshold (two panels ≤ ~320 cm² each), or accept $57 if the quote
   shows it.
3. **Split the panel** to use NextPCB Rev 0 (≤ 150 mm on one side, single
   design). Only worth it after a quote.
4. **HASL vs ENIG** for the 0.4 mm QFN-80: ~$10–25, a yield trade-off.
5. **Touch band** (D12): dropping it saves ~$9 of fees plus parts, but cuts
   a feature.
6. **Modules:** not recommended. Using the WeAct board would mean a bigger
   knob board and more height than the ~6 mm parts room.

## Quotes to get

1. JLC cart with the real files and a US address (Economic, check the
   panel fee, large-size fee, X-ray, Global Sourcing TMC6300).
2. PCBWay and Elecrow: 1 assembled set, the same panel, turnkey parts.
3. NextPCB Rev 0: whether a split panel qualifies and what "first order"
   covers.
4. Aisler: 1 assembled set, for a low-duty comparison.
