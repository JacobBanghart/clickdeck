# Web configurator and host software

How clickdeck is set up and used from a computer. A plan; nothing is
written yet. Wire-level details: [protocol.md](protocol.md).

## The idea

Like [VIA](https://www.caniusevia.com/) for keyboards: a web page talks to
the device over USB, you set it up there, and **everything is stored on the
device**. After that clickdeck works on any computer with no software
installed: keys send their shortcuts and macros, knobs keep their feel, and
the screen shows its pages.

Three layers, each optional on top of the one before:

| Layer | What it is | Needed for |
|---|---|---|
| **Device** | Firmware on both chips, settings in their flash | Everything that works standalone: keys, macros, knob feel, pages and images |
| **Web configurator** | A static web page (WebUSB, WebHID, Web Serial) | Setting it up, firmware updates, recovery |
| **Host daemon** (`clickdeckd`) | A small optional program on the PC | Live integrations: changing images, app state (mic muted, volume), running scripts |

OpenDeck or Companion Satellite thin clients are possible later, on top of
the daemon. They aren't planned now: their APIs can't carry knob feel,
pages or swipes ([design-review.md](design-review.md), D4).

## Web configurator

**What it sets** (all saved to the device):
- Key layout and pages: which image and action each key has.
- Actions: HID shortcuts, media keys, macros (key sequences with delays),
  page switches, and "host" actions handed to the daemon.
- Knob feel per knob and page: detents, smooth, spring, end stops,
  strength, a tick at a preset, and what turning and pressing send.
  (Attention nudges and haptic notifications are an optional firmware
  module, off by default; the page shows them only if the device has it.)
- Touch band actions, if a band is fitted (optional add-on, D24): tap and swipe.
- Images: drop in a picture; the page scales it to the key size the device
  reports and uploads it compressed.
- Brightness and idle timeout.
- Firmware updates for both chips, and **Restore factory firmware**
  ([recovery.md](recovery.md)).
- Knob calibration, power status (the port's advertised current, the motor
  budget) and import/export of a whole profile as a file.

**Knob slots (D23):** the device reports what's in each slot: haptic,
lite or empty ([protocol.md](protocol.md)). The page shows one knob per
filled slot, in slot order, and hides empty slots. Knob feel, calibration
and the motor budget appear only for haptic slots; a lite slot keeps what
turning and pressing send and the software limits. Profiles move between
configurations: a slot's settings are kept when its module changes, and
unused until a matching module is back. Swapping a module means unplugging
USB first; the page notices the new layout on reconnect.

**Browsers:** Chromium-based only (Chrome, Edge, Brave, Opera). Firefox and
Safari don't support WebUSB. The device itself works everywhere; only setup
needs Chromium. The page can also be saved and run offline.

**Both chips at once:** the page opens two USB devices, the backplane and
the display board, and treats them as one clickdeck (pairing:
[protocol.md](protocol.md)). The first time, the browser asks permission for
each one; after that it remembers them.

**Trust (VIA-style, D17):** the browser's device picker is the
confirmation, as with VIA and Elgato's app. Keymap changes and firmware
updates apply with no physical OK, and a random web page can't reach
clickdeck unless you pick it. Malware on the PC could reflash it, but that
malware already controls the PC.

**Lock (optional):** a setting on the page, stored on the device, off by
default. With lock on, keymap changes and firmware updates need a 3 s knob
hold; until then the device ignores the change ([protocol.md](protocol.md)).

**Firmware updates** go through each chip's ROM bootloader, so a failed
update can always be retried:
- **Display (ESP32-S3):** the page asks it to reboot into download mode,
  then flashes it with [esptool-js](https://github.com/espressif/esptool-js)
  over Web Serial. You pick the port once in the browser's dialog. No BOOT
  button needed. Only with lock on and no optional GPIO6 link, the display
  can't see the knob hold, so the page asks you to start its bootloader
  with the BOOT pinhole instead ([recovery.md](recovery.md)).
- **Backplane (RP2350B):** the page asks it to reboot into its UF2
  bootloader, then writes the firmware over WebUSB (picotool-style). Drag
  and drop of a UF2 file onto the RP2350 drive works too.
- Builds come from the project's GitHub Releases, pinned by version and
  SHA-256 hash.

There are no A/B (OTA) slots: the ROM bootloader is the safety net. That
leaves more flash for images.

## Host daemon (`clickdeckd`)

Optional. Runs in the background and talks to the device over the same
WebUSB interfaces (with libusb). It:
- receives events from keys and knobs set to "host" actions;
- pushes live images and labels (overlays) that never touch flash;
- runs scripts and integrations (a small Python library, a local socket
  API);
- relays activity to the display, so idle blanking works (see below).

**One program at a time:** a USB interface can only be claimed by one
program. When the configurator opens, the daemon lets go of the device and
reconnects when the page closes.

**Screen blanking:** with no host and no GPIO6 link, the display never
idle-blanks, because it can't see key or knob activity and would have no
way to wake. With the daemon running, or with the link fitted
([wiring.md](wiring.md)), it blanks after the idle timeout and wakes on any
input. It always blanks while the PC is asleep (USB suspend).

## Linux setup

Chrome on Linux needs read/write access to the USB devices. Install the
udev rule shipped in the repo, then replug. It grants access with `uaccess`
(the logged-in user only, no group changes) and tells ModemManager to leave
the serial ports alone. It covers the normal firmware IDs and the
bootloader IDs, since updates and recovery use those:

```
# clickdeck (sketch; real product IDs to be assigned)
SUBSYSTEM=="usb", ATTRS{idVendor}=="2e8a", ATTRS{idProduct}=="<inputs PID>",  TAG+="uaccess"
SUBSYSTEM=="usb", ATTRS{idVendor}=="303a", ATTRS{idProduct}=="<display PID>", TAG+="uaccess"
# bootloaders: RP2350 BOOTSEL, ESP32-S3 USB serial/JTAG (download mode)
SUBSYSTEM=="usb", ATTRS{idVendor}=="2e8a", ATTRS{idProduct}=="000f", TAG+="uaccess"
SUBSYSTEM=="usb", ATTRS{idVendor}=="303a", ATTRS{idProduct}=="1001", TAG+="uaccess"
SUBSYSTEM=="tty", ATTRS{idVendor}=="303a", ATTRS{idProduct}=="1001", TAG+="uaccess", ENV{ID_MM_DEVICE_IGNORE}="1"
```

A snap-packaged Chromium also needs `snap connect chromium:raw-usb`.

Windows and macOS need nothing: the firmware's Microsoft OS 2.0
descriptors make Windows load WinUSB on its own.
