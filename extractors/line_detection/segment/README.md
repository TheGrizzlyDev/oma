# Segmentation pass

This pass isolates candidate pixels from the source map using configurable color
space thresholds and conservative/aggressive masks.

## Usage

```bash
python extractors/line_detection/segment/segment_lines.py \
  --image path/to/map.png \
  --output-conservative out_conservative.png \
  --output-aggressive out_aggressive.png \
  --output-merged out_merged.png \
  --output-debug out_debug.png \
  --colorspace hsv \
  --channels 0,1,2 \
  --lower 100,50,50 \
  --upper 140,255,255
```
