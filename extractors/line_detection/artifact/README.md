# Artifact suppression pass

Suppresses grid/circle artifacts or ROI regions before skeletonization.

## Usage

```bash
python extractors/line_detection/artifact/artifact_mask.py \
  --mask cleaned.png \
  --output masked.png \
  --output-debug debug.png \
  --detect-grid
```
