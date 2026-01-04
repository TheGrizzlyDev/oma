load("//extractors/line_detection:defs.bzl", "TransformationInfo")
load("//tools/previewer:preview_rules.bzl", "run_preview_action")


def _topology_impl(ctx):
    output = ctx.outputs.out
    debug = ctx.outputs.debug
    args = ctx.actions.args()
    args.add("--input", ctx.file.input_geojson.path)
    args.add("--output", output.path)
    args.add("--output-debug", debug.path)
    args.add("--spur-length", ctx.attr.spur_length)
    args.add("--snap-tolerance", ctx.attr.snap_tolerance)
    args.add("--simplify", ctx.attr.simplify)
    args.add("--smooth-iterations", ctx.attr.smooth_iterations)

    ctx.actions.run(
        inputs = [ctx.file.input_geojson],
        outputs = [output, debug],
        executable = ctx.executable._tool,
        arguments = [args],
        tools = [ctx.executable._tool],
        progress_message = "Cleaning vector topology",
    )

    preview = run_preview_action(
        ctx,
        image = ctx.file.image,
        overlay_geojson = output,
        bbox = ctx.attr.bbox,
        debug_images = [],
        title = "Topology cleanup preview",
        parameters = {
            "spur_length": ctx.attr.spur_length,
            "snap_tolerance": ctx.attr.snap_tolerance,
            "simplify": ctx.attr.simplify,
            "smooth_iterations": str(ctx.attr.smooth_iterations),
        },
        assets = [
            {"label": "geojson", "path": output.short_path},
            {"label": "cleanup_stats", "path": debug.short_path},
        ],
    )

    return [
        DefaultInfo(files = depset([output, debug, preview])),
        TransformationInfo(
            description = "Cleanup and simplify line topology.",
            metadata = {"spur_length": ctx.attr.spur_length},
        ),
    ]


line_topology_cleanup = rule(
    implementation = _topology_impl,
    attrs = {
        "image": attr.label(allow_single_file = True, mandatory = True),
        "input_geojson": attr.label(allow_single_file = True, mandatory = True),
        "bbox": attr.string_list(mandatory = True),
        "out": attr.output(mandatory = True),
        "debug": attr.output(mandatory = True),
        "spur_length": attr.string(default = "0.0"),
        "snap_tolerance": attr.string(default = "0.0"),
        "simplify": attr.string(default = "0.0"),
        "smooth_iterations": attr.int(default = 0),
        "_tool": attr.label(
            default = Label("//extractors/line_detection/topology:topology_cleanup"),
            executable = True,
            cfg = "exec",
        ),
        "_preview_tool": attr.label(
            default = Label("//tools/previewer:preview_pass"),
            executable = True,
            cfg = "exec",
        ),
    },
    doc = "Topology cleanup pass.",
)
