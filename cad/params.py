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
CAP_EDGE_R = 1.0          # vertical cap edges (the PCB/plate window corners can't be sharp)
FLANGE_T = 1.2            # thickness of the tab and lips under the top plate
LIP_W = 0.8               # left/right retention lips (keep the cap from lifting out)
LIP_LEN = 10.0
TAB_W = 6.0               # bottom-edge tab that presses the switch
NUB_D = 2.0               # domed nub on the tab, sits on the switch actuator
NUB_H = 0.3
CAP_TO_PLATE = 0.2        # gap between flange top and top plate underside

# Micro switch: Omron B3U-1000P SMD tactile, 3.0 x 2.5 x 1.6, 0.15 mm travel.
# 13 mm mouse switches do not fit between keys at this pitch.
SW_L, SW_W, SW_H = 3.0, 2.5, 1.6
SW_EDGE_MARGIN = 0.3      # switch body to the PCB window edge (its pads sit ~0.7 mm in)

# --- PCBs -----------------------------------------------------------------
PCB_T = 1.6
FRAME_PCB_MARGIN = 3.0    # frame PCB extends this far past the panel active area
PCB_WIN_EXTRA = 0.1       # PCB key windows are this much larger per side than the plate's,
                          # so the printed plate (not the PCB edge) guides the cap
PCB_WIN_R = 0.5           # inside corner radius of milled PCB windows (JLC mills ~R0.5)
HOLE_COMP = 0.0           # added to printed hole sizes (cap/window/hub holes, magnet
                          # pockets); set it from print_fit_coupon.stl on your printer
GLASS_GAP = 0.2           # frame PCB / cap bottoms sit this far above the glass

