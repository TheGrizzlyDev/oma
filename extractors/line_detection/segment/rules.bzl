load("//extractors/line_detection:defs.bzl", "TransformationInfo")
load("//tools/previewer:preview_rules.bzl", "run_preview_action")


def _segment_lines_impl(ctx):
    conservative = ctx.outputs.conservative
    aggressive = ctx.outputs.aggressive
    merged = ctx.outputs.merged
    debug = ctx.outputs.debug

    args = ctx.actions.args()
    args.add("--image", ctx.file.image.path)
    args.add("--output-conservative", conservative.path)
    args.add("--output-aggressive", aggressive.path)
    args.add("--output-merged", merged.path)
    args.add("--output-debug", debug.path)
    args.add("--colorspace", ctx.attr.colorspace)
    args.add("--channels", ctx.attr.channels)
    args.add("--lower", ctx.attr.lower)
    args.add("--upper", ctx.attr.upper)
    if ctx.attr.aggressive_lower:
        args.add("--aggressive-lower", ctx.attr.aggressive_lower)
    if ctx.attr.aggressive_upper:
        args.add("--aggressive-upper", ctx.attr.aggressive_upper)
    args.add("--merge-strategy", ctx.attr.merge_strategy)
    args.add("--merge-radius", ctx.attr.merge_radius)
    if ctx.attr.clahe:
        args.add("--clahe")
    args.add("--clahe-clip", ctx.attr.clahe_clip)
    args.add("--clahe-tile", ctx.attr.clahe_tile)

    ctx.actions.run(
        inputs = [ctx.file.image],
        outputs = [conservative, aggressive, merged, debug],
        executable = ctx.executable._tool,
        arguments = [args],
        tools = [ctx.executable._tool],
        progress_message = "Segmenting candidate line pixels",
    )

    preview = run_preview_action(
        ctx,
        image = ctx.file.image,
        overlay_mask = merged,
        debug_images = [debug],
        title = "Segmentation preview",
        parameters = {
            "colorspace": ctx.attr.colorspace,
            "channels": ctx.attr.channels,
            "lower": ctx.attr.lower,
            "upper": ctx.attr.upper,
            "aggressive_lower": ctx.attr.aggressive_lower,
            "aggressive_upper": ctx.attr.aggressive_upper,
            "merge_strategy": ctx.attr.merge_strategy,
            "merge_radius": str(ctx.attr.merge_radius),
            "clahe": str(ctx.attr.clahe),
            "clahe_clip": ctx.attr.clahe_clip,
            "clahe_tile": str(ctx.attr.clahe_tile),
        },
        assets = [
            {"label": "conservative_mask", "path": conservative.short_path},
            {"label": "aggressive_mask", "path": aggressive.short_path},
            {"label": "merged_mask", "path": merged.short_path},
            {"label": "debug_overlay", "path": debug.short_path},
        ],
    )

    return [
        DefaultInfo(files = depset([conservative, aggressive, merged, debug, preview])),
        TransformationInfo(
            description = "Segment candidate pixels into conservative/aggressive masks.",
            metadata = {
                "colorspace": ctx.attr.colorspace,
                "channels": ctx.attr.channels,
                "lower": ctx.attr.lower,
                "upper": ctx.attr.upper,
                "merge_strategy": ctx.attr.merge_strategy,
            },
        ),
    ]


line_segmentation = rule(
    implementation = _segment_lines_impl,
    attrs = {
        "image": attr.label(allow_single_file = True, mandatory = True),
        "conservative": attr.output(mandatory = True),
        "aggressive": attr.output(mandatory = True),
        "merged": attr.output(mandatory = True),
        "debug": attr.output(mandatory = True),
        "colorspace": attr.string(default = "hsv"),
        "channels": attr.string(default = "0,1,2"),
        "lower": attr.string(mandatory = True),
        "upper": attr.string(mandatory = True),
        "aggressive_lower": attr.string(default = ""),
        "aggressive_upper": attr.string(default = ""),
        "merge_strategy": attr.string(default = "seed_proximity"),
        "merge_radius": attr.int(default = 4),
        "clahe": attr.bool(default = False),
        "clahe_clip": attr.string(default = "2.0"),
        "clahe_tile": attr.int(default = 8),
        "_tool": attr.label(
            default = Label("//extractors/line_detection/segment:segment_lines"),
            executable = True,
            cfg = "exec",
        ),
        "_preview_tool": attr.label(
            default = Label("//tools/previewer:preview_pass"),
            executable = True,
            cfg = "exec",
        ),
    },
    doc = "Segmentation pass for line detection.",
)
