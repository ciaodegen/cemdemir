#!/bin/sh
# usage: scripts/preview.sh <name> <out.png>
set -e
npx tsx scripts/preview-svg.tsx "$1" > "$2.svg"
python3 -c "import cairosvg,sys; cairosvg.svg2png(url=sys.argv[1], write_to=sys.argv[2])" "$2.svg" "$2"
