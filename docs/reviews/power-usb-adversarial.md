# Power and USB: adversarial review

**Summary.** The hub may not run at all: the CH334F has no crystal, and its crystal-free mode is off by default on some packages. Reversing the JST-GH cable puts the PC's 5 V straight onto two RP2350B ADC pins.
The power budget fails on legal hardware. A 4.6 V brownout guard trips on spec-compliant 3 A ports. Default ports and miswired A-to-C cables get overdrawn. The hub's bus/self-power strap is undefined.
Also: the external-socket notch leaves a 0.4 mm FR-4 web, the SY6280 conducts backwards while enabled, and the "5 V TVS" doesn't protect a part with a 6 V absolute maximum.

Sources: CH334/335 datasheet V2.5 ([PDF](https://cdn-learn.adafruit.com/assets/assets/000/131/435/original/CH334DS1.PDF?1721660148=)); SY6280 Rev 0.3 ([PDF](https://olimex.com/Products/Components/IC/SY6280/resources/SY6280AAC.PDF)); Waveshare 7B schematic ([PDF](https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-7B/ESP32-S3-Touch-LCD-7B-Schematic.pdf)); JST GH contact listing ([RS](https://ph.rs-online.com/web/p/crimp-contacts/1667204)); USB 2.0 and USB Type-C specs (cited by section from memory).

## Blocker

### B1. A CH334F without a crystal may not run
- **Assumption attacked:** "CH334F (QFN-24, internal clock, no crystal)" (`docs/pcb.md:62`, `docs/wiring.md:276`, `docs/bom.md:162`).
- **Evidence:** CH334 datasheet §6.2: *"Crystal-free belongs to the configurable function, CH335 and CH334 part of the package form is not turned on by default, can be confirmed at the time of ordering… some of the indicators may deviate from the USB specification, and are only applicable to non-precision occasions."* Crystal-free mode is selected with XI tied to GND.
- **Failure:** JLC fits whatever lot it stocks; you can't "confirm at ordering" through JLC. If crystal-free mode is off in that lot, the hub gets no clock, and neither the ESP32-S3 nor the RP2350B enumerates. Even when it's on, the clock may be out of USB tolerance on some hosts.
- **Cheapest test:** ask WCH or LCSC whether lot C5187527 has crystal-free enabled. Or put a $3 CH334F breakout with XI grounded on 3 PCs.
- **Fix [no-decision]:** add a 12 MHz crystal footprint on XI/XO (the load caps are built in, per the datasheet), plus a 0 Ω link that can ground XI. Fit the crystal (~$0.1, 3.2 × 2.5 mm).

## High

### H1. A reversed JST-GH cable destroys the RP2350B
- **Assumption attacked:** cable "pin 1 to pin 1" (`docs/wiring.md:161-162`, `docs/bom.md:200`). AliExpress sells "same direction" and "reverse direction" versions of the same cable.
- **Evidence:** with a reversed cable, USB-board pin k meets knob-board pin 9−k. VBUS (pins 1 and 2) lands on knob pins 8 and 7, the CC-sense inputs. The 10 kΩ series resistors are on the **USB board** (`wiring.md:116-118`), so the knob end sees stiff 5 V straight onto RP2350B ADC pins. Those pins aren't 5 V tolerant.
- **Failure:** the 5 V back-powers 3V3 through the pins' clamp diodes, and the RP2350B dies. The knob board's real 5 V input instead connects to the PC's CC lines through the 10 kΩ resistors.
- **Test:** an ohmmeter on the cable that arrives; review the netlist.
- **Fix [no-decision]:** use a mirror-symmetric pinout, `GND · VBUS · CC1 · D− · D+ · CC2 · VBUS · GND`. Reversed, it only swaps D+/D− (no enumeration) and CC1/CC2 (harmless). Also put the series resistors at the knob end.

### H2. The 4.6 V brownout guard trips on compliant ports
- **Assumption attacked:** "if the 5 V input drops below ~4.6 V… cuts motor current" (`wiring.md:135-136`).
- **Evidence:**
  - Type-C vSafe5V is 4.75–5.5 V at the *source*. USB 2.0 Table 7-7 allows 4.40 V at a low-power port.
  - Estimated drops at a 1.6–2.0 A total draw:
    - 1 m C-to-C cable at ~150 mΩ round trip: 0.25–0.3 V.
    - JST-GH path (two 28 AWG × 0.1 m conductors at 21 mΩ, with 30 mΩ max per contact × 2 ends, each way): ~80 mΩ, so 0.13 V.
    - Soft-start switch at 50–100 mΩ: up to 0.15 V.
  - That puts the knob board at about 4.2–4.4 V on a fully compliant 3 A port.
- **Failure:** the guard trips under legitimate load and "lowers the budget" every time. Haptics are weak on exactly the ports that were meant to give 1.5 A. Or the motor current hunts between cut and restore.
- **Test:** an electronic load at 1.8 A through a 1 m C-to-C cable from a laptop; log VBUS at the far end of a 100 mm GH cable.
- **Fix [no-decision]:** trip on a *drop relative to the idle voltage* (e.g. >300 mV) plus an absolute floor near 4.2 V, as a fast comparator rather than ADC polling. Size the floor from the hub's needs: CH334 V5 is specified at 4.5 V min, and its low-voltage reset (Vlvr) is 2.5–3.2 V.

### H3. Overdraw on default ports and A-to-C cables
- **Assumption attacked:** "most ports allow it, and the brownout guard catches the ones that don't" (`wiring.md:127-131`).
- **Evidence:**
  - Baseline draw before any motor current: display 350 mA + hub up to 85 mA (CH334 ICC) + logic 60 mA ≈ 0.5 A.
  - That baseline alone hits the USB 2.0 500 mA limit, and it's drawn *before configuration*. USB 2.0 §7.2.1 allows 100 mA until the device is configured.
  - Non-compliant A-to-C cables with a 10 kΩ Rp (the Type-C spec requires 56 kΩ) put 5 V × 5.1/15.1 = 1.69 V on CC. The table (`wiring.md:121-125`) reads that as a 3 A port, so the device sets a 1.5 A motor budget on a 500 mA USB-A port.
  - Type-C also requires a sink to cut its draw within tSinkAdj (60 ms) when Rp changes. The docs only describe reading the offer at startup.
- **Failure:** the port's polyfuse or power switch shuts it off (Windows reports a "power surge on USB port"), and both MCUs drop together. A firmware guard can't beat a power switch that drops VBUS within microseconds.
- **Test:** a USB-A 2.0 port on an old laptop and on a bus-powered hub, plus one known 10 kΩ A-to-C cable.
- **Fix:** [no-decision] keep the backlight at minimum and the motors off until both devices are configured; poll CC continuously. [decision] require a C-to-C cable and refuse motor current at a default offer (feature trade-off), or add a PD sink controller to get a real contract (cost about $0.5, plus one extended part).

### H4. The hub's bus-power/self-power strap is undefined
- **Evidence:** CH334 datasheet: *"PSELF… built-in pull-up resistor: default high level is self-powered."* The docs don't mention PSELF.
  - Left at the default, the hub tells the host it's self-powered, which is false.
  - Strapped bus-powered (correct), USB 2.0 §11.13 limits each port to one unit load (100 mA). Linux then logs "rejected configuration due to insufficient available bus power" for any device whose bMaxPower is over 100 mA. The TinyUSB/Arduino-ESP32 defaults are often 500 mA.
- **Test:** strap PSELF low on a breakout and plug an ESP32-S3 running default TinyUSB into it.
- **Fix [decision]:** choose either "PSELF high (works everywhere, misreports power)" or "PSELF low, with both firmwares declaring 100 mA" (compliant on paper, but the real draw still exceeds it). Document the choice.

### H5. The external-socket notch leaves a 0.4 mm board web
- **Assumption attacked:** a mid-mount socket in the 8.5 mm strip (`wiring.md:193-205`, `model.py:683-684`).
- **Evidence:** I probed the model. At x = −16 and −12 the USB board exists only at y 45.2–45.6, so the notch (7.65 mm deep) leaves **0.4 mm** of FR-4 in front of the socket. JLC's routed slot and web minimums are larger, and a real mid-mount footprint needs PCB under the rear of the shell for the SMD signal pads.
- **Failure:** the footprint doesn't fit. Or the web cracks at depanelization or the first push-in, and then the backstop bears on nothing.
- **Test:** overlay the C2894902 drawing on `full_usb_board_outline.dxf`.
- **Fix [decision]:** widen the arm (eat into the clearance behind the display board), move the arm, or use a top-mount socket with a printed saddle (look: the socket sits higher in the wall).

## Medium

### M1. The SY6280 backfeeds while enabled
- **Evidence:** SY6280: *"In case the output is pulled higher than the input voltage under the shutdown, the SY6280 can block…"*. It blocks only in shutdown, and EN is "always on" (`wiring.md:98`).
  - On the 7B, the native port's VBUS is the 5V net.
  - The UART port feeds 5V through an AO3401 ideal diode (Q10) and D11 (1N5819).
  - The CS8501 boost drives 5V from J3's battery, and its charger input (VCC) is reachable only from the UART port.
- **Failure:** while debugging over the 7B's UART port, that port powers the hub, the motors and the external receptacle's VBUS, and back-drives the PC's VBUS (USB 2.0 forbids this). If a user fits a LiPo to J3, the device never powers off, the battery drains, and it never charges.
- **Test:** power the 7B's UART port alone and measure the external receptacle's VBUS.
- **Fix [no-decision]:** use a switch with true reverse-current blocking (or an ideal diode) for port 2. Document "no battery on J3".

### M2. Hot-plug overshoot vs the SY6280's 6 V absolute maximum, and inrush
- **Evidence:** SY6280 absolute maximum is "All pins… 6V". The VBUS "TVS" is unspecified (`bom.md:168`). A typical 5 V TVS clamps at ~9 V at its peak current. Ceramic-only input capacitance plus cable inductance rings to ~2× on hot-plug.
- **Inrush:** the display's 5V net carries ≥120 µF (C4 100 µF + C3/C8/C10), charged at the SY6280 limit (0.75–1.25 A at Rset 6.8 kΩ). The knob board adds 470 µF. That's far beyond USB 2.0 §7.2.4.1's 10 µF / 50 µC.
- **Test:** scope VBUS on the USB board while hot-plugging 20 times; run a USB-IF inrush measurement.
- **Fix [no-decision]:** pick a TVS with Vc < 6 V at the expected surge; add 22–47 µF of polymer or electrolytic at the input for damping; ramp the SY6280 enable with an RC; set Rset explicitly.

### M3. The JST-GH current claim
- **Evidence:** the GH contact is rated 1 A (the RS listing; JST's rating is for 26 AWG). Contact resistance is up to 30 mΩ. Ready-made cables are typically 28 AWG.
- **Failure:** contact resistances of 10 vs 30 mΩ split 1.8 A as 1.35/0.45 A, so one contact runs well past 1 A, plus the voltage drop counted in H2.
- **Fix [decision]:** use 3 VBUS + 3 GND contacts on a 10-pin GH (pin count/size), or cap the motor budget at 1.2 A.

### M4. Hub resets from motor dips
- **Evidence:** the CH334 datasheet itself warns that dynamic load *"may generate LVR low-voltage reset and thus the whole HUB disconnected and reconnected."* The 470 µF bulk sits behind the knob board's soft-start switch, so it doesn't support the hub.
- **Failure:** any VBUS collapse re-enumerates *both* devices, and the host app loses its pairing.
- **Fix [no-decision]:** put 22 µF on VDD33 (the datasheet's own advice), or feed the hub's VDD33 from a separate LDO behind a diode with its own hold-up capacitance.

## Low

- **L1. CC sense details.** The RP2350 GPIO leakage erratum (E9) applies if the ADC pads' input buffers are left enabled: about 100 µA through 10 kΩ is a ~1 V error. Firmware must clear IE on the ADC pins. [no-decision]
- **L2. Suspend.** The design doesn't cover USB suspend (≤2.5 mA). The backlight and drivers stay on when the host sleeps. [no-decision: firmware]
- **L3. Always-on port 2.** Its VBUS is live with nothing attached (Type-C requires vSafe0V). It's internal, but it's a shorting hazard during service. [no-decision]
- **L4. Strain relief.** The overmold has 0.75 mm of clearance per side in the 14 × 8 pocket (`params.py:182`; 12.5 × 6.5 overmold), so the socket shell and its legs take the lever load *before* the overmold touches the wall. The claim "levers the plug against the case, not the socket" (`wiring.md:198-199`) only holds after deflection. Cheaper fix [no-decision]: shrink the pocket to about 13 × 7 mm (Type-C recommends overmolds ≤12.35 × 6.5 mm).
- **L5. Back-EMF.** At 260 KV, a hand flick at 600 RPM gives ~2.3 V. When the device is unplugged, the drivers' body diodes rectify it onto VS, partly powering the logic. Harmless unless firmware writes flash at boot.

## What I could not verify

- CH334F crystal-free status for the LCSC lot.
- The C2894902 mid-mount footprint drawing.
- JST's official GH derating per wire gauge.
- The exact USB-C clause on cable IR drop.
- The TMC6300's current-sense capability; the budget appears to be an open-loop estimate.
- The 7B's real 5V-net capacitance and backlight current (350 mA is Waveshare's figure).
- The final, non-preliminary SY6280 datasheet.
- RP2350 erratum E9 wording, and whether the RP2350B's ADC pins are 5 V tolerant when unpowered.
- The soft-start load switch's reverse blocking (the part isn't chosen yet).
