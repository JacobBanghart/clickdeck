# USB protocol (draft v0)

How the PC talks to clickdeck, and how the display board talks to the knob
board. A draft for the prototype firmware; untested. Built on the lessons
from Stream32's documented protocol and Elgato's published HID docs
([lessons.md](lessons.md) #11–16, #20).

## USB device

One composite USB device on the ESP32-S3's native port:

| Interface | Purpose |
|---|---|
| **HID keyboard + consumer control** | Fallback: works with no host software. Keys send their stored shortcut; knobs send volume up/down (or arrow keys); knob press sends mute/enter. Standard boot keyboard, no driver. |
| **Data channel** | Everything else: images, settings, events to the host app. Prototype: USB CDC (serial, no driver anywhere). Later, if needed: vendor bulk with WinUSB descriptors for speed. |

- **IDs:** Espressif gives open-source projects free product IDs under its
  vendor ID 0x303A (requested through the espressif/usb-pids repo on GitHub).
  Until then, the prototype uses Espressif's development PID. The USB serial
  number is the device ID (from the ESP32-S3's MAC), so the host never grabs
  the wrong port.
- **Mode switch:** after the host app's `HELLO`, the device stops sending HID
  keystrokes and sends events on the data channel instead. If the app
  disconnects (no `PING` for 3 s), it falls back to HID keyboard mode.

## Framing (data channel)

Binary frames, not JSON (Stream32 found base64 JSON slow):

```
| magic 0xCD | type u8 | seq u16 | len u16 | payload (len bytes) | crc16 u16 |
```

- Little-endian. `crc16` is CRC-16/CCITT over type..payload.
- `seq` increments per frame; replies echo the request's `seq`.
- Max payload 4096 bytes; images are sent in chunks.
- Any frame the receiver doesn't understand gets `ERROR(unknown-type)`, so
  old firmware and new hosts (or the reverse) fail cleanly.

## Handshake

| Dir | Type | Payload |
|---|---|---|
| host → dev | `HELLO` | protocol version, host app name/version |
| dev → host | `HELLO_ACK` | protocol version, firmware version (ESP32-S3 and knob board), board ID, device ID, **feature list** (strings, e.g. `image-rle`, `image-jpeg`, `knob-haptics`, `touch-band`, `brightness`), key grid (cols, rows), **key image size in px**, knob count, knob display size in px |

- The host only uses features in the list (additive versioning: new features
  never break old firmware).
- The device reports key and knob-display sizes in pixels; the host renders
  artwork at exactly that size.

## Images

| Dir | Type | Payload |
|---|---|---|
| host → dev | `LAYOUT` | page number, for each key: image CRC32, action flags (e.g. "go to page N" handled on the device) |
| dev → host | `LAYOUT_ACK` | list of keys whose image isn't in the device's cache |
| host → dev | `IMAGE` | target (key n / knob display n / full strip), CRC32, encoding (`raw565`, `rle565`, `jpeg`), chunk index/count, data |
| dev → host | `IMAGE_ACK` | target, chunk index (host may have up to 4 chunks in flight) |
| host → dev | `OVERLAY` | temporary image or label for a key or knob display, kept in RAM only, expires 30 s after the host disconnects |

- **Cache by CRC:** images persist in flash keyed by CRC32 of the raw
  pixels. On reconnect, `LAYOUT_ACK` asks only for missing ones, usually
  none.
- **Saved pages work offline:** layouts and images persist; page switching
  keys work without a host.
- **Overlays** are for live state (mic muted, current volume) and never
  touch flash.
- The host picks the smallest encoding the device supports; flat icons
  compress ~99% with RLE.

## Input events (device → host)

| Type | Payload |
|---|---|
| `KEY` | key index, `down` / `up` / `long` (long-press threshold set by host) |
| `KNOB` | knob index, position (detent index or raw angle), delta since last event, velocity |
| `KNOB_PRESS` | knob index, `down` / `up` / `long` |
| `TOUCH` | position along the band (0–1), `tap` / `swipe_start` / `swipe` / `swipe_end` |
| `STATUS` | 5 V input voltage, estimated motor current, budget, errors (e.g. driver fault) |

Key down and key up are separate events, so push-to-talk and held
modifiers work (lessons.md #20).

## Knob configuration (host → device)

`KNOB_CONFIG` per knob, applied immediately, stored per page:

| Field | Meaning |
|---|---|
| `mode` | `detents`, `smooth`, `spring` (returns to center) |
| `detents` | clicks per turn (e.g. 24) |
| `detent_strength` | 0–1 |
| `friction` | 0–1 (smooth mode drag) |
| `min`, `max` | end stops in detents (omit for unbounded) |
| `stop_strength` | 0–1 |
| `position` | current position (so a knob can start at the app's current value) |

`HAPTIC` plays a one-off effect on a knob: `tick`, `buzz`, `bump`, with
strength and duration (queued so pulses never overlap, power budget rules
apply).

## Display and power (host → device)

| Type | Payload |
|---|---|
| `DISPLAY` | brightness 0–100, idle timeout (s), `blank_now`, `wake` |
| `POWER` | motor current budget (mA), defaults to 500 |
| `HID_MAP` | the shortcut each key and knob sends in fallback HID mode |

All of these persist in flash outside the firmware partition, so firmware
updates don't erase them.

## Firmware updates

- **ESP32-S3:** standard ESP32 USB flashing (esptool) over the same native
  USB port; the host app can trigger the reboot into the bootloader.
- **Knob board (RP2350B):** relayed by the ESP32-S3 over the internal UART:
  `FW_BEGIN` (size, SHA-256), `FW_CHUNK`, `FW_END`. The ESP32-S3 resets the
  RP2350B into its bootloader via the RUN line, streams the image, and the
  bootloader checks the hash before switching. Recovery: USB pads + BOOTSEL
  on the knob board.

## Internal link (display board ↔ knob board)

UART at 2 Mbaud on the 7B's UART2 connector. Same frame format, with COBS
encoding so a dropped byte can't desynchronize the stream. Message types
are a subset: `KEY`, `KNOB`, `KNOB_PRESS`, `TOUCH`, `STATUS` (knob board →
display board), `KNOB_CONFIG`, `HAPTIC`, `POWER`, `FW_*` (display board →
knob board). The display board forwards events to the host and configs to
the knob board, adding nothing in between.

## Open points

- CDC vs vendor bulk: measure image throughput on the prototype first
  (target: one key image under ~50 ms).
- Exact HID report descriptors and the default fallback key map.
- Whether OpenDeck's device-plugin interface needs anything extra from the
  device (check when writing the plugin).
