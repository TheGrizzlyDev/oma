load("//extractors/line_detection:defs.bzl", "TransformationInfo")
load("//tools/previewer:preview_rules.bzl", "run_preview_action")


def _artifact_impl(ctx):
    output = ctx.outputs.out
    debug = ctx.outputs.debug
    args = ctx.actions.args()
    args.add("--mask", ctx.file.mask.path)
    args.add("--output", output.path)
    args.add("--output-debug", debug.path)
    if ctx.file.roi_mask:
        args.add("--roi-mask", ctx.file.roi_mask.path)
        args.add("--roi-mode", ctx.attr.roi_mode)
    if ctx.attr.detect_grid:
        args.add("--detect-grid")
    args.add("--grid-min-length", ctx.attr.grid_min_length)
    args.add("--grid-gap", ctx.attr.grid_gap)
    args.add("--grid-thickness", ctx.attr.grid_thickness)
    if ctx.attr.detect_circles:
        args.add("--detect-circles")
    args.add("--circle-min-radius", ctx.attr.circle_min_radius)
    args.add("--circle-max-radius", ctx.attr.circle_max_radius)
    args.add("--circle-param1", ctx.attr.circle_param1)
    args.add("--circle-param2", ctx.attr.circle_param2)

    inputs = [ctx.file.mask]
    if ctx.file.roi_mask:
        inputs.append(ctx.file.roi_mask)

    ctx.actions.run(
        inputs = inputs,
        outputs = [output, debug],
        executable = ctx.executable._tool,
        arguments = [args],
        tools = [ctx.executable._tool],
        progress_message = "Suppressing artifacts",
    )

    preview = run_preview_action(
        ctx,
        image = ctx.file.image,
        overlay_mask = output,
        debug_images = [debug],
        title = "Artifact suppression preview",
        parameters = {
            "roi_mode": ctx.attr.roi_mode,
            "detect_grid": str(ctx.attr.detect_grid),
            "grid_min_length": str(ctx.attr.grid_min_length),
            "grid_gap": str(ctx.attr.grid_gap),
            "grid_thickness": str(ctx.attr.grid_thickness),
            "detect_circles": str(ctx.attr.detect_circles),
            "circle_min_radius": str(ctx.attr.circle_min_radius),
            "circle_max_radius": str(ctx.attr.circle_max_radius),
            "circle_param1": ctx.attr.circle_param1,
            "circle_param2": ctx.attr.circle_param2,
        },
        assets = [
            {"label": "artifact_masked", "path": output.short_path},
            {"label": "debug_overlay", "path": debug.short_path},
        ],
    )

    return [
        DefaultInfo(files = depset([output, debug, preview])),
        TransformationInfo(
            description = "Suppress grid/circle artifacts before skeletonization.",
            metadata = {"detect_grid": ctx.attr.detect_grid, "detect_circles": ctx.attr.detect_circles},
        ),
    ]


line_artifact_mask = rule(
    implementation = _artifact_impl,
    attrs = {
        "image": attr.label(allow_single_file = True, mandatory = True),
        "mask": attr.label(allow_single_file = True, mandatory = True),
        "roi_mask": attr.label(allow_single_file = True),
        "roi_mode": attr.string(default = "exclude"),
        "out": attr.output(mandatory = True),
        "debug": attr.output(mandatory = True),
        "detect_grid": attr.bool(default = False),
        "grid_min_length": attr.int(default = 120),
        "grid_gap": attr.int(default = 8),
        "grid_thickness": attr.int(default = 6),
        "detect_circles": attr.bool(default = False),
        "circle_min_radius": attr.int(default = 30),
        "circle_max_radius": attr.int(default = 200),
        "circle_param1": attr.string(default = "120"),
        "circle_param2": attr.string(default = "30"),
        "_tool": attr.label(
            default = Label("//extractors/line_detection/artifact:artifact_mask"),
            executable = True,
            cfg = "exec",
        ),
        "_preview_tool": attr.label(
            default = Label("//tools/previewer:preview_pass"),
            executable = True,
            cfg = "exec",
        ),
    },
    doc = "Artifact masking pass.",
)