# --- 7" panel: Waveshare ESP32-S3-LCD-7B (1024x600) -----------------------
# From Waveshare's dimension drawing (docs.waveshare.com/ESP32-S3-Touch-LCD-7B).
# Mounted with the panel's thick border (where the ribbon cable exits) toward
# the knobs, so Waveshare's ESP32 board sits at the back, clear of our knob
# board. "Left" is as seen from the front.
PANEL_W, PANEL_H = 165.72, 97.6          # metal back frame (the glass is 164 x 97)
PANEL_T = 3.7                            # glass front to the frame's back sheet (Waveshare STEP model)
PANEL_TAB_T = 1.7                        # M3 tabs: thread length; tab face is 2.5 mm below the back sheet
AA_W, AA_H = 153.84, 85.632              # active area
PANEL_BORDER_FRONT = 9.5                 # frame edge to active area, knob side (EST from drawing)
PANEL_BORDER_LEFT = 3.1                  # (EST from drawing); right border is the remainder
PANEL_M3_DX = 126.2                      # 4x M3 mounting tabs on the back frame
PANEL_M3_FROM_FRONT = 18.31
PANEL_M3_FROM_BACK = 13.64
# Waveshare's ESP32-S3 board, screwed flat onto the panel's back frame, parts
# facing down. Depths measured from Waveshare's STEP model (2026-10-17).
DISPLAY_PCB = (106.02, 73.02)
DISPLAY_PCB_LEFT = 26.0                  # frame left edge to the board's left edge (STEP)
DISPLAY_PCB_BACK = 0.2                   # frame back edge to the board's back edge (STEP)
DISPLAY_STANDOFF_H = 2.5                 # board sits on 2.5 mm bosses, level with the tab faces (STEP)
DISPLAY_PARTS_H = 5.0                    # deepest general part under the board: the microSD socket (STEP)
DISPLAY_CONNECTOR_H = 8.3                # the row of six HY2.0 connectors on one edge (STEP)
FLOOR_POCKET_MARGIN = 1.0                # floor pocket under the connectors, if they need one
DISPLAY_CONN_ROW = (46.7, 47.0)          # connector row: center from the board's back edge, length (STEP)
# Two USB-C ports on the board's left edge, facing left (Waveshare STEP model, 2026-10-17):
# the native USB port ("USB", Type_C2) and the USB-to-UART port behind it. Which
# is which is from the earlier estimate: check the silkscreen on the real board.
USB_FROM_PCB_BACK = 36.1                 # native USB-C port center from the board's back edge
UART_USB_FROM_PCB_BACK = 51.2            # USB-to-UART port (not used)
USB_BELOW_PCB = 1.22                     # port center below the board's underside (STEP)

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
MT6701 = (4.9, 3.9, 1.5)                # MT6701CT-STD, SOP-8 body (the QT is a 3x3 QFN-16)
# Motor mount: the stator base sits on a printed spacer ring (sensor + gap + magnet
# tall) and is screwed from under the tongue into the base's threaded holes.
MOTOR_SPACER_ID = 12.0                  # clears the sensor and the magnet
MOTOR_SPACER_OD = 21.0                  # inside the base; clears the driver at (9, -9)
MOTOR_SCREW_BC = 16.0                   # base screw bolt circle, 4x M2 (EST: measure)
MOTOR_THREAD_DEPTH = 3.0                # threaded depth in the stator base (EST: measure)
MOTOR_LOCATE_PIN_D = 1.5                # two spacer pins into NPTH holes in the tongue (centering)
TMC6300 = (3.0, 3.0, 0.9)               # QFN-20
# Knob board: one PCB for all knobs (sensors, drivers, RP2040). Each knob sits
# on a tongue cut free by a U-shaped slot, hinged at the back. Pressing the
# knob flexes the tongue onto a B3U switch under its front tip (press-to-click).
TONGUE = 26.0                           # tongue size (square), centered on the knob
TONGUE_SLOT = 1.0                       # slot width around the tongue
TONGUE_HINGE_W = 8.0                    # uncut neck at the back = the hinge
KNOB_PRESS_GAP = 0.2                    # press switch actuator to its striker (nominal)
STRIKER_PROUD = 0.4                     # M2x3 set screw (striker) tip above the floor; set at calibration
STRIKER_LEN = 3.0
KNOB_BOARD_EDGE = 5.0                   # solid border outside the slots (front edge carries screws)
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
KNOB_WIN_LEDGE = (0.9, 0.8)             # plate ledge under each clear window cover (width, thickness)
# Touch band: a thin capacitive sensor PCB glued under the top plate, right
# below the knob displays. Tap or swipe on the plate surface (like the + XL
# touch strip). Touching the display glass itself doesn't work: it sits ~7 mm
# below the top surface because of the key stack.
TOUCH_BAR = True
TOUCH_BAR_T = 0.8                       # thin PCB
TOUCH_BAR_MARGIN = 0.8                  # clearance to the window above and motors below
TOUCH_BAR_MIN_H = 5.0
TOUCH_BAR_H = 11.2                      # knobs move forward as needed to make room
TOUCH_BAR_RECESS = 0.4                  # flat pocket in the plate underside the band sits in
MOTOR_TO_PLATE = 0.8                    # bell (hub flange) to plate underside

# --- Case -----------------------------------------------------------------
# Case parts should fit a common home 3D printer bed (Bambu A1/P1, Prusa MK4).
PRINT_BED = (256.0, 256.0, 256.0)
# The case is a slab on a separate wedge stand, like the Stream Deck + XL.
TILT_DEG = 42.0           # slab angle toward the user (40–45° range chosen)
STAND_INSET = 8.0         # stand is this much narrower than the slab on each side
STAND_LIFT = 3.0          # stand material under the slab's front-bottom edge
STAND_LIP = (3.0, 2.5)    # lip in front of the slab's front face (height up the face, thickness)
STAND_SHELL = 3.0         # stand wall thickness (open underneath, with ribs)
WALL = 2.5
FLOOR = 3.0               # room to recess screw heads and magnets underneath
TOP_PLATE_T = 2.0
CORNER_R = 4.0
INNER_CLEAR = 1.0

