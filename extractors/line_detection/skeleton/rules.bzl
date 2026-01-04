load("//extractors/line_detection:defs.bzl", "TransformationInfo")
load("//tools/previewer:preview_rules.bzl", "run_preview_action")


def _skeleton_impl(ctx):
    output = ctx.outputs.out
    debug = ctx.outputs.debug
    args = ctx.actions.args()
    args.add("--mask", ctx.file.mask.path)
    args.add("--output", output.path)
    args.add("--output-debug", debug.path)
    args.add("--method", ctx.attr.method)
    args.add("--prune-spurs", ctx.attr.prune_spurs)

    ctx.actions.run(
        inputs = [ctx.file.mask],
        outputs = [output, debug],
        executable = ctx.executable._tool,
        arguments = [args],
        tools = [ctx.executable._tool],
        progress_message = "Skeletonizing mask",
    )

    preview = run_preview_action(
        ctx,
        image = ctx.file.image,
        overlay_mask = output,
        debug_images = [debug],
        title = "Skeleton preview",
        parameters = {
            "method": ctx.attr.method,
            "prune_spurs": str(ctx.attr.prune_spurs),
        },
        assets = [
            {"label": "skeleton", "path": output.short_path},
            {"label": "debug_overlay", "path": debug.short_path},
        ],
    )

    return [
        DefaultInfo(files = depset([output, debug, preview])),
        TransformationInfo(
            description = "Skeletonize mask to centerline.",
            metadata = {"method": ctx.attr.method, "prune_spurs": ctx.attr.prune_spurs},
        ),
    ]


line_skeleton = rule(
    implementation = _skeleton_impl,
    attrs = {
        "image": attr.label(allow_single_file = True, mandatory = True),
        "mask": attr.label(allow_single_file = True, mandatory = True),
        "out": attr.output(mandatory = True),
        "debug": attr.output(mandatory = True),
        "method": attr.string(default = "morphological"),
        "prune_spurs": attr.int(default = 0),
        "_tool": attr.label(
            default = Label("//extractors/line_detection/skeleton:skeletonize_mask"),
            executable = True,
            cfg = "exec",
        ),
        "_preview_tool": attr.label(
            default = Label("//tools/previewer:preview_pass"),
            executable = True,
            cfg = "exec",
        ),
    },
    doc = "Skeletonization pass.",
)
