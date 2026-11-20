#!/bin/sh
# Render a spectrogram PNG of a time range of an audio file, to look for steady lines (tones), gaps and lowpass edges.
# Usage: scripts/denoise-audio/spectrogram.sh IN.mp3 OUT.png [START_SECONDS [DURATION_SECONDS]]
set -e
[ $# -ge 2 ] || { sed -n '2,3p' "$0"; exit 1; }
ffmpeg -v error -y -ss "${3:-0}" -t "${4:-150}" -i "$1" \
  -lavfi "showspectrumpic=s=1600x800:legend=1:scale=log:fscale=lin:drange=110:limit=-30:stop=22050:color=intensity" "$2"
