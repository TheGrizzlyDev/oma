load("//extractors/line_detection:defs.bzl", "TransformationInfo")
load("//tools/previewer:preview_rules.bzl", "run_preview_action")


def _vectorize_impl(ctx):
    output = ctx.outputs.out
    debug = ctx.outputs.debug
    stats = ctx.outputs.stats

    args = ctx.actions.args()
    args.add("--mask", ctx.file.mask.path)
    args.add("--bbox")
    args.add_all(ctx.attr.bbox)
    args.add("--output", output.path)
    args.add("--output-debug", debug.path)
    args.add("--output-stats", stats.path)
    args.add("--min-path-length", ctx.attr.min_path_length)
    args.add("--gap-bridge", ctx.attr.gap_bridge)

    ctx.actions.run(
        inputs = [ctx.file.mask],
        outputs = [output, debug, stats],
        executable = ctx.executable._tool,
        arguments = [args],
        tools = [ctx.executable._tool],
        progress_message = "Vectorizing skeleton",
    )

    preview = run_preview_action(
        ctx,
        image = ctx.file.image,
        overlay_geojson = output,
        bbox = ctx.attr.bbox,
        debug_images = [debug],
        title = "Vectorization preview",
        parameters = {
            "min_path_length": str(ctx.attr.min_path_length),
            "gap_bridge": ctx.attr.gap_bridge,
        },
        assets = [
            {"label": "geojson", "path": output.short_path},
            {"label": "debug_overlay", "path": debug.short_path},
            {"label": "graph_stats", "path": stats.short_path},
        ],
    )

    return [
        DefaultInfo(files = depset([output, debug, stats, preview])),
        TransformationInfo(
            description = "Vectorize skeleton into GeoJSON lines.",
            metadata = {"min_path_length": ctx.attr.min_path_length},
        ),
    ]


line_vectorize = rule(
    implementation = _vectorize_impl,
    attrs = {
        "image": attr.label(allow_single_file = True, mandatory = True),
        "mask": attr.label(allow_single_file = True, mandatory = True),
        "bbox": attr.string_list(mandatory = True),
        "out": attr.output(mandatory = True),
        "debug": attr.output(mandatory = True),
        "stats": attr.output(mandatory = True),
        "min_path_length": attr.int(default = 10),
        "gap_bridge": attr.string(default = "0.0"),
        "_tool": attr.label(
            default = Label("//extractors/line_detection/vectorize:vectorize_skeleton"),
            executable = True,
            cfg = "exec",
        ),
        "_preview_tool": attr.label(
            default = Label("//tools/previewer:preview_pass"),
            executable = True,
            cfg = "exec",
        ),
    },
    doc = "Vectorization pass.",
)
