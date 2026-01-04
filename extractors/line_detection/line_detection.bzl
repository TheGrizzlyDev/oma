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

    overlay_script = ctx.actions.declare_file(ctx.label.name + "_overlay.sh")
    overlay_output = ctx.label.name + "_overlay.html"
    image_short_path = ctx.file.image.short_path
    geojson_short_path = output.short_path
    viewer_short_path = ctx.executable._viewer.short_path

    ctx.actions.expand_template(
        template = ctx.file._overlay_template,
        output = overlay_script,
        substitutions = {
            "@WORKSPACE@": ctx.workspace_name,
            "@IMAGE_SHORT_PATH@": image_short_path,
            "@GEOJSON_SHORT_PATH@": geojson_short_path,
            "@VIEWER_SHORT_PATH@": viewer_short_path,
            "@OUTPUT_FILE@": overlay_output,
            "@BBOX@": " ".join(ctx.attr.bbox),
        },
        is_executable = True,
    )

    metadata = {
        "bbox": ctx.attr.bbox,
        "polygon": ctx.attr.polygon,
        "lower_hsv": ctx.attr.lower_hsv,
        "upper_hsv": ctx.attr.upper_hsv,
        "simplify": ctx.attr.simplify,
        "image": str(ctx.attr.image.label),
    }

    viewer_runfiles = ctx.runfiles(
        files = [ctx.executable._viewer],
        transitive_files = ctx.attr._viewer[DefaultInfo].default_runfiles.files,
    )

    return [
        DefaultInfo(
            files = depset([output, overlay_script]),
            executable = overlay_script,
            runfiles = ctx.runfiles(
                files = [
                    ctx.file.image,
                    output,
                    ctx.executable._viewer,
                ],
            ).merge(viewer_runfiles),
        ),
        TransformationInfo(
            description = "Detect colored linework and export GeoJSON LineStrings.",
            metadata = metadata,
        ),
    ]


line_detection_geojson = rule(
    implementation = _line_detection_geojson_impl,
    executable = True,
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
        "_viewer": attr.label(
            default = Label("//extractors/line_detection:visualize_overlay"),
            executable = True,
            cfg = "exec",
            doc = "HTML overlay viewer generator.",
        ),
        "_overlay_template": attr.label(
            default = Label("//extractors/line_detection:overlay_runner.sh.tpl"),
            allow_single_file = True,
            doc = "Template for the overlay runner script.",
        ),
    },
    doc = (
        "Detect colored linework from an image into GeoJSON LineStrings. "
        + "Use bbox to map pixel coordinates to world coordinates."
    ),
)
