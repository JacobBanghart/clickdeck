"""All dimensions in mm. Change values here, then run `python cad/build.py`.

Values marked (EST) come from datasheets or seller listings. Measure the real
part before ordering anything that depends on them.
"""

# --- Keys ----------------------------------------------------------------
KEY_COLS = 7
KEY_ROWS = 3
KEY_PITCH = 22.0          # center-to-center, about Stream Deck XL density
CAP_SIZE = 18.0           # clear cap body, square
CAP_CLEAR = 0.2           # cap-to-hole clearance per side (top plate + PCB window)
CAP_PROTRUDE = 1.5        # how far caps stand above the top plate
CAP_TOP_FILLET = 0.6
FLANGE_T = 1.2            # thickness of the tab and lips under the top plate
LIP_W = 0.8               # left/right retention lips (keep the cap from lifting out)
LIP_LEN = 10.0
TAB_W = 6.0               # bottom-edge tab that presses the switch
NUB_D = 1.5               # nub on the tab, sits on the switch actuator
NUB_H = 0.3
CAP_TO_PLATE = 0.2        # gap between flange top and top plate underside

# Micro switch: Omron B3U-1000P SMD tactile, 3.0 x 2.5 x 1.6, 0.15 mm travel.
# 13 mm mouse switches do not fit between keys at this pitch.
SW_L, SW_W, SW_H = 3.0, 2.5, 1.6
SW_EDGE_MARGIN = 0.3      # copper keep-out from the PCB window edge

# --- PCBs -----------------------------------------------------------------
PCB_T = 1.6
FRAME_PCB_MARGIN = 3.0    # frame PCB extends this far past the panel active area
GLASS_GAP = 0.2           # frame PCB / cap bottoms sit this far above the glass

# --- 7" panel: Waveshare ESP32-S3-LCD-7B (1024x600) -----------------------
# From Waveshare's dimension drawing (docs.waveshare.com/ESP32-S3-Touch-LCD-7B).
# Mounted with the panel's thick border (where the ribbon cable exits) toward
# the knobs, so Waveshare's ESP32 board sits at the back, clear of our knob
# board. "Left" is as seen from the front.
PANEL_W, PANEL_H = 165.72, 97.6          # metal back frame (the glass is 164 x 97)
PANEL_T = 5.7                            # glass + backlight + frame (EST, not published)
AA_W, AA_H = 153.84, 85.632              # active area
PANEL_BORDER_FRONT = 9.5                 # frame edge to active area, knob side (EST from drawing)
PANEL_BORDER_LEFT = 3.1                  # (EST from drawing); right border is the remainder
PANEL_M3_DX = 126.2                      # 4x M3 mounting tabs on the back frame
PANEL_M3_FROM_FRONT = 18.31
PANEL_M3_FROM_BACK = 13.64
# Waveshare's ESP32-S3 board, on M2.5 standoffs behind the panel, parts facing down
DISPLAY_PCB = (105.0, 72.0)              # (EST from photo)
DISPLAY_PCB_LEFT = 27.2                  # frame left edge to the board's left edge (EST)
DISPLAY_PCB_BACK = 0.5                   # frame back edge to the board's back edge (EST)
DISPLAY_STANDOFF_H = 3.0                 # frame to board (EST, measure)
DISPLAY_PARTS_H = 5.0                    # tallest part under the board, HY2.0 connectors (EST)
USB_FROM_PCB_BACK = 35.6                 # native USB-C port center, on the board's left edge (EST)
USB_TUNNEL = (12.5, 7.5)                 # hole through the left wall for a USB-C plug (w x h)

# --- 2.4" 240x320 SPI module, used landscape in the prototype (EST) -----
P24_GLASS = (60.26, 42.72, 2.5)
P24_AA = (48.96, 36.72)
P24_PCB = (77.0, 44.0)
P24_PCB_OFFSET_X = 8.25    # module PCB sticks out past the glass on the header side

