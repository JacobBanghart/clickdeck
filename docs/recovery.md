# Recovery and factory reset

How to get clickdeck back to a known-good state after experimenting with
firmware or settings. Untested, like everything else in this repo.

clickdeck has two chips, each on its own USB connection through the internal
hub ([wiring.md](wiring.md)):

- **Display board** (Waveshare 7B, ESP32-S3): images, pages, brightness.
- **Backplane** (RP2350B): keys, knobs, touch band, keymap, knob feel.

Both chips have a bootloader in ROM. Nothing we flash can overwrite it, so
a bad update can always be retried. The only way to truly brick a chip is
to burn its one-time fuses (see the warning at the end).

## Step 0: unplug for 10 seconds

Always start here. Unplug the USB cable from the PC, wait 10 s, plug it back
in.

Why: the 7B has a small helper chip (a CH32V003 I/O expander) that an
ESP32-S3 reset doesn't reset. One of its pins (EXIO5) switches the ESP32's
USB lines between USB and CAN. If buggy firmware drives it high, the
display board vanishes from USB and stays gone until the helper chip loses
power. 10 s lets the board's capacitors drain. The pin has a pull-down, so
after a real power-off it comes back as USB.

If the device works again after this, you're done.

## Level 1: reset settings (firmware kept)

Use this when the firmware runs but a keymap, knob setting or page is
broken.

1. Unplug.
2. Hold the **top-left key**.
3. Plug in and keep holding for about 3 s. The knobs give a short buzz
   when the reset is done (with the GPIO6 link fitted, the screen says so
   too).

What it clears: the keymap, macros, knob feel, pages, images and display
settings. What it keeps: the firmware, and each knob's calibration (that's
measured on your hardware, not a setting; the configurator can redo it).

The backplane reads the key. With the optional GPIO6 link fitted
([wiring.md](wiring.md)), it passes the reset to the display board. Without
the link, reset the display side from the web configurator ("Reset display
settings"), or use Level 2.

**Automatic fallback:** every stored settings block carries a version
number and a checksum. If either doesn't check out (a power cut during a
save, or settings from a newer firmware), the chip boots with defaults and
shows a notice. It doesn't overwrite the old block until you save again, so
going back to the matching firmware brings the settings back.

## Level 2: restore factory firmware (web configurator)

Use this when firmware is broken, or to undo your own builds.

1. Open the web configurator in Chrome or Edge ([configurator.md](configurator.md)).
2. Choose **Restore factory firmware**.
3. Follow the prompts. The page:
   - downloads the pinned builds from the project's GitHub Release and
     checks their SHA-256 hashes;
   - asks each chip to reboot into its ROM bootloader, with no button or
     pinhole. If lock is on, you hold a knob for 3 s to confirm
     ([protocol.md](protocol.md)); with lock on and no optional GPIO6 link
     the display board can't see the hold, so the page asks you to use its
     BOOT pinhole (below) instead;
   - flashes the display board with esptool-js over Web Serial (ESP32-S3
     download mode) and the backplane over WebUSB (RP2350B UF2 bootloader);
   - offers to erase stored settings as well (off by default).

If a chip's firmware is too broken to answer, the page tells you to use the
pinholes below to start its bootloader by hand, then carries on.

## Level 3: pinholes (manual bootloader entry)

Three pinholes on the outside of the case. BOOT and RESET are in the back
wall. BOOTSEL is in the case floor under the backplane's left end, 11 mm
from the left edge and 30.5 mm from the front: lift the slab off the stand
to reach it. Pictures: [assembly.md](assembly.md). Use a paper clip or a
SIM tool.

| Pinhole | Chip | What it does |
|---|---|---|
| BOOT | ESP32-S3 (display board) | Held while powering up (or while tapping RESET): starts ROM download mode |
| RESET | ESP32-S3 (display board) | Restarts the display board |
| BOOTSEL | RP2350B (backplane) | Held while plugging in: starts the RP2350B's ROM UF2 bootloader |

**Display board:** do Step 0. Hold BOOT, plug in, release BOOT. The board
shows up as an Espressif USB serial device; the configurator (or plain
esptool) can flash it.

**Backplane:** do Step 0. Hold BOOTSEL, plug in, release. The board shows
up as an "RP2350" USB drive. The configurator flashes it, or drag a UF2 file
onto the drive. The motor drivers stay off in the bootloader (hardware
pull-downs hold them in standby).

After flashing, unplug for 10 s again so both chips start clean.

## Linux

Chrome needs permission to open the devices, including their bootloader
modes. Install the udev rule from the repo (it uses `uaccess`), then replug.
Details: [configurator.md](configurator.md).

## Never burn fuses

**Never burn ESP32 eFuses or RP2350 OTP.** That includes secure boot, flash
encryption, disabling download mode or BOOTSEL, and JTAG/debug lock bits.
These are one-way: once set, no pinhole, cable or tool can undo them, and the
chip may refuse to run anything but signed code. That is the only truly
irreversible brick.

clickdeck firmware never writes them, and the configurator has no option
to. Don't run `espefuse.py burn_*` or `picotool otp` commands on a
clickdeck, and check what someone else's firmware does before you flash it.
