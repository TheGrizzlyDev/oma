"""Repository rule for fetching OMA data artifacts with metadata."""

load("//bazel/data:validation.bzl", "validate_artifact_settings")

_BUILD_ARCHIVE_TEMPLATE = Label("//bazel/data/templates:BUILD.archive.tmpl.bazel")
_BUILD_ARCHIVE_EXTRACT_TEMPLATE = Label("//bazel/data/templates:BUILD.archive_extract.tmpl.bazel")
_BUILD_FILE_TEMPLATE = Label("//bazel/data/templates:BUILD.file.tmpl.bazel")
_METADATA_BUILD_TEMPLATE = Label("//bazel/data/templates:metadata/BUILD.tmpl.bazel")
_ARTIFACT_RULE_TEMPLATE = Label("//bazel/data/templates:oma_data_artifact.tmpl.bzl")


def _repo_impl(ctx):
    errors = validate_artifact_settings(
        name = ctx.attr.name,
        urls = ctx.attr.urls,
        sha256 = ctx.attr.sha256,
        integrity = ctx.attr.integrity,
        archive_type = ctx.attr.archive_type,
        extract = ctx.attr.extract,
        strip_prefix = ctx.attr.strip_prefix,
        purl = ctx.attr.purl,
    )
    if errors:
        fail("Invalid oma_data artifact {}: {}".format(ctx.attr.name, "; ".join(errors)))

    archive_name = ""
    if ctx.attr.archive_type:
        archive_name = "archive.{}".format(ctx.attr.archive_type)
        ctx.download(
            url = ctx.attr.urls,
            output = archive_name,
            sha256 = ctx.attr.sha256,
            integrity = ctx.attr.integrity,
        )
        if ctx.attr.extract:
            ctx.extract(
                archive = archive_name,
                output = "extracted",
                strip_prefix = ctx.attr.strip_prefix,
            )
    else:
        ctx.download(
            url = ctx.attr.urls,
            output = "artifact.data",
            sha256 = ctx.attr.sha256,
            integrity = ctx.attr.integrity,
        )

    license_block = ""
    package_metadata_attributes = "[]"
    license_aliases = ""
    if ctx.attr.license_kind_label:
        license_text_line = ""
        if ctx.attr.license_text:
            license_text_line = "    text = \"{}\",".format(ctx.attr.license_text)
        license_block = "\n".join([
            "alias(",
            "    name = \"license_kind\",",
            "    actual = \"{}\",".format(ctx.attr.license_kind_label),
            ")",
            "",
            "license(",
            "    name = \"license\",",
            "    kind = \":license_kind\",",
            license_text_line,
            "    visibility = [\"//visibility:public\"],",
            ")",
            "",
        ])
        package_metadata_attributes = "[\":license\"]"
        license_aliases = "\n".join([
            "alias(",
            "    name = \"license\",",
            "    actual = \"//metadata:license\",",
            ")",
            "",
            "alias(",
            "    name = \"license_kind\",",
            "    actual = \"//metadata:license_kind\",",
            ")",
        ])

    ctx.template(
        "metadata/BUILD.bazel",
        _METADATA_BUILD_TEMPLATE,
        substitutions = {
            "%{license_block}": license_block,
            "%{package_metadata_attributes}": package_metadata_attributes,
            "%{purl}": ctx.attr.purl,
        },
    )
    ctx.template(
        "oma_data_artifact.bzl",
        _ARTIFACT_RULE_TEMPLATE,
        substitutions = {},
    )

    if ctx.attr.archive_type:
        template = _BUILD_ARCHIVE_EXTRACT_TEMPLATE if ctx.attr.extract else _BUILD_ARCHIVE_TEMPLATE
        ctx.template(
            "BUILD.bazel",
            template,
            substitutions = {
                "%{archive_name}": archive_name,
                "%{license_aliases}": license_aliases,
            },
        )
    else:
        ctx.template(
            "BUILD.bazel",
            _BUILD_FILE_TEMPLATE,
            substitutions = {
                "%{license_aliases}": license_aliases,
            },
        )


oma_data_repo = repository_rule(
    implementation = _repo_impl,
    attrs = {
        "archive_type": attr.string(default = ""),
        "extract": attr.bool(default = False),
        "integrity": attr.string(default = ""),
        "license_kind_label": attr.label(),
        "license_text": attr.string(default = ""),
        "purl": attr.string(mandatory = True),
        "sha256": attr.string(default = ""),
        "strip_prefix": attr.string(default = ""),
        "urls": attr.string_list(mandatory = True),
    },
    doc = "Downloads a data artifact and exposes it with supply-chain metadata.",
)
