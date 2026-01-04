# Vectorization pass

Converts a skeleton raster into GeoJSON LineStrings.

## Usage

```bash
python extractors/line_detection/vectorize/vectorize_skeleton.py \
  --mask skeleton.png \
  --bbox 0 0 1200 958 \
  --output lines.geojson \
  --output-debug debug.png \
  --output-stats stats.json
```
