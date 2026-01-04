# Line detection utilities

## GeoJSON extraction

Use the existing detector to extract linework from a map image:

```bash
python -m pip install -r extractors/line_detection/requirements.txt

python extractors/line_detection/detect_lines.py \
  --image path/to/map.png \
  --bbox 0 0 1200 958 \
  --polygon "0,0 1200,0 1200,958 0,958" \
  --output lines.geojson
```

## Overlay viewer

Generate an HTML viewer that overlays the source image with the extracted GeoJSON:

```bash
python extractors/line_detection/visualize_overlay.py \
  --image path/to/map.png \
  --geojson lines.geojson \
  --bbox 0 0 1200 958 \
  --output overlay.html
```

Open `overlay.html` in a browser. Use the opacity slider to compare the extracted
linework against the original map.

If you are using Bazel, each `line_detection_geojson` target also generates a
run target that writes an HTML overlay in the current directory:

```bash
bazel run //extractors/line_detection:cam_waterlines_geojson
```

## Waterlines example

The waterlines sample is wired through Bazel data in `extractors/line_detection/BUILD.bazel`.
To reproduce the example locally:

```bash
curl -L "https://cam.iswebcloud.it/output_allegato.php?id=356489&larghezza=1920" \
  -o /tmp/cam_waterlines_map.png

python extractors/line_detection/detect_lines.py \
  --image /tmp/cam_waterlines_map.png \
  --bbox 0 0 1200 958 \
  --polygon "0,0 1200,0 1200,958 0,958" \
  --output /tmp/cam_waterlines.geojson

python extractors/line_detection/visualize_overlay.py \
  --image /tmp/cam_waterlines_map.png \
  --geojson /tmp/cam_waterlines.geojson \
  --bbox 0 0 1200 958 \
  --output /tmp/cam_waterlines_overlay.html
```

Open `/tmp/cam_waterlines_overlay.html` to compare the line detection output
with the original image.
