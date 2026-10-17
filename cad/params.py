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

# --- 7" 800x480 panel, AT070TN9x-class (EST) ----------------------------
PANEL_W, PANEL_H, PANEL_T = 164.9, 100.0, 5.7
AA_W, AA_H = 154.21, 85.92
PANEL_BORDER_BOTTOM = 4.0  # border on the knob side; FPC side faces the back

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
KNOB_PCB = (30.0, 30.0)
KNOB_PCB_LIFT = 1.0                     # bosses under the knob module
KNOB_CAP_D = 24.0
KNOB_CAP_H = 12.0                       # height above the top plate
KNOB_HOLE_D = 25.0
KNOB_WIN = (26.0, 15.0)                 # knob display window (max size)
MOTOR_TO_PLATE = 0.3

# --- Case -----------------------------------------------------------------
WALL = 2.5
FLOOR = 2.0
TOP_PLATE_T = 2.0
CORNER_R = 4.0
INNER_CLEAR = 1.0
USB_CUTOUT = (9.5, 3.6)
MAIN_PCB = (70.0, 40.0)

# --- Prototype (2 keys + 1 knob), laser-cut acrylic sandwich -------------
PROTO_KEYS = 2
PROTO_PLATE_T = 3.0        # 3 mm cast acrylic, top and base
PROTO_STANDOFF_D = 6.0     # M3 hex standoff (drawn round)

# --- Drawing ----------------------------------------------------------------
EXPLODE = 22.0
