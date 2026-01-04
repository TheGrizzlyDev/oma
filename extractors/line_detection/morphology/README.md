# Morphology pass

Repairs gaps and removes small components from the binary mask.

## Usage

```bash
python extractors/line_detection/morphology/morphology_filter.py \
  --mask binary.png \
  --output cleaned.png \
  --output-debug debug.png \
  --output-stats stats.json \
  --do-close
```
