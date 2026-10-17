# Prototype tests (go/no-go)

What the 2-key + 1-knob prototype has to show before the full build. The
targets are starting points, not specs. Adjust them once there's hardware to
feel, and record the results here.

Tools: USB power meter between the computer and the board, the calipers, a
phone slow-motion video for timing, and a kitchen scale (0.1 g) for press
force.

## Knob

| Test | How | Pass |
|---|---|---|
| Clicky mode | Set 24 and 48 clicks per turn; turn slowly and fast | Clicks feel distinct and even, none skipped at normal speed |
| Smooth mode | Zero torque; turn slowly by hand | No noticeable cogging (bumps). If it fails, try the second motor or SparkFun ROB-20441 |
| End stops | Bounded 0–100; push past each end | Firm stop, springs back, no buzzing; eases off after a few seconds of pushing |
| Current at rest | Power meter, knob untouched | Driver asleep; motor draws ~0 mA (only sensor and board idle current) |
| Current while clicking | Spin through detents | Record peak and average |
| Current at an end stop | Lean on the stop | Record; the firmware time limit must keep it within the power budget |
| Wake latency | Turn from rest | No dead zone or delay you can feel before the first click |
| Press feel | Kitchen scale under the knob | Clicks at roughly 150–400 g, one clear click, no rocking |
| Press while turning | Turn hard without pressing | No accidental press events |
| Calibration | Store, power-cycle 10× | Knob never twitches at power-on; angle and direction stay correct |
| Noise | Listen up close in a quiet room | No audible whine or buzz at rest or while turning |

## Keys

| Test | How | Pass |
|---|---|---|
| Click feel | Press each key 50× | Crisp click every time; decide whether 0.15 mm travel feels good or too short |
| Corners | Press each corner and the far edge from the switch | Every press clicks, no tilting or sticking |
| Rattle | Shake the prototype; tap keys lightly | No rattle you'd notice in use |
| Image | Look through the cap from straight on and at 45° | Image looks like it's on the key surface; edges and gaps acceptable |
| Down and up events | Hold a key 3 s | Separate key-down and key-up events (push-to-talk works) |

## Touch band

| Test | How | Pass |
|---|---|---|
| Tap | Tap each of the knob-display positions 20× | 20/20 detected, no ghost taps |
| Swipe | Swipe left and right along the band | Direction and position tracked smoothly |
| Hand nearby | Turn the knob, rest a hand on the plate | No false touches |

## USB and display

| Test | How | Pass |
|---|---|---|
| Image speed | Send one full-color key image | Shows in under ~50 ms |
| Reconnect | Unplug and replug | Keys reappear without resending images (cache works) |
| Plain HID | Unplug from the host software | Keys still work as a keyboard |
| Idle | Leave untouched | Screen blanks after the idle timeout; wakes on touch, key or knob |

## Decision

- **Go:** knob feel (clicky, smooth, stops, press) and key click both pass,
  and current numbers fit the power budget.
- **Adjust and retest:** a mechanical part fails (cap, tongue, motor) but
  the approach works. Change `params.py`, reorder that part.
- **Rethink:** smooth mode cogs with every motor tried, or the key click
  can't be made to feel good.