# --- Mounting and service (full device) ----------------------------------
# Everything mounts upward from the tray. Screws into printed plastic are
# self-tapping (no inserts). Screws from below hide under the stand.
INNER_CLEAR_BACK = 8.0      # room behind the panel for the top plate's back posts
PANEL_POST_D = 8.0          # posts under the panel's M3 tabs; M3 screws from below
PANEL_SCREW_PAST = 1.95     # screw tip past the tab face: tab ~1.7 thick, LCD back sheet 2.5 above
PANEL_SCREW_MAX = 2.2       # check limit for the above
FLOOR_WEB_MIN = 1.2         # floor left above a screw counterbore
PLATE_POST_D = 7.0          # top plate posts down to the floor; M3 self-tapping from below
PLATE_POST_INSET = 4.0      # post center from the inner wall
M3_CLEAR, M3_PILOT = 3.4, 2.6
M3_HEAD = (6.0, 1.8)        # pan head (ISO 7045 / K30 thread-forming) diameter, height
M2_CLEAR, M2_PILOT = 2.2, 1.7
M2_HEAD = (3.8, 1.3)
M2_CSK_HEAD = (3.8, 1.2)    # countersunk (knob hub flange)
KNOB_BOARD_BOSS_D = 5.5     # floor bosses under the knob board (M2 from above)
FRAME_PCB_MARGIN_SIDE = 7.0 # frame PCB side margins carry its mounting holes
FRAME_BOSS_D = 5.5          # top plate bosses the frame PCB screws into (M2 from below)
FRAME_PIN_D = 1.5           # locating pins on the plate into NPTH holes in the frame PCB
KNOB_HUB_D = 10.0           # hub on the motor bell; the knob cap presses onto it
KNOB_HUB_FLAT = 8.5         # D-flat: width across the flat (drives the cap)
KNOB_HUB_RIB = 0.15         # 3 crush ribs in the cap bore: interference on the hub
HUB_FLANGE_T = 2.0          # hub flange screwed to the bell's threaded holes
HUB_FLANGE_D = 24.0
HUB_SCREW_BC = 16.0         # bell top holes, 4x M2 (EST: measure); the flange centers on the shaft bore
BELL_THREAD_DEPTH = 1.5     # bell top thickness at the holes (EST: measure)
KNOB_HUB_ENGAGE = 6.0       # how far the hub reaches into the knob cap
KNOB_HUB_HOLE_CLEAR = 1.0   # top plate hole = hub + this (the plate lifts off over the hubs)
MAGNET_TRAY = (8.0, 1.5)    # magnets in the tray bottom (diameter, thickness)
MAGNET_ROWS = (0.45, 0.85)  # magnet rows, fraction of the tray depth from the front
                            # (behind the knob board, away from the angle sensors)
MAGNET_STAND = (8.0, 3.0)   # matching magnets in the stand
FOOT = (10.0, 1.5)          # rubber feet (diameter, thickness)
PINHOLE_D = 3.0             # back-wall holes to press the display board's BOOT/RESET
# Display board button positions, from its left (USB) edge as seen from the front (STEP)
DISPLAY_BUTTONS = {"BOOT": 59.2, "RESET": 48.1}
DISPLAY_BUTTON_Z = 0.3      # button center below the board's underside (STEP)
TOOL_D = 5.0                # screwdriver shaft diameter used for the access check

# --- Prototype (2 keys + 1 knob), laser-cut acrylic sandwich -------------
PROTO_KEYS = 2
PROTO_PLATE_T = 3.0        # 3 mm cast acrylic, top and base
PROTO_STANDOFF_D = 6.0     # M3 hex standoff (drawn round)
PROTO_FRAME_HALF_W = 36.0  # proto frame PCB half width: holes and pads clear the 2.4" glass (+-30.1)
PROTO_COPPER_EDGE = 0.5    # proto frame PCB copper-to-edge clearance
# The frame PCB hangs from the top plate on M2 standoffs at its side margins
FRAME_MOUNT_INSET = 3.0    # hole center from the frame PCB's side edge
FRAME_MOUNT_Y = (8.0, -12.0)
FRAME_MOUNT_HOLE_D = 2.2   # M2 clearance

