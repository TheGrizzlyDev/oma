"""Bazel rule for detecting colored lines into GeoJSON."""

TransformationInfo = provider(
    doc = "Describes a line-detection transformation and its parameters.",
    fields = ["description", "metadata"],
)

def _line_detection_geojson_impl(ctx):
    output = ctx.outputs.out
    args = ctx.actions.args()
    args.add("--image", ctx.file.image.path)
    args.add("--bbox")
    args.add_all(ctx.attr.bbox)
    args.add("--polygon", ctx.attr.polygon)
    args.add("--output", output.path)
    args.add("--lower-hsv", ctx.attr.lower_hsv)
    args.add("--upper-hsv", ctx.attr.upper_hsv)
    args.add("--simplify", ctx.attr.simplify)

    ctx.actions.run(
        inputs = [ctx.file.image],
        outputs = [output],
        executable = ctx.executable._tool,
        arguments = [args],
        tools = [ctx.executable._tool],
        progress_message = "Detecting colored lines",
    )

    metadata = {
        "bbox": ctx.attr.bbox,
        "polygon": ctx.attr.polygon,
        "lower_hsv": ctx.attr.lower_hsv,
        "upper_hsv": ctx.attr.upper_hsv,
        "simplify": ctx.attr.simplify,
        "image": str(ctx.attr.image.label),
    }

    return [
        DefaultInfo(files = depset([output])),
        TransformationInfo(
            description = "Detect colored linework and export GeoJSON LineStrings.",
            metadata = metadata,
        ),
    ]


line_detection_geojson = rule(
    implementation = _line_detection_geojson_impl,
    attrs = {
        "image": attr.label(
            allow_single_file = True,
            mandatory = True,
            doc = "Input raster image containing the linework to detect.",
        ),
        "bbox": attr.string_list(
            mandatory = True,
            doc = "World-coordinate bounding box as a 4-item list: [min_x, min_y, max_x, max_y].",
        ),
        "polygon": attr.string(
            mandatory = True,
            doc = (
                "Polygon clip region as space-separated x,y pairs, "
                + 'for example: "0,0 10,0 10,5 0,5".'
            ),
        ),
        "lower_hsv": attr.string(
            mandatory = True,
            doc = "Lower HSV threshold as H,S,V (e.g. \"100,50,50\").",
        ),
        "upper_hsv": attr.string(
            mandatory = True,
            doc = "Upper HSV threshold as H,S,V (e.g. \"140,255,255\").",
        ),
        "simplify": attr.string(
            mandatory = True,
            doc = "Simplification tolerance as a fraction of contour length (e.g. \"0.002\").",
        ),
        "out": attr.output(
            mandatory = True,
            doc = "Output GeoJSON file.",
        ),
        "_tool": attr.label(
            default = Label("//extractors/line_detection:detect_lines"),
            executable = True,
            cfg = "exec",
            doc = "Line detection executable.",
        ),
    },
    doc = (
        "Detect colored linework from an image into GeoJSON LineStrings. "
        + "Use bbox to map pixel coordinates to world coordinates."
    ),
)
