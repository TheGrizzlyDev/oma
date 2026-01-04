# Binarization pass

Converts the segmented mask into a binary mask using adaptive, hysteresis, or
fixed thresholding.

## Usage

```bash
python extractors/line_detection/binarize/binarize_mask.py \
  --image path/to/map.png \
  --mask segmented.png \
  --output binary.png \
  --output-debug debug.png \
  --method adaptive
```
