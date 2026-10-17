# USB protocol (draft v0)

How the PC talks to clickdeck. A draft for the prototype firmware; untested. Built on the lessons
from Stream32's documented protocol and Elgato's published HID docs
([lessons.md](lessons.md) #11–16, #20).

## Two USB devices behind a hub

The device has a USB 2.0 hub inside ([wiring.md](wiring.md)), so the PC sees
two devices. They never talk to each other directly; the host app talks to
both.

| Device | Chip | Does |
|---|---|---|
| **Inputs** | RP2350B on the knob board | Keys, knob turns and presses, touch band, haptics, motor power budget |
| **Display** | ESP32-S3 on the Waveshare board | Key images, knob display areas, brightness, idle blanking |

Interfaces:

| Device | Interface | Purpose |
|---|---|---|
| Inputs | **HID keyboard + consumer control** (two HID interfaces: a boot keyboard and a consumer-control one) | Fallback: works with no host software. Keys send their stored shortcut; knobs send volume up/down (or arrow keys); knob press sends mute/enter. Standard boot keyboard, no driver. |
| Inputs | **Data channel** (USB CDC) | Input events to the host app; knob settings, haptics, power settings from it. Low bandwidth |
| Display | **Data channel** | Images, display settings. Prototype: USB CDC (serial, no driver anywhere). Later, if needed: vendor bulk with WinUSB descriptors for speed |

- **IDs:** the display device uses Espressif's vendor ID 0x303A (free
  product IDs for open-source projects via the espressif/usb-pids repo); the
  inputs device uses Raspberry Pi's 0x2E8A (free product IDs via the
  raspberrypi/usb-pid repo). Until assigned, the development PIDs, which
  collide with every Pico and ESP32 board: apply for real PIDs before the
  first release, and have the host probe only ports whose USB product
  string matches. USB serial numbers come from each chip's unique ID.
- **Power descriptor:** both devices declare bMaxPower ≤ 100 mA. They sit
  behind a bus-powered hub, and Linux refuses configurations above 100 mA
  there (Arduino-ESP32 defaults to 500 mA, the Pico SDK to 250 mA).
- **Mode switch:** after the host app's `HELLO`, the inputs device stops
  sending HID keystrokes and sends events on its data channel instead. If the
  app disconnects (no `PING` for 3 s), it falls back to HID keyboard mode.
  On every mode switch it releases all HID keys first, so nothing stays held.
  The display device has the same `PING` timeout (overlay expiry depends on
  it).
- **USB suspend** (PC asleep): the display blanks the backlight and stops
  the panel scan; the inputs device puts every driver in standby. After
  resume, the 3 s timeout must not fire stored HID shortcuts.
