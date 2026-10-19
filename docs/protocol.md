# USB protocol (draft v0)

How the PC talks to clickdeck. A draft for the prototype firmware; untested. Built on the lessons
from Stream32's documented protocol and Elgato's published HID docs
([lessons.md](lessons.md) #11–16, #20). What the software does with it:
[configurator.md](configurator.md).

## Two USB devices behind a hub

The device has a USB 2.0 hub inside ([wiring.md](wiring.md)), so the PC sees
two devices. Over USB they never talk to each other; the web configurator
and the optional host daemon open both. An optional one-wire link inside
the case (below) carries a few things from the backplane to the display.

| Device | Chip | Does |
|---|---|---|
| **Inputs** | RP2350B on the backplane | Keys, knob turns and presses, touch band, haptics, motor power budget, keymap and macros |
| **Display** | ESP32-S3 on the Waveshare board | Key images and pages, knob display areas, brightness, idle blanking |

Interfaces per chip:

| Device | Interface | Purpose |
|---|---|---|
| Inputs | **HID keyboard** (boot protocol) | Keys, macros and knobs send their stored shortcuts. Works with no software on any OS |
| Inputs | **HID consumer control** | Media keys: volume, mute, play/pause |
| Inputs | **Vendor bulk (WebUSB)** | Data channel: keymap, knob feel settings, power settings, events for "host" actions. Low bandwidth |
| Display | **Vendor bulk (WebUSB)** | Data channel: images, pages, display settings |

- **Why bulk, not HID, for data:** WebHID moves 64-byte reports, one per
  1 ms frame at full speed, so about 64 KB/s; one raw key image would take
  over half a second. A vendor bulk interface is reachable from the browser
  through WebUSB and from the daemon through libusb. The inputs device uses
  the same kind of interface so the page and the daemon need one code path.
- **Descriptors:** both devices carry a WebUSB platform capability in their
  BOS descriptor and Microsoft OS 2.0 descriptors, so Windows binds WinUSB
  to the vendor interface with no driver install. macOS needs nothing.
  Linux needs a udev rule ([configurator.md](configurator.md)).
- **IDs:** the display device uses Espressif's vendor ID 0x303A (free
  product IDs for open-source projects via the espressif/usb-pids repo); the
  inputs device uses Raspberry Pi's 0x2E8A (free product IDs via the
  raspberrypi/usb-pid repo). Until assigned, the development PIDs, which
  collide with every Pico and ESP32 board: apply for real PIDs before the
  first release, and have the software open only devices whose USB product
  string matches. USB serial numbers come from each chip's unique ID.
- **Power descriptor:** both devices declare bMaxPower ≤ 100 mA. They sit
  behind a bus-powered hub, and Linux refuses configurations above 100 mA
  there (Arduino-ESP32 defaults to 500 mA, the Pico SDK to 250 mA).
- **Standalone first:** the inputs device always acts on its stored keymap.
  A key set to a shortcut or macro sends HID, whether or not any software
  is running. A key set to a "host" action sends a `KEY` event on the data
  channel instead, and does nothing if no host is listening. There's no
  mode switch. On every page switch, and when a host connects or goes away,
  it releases all HID keys first, so nothing stays held.
- **Host gone:** each device treats 3 s without a `PING` as "host gone".
  Overlays expire 30 s after that.
- **USB suspend** (PC asleep): the display blanks the backlight and stops
  the panel scan; the inputs device puts every driver in standby. Stored
  shortcuts don't fire on resume.
- **One program at a time:** a vendor interface can be claimed by one
  program only. The daemon releases it when the configurator asks
  ([configurator.md](configurator.md)).

### Pairing the two devices

A host may have more than one clickdeck, so the software has to know which
display goes with which backplane:

1. **Pairing ID** (first choice): on first contact the configurator writes
   a random 64-bit pairing ID to both devices (`PAIR`), stored in flash.
   Both report it in `HELLO_ACK`. This works in the browser, which can't
   see the USB topology, and through another hub or USB/IP. First pairing
   is interactive: the display shows a short code and the user presses a
   key, so the page can't pair the wrong display with the wrong backplane.
2. **Hub topology** (daemon check): both devices hang off the same hub, the
   CH334F (WCH vendor ID 0x1A86), on ports 1 (inputs) and 2 (display). On
   Linux the sysfs path shows it (`…-1.1` and `…-1.2` under the same
   parent); Windows and macOS expose the same location info. The daemon
   uses it to sanity-check the pairing ID.

