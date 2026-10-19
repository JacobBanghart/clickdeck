"""All dimensions in mm. Change values here, then run `python cad/build.py`.

Values marked (EST) come from datasheets or seller listings. Measure the real
part before ordering anything that depends on them.
"""

# --- Keys ----------------------------------------------------------------
KEY_COLS = 7
KEY_ROWS = 3
KEY_PITCH = 22.0          # center-to-center
CAP_SIZE = 18.0           # clear cap body, square
CAP_CLEAR = 0.2           # cap-to-window clearance per side, base of the PCB window
                          # (the plate's guide uses KEY_GUIDE_CLEAR)
CAP_PROTRUDE = 1.5        # how far caps stand above the top plate
CAP_TOP_FILLET = 0.6
CAP_EDGE_R = 1.0          # vertical cap edges (the PCB/plate window corners can't be sharp)
FLANGE_T = 1.2            # thickness of the tab and lips under the top plate
LIP_W = 1.2               # left/right retention lips (keep the cap from lifting out);
                          # wide enough that their down-stop rails land on the PCB
LIP_LEN = 10.0
TAB_W = 6.0               # bottom-edge tab that presses the switch
NUB_D = 2.0               # domed nub on the tab, sits on the switch actuator
NUB_H = 0.3
CAP_TO_PLATE = 0.2        # gap between flange top and top plate underside
# Cap down-stop (D8): rails under the side lips and two lugs at the back corners
# stop on the frame PCB's top face after KEY_STOP_GAP of travel, so a hard or
# off-center press lands on the PCB, never on the glass. The switch trips first.
KEY_STOP_GAP = 0.5        # stop feet to the PCB top, at rest
STOP_RAIL_W = 0.6         # rail under each side lip (outer part of the lip, over the PCB)
STOP_LUG_X = (5.5, 8.5)   # back lugs: x range from the cap center (clear of the next row's tab)
STOP_LUG_REACH = 1.8      # back lugs stick out this far past the cap's back edge
SW_TRAVEL_MAX = 0.35      # B3U actuator travel to the click, worst case (Omron A162-E1: pretravel max)
# Cap guide (D8, B3): caps move straight up and down, guided by the plate. No
# rocker, hinged, tilting or pivoting caps. The plate's key hole continues down as
# a skirt around the cap (cut away where the lips, tabs, lugs and switches pass) to
# just above the frame PCB. Tilt = guide clearance over engagement length; it is
# guide slop, not a feature. The down-stop keeps the cap off the glass.
KEY_GUIDE_CLEAR = 0.05    # cap to guide, per side (printed PETG plate, SLA caps); the plate's
                          # key hole uses it too. Tune with the fit coupon via HOLE_COMP
KEY_GUIDE_WALL = 0.8      # skirt wall thickness (two 0.4 mm perimeters)
KEY_GUIDE_GAP = 0.2       # skirt bottom to the frame PCB's top face
KEY_GUIDE_POCKET = 0.3    # skirt clearance around the cap's lips, tabs, lugs and the switches
KEY_PRESS_DESIGN_N = 3.0  # a firm press; the cap must stay off the glass at this force
KEY_GLASS_MARGIN = 0.1    # required cap/PCB-to-glass clearance at the design force
FR4_E, FR4_G = 20000.0, 4000.0   # N/mm², for the frame PCB deflection estimate (grillage)

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
GLASS_GAP = 0.8           # frame PCB / cap bottoms sit this far above the glass (D8: 0.5–0.8;
                          # costs ~0.6 mm more image depth than the old 0.2)

# --- 7" panel: Waveshare ESP32-S3-LCD-7B (1024x600) -----------------------
# From Waveshare's dimension drawing (docs.waveshare.com/ESP32-S3-Touch-LCD-7B).
# Mounted with the panel's thick border (where the ribbon cable exits) toward
# the knobs, so Waveshare's ESP32 board sits at the back, clear of our knob
# board. "Left" is as seen from the front.
PANEL_W, PANEL_H = 165.72, 97.6          # metal back frame
PANEL_GLASS = (164.0, 97.0)              # glass, centered on the frame (nothing may sit on it)
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
# J8 (HY2.0 3-pin: 3V3, GND, GPIO6), the optional link from the knob board (D5). Which of
# the six connectors in the row is J8 is an estimate: check the silkscreen.
DISPLAY_J8_FROM_PCB_BACK = 66.3          # J8 center from the board's back edge (EST: front-most slot)
DISPLAY_J8_BELOW_PCB = 2.5               # J8 mouth center below the board's underside (EST)

