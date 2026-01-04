# Topology cleanup pass

Cleans and simplifies vector output (spur pruning, snapping, simplification).

## Usage

```bash
python extractors/line_detection/topology/topology_cleanup.py \
  --input lines.geojson \
  --output cleaned.geojson \
  --output-debug stats.json
```
