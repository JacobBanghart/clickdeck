# Rev 0 knob module (prototype)

One knob's section of the full knob board: MT6701 sensor, TMC6300 driver
with 3-PWM drive, B3U press switch on a hinged tongue. It plugs into the
ESP32-S3 dev board with jumper wires. This is the netlist-level spec to
draw the KiCad schematic from. Untested.

Outline (with the tongue slots): `cad/out/proto_knob_module_outline.dxf`.
**Layout waits on measuring the 2204 motor** (bolt pattern, base height).

## Parts

| Ref | Part | Package | LCSC | Notes |
|---|---|---|---|---|
| U1 | TMC6300-LA | QFN-20 3×3 | C5196961 / C5274455 (check stock) | Extended part; JLC assembles it |
| U2 | MT6701QT-STD | SOP-8 | C2913974 | Magnetic angle sensor, SSI mode |
| U3 | SN74LVC3G04DCTR | VSSOP-8 | C139324 | Triple inverter, derives low-side inputs |
| SW1 | B3U-1000P | SMD | C231329 | Press switch, **bottom side**, under the tongue tip |
| C1, C2 | 22 µF 10 V X5R | 0805 | (basic part) | VS bulk, at U1 |
| C3 | 220 µF 10 V electrolytic | footprint only | — | Optional extra bulk; fit if motor current dips the 5 V |
| C4 | 100 nF | 0402 | (basic) | VS high-frequency, at U1 |
| C5 | 100 nF | 0402 | (basic) | U1 1.8VOUT |
| C6 | 22 nF 10 V | 0402 | (basic) | U1 VCP to VS (charge pump, 1–100 nF) |
| C7 | 100 nF | 0402 | (basic) | U1 VIO |
| C8 | 100 nF + 1 µF | 0402 | (basic) | U2 VDD |
| C9 | 100 nF | 0402 | (basic) | U3 VCC |
| R1 | 10 kΩ | 0402 | (basic) | U2 CSN pull-up (keeps the sensor idle when unwired) |
| JP1–JP3 | Solder jumpers, 3-pad | — | — | Low-side source: inverter (default) or header pin (6-PWM mode) |
| J1 | 1×14 pin header, 2.54 mm | THT | — | Signals to the ESP32-S3 dev board |
| J2 | 2 pads, large | THT | — | 5 V and GND from the bench supply (short, thick wires) |
| J3 | 3 pads | THT | — | Motor phases U, V, W |

LCSC numbers were looked up on 2026-10-17; "basic" parts avoid JLC's
extended-part fee. Confirm everything in JLC's parts library when ordering.

## Netlist

**Power**
- `+5V`: J2 → U1 VS (pins per datasheet), C1–C4.
- `+3V3`: J1 (from the dev board's 3.3 V) → U2 VDD, R1, C8.
- `GND`: everything, plus U1's exposed pad (thermal: stitch vias under it).

**Driver (U1, TMC6300)**
- `VIO` (VIO/NSTDBY) ← J1 `NSTDBY` (a GPIO: high = run, low = standby).
  **Also powers U3** (see "Standby" below). C7 to GND.
- `UH`, `VH`, `WH` ← J1 `PWM_U`, `PWM_V`, `PWM_W`.
- `UL`, `VL`, `WL` ← JP1–JP3 common pin; JP default side = U3 outputs
  (inverted `PWM_x`), other side = J1 `UL`/`VL`/`WL` for 6-PWM mode.
- `U`, `V`, `W` outputs → J3 (motor).
- `VCP` → C6 → `+5V`. `1.8VOUT` → C5 → GND. `DIAG` → J1 `DIAG`.

**Inverter (U3, SN74LVC3G04)**
- `VCC` = `NSTDBY` net (not 3V3). C9 to GND.
- Inputs `PWM_U`, `PWM_V`, `PWM_W`; outputs to JP1–JP3.

**Sensor (U2, MT6701)**
- `MODE` pin strapped for **SSI** (see the datasheet; breakout boards often
  default to ABZ/I²C, lessons.md #5).
- SSI: `CSN` ← J1 `CS` (R1 pull-up), `CLK` ← J1 `CLK`, `DO` → J1 `DATA`.
- ABZ/UVW/PWM outputs unused (leave open or per datasheet).
- Centered exactly under the motor shaft; the board's motor holes set the
  magnet position.

**Press switch (SW1)**
- Between J1 `PRESS` and GND. Firmware enables the GPIO pull-up.

**J1 pinout (1×14, 2.54 mm)**
`1 3V3 · 2 GND · 3 PWM_U · 4 PWM_V · 5 PWM_W · 6 NSTDBY · 7 CS · 8 CLK ·
9 DATA · 10 PRESS · 11 DIAG · 12 UL · 13 VL · 14 WL`
(pins 12–14 only matter in 6-PWM mode)

## Design notes

- **3-PWM is safe:** the TMC6300 datasheet: *"Internal break-before-make
  (BBM) logic ensures that no cross-conduction occurs."* So a low-side
  input driven by an inverted copy of the high-side input can't short the
  half-bridge.
- **Standby:** the datasheet says no digital input may be high while
  VIO/NSTDBY is pulled low (the input protection diodes would power the chip
  back up through those pins). An inverter outputs *high* when its input
  is low, so U3 is powered from the `NSTDBY` net: pulling `NSTDBY` low
  unpowers U3 and its outputs drop. Firmware must also drive `PWM_U/V/W`
  low before standby, and stop the motor first.
- **NSTDBY from a GPIO:** VIO accepts 1.8–5.25 V; a 3.3 V GPIO is fine. It
  supplies the TMC6300's logic and U3, both small loads.
- **Thermal and supply:** TMC6300 VS wants >10 µF ceramic close to the pin
  (100 µF electrolytic or 10 µF ceramic minimum per the datasheet); keep
  the VS/GND loop tight; stitching vias under the exposed pad.
- **Tongue:** the motor, U2 and SW1 are on the tongue; U1, U3 and the
  connectors on the fixed part, so the hinge only flexes thin traces (route
  them straight across the hinge, no vias on it).
- **DIAG:** one per driver. On the full knob board, diode-OR the five DIAG
  lines into one spare pin.

## Bring-up order

1. 3.3 V only: read the MT6701 over SSI while turning the motor by hand.
2. Add 5 V on the bench supply with a current limit (~300 mA): open-loop
   spin at low voltage limit.
3. Closed-loop FOC; store calibration (lessons.md #4).
4. Haptics: detents, smooth, end stops; then the press switch.
5. Standby/wake cycling: confirm ~0 mA in standby on the power meter.