- **Linux:** ship a udev rule that sets `ID_MM_DEVICE_IGNORE=1` (so
  ModemManager doesn't probe the CDC ports) and grants access through
  `uaccess`.

### Pairing the two devices

A host may have more than one clickdeck, so the app has to know which
display goes with which knob board:

1. **Hub topology** (first choice): both devices hang off the same hub, the
   CH334F (WCH vendor ID 0x1A86), on ports 1 (inputs) and 2 (display). On
   Linux the sysfs path shows it (`…-1.1` and `…-1.2` under the same parent);
   Windows and macOS expose the same location info.
2. **Pairing ID** (fallback and check): on first contact the app writes a
   random 64-bit pairing ID to both devices (`PAIR`), stored in flash.
   Both report it in `HELLO_ACK`, so the pair is found again even through
   another hub or a USB/IP setup. First pairing is interactive: the display
   shows a short code and the user presses a key, so the app can't pair the
   wrong display with the wrong knob board.

The app treats the pair as one device: it renders images for the display
device and maps events from the inputs device onto the same keys.

## Framing (data channel)

Binary frames, not JSON (Stream32 found base64 JSON slow):

```
COBS( type u8 | seq u16 | len u16 | payload (len bytes) | crc16 u16 ) 0x00
```

- **COBS framing:** each frame is COBS-encoded and ends with a 0x00 byte,
  which never appears inside an encoded frame. A receiver that loses sync
  drops bytes up to the next 0x00 and starts again. (A single magic byte
  can also appear inside payloads, so it can't resync.)
- Little-endian. `crc16` is CRC-16/CCITT over the whole frame before
  encoding (type..payload). A frame with a bad CRC or length is dropped and
  answered with `ERROR(bad-frame)` if its `seq` is readable.
- **Sequence numbers:** each direction has its own `seq` counter, so
  unsolicited events never clash with requests. Replies echo the request's
  `seq`.
- Max payload 4096 bytes; images are sent in chunks. Each chunk is acked;
  a `NAK` (with chunk index and error code) or a 500 ms timeout makes the
  host resend that chunk, up to 3 times.
- **`PING` / `PONG`:** the host sends `PING` every 1 s to both devices; no
  payload. Each device treats 3 s without one as "host gone".
- **Errors:** `ERROR` carries the request's `seq` and a code:

| Code | Name | Meaning |
|---|---|---|
| 1 | `unknown-type` | Frame type not supported; old firmware and new hosts (or the reverse) fail cleanly |
| 2 | `bad-frame` | CRC or length wrong |
| 3 | `bad-args` | Payload doesn't parse or a value is out of range |
| 4 | `busy` | Try again later (e.g. a flash write is running) |
| 5 | `no-space` | Image cache full and nothing can be evicted |
| 6 | `version` | Protocol major version outside the supported range |
| 7 | `internal` | Firmware fault |

- **One codec:** a single C framing library for both firmwares, plus a
  Python twin for the host, checked against shared golden test vectors and
  a malformed-frame fuzz test.

## Handshake

| Dir | Type | Payload |
|---|---|---|
| host → dev | `HELLO` | supported protocol version range (min, max), host app name/version |
| dev → host | `HELLO_ACK` | protocol version chosen (or `ERROR(version)` if the ranges don't overlap), role (`inputs` / `display`), firmware version, board ID, device ID, pairing ID, **feature list** (strings, e.g. `image-rle`, `image-jpeg`, `knob-haptics`, `touch-band`, `brightness`), key grid (cols, rows); display: **key image size in px**, knob display size in px; inputs: knob count, advertised USB current |
| host → dev | `PAIR` | pairing ID (both devices) |

- The host only uses features in the list (additive versioning: new features
  never break old firmware).
- The device reports key and knob-display sizes in pixels; the host renders
  artwork at exactly that size.

## Images (display device)

| Dir | Type | Payload |
|---|---|---|
| host → dev | `LAYOUT` | page number, for each key: image CRC32 |
| dev → host | `LAYOUT_ACK` | list of keys whose image isn't in the device's cache |
| host → dev | `IMAGE` | target (key n / knob display n / full strip), CRC32, encoding (`raw565`, `rle565`, `jpeg`), chunk index/count, data |
| dev → host | `IMAGE_ACK` | target, chunk index (host may have up to 4 chunks in flight) |
| host → dev | `OVERLAY` | temporary image or label for a key or knob display, kept in RAM only, expires 30 s after the host disconnects |
| host → dev | `PERSIST` | save the current page, its images and the display settings to flash (batched, at the next blank or idle moment) |

- **Flash writes glitch the panel.** The 7B drives an RGB panel from a
  PSRAM framebuffer, and ESP-IDF says the LCD can't work while the external
  memory cache is disabled, which happens during every flash write. A
  missed bounce-buffer refill can also shift the image until reboot. So:
  - Framebuffer in PSRAM; bounce buffers (≥ 10 lines) in internal SRAM;
    `CONFIG_SPIRAM_XIP_FROM_PSRAM` (code runs from PSRAM, not flash);
    `LCD_RGB_RESTART_IN_VSYNC` as a backstop; PCLK ≤ 30 MHz. These are
    ESP-IDF sdkconfig settings, which a precompiled Arduino-ESP32 core
    can't change (toolchain choice: [open-questions.md](open-questions.md)).
  - Two framebuffers swapped at VSYNC, and dirty-rect redraws only.
- **Cache by CRC:** images are cached in PSRAM keyed by CRC32 of the raw
  pixels, with LRU eviction. On reconnect, `LAYOUT_ACK` asks only for
  missing ones, usually none.
- **Saved pages persist only on `PERSIST`:** flash is written lazily, in
  one batch, when the host says so, and only while the screen is blanked or
  idle. Then the last page shows without a host. Anything the host updates
  more than about once a minute should be an overlay. Switching pages
  offline needs a link between the chips (see Open points).
- **Overlays** are for live state (mic muted, current volume) and never
  touch flash.
- **Encoding:** RLE or JPEG by default, raw only as a fallback. The host
  picks the smallest encoding the device supports; flat icons compress ~99%
  with RLE.
- **Throughput:** plan on ~0.5 MB/s over full-speed CDC (Espressif's own
  figure). One raw 146×146 key (42.6 KB) then takes ~85 ms and a raw full
  page ~1.8 s; compressed is much faster.

## Input events (inputs device → host)

| Type | Payload |
|---|---|
| `KEY` | key index, `down` / `up` / `long` (long-press threshold set by host) |
| `KNOB` | knob index, timestamp, position (detent index or raw angle), delta since last event, velocity. Sent at most 200 times a second |
| `KNOB_PRESS` | knob index, `down` / `up` / `long` |
| `TOUCH` | position along the band (0–1), segment (which knob's area), `tap` / `long` / `swipe_start` / `swipe` / `swipe_end` |
| `STATUS` | 5 V input voltage, the port's advertised current (default / 1.5 A / 3 A), estimated motor current, budget, brownout trip count, errors (e.g. driver fault, sensor CRC error) |

Key down and key up are separate events, so push-to-talk and held
modifiers work (lessons.md #20).

## Knob configuration (host → inputs device)

`KNOB_CONFIG` per knob, applied immediately and kept in RAM (the host
resends it on each page switch). Flash writes stall the RP2350's FOC loop,
so configs reach flash only on an explicit `SAVE`, and only while every
motor is asleep. The FOC loop runs from RAM (`__not_in_flash_func`).
Fields:

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
| `DISPLAY` (display) | brightness 0–100, idle timeout (s), `blank_now`, `wake` |
| `POWER` (inputs) | motor current budget (mA); default comes from the port's advertised current (500 / 1000 / 1500) |
| `HID_MAP` (inputs) | the shortcut each key and knob sends in fallback HID mode |
| `SAVE` (inputs) | write knob configs, `POWER` and `HID_MAP` to flash, once every motor is asleep |

The app forwards activity (a key press, a knob turn) to the display device
as `DISPLAY wake`, since idle blanking lives on the display side and the
display can't see the inputs itself.

These apply at once and stay in RAM. They reach flash (outside the
firmware partition, so firmware updates don't erase them) only on `SAVE`
(inputs) or `PERSIST` (display).

## Firmware updates

- **Display (ESP32-S3):** standard ESP32 USB flashing (esptool) over its
  own USB connection; the host app can trigger the reboot into the
  bootloader.
- **Inputs (RP2350B):** `REBOOT_BOOTLOADER` puts it into the RP2350's
  built-in USB bootloader; the app (or the user, drag and drop) copies a UF2
  file. Recovery: hold the BOOTSEL button on the knob board while plugging
  in; make it reachable through a pinhole, or use the RP2350's A/B
  partitions with rollback so a bad UF2 can't brick it.
- **Toolchains:** pin every version for both firmwares and build them in
  CI (lessons.md #7).

There's no internal link between the two chips any more (the earlier draft
relayed the knob board's events and firmware over a UART).

## Open points

- **Offline page switching.** Without the host app the keys still work as a
  keyboard (stored shortcuts) and the display shows its last saved page, but
  a "go to page N" key can't change the images: the two chips can't reach
  each other without the host. Fix if wanted: a 3-wire lead from the display
  board's GPIO6 connector (J8) to a header on the knob board, carrying a page
  number. See [open-questions.md](open-questions.md).
- CDC vs vendor bulk: measure image throughput first (plan: ~0.5 MB/s;
  target: a full page in under 300 ms with compression). Vendor bulk with
  WinUSB is the fallback.
- Exact HID report descriptors and the default fallback key map.
- Whether OpenDeck's device-plugin interface needs anything extra from the
  device (check when writing the plugin).