# --- Knob (Mitoot 2204 gimbal motor + MT6701 sensor) ----------------------
KNOBS = 5
MOTOR_D, MOTOR_H = 27.85, 13.1          # (EST) measure when it arrives
MOTOR_BASE_D, MOTOR_BASE_H = 22.0, 3.0  # stator mount (EST)
SHAFT_BORE = 3.4
MAGNET_D, MAGNET_H = 6.0, 2.5           # diametric magnet on the shaft end
SENSOR_GAP = 1.0                        # magnet face to MT6701 top
MT6701 = (4.9, 3.9, 1.5)                # MT6701CT-STD, SOP-8 body (the QT is a 3x3 QFN-16)
# Motor mount: the stator base sits on a printed spacer ring (sensor + gap + magnet
# tall) and is screwed from under the tongue into the base's threaded holes. The
# spacer has an arm forward over the slot that presses the knob's press switch (D6).
MOTOR_SPACER_ID = 12.0                  # clears the sensor and the magnet
MOTOR_SPACER_OD = 21.0                  # inside the base; clears the driver at (9, -9)
MOTOR_SCREW_BC = 16.0                   # base screw bolt circle, 4x M2 (EST: measure)
MOTOR_THREAD_DEPTH = 3.0                # threaded depth in the stator base (EST: measure)
MOTOR_LOCATE_PIN_D = 1.5                # two spacer pins into NPTH holes in the tongue (centering)
MOTOR_SPACER_ARM_W = 5.0                # arm from the spacer to over the press switch
TMC6300 = (3.0, 3.0, 0.9)               # QFN-20; on the back strip next to its motor header (D16)
# Knob board: one PCB for all knobs (sensors, drivers, RP2350B). Each knob sits
# on a tongue cut free by a U-shaped slot, hinged at the back. Every part is on
# the top side (D6): pressing the knob flexes the tongue down, and the arm on
# the motor spacer presses a B3U on the fixed front border (press-to-click).
TONGUE = 26.0                           # tongue size (square), centered on the knob
TONGUE_SLOT = 1.0                       # slot width around the tongue
TONGUE_HINGE_W = 8.0                    # uncut neck at the back = the hinge
KNOB_PRESS_GAP = 0.2                    # press switch actuator to its striker (nominal)
STRIKER_LEN = 3.0                       # M2x3 set screw in the spacer arm (striker); set at calibration
KNOB_UNDER_CLEAR = 2.0                  # tongue underside to the floor: motor screw heads (1.3) + travel
KNOB_BOARD_EDGE = 5.0                   # solid border outside the slots (front edge carries screws)
KNOB_BOARD_BACK = 19.0                  # solid strip behind the tongues (RP2350B, drivers, connectors)
RP2350B = (10.0, 10.0, 0.85)            # QFN-80
# BOOTSEL (recovery): a reverse-mount tact switch on the knob board's left border,
# its plunger through the board, pressed with a paperclip through a hole in the
# case floor (lift the slab off the stand). A plain tact switch on the bottom side
# fits the same spot if no reverse-mount part is found (it'd be the one bottom part).
BOOTSEL_SW = (3.0, 4.0, 1.5)            # body on the top side (x, y, h) (EST: part not chosen)
BOOTSEL_PLUNGER = (1.2, 0.3)            # plunger diameter, how far it reaches below the board
BOOTSEL_FROM_KNOB0 = 8.0                # y offset from knob 0's center, on the left border
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
# below the knob displays. Tap or swipe on the plate surface. Touching the display glass itself doesn't work: it sits ~7 mm
# below the top surface because of the key stack.
TOUCH_BAR = True                        # False: no band, no touch cable/header (D12: optional)
TOUCH_BAR_T = 0.8                       # thin PCB
TOUCH_BAR_MARGIN = 0.8                  # clearance to the window above and motors below
TOUCH_BAR_MIN_H = 5.0
TOUCH_BAR_H = 11.2                      # knobs move forward as needed to make room
TOUCH_BAR_RECESS = 0.4                  # flat pocket in the plate underside the band sits in
MOTOR_TO_PLATE = 0.8                    # bell (hub flange) to plate underside

# --- Case -----------------------------------------------------------------
# Case parts should fit a common home 3D printer bed (Bambu A1/P1, Prusa MK4).
PRINT_BED = (256.0, 256.0, 256.0)
# The case is a slab on a separate wedge stand that tilts it toward the user.
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
# Everything mounts upward from the tray. Screws from below hide under the stand.
# The top plate's posts (undone for every service) take M3 heat-set inserts (D14);
# the other screws into printed plastic are thread-forming.
INNER_CLEAR_BACK = 9.0      # room behind the panel for the top plate's back posts
PANEL_POST_D = 8.0          # posts under the panel's M3 tabs; M3 screws from below
PANEL_SCREW_PAST = 1.95     # screw tip past the tab face: tab ~1.7 thick, LCD back sheet 2.5 above
PANEL_SCREW_MAX = 2.2       # check limit for the above
FLOOR_WEB_MIN = 1.2         # floor left above a screw counterbore
PLATE_POST_D = 8.0          # top plate posts down to the floor; M3 from below into a heat-set insert
PLATE_POST_INSET = 4.5      # post center from the inner wall
INSERT_M3 = (4.0, 5.7)      # M3 heat-set insert: hole diameter, length (e.g. Ruthex RX-M3x5.7)
M3_CLEAR, M3_PILOT = 3.4, 2.6
M3_HEAD = (6.0, 1.8)        # pan head (ISO 7045 / K30 thread-forming) diameter, height
M2_CLEAR, M2_PILOT = 2.2, 1.7
M2_HEAD = (3.8, 1.3)
M2_CSK_HEAD = (3.8, 1.2)    # countersunk (knob hub flange)
KNOB_BOARD_BOSS_D = 5.5     # floor bosses under the knob board (M2 from above)
FRAME_PCB_MARGIN_SIDE = 7.0 # frame PCB side margins carry its mounting holes
FRAME_BOSS_D = 5.5          # top plate bosses the frame PCB screws into (M2 from below)
FRAME_INNER_BOSS_D = 4.0    # bosses at strip crossings between keys (room between the caps' lugs)
# Frame PCB support (D8). Pan-head screws only where there's no glass under the
# head (back edge, left side); everywhere else countersunk M2 in countersunk holes
# (JLC option), heads flush with the PCB underside. Supports: the webs between the
# knob windows, the right edge, and two strip crossings between keys.
FRAME_INNER_SUPPORT_X = (-33.0, 33.0)   # strip crossings (x) between key rows 2 and 3
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
PINHOLE_D = 3.0             # back-wall holes for the display board's BOOT/RESET, floor hole for BOOTSEL
# Display board button positions, from its left (USB) edge as seen from the front (STEP)
DISPLAY_BUTTONS = {"BOOT": 59.2, "RESET": 48.1}
DISPLAY_BUTTON_Z = 0.3      # button center below the board's underside (STEP)
TOOL_D = 5.0                # screwdriver shaft diameter used for the access check

