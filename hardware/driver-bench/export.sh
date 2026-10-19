#!/usr/bin/env bash
# Generate the driver bench board (D24), check it, and export JLC files.
#   hardware/driver-bench/export.sh
# Needs KiCad 9 (kicad-cli + pcbnew for the system Python). No CAD step: this board
# isn't part of the device.
set -euo pipefail
cd "$(dirname "$0")"
PCB=driver-bench.kicad_pcb

/usr/bin/python3 gen_pcb.py

# DRC: fail on any error-level violation or unconnected item
kicad-cli pcb drc --severity-error --exit-code-violations -o drc.rpt "$PCB"

rm -rf jlc && mkdir -p jlc/gerbers
kicad-cli pcb export gerbers -o jlc/gerbers/ \
  --layers F.Cu,B.Cu,F.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts \
  --no-protel-ext "$PCB" > /dev/null
kicad-cli pcb export drill -o jlc/gerbers/ --format excellon --excellon-separate-th "$PCB" > /dev/null
(cd jlc/gerbers && zip -q ../driver-bench-gerbers.zip ./*)

# Pick-and-place: the SMD parts (U, C, R). The headers are through-hole and soldered by hand
kicad-cli pcb export pos -o jlc/pos-raw.csv --format csv --units mm --side front "$PCB" > /dev/null
{
  echo "Designator,Mid X,Mid Y,Layer,Rotation"
  awk -F, 'NR>1 {gsub(/"/,""); if ($1 ~ /^[UCR][0-9]/) print $1","$4"mm,"$5"mm,Top,"$6}' jlc/pos-raw.csv
} > jlc/driver-bench-cpl.csv
rm jlc/pos-raw.csv
mv bom.csv jlc/driver-bench-bom.csv

kicad-cli pcb render --side top --width 1600 --height 1200 --zoom 1.1 -o render_top.png "$PCB" > /dev/null
kicad-cli pcb render --side bottom --width 1600 --height 1200 --zoom 1.1 -o render_bottom.png "$PCB" > /dev/null
echo "OK: DRC clean; files in hardware/driver-bench/jlc/"
