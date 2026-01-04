"""Bzlmod extension for declaring OMA open-data artifacts."""

load("//bazel/data:repo.bzl", "oma_data_repo")
load("//bazel/data:validation.bzl", "validate_archive_settings", "validate_file_settings")


def _artifact_repo_name(module_name, artifact_name):
    return "oma_data_{}_{}".format(module_name, artifact_name)


def _oma_data_extension_impl(module_ctx):
    seen = {}
    for module in module_ctx.modules:
        for tag in module.tags.file:
            errors = validate_file_settings(
                name = tag.name,
                urls = tag.urls,
                sha256 = tag.sha256,
                integrity = tag.integrity,
                purl = tag.purl,
            )
            if errors:
                fail("Invalid oma file artifact {}: {}".format(tag.name, "; ".join(errors)))

            repo_name = _artifact_repo_name(module.name, tag.name)
            if repo_name in seen:
                fail("Duplicate oma_data artifact repository name: {}".format(repo_name))
            seen[repo_name] = True

            oma_data_repo(
                name = repo_name,
                archive_type = "",
                extract = False,
                integrity = tag.integrity,
                license_kind_label = tag.license_kind_label,
                license_text = tag.license_text,
                purl = tag.purl,
                sha256 = tag.sha256,
                strip_prefix = "",
                urls = tag.urls,
            )
        for tag in module.tags.archive:
            errors = validate_archive_settings(
                name = tag.name,
                urls = tag.urls,
                sha256 = tag.sha256,
                integrity = tag.integrity,
                archive_type = tag.archive_type,
                extract = tag.extract,
                strip_prefix = tag.strip_prefix,
                purl = tag.purl,
            )
            if errors:
                fail("Invalid oma archive artifact {}: {}".format(tag.name, "; ".join(errors)))

            repo_name = _artifact_repo_name(module.name, tag.name)
            if repo_name in seen:
                fail("Duplicate oma_data artifact repository name: {}".format(repo_name))
            seen[repo_name] = True

            oma_data_repo(
                name = repo_name,
                archive_type = tag.archive_type,
                extract = tag.extract,
                integrity = tag.integrity,
                license_kind_label = tag.license_kind_label,
                license_text = tag.license_text,
                purl = tag.purl,
                sha256 = tag.sha256,
                strip_prefix = tag.strip_prefix,
                urls = tag.urls,
            )


oma = module_extension(
    implementation = _oma_data_extension_impl,
    tag_classes = {
        "file": tag_class(
            attrs = {
                "name": attr.string(mandatory = True),
                "urls": attr.string_list(mandatory = True),
                "sha256": attr.string(default = ""),
                "integrity": attr.string(default = ""),
                "purl": attr.string(mandatory = True),
                "license_kind_label": attr.label(),
                "license_text": attr.string(default = ""),
            },
        ),
        "archive": tag_class(
            attrs = {
                "name": attr.string(mandatory = True),
                "urls": attr.string_list(mandatory = True),
                "sha256": attr.string(default = ""),
                "integrity": attr.string(default = ""),
                "archive_type": attr.string(mandatory = True),
                "strip_prefix": attr.string(default = ""),
                "extract": attr.bool(default = False),
                "purl": attr.string(mandatory = True),
                "license_kind_label": attr.label(),
                "license_text": attr.string(default = ""),
            },
        ),
    },
)