# --- Knob (Mitoot 2204 gimbal motor + MT6701 knob module) ---------------
KNOBS = 5
MOTOR_D, MOTOR_H = 27.85, 13.1          # (EST) measure when it arrives
MOTOR_BASE_D, MOTOR_BASE_H = 22.0, 3.0  # stator mount (EST)
SHAFT_BORE = 3.4
MAGNET_D, MAGNET_H = 6.0, 2.5           # diametric magnet on the shaft end
SENSOR_GAP = 1.0                        # magnet face to MT6701 top
MT6701 = (4.9, 3.9, 1.5)                # SOIC-8 body
TMC6300 = (3.0, 3.0, 0.9)               # QFN-20
# Knob board: one PCB for all knobs (sensors, drivers, RP2040). Each knob sits
# on a tongue cut free by a U-shaped slot, hinged at the back. Pressing the
# knob flexes the tongue onto a B3U switch under its front tip (press-to-click).
TONGUE = 26.0                           # tongue size (square), centered on the knob
TONGUE_SLOT = 1.0                       # slot width around the tongue
TONGUE_HINGE_W = 8.0                    # uncut neck at the back = the hinge
KNOB_PRESS_GAP = 0.05                   # press switch actuator to case floor
KNOB_BOARD_EDGE = 3.0                   # solid border outside the slots
KNOB_BOARD_BACK = 18.0                  # solid strip behind the tongues (RP2040, connector)
RP2040 = (7.0, 7.0, 0.9)
# Knob: tapered, wider at the top (similar in size to common aluminum
# encoder knobs). Printed (or CNC'd) as part of the build, so builders don't
# need to buy knobs.
#
# KNOB_STYLE:
#   "integrated"    one printed/CNC part per knob that bolts straight onto
#                   the motor bell (no adapter). Default.
#   "shaft_adapter" use any standard 6 mm D-shaft encoder knob on a small
#                   adapter that bolts onto the motor bell.
KNOB_STYLE = "integrated"
KNOB_TOP_D = 19.0
KNOB_BOT_D = 16.0
KNOB_H = 15.0
KNOB_BORE_D = 6.0                       # standard 6 mm D-shaft (EC11)
KNOB_BORE_DEPTH = 10.0
KNOB_GAP = 1.0                          # knob bottom to top plate
KNOB_STEM_D = 14.0                      # integrated: stem through the top plate to the bell
# Shaft adapter (shaft_adapter style only): screws onto the motor bell, gives the knob a 6 mm D-shaft
ADAPTER_D = 14.0
ADAPTER_H = 1.5
SHAFT_FLAT = 4.5                        # D-shaft: 6 mm round with a flat at 4.5 mm
PLATE_SHAFT_HOLE_D = 8.0                # top plate hole, shaft_adapter style
KNOB_WIN = (26.0, 15.0)                 # knob display area per knob (max size)
# Touch band: a thin capacitive sensor PCB glued under the top plate, right
# below the knob displays. Tap or swipe on the plate surface (like the + XL
# touch strip). Touching the display glass itself doesn't work: it sits ~7 mm
# below the top surface because of the key stack.
TOUCH_BAR = True
TOUCH_BAR_T = 0.8                       # thin PCB
TOUCH_BAR_MARGIN = 0.8                  # clearance to the window above and motors below
TOUCH_BAR_MIN_H = 5.0
TOUCH_BAR_H = 10.0                      # knobs move forward as needed to make room
MOTOR_TO_PLATE = 0.3

# --- Case -----------------------------------------------------------------
# Case parts should fit a common home 3D printer bed (Bambu A1/P1, Prusa MK4).
PRINT_BED = (256.0, 256.0, 256.0)
# The case is a slab on a separate wedge stand, like the Stream Deck + XL.
TILT_DEG = 42.0           # slab angle toward the user (40–45° range chosen)
STAND_INSET = 8.0         # stand is this much narrower than the slab on each side
STAND_FRONT_SETBACK = 6.0  # stand starts this far behind the slab's front edge
WALL = 2.5
FLOOR = 2.0
TOP_PLATE_T = 2.0
CORNER_R = 4.0
INNER_CLEAR = 1.0

# --- Prototype (2 keys + 1 knob), laser-cut acrylic sandwich -------------
PROTO_KEYS = 2
PROTO_PLATE_T = 3.0        # 3 mm cast acrylic, top and base
PROTO_STANDOFF_D = 6.0     # M3 hex standoff (drawn round)

# --- Drawing ----------------------------------------------------------------
EXPLODE = 22.0