# --- Internal cabling (full device) ----------------------------------------
# No soldering or crimping by the builder: every internal link is a bought
# cable plugged into a connector JLC fits. See docs/wiring.md.
# USB-C plug bodies (overmold + the metal that sticks out of the socket):
# (width, thickness, length out of the socket face). Typical cables measure
# 10.5-12.5 x 5.5-6.5 mm; the model uses the large end.
USB_PLUG_STRAIGHT = (12.5, 6.5, 22.0)
USB_PLUG_RA = (12.5, 6.5, 13.0)         # right-angle ("side-angle") plug: cable leaves sideways
USB_CABLE_D = 3.5                       # USB 2.0 C-to-C cable
USB_BEND_R = 10.0                       # minimum bend radius for the USB-C cable
USB_C_SOCKET = (8.94, 3.26, 7.35)       # receptacle shell (w, h, depth)
# USB board: hub + external USB-C socket, back-left corner of the tray (docs/wiring.md)
USB_BOARD_Z = 2.5                       # board underside above the floor (on printed bosses)
USB_EXT_X = -16.0                       # external port, x from the case center (left of the pinholes)
USB_EXT_POCKET = (13.0, 7.0)            # opening in the back wall the plug overmold seats in
USB_ARM_UNDER = 3.6                     # USB board arm reaches this far under the display board
                                        # (clears its underside parts) so the socket has board behind it
GH_PLUG = (10.8, 4.3, 5.5)              # JST-GH 8-pin plug outside its header (w, h, length)
GH_HEADER = (12.8, 4.3, 4.3)            # SM08B-GHS-TB side-entry header (w, h, depth)
GH_CABLE_D = 3.0
# 2204 motor leads: ~30 cm with a 3-pin 2.54 mm servo-style plug (Futaba/JR) per one
# listing; VERIFY ON ARRIVAL. The knob board has a right-angle 1x3 header per motor.
MOTOR_PLUG = (7.6, 2.6, 14.0)           # plug body (w, h, length)
MOTOR_LEAD_LEN = 300.0
MOTOR_LEAD_D = 2.2
HEADER_3P = (2.5, 7.6, 2.5)             # right-angle 1x3 header body (along the pins, w, h)
# Keys: 12-pin 1.0 mm FFC between two flip-lock ZIF connectors. Touch: JST-SH 6-pin.
ZIF_12P = (16.0, 4.6, 2.0)              # (length along the pins' row, depth, height) (EST)
SH_HEADER_SIDE = (9.0, 4.25, 2.9)       # SM06B-SRSS-TB, side entry (w, depth, h)
SH_HEADER_TOP = (9.0, 4.25, 4.25)       # BM06B-SRSS-TB, top entry (w, depth, h)
SH_PLUG = (7.0, 3.0, 4.5)               # JST-SH 6-pin plug body outside the header (w, h, length)
# Plug insertion check: each plug needs a straight path this long behind it: its
# travel into the socket plus ~3 mm, at the step that connects it (fingers grip the
# plug body from the sides; the cable trails behind).
# Motor plugs: the header pins are ~6 mm long.
PLUG_APPROACH = {"usb": 10.0, "gh": 6.0, "sh": 5.0, "motor": 6.0, "ffc": 2.0}
LIFT_SERVICE = 40.0                     # top plate lifts this far with its cables still plugged in
CLIP = (2.0, 1.2)                       # printed cable clip prong (thickness, lip)

# --- Drawing ----------------------------------------------------------------
EXPLODE = 22.0
