def run_preview_action(
        ctx,
        image,
        overlay_mask = None,
        overlay_geojson = None,
        bbox = None,
        debug_images = None,
        title = "Line detection preview",
        parameters = None,
        assets = None):
    output = ctx.actions.declare_file(ctx.label.name + "_preview.html")
    args = ctx.actions.args()
    args.add("--image", image.path)
    if overlay_mask:
        args.add("--mask", overlay_mask.path)
    if overlay_geojson:
        args.add("--geojson", overlay_geojson.path)
    if bbox:
        args.add("--bbox")
        args.add_all(bbox)
    args.add("--title", title)
    args.add("--output", output.path)
    if debug_images:
        for debug_image in debug_images:
            args.add("--debug", debug_image.path)

    inputs = [image]
    if overlay_mask:
        inputs.append(overlay_mask)
    if overlay_geojson:
        inputs.append(overlay_geojson)
    if debug_images:
        inputs.extend(debug_images)

    if parameters:
        params_file = ctx.actions.declare_file(ctx.label.name + "_preview_params.json")
        ctx.actions.write(output = params_file, content = _encode_json(parameters))
        args.add("--params-json", params_file.path)
        inputs.append(params_file)

    if assets:
        assets_file = ctx.actions.declare_file(ctx.label.name + "_preview_assets.json")
        ctx.actions.write(output = assets_file, content = _encode_json(assets))
        args.add("--assets-json", assets_file.path)
        inputs.append(assets_file)

    ctx.actions.run(
        inputs = inputs,
        outputs = [output],
        executable = ctx.executable._preview_tool,
        arguments = [args],
        tools = [ctx.executable._preview_tool],
        progress_message = "Generating line detection preview",
    )
    return output


def _encode_json(value):
    if value == None:
        return "null"
    if type(value) == type([]):
        return _encode_list(value)
    if type(value) == type({}):
        return _encode_dict(value)
    return _encode_scalar(value)


def _encode_list(values):
    items = []
    for item in values:
        if type(item) == type({}):
            items.append(_encode_dict(item))
        else:
            items.append(_encode_scalar(item))
    return "[" + ", ".join(items) + "]"


def _encode_dict(values):
    items = []
    for key in sorted(values.keys()):
        items.append(_encode_scalar(str(key)) + ": " + _encode_scalar(values[key]))
    return "{" + ", ".join(items) + "}"


def _encode_scalar(value):
    if value == None:
        return "null"
    if type(value) == type(True):
        return "true" if value else "false"
    if type(value) in [type(0), type(0.0)]:
        return str(value)
    if type(value) == type(""):
        return "\"" + _escape_json(value) + "\""
    return "\"" + _escape_json(str(value)) + "\""


def _escape_json(value):
    return value.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
