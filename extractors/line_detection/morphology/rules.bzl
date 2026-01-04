load("//extractors/line_detection:defs.bzl", "TransformationInfo")
load("//tools/previewer:preview_rules.bzl", "run_preview_action")


def _morphology_impl(ctx):
    output = ctx.outputs.out
    debug = ctx.outputs.debug
    stats = ctx.outputs.stats

    args = ctx.actions.args()
    args.add("--mask", ctx.file.mask.path)
    args.add("--output", output.path)
    args.add("--output-debug", debug.path)
    args.add("--output-stats", stats.path)
    if ctx.attr.do_close:
        args.add("--do-close")
    if ctx.attr.do_open:
        args.add("--do-open")
    args.add("--close-kernel", ctx.attr.close_kernel)
    args.add("--open-kernel", ctx.attr.open_kernel)
    args.add("--kernel-shape", ctx.attr.kernel_shape)
    args.add("--close-iterations", ctx.attr.close_iterations)
    args.add("--open-iterations", ctx.attr.open_iterations)
    args.add("--min-area", ctx.attr.min_area)
    args.add("--min-extent", ctx.attr.min_extent)

    ctx.actions.run(
        inputs = [ctx.file.mask],
        outputs = [output, debug, stats],
        executable = ctx.executable._tool,
        arguments = [args],
        tools = [ctx.executable._tool],
        progress_message = "Filtering morphology and components",
    )

    preview = run_preview_action(
        ctx,
        image = ctx.file.image,
        overlay_mask = output,
        debug_images = [debug],
        title = "Morphology preview",
        parameters = {
            "do_close": str(ctx.attr.do_close),
            "do_open": str(ctx.attr.do_open),
            "close_kernel": str(ctx.attr.close_kernel),
            "open_kernel": str(ctx.attr.open_kernel),
            "kernel_shape": ctx.attr.kernel_shape,
            "close_iterations": str(ctx.attr.close_iterations),
            "open_iterations": str(ctx.attr.open_iterations),
            "min_area": str(ctx.attr.min_area),
            "min_extent": str(ctx.attr.min_extent),
        },
        assets = [
            {"label": "filtered_mask", "path": output.short_path},
            {"label": "debug_overlay", "path": debug.short_path},
            {"label": "component_stats", "path": stats.short_path},
        ],
    )

    return [
        DefaultInfo(files = depset([output, debug, stats, preview])),
        TransformationInfo(
            description = "Apply morphology cleanup and component filtering.",
            metadata = {"min_area": ctx.attr.min_area, "min_extent": ctx.attr.min_extent},
        ),
    ]


line_morphology = rule(
    implementation = _morphology_impl,
    attrs = {
        "image": attr.label(allow_single_file = True, mandatory = True),
        "mask": attr.label(allow_single_file = True, mandatory = True),
        "out": attr.output(mandatory = True),
        "debug": attr.output(mandatory = True),
        "stats": attr.output(mandatory = True),
        "do_close": attr.bool(default = True),
        "do_open": attr.bool(default = False),
        "close_kernel": attr.int(default = 3),
        "open_kernel": attr.int(default = 3),
        "kernel_shape": attr.string(default = "ellipse"),
        "close_iterations": attr.int(default = 1),
        "open_iterations": attr.int(default = 1),
        "min_area": attr.int(default = 20),
        "min_extent": attr.int(default = 10),
        "_tool": attr.label(
            default = Label("//extractors/line_detection/morphology:morphology_filter"),
            executable = True,
            cfg = "exec",
        ),
        "_preview_tool": attr.label(
            default = Label("//tools/previewer:preview_pass"),
            executable = True,
            cfg = "exec",
        ),
    },
    doc = "Morphology + component filtering pass.",
)