The software treats the pair as one device: it sends images to the display
device and maps events from the inputs device onto the same keys.

## Framing (data channel)

Binary frames, not JSON (Stream32 found base64 JSON slow):

```
COBS( type u8 | seq u16 | len u16 | payload (len bytes) | crc16 u16 ) 0x00
```

- **COBS framing:** each frame is COBS-encoded and ends with a 0x00 byte,
  which never appears inside an encoded frame. A receiver that loses sync
  drops bytes up to the next 0x00 and starts again. (A single magic byte
  can also appear inside payloads, so it can't resync.) Bulk transfers can
  split or merge frames, so the framing stays even though USB itself is
  packet-based.
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
| 5 | `no-space` | Image storage full and nothing can be evicted |
| 6 | `version` | Protocol major version outside the supported range |
| 7 | `internal` | Firmware fault |
| 8 | `not-confirmed` | Lock is on and a change that needs the 3 s knob hold wasn't confirmed in time |

- **One codec:** a single C framing library for both firmwares, plus a
  TypeScript twin for the configurator and a Python twin for the daemon,
  all checked against shared golden test vectors and a malformed-frame
  fuzz test.

## Handshake

| Dir | Type | Payload |
|---|---|---|
| host → dev | `HELLO` | supported protocol version range (min, max), host kind (`configurator` / `daemon` / other) and version |
| dev → host | `HELLO_ACK` | protocol version chosen (or `ERROR(version)` if the ranges don't overlap), role (`inputs` / `display`), firmware version, slot types (inputs: one per knob slot, `haptic`, `lite` or `empty`, D23), device ID, pairing ID, **feature list** (strings, e.g. `image-rle`, `image-jpeg`, `knob-haptics`, `touch-band`, `brightness`, `link`), key grid (cols, rows); display: **key image size in px**, knob display size in px, free image storage; inputs: knob count, advertised USB current |
| host → dev | `PAIR` | pairing ID (both devices) |

- The host only uses features in the list (additive versioning: new features
  never break old firmware).
- The device reports key and knob-display sizes in pixels; the host renders
  artwork at exactly that size.
- **Knob slots (D23):** the backplane's RP2350B reads what's in each of
  the five slots at power-up from two ID rows in the key matrix (a haptic
  module has a diode to ID row A, a lite module to ID row B, an empty slot
  or blank has neither; [wiring.md](wiring.md)). A slot that reads haptic
  but gives no valid MT6701 frame is reported `empty` and its motor stays
  off. Modules aren't hot-plugged: the list is read once per power-up.
  `knob-haptics` is listed when at least one slot is haptic. Knob indices
  in `KNOB` and `KNOB_CONFIG` are slot numbers (0–4, left to right); empty
  slots send nothing. The host hides empty slots, and shows knob feel and
  motor power only for haptic slots.

## Trust and the optional lock

VIA-style trust (D17), as with VIA/QMK and Elgato's app. By default,
`KEYMAP`, `SAVE` and `REBOOT_BOOTLOADER` apply at once, with no physical
confirmation. The browser's WebUSB/Web Serial device picker is the
confirmation: a random web page can't touch clickdeck unless the user
picks it. The threat a physical OK would stop is malware on the PC
reflashing the device to stay around (BadUSB-style). That malware already
controls the PC, so for a macro pad the gain is small.

**Lock (optional, off by default).** A setting in the configurator, stored
on the device (`LOCK`). With lock on, `KEYMAP` (when saved), `SAVE` of a
keymap and `REBOOT_BOOTLOADER` need a 3 s knob hold:

1. The host sends the request. The inputs device answers `PENDING`, gives
   a short haptic tick (on a haptic slot), and the configurator shows "Hold any knob pressed
   for 3 s".
2. The user holds a knob pressed for 3 s. The device applies the change and
   answers `OK`.
3. No hold within 30 s: `ERROR(not-confirmed)`, nothing changes.

The display chip can't see the knobs. With the GPIO6 link fitted, the knob
board passes the confirmation over it, so the display's
`REBOOT_BOOTLOADER` is confirmed the same way. With lock on and no link,
the display refuses `REBOOT_BOOTLOADER` (`ERROR(not-confirmed)`) and the
configurator asks for the BOOT pinhole instead. That is the only case
outside recovery that needs a pinhole.

## Pages and images (display device)

Pages, their images and the display settings are stored on the device, so
the screen shows the right page with no host.

| Dir | Type | Payload |
|---|---|---|
| host → dev | `LAYOUT` | page number, for each key and knob display: image CRC32 |
| dev → host | `LAYOUT_ACK` | list of images the device doesn't have |
| host → dev | `IMAGE` | CRC32, size, encoding (`raw565`, `rle565`, `jpeg`), chunk index/count, data |
| dev → host | `IMAGE_ACK` | CRC32, chunk index (host may have up to 4 chunks in flight) |
| host → dev | `PAGE` | show page n now |
| host → dev | `OVERLAY` | temporary image or label for a key or knob display, kept in RAM only, expires 30 s after the host goes away |
| host → dev | `PERSIST` | save pages, their images and the display settings to flash |

- **Flash writes glitch the panel.** The 7B drives an RGB panel from a
  PSRAM framebuffer, and ESP-IDF says the LCD can't work while the external
  memory cache is disabled, which happens during every flash write. A
  missed bounce-buffer refill can also shift the image until reboot. So:
  - ESP-IDF 5.x (esp_lcd + esp_tinyusb), pinned. Framebuffer in PSRAM;
    bounce buffers (≥ 10 lines) in internal SRAM;
    `CONFIG_SPIRAM_XIP_FROM_PSRAM` (code runs from PSRAM, not flash);
    `LCD_RGB_RESTART_IN_VSYNC` as a backstop; PCLK ≤ 30 MHz.
  - Two framebuffers swapped at VSYNC, and dirty-rect redraws only.
  - `PERSIST` writes in one batch with the backlight off ("Saving…" shown
    in the configurator), then redraws.
- **Images by CRC:** images are stored keyed by CRC32 of the raw pixels and
  shared between pages. Working copies sit in PSRAM with LRU eviction. On
  reconnect, `LAYOUT_ACK` asks only for missing ones, usually none.
- **Storage:** no OTA slots ([configurator.md](configurator.md)), so all
  flash past the one app partition holds images and settings. `HELLO_ACK`
  reports what's free.
- **Overlays** are for live state from the daemon (mic muted, current
  volume) and never touch flash.
- **Encoding:** RLE or JPEG by default, raw only as a fallback. The host
  picks the smallest encoding the device supports; flat icons compress ~99%
  with RLE.
- **Throughput:** plan on ~0.5 MB/s over full-speed USB (Espressif's own
  figure for its USB stack) until measured on a 7B. One raw 146×146 key
  (42.6 KB) then takes ~85 ms and a raw full page ~1.8 s; compressed is
  much faster. Target: a full page in under 300 ms.

## Link inside the case (optional)

A one-wire UART from a spare RP2350B pin to the 7B's GPIO6 connector (J8),
on a bought 3-pin HY2.0 lead ([wiring.md](wiring.md)). One way, backplane
to display. Short binary messages, same CRC:

| Message | Meaning |
|---|---|
| `page n` | A page-switch key was pressed: show page n |
| `activity` | A key, knob or touch was used: reset the idle timer, wake |
| `confirm` | The 3 s knob hold happened (for the display's bootloader request when lock is on) |
| `reset-settings` | Settings reset at power-up ([recovery.md](recovery.md)) |

Without the link, page switching and idle blanking need a host, and the
display never idle-blanks on its own.

## Input events (inputs device → host)

Sent for keys and knobs set to "host" actions, or for everything if the
host subscribes (`SUBSCRIBE all`).

| Type | Payload |
|---|---|
| `KEY` | key index, page, `down` / `up` / `long` (long-press threshold in the keymap) |
| `KNOB` | knob index, timestamp, position (detent index or raw angle), delta since last event, velocity. Sent at most 200 times a second |
| `KNOB_PRESS` | knob index, `down` / `up` / `long` |
| `TOUCH` | position along the band (0–1), segment (which knob's area), `tap` / `long` / `swipe_start` / `swipe` / `swipe_end` |
| `STATUS` | 5 V input voltage, the port's advertised current (default / 1.5 A / 3 A), estimated motor current, budget, brownout trip count, errors (e.g. driver fault, sensor CRC error) |

Key down and key up are separate events, so push-to-talk and held
modifiers work (lessons.md #20).

## Keymap (host → inputs device)

`KEYMAP` sets, per page, what each key, knob turn, knob press and touch
gesture does:

| Action | Does |
|---|---|
| `hid` | A shortcut: modifiers + key, or a consumer code |
| `macro` | A sequence of key downs/ups and delays |
| `page` | Switch page (keymap and knob feel at once; images too if the link is fitted or a host is running) |
| `host` | Send an event to the daemon |
| `none` | Nothing |

## Knob configuration (host → inputs device)

`KNOB_CONFIG` per knob and page. Applied at once and kept in RAM for every
page, so page switches don't touch flash. Flash writes stall the RP2350's
FOC loop, so configs reach flash only on an explicit `SAVE`, and only while
every motor is asleep. The FOC loop runs from RAM (`__not_in_flash_func`).
Fields:

| Field | Meaning |
|---|---|
| `mode` | `detents`, `smooth`, `spring` (returns to center) |
| `detents` | clicks per turn (e.g. 24) |
| `detent_strength` | 0–1 |
| `friction` | 0–1 (smooth mode drag) |
| `min`, `max` | end stops in detents (omit for unbounded) |
| `stop_strength` | 0–1 |
| `marks` | positions (in detents) that give a tick as the knob passes them, e.g. a preset |
| `position` | current position (so a knob can start at the app's current value) |

These fields are the core knob feel (D20). A lite slot uses only `min`,
`max` (limits in software, nothing to feel) and `position`, counted in
encoder steps (24 per turn); its detents are fixed by the encoder
ordered. A config for an empty slot is stored and ignored. Their behavior follows
SimpleFOC and SmartKnob's documented detent and end-stop profiles
([lessons.md](lessons.md)).

**Optional, not part of v0:** host-triggered haptic effects (attention
nudges, notifications) belong to an optional firmware module, off by
default, that a build can leave out. If it's ever added, it gets its own
message and a `haptic-effects` feature flag in `HELLO_ACK`, and the host
uses it only when the device lists that flag.

## Display and power (host → device)

| Type | Payload |
|---|---|
| `DISPLAY` (display) | brightness 0–100, idle timeout (s), `blank_now`, `wake` |
| `POWER` (inputs) | motor current budget (mA); the default comes from the port's advertised current ([wiring.md](wiring.md)). Only with a haptic slot |
| `SAVE` (inputs) | write the keymap, knob configs and `POWER` to flash, once every motor is asleep |
| `RESET_SETTINGS` (both) | back to defaults; knob calibration kept |
| `LOCK` (both) | lock on/off (off by default); on: keymap saves and `REBOOT_BOOTLOADER` need the 3 s knob hold |
| `REBOOT_BOOTLOADER` (both) | reboot into the ROM bootloader (needs the 3 s knob hold only when lock is on) |

The daemon forwards activity (a key press, a knob turn) to the display
device as `DISPLAY wake`, since idle blanking lives on the display side.
With no host and no link, the display never idle-blanks.

Settings live in flash outside the firmware, so updates don't erase them.
Each settings block has a version and a checksum; a bad one boots defaults
without overwriting it ([recovery.md](recovery.md)).

## Firmware updates

Through each chip's ROM bootloader, from the web configurator
([configurator.md](configurator.md)). No OTA slots, no custom bootloader.

- **Display (ESP32-S3):** `REBOOT_BOOTLOADER` sets the force-download flag
  and restarts; the chip comes back as Espressif's USB serial/JTAG device
  (303A:1001), and esptool-js flashes it over Web Serial. Plain esptool
  works too. No BOOT button needed. Recovery (dead firmware): the BOOT
  pinhole.
- **Inputs (RP2350B):** `REBOOT_BOOTLOADER` restarts into the RP2350's ROM
  UF2 bootloader (2E8A:000F); the page writes the image over WebUSB
  (PICOBOOT interface, as picotool does), or the user drags a UF2 file onto
  the drive. Recovery (dead firmware): the BOOTSEL pinhole.
- **Toolchains:** ESP-IDF 5.x for the display; arduino-pico + SimpleFOC for
  the RP2350B. Pin every version for both firmwares and build them in CI
  (lessons.md #7). Releases carry SHA-256 hashes.
- Never burn eFuses or OTP ([recovery.md](recovery.md)).

## Open points

- Measure image throughput on a 7B over the vendor bulk interface (plan:
  ~0.5 MB/s; target: a full page in under 300 ms with compression).
- Exact HID report descriptors and the default keymap.
- Daemon API (local socket, Python library) and how OpenDeck or Companion
  Satellite clients would sit on it.
