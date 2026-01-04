load("@package_metadata//providers:package_metadata_info.bzl", "PackageMetadataInfo")


def _oma_data_artifact_impl(ctx):
    files = depset(transitive = [src[DefaultInfo].files for src in ctx.attr.srcs])
    if not ctx.attr.package_metadata:
        fail("package_metadata must be set")
    metadata = ctx.attr.package_metadata[0][PackageMetadataInfo]
    return [
        DefaultInfo(files = files),
        metadata,
    ]


oma_data_artifact = rule(
    implementation = _oma_data_artifact_impl,
    attrs = {
        "srcs": attr.label_list(allow_files = True, mandatory = True),
    },
)
