#!/usr/bin/env bash
# Regenerate the prototype frame PCB from the CAD, check it, and export JLC files.
#   hardware/proto-frame/export.sh
# Needs: the project's .venv (CAD) and KiCad 9 (kicad-cli + pcbnew for the system Python).
set -euo pipefail
cd "$(dirname "$0")"
ROOT=../..
PCB=proto-frame.kicad_pcb

"$ROOT/.venv/bin/python" "$ROOT/cad/build.py" --no-render --strict > /dev/null
/usr/bin/python3 gen_pcb.py

# DRC: fail on any error-level violation or unconnected item
kicad-cli pcb drc --severity-error --exit-code-violations -o drc.rpt "$PCB"

rm -rf jlc && mkdir -p jlc/gerbers
kicad-cli pcb export gerbers -o jlc/gerbers/ \
  --layers F.Cu,B.Cu,F.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts \
  --no-protel-ext "$PCB" > /dev/null
kicad-cli pcb export drill -o jlc/gerbers/ --format excellon --excellon-separate-th "$PCB" > /dev/null
(cd jlc/gerbers && zip -q ../proto-frame-gerbers.zip ./*)

# Pick-and-place (only the switches are assembled; test pads and holes aren't parts)
kicad-cli pcb export pos -o jlc/pos-raw.csv --format csv --units mm --side front "$PCB" > /dev/null
{
  echo "Designator,Mid X,Mid Y,Layer,Rotation"
  awk -F, 'NR>1 && $1 ~ /SW/ {gsub(/"/,""); print $1","$4"mm,"$5"mm,Top,"$6}' jlc/pos-raw.csv
} > jlc/proto-frame-cpl.csv
rm jlc/pos-raw.csv

cat > jlc/proto-frame-bom.csv <<'EOF'
Comment,Designator,Footprint,LCSC
B3U-1000P,"SW1,SW2",SW_SPST_B3U-1000P,C231329
EOF

kicad-cli pcb render --side top --width 1600 --height 1200 --zoom 1.1 -o render_top.png "$PCB" > /dev/null
kicad-cli pcb render --side bottom --width 1600 --height 1200 --zoom 1.1 -o render_bottom.png "$PCB" > /dev/null
echo "OK: DRC clean; files in hardware/proto-frame/jlc/"