# --- Prototype (2 keys on the real 7B): printed top plate, acrylic base -----
# Changed 2026-10-18 (D3): the real Waveshare 7B and the full build's 2 top-left
# keys with their own small frame PCB (second-switch footprints for the force
# test). The knob is tested on its own printed stand (below), with bought
# breakouts; the knob board, hub and touch circuits are first tested on Rev A.
PROTO_KEY_IDX = (0, 1)     # which of the full build's keys (top-left two)
PROTO_PLATE_T = 3.0        # top plate: 3 mm print (it carries the cap guides); base: 3 mm cast acrylic
PROTO_STANDOFF_D = 6.0     # M3 hex standoff (drawn round)
PROTO_PLATE_MARGIN = 9.0   # plates reach this far past the panel
PROTO_FRAME_RIGHT = 8.0    # proto frame PCB margin right of the keys (holes + a routing channel)
PROTO_COPPER_EDGE = 0.5    # proto frame PCB copper-to-edge clearance
PROTO_SECOND_SWITCH = True # second B3U footprint above each key window (D8 force test)
FRAME_MOUNT_HOLE_D = 2.2   # M2 clearance
# Knob test stand (JLC3DP print): a deck the 2204 screws onto (M2 from below), an
# MT6701 breakout slid in on rails under the deck with its chip up in the deck's
# center hole, and an open tunnel for the header wires. The knob sits as high above
# the motor as in the full build.
KTS_W, KTS_D = 40.0, 40.0          # footprint
KTS_BASE_T = 3.0                   # base plate on the desk
KTS_WALL = 4.0                     # side walls (they carry the rails)
KTS_TUNNEL_H = 20.0                # base to the breakout's underside (header pins, jumper housings)
KTS_CBORE = 2.0                    # counterbore depth for the M2 motor screw heads (from below)
MT6701_BREAKOUT = (16.0, 1.6)      # (EST) breakout width across the rails, PCB thickness: measure it

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
# Optional GPIO6 link (D5): HY2.0 3-pin, knob board header (side entry, top side) to the 7B's J8
HY_LINK = True                          # model the optional lead (the header footprint is always there)
HY_HEADER = (8.0, 4.0, 4.5)             # SMD side-entry header (w, depth, h) (EST)
HY_PLUG = (8.0, 4.5, 6.0)               # HY2.0 3-pin plug body outside its socket (w, h, length) (EST)
HY_CABLE_D = 2.4
HY_KNOB_X = 57.0                        # header x on the knob board's back edge
# Optional USB-PD sink (D9): CH224-class, not fitted by default; area on the USB board
PD_SINK = (5.0, 4.0, 1.0)               # chip + passives keep-out (EST)
SH_HEADER_SIDE = (9.0, 4.25, 2.9)       # SM06B-SRSS-TB, side entry (w, depth, h)
SH_HEADER_TOP = (9.0, 4.25, 4.25)       # BM06B-SRSS-TB, top entry (w, depth, h)
SH_PLUG = (7.0, 3.0, 4.5)               # JST-SH 6-pin plug body outside the header (w, h, length)
# Plug insertion check: each plug needs a straight path this long behind it: its
# travel into the socket plus ~3 mm, at the step that connects it (fingers grip the
# plug body from the sides; the cable trails behind).
# Motor plugs: the header pins are ~6 mm long.
PLUG_APPROACH = {"usb": 10.0, "gh": 6.0, "sh": 5.0, "motor": 6.0, "ffc": 2.0, "hy": 5.0}
LIFT_SERVICE = 40.0                     # top plate lifts this far with its cables still plugged in
CLIP = (2.0, 1.2)                       # printed cable clip prong (thickness, lip)

# --- Drawing ----------------------------------------------------------------
EXPLODE = 22.0
