load("//extractors/line_detection:line_detection.bzl", _line_detection_geojson = "line_detection_geojson")
load("//extractors/line_detection/segment:rules.bzl", _line_segmentation = "line_segmentation")
load("//extractors/line_detection/binarize:rules.bzl", _line_binarize = "line_binarize")
load("//extractors/line_detection/morphology:rules.bzl", _line_morphology = "line_morphology")
load("//extractors/line_detection/artifact:rules.bzl", _line_artifact_mask = "line_artifact_mask")
load("//extractors/line_detection/skeleton:rules.bzl", _line_skeleton = "line_skeleton")
load("//extractors/line_detection/vectorize:rules.bzl", _line_vectorize = "line_vectorize")
load("//extractors/line_detection/topology:rules.bzl", _line_topology_cleanup = "line_topology_cleanup")

line_detection_geojson = _line_detection_geojson
line_segmentation = _line_segmentation
line_binarize = _line_binarize
line_morphology = _line_morphology
line_artifact_mask = _line_artifact_mask
line_skeleton = _line_skeleton
line_vectorize = _line_vectorize
line_topology_cleanup = _line_topology_cleanup
