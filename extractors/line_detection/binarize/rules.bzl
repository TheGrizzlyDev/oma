load("//extractors/line_detection:defs.bzl", "TransformationInfo")
load("//tools/previewer:preview_rules.bzl", "run_preview_action")


def _binarize_impl(ctx):
    output = ctx.outputs.out
    debug = ctx.outputs.debug
    args = ctx.actions.args()
    args.add("--image", ctx.file.image.path)
    args.add("--mask", ctx.file.mask.path)
    args.add("--output", output.path)
    args.add("--output-debug", debug.path)
    args.add("--method", ctx.attr.method)
    args.add("--adaptive-window", ctx.attr.adaptive_window)
    args.add("--adaptive-c", ctx.attr.adaptive_c)
    args.add("--hysteresis", ctx.attr.hysteresis)
    args.add("--global-threshold", ctx.attr.global_threshold)
    args.add("--blur", ctx.attr.blur)
    args.add("--blur-radius", ctx.attr.blur_radius)

    ctx.actions.run(
        inputs = [ctx.file.image, ctx.file.mask],
        outputs = [output, debug],
        executable = ctx.executable._tool,
        arguments = [args],
        tools = [ctx.executable._tool],
        progress_message = "Binarizing candidate mask",
    )

    preview = run_preview_action(
        ctx,
        image = ctx.file.image,
        overlay_mask = output,
        debug_images = [debug],
        title = "Binarization preview",
        parameters = {
            "method": ctx.attr.method,
            "adaptive_window": str(ctx.attr.adaptive_window),
            "adaptive_c": ctx.attr.adaptive_c,
            "hysteresis": ctx.attr.hysteresis,
            "global_threshold": str(ctx.attr.global_threshold),
            "blur": ctx.attr.blur,
            "blur_radius": str(ctx.attr.blur_radius),
        },
        assets = [
            {"label": "binary_mask", "path": output.short_path},
            {"label": "debug_overlay", "path": debug.short_path},
        ],
    )

    return [
        DefaultInfo(files = depset([output, debug, preview])),
        TransformationInfo(
            description = "Binarize the candidate mask using adaptive or hysteresis thresholding.",
            metadata = {"method": ctx.attr.method},
        ),
    ]


line_binarize = rule(
    implementation = _binarize_impl,
    attrs = {
        "image": attr.label(allow_single_file = True, mandatory = True),
        "mask": attr.label(allow_single_file = True, mandatory = True),
        "out": attr.output(mandatory = True),
        "debug": attr.output(mandatory = True),
        "method": attr.string(default = "adaptive"),
        "adaptive_window": attr.int(default = 31),
        "adaptive_c": attr.string(default = "2.0"),
        "hysteresis": attr.string(default = "60,140"),
        "global_threshold": attr.int(default = 120),
        "blur": attr.string(default = "gaussian"),
        "blur_radius": attr.int(default = 3),
        "_tool": attr.label(
            default = Label("//extractors/line_detection/binarize:binarize_mask"),
            executable = True,
            cfg = "exec",
        ),
        "_preview_tool": attr.label(
            default = Label("//tools/previewer:preview_pass"),
            executable = True,
            cfg = "exec",
        ),
    },
    doc = "Binarization pass for line detection.",
)
