"""Validation helpers for OMA data artifacts."""

_ARCHIVE_TYPES = [
    "zip",
    "tar",
    "tar.gz",
    "tgz",
    "tar.bz2",
    "tar.xz",
]


def allowed_archive_types():
    return list(_ARCHIVE_TYPES)


def _validate_common_settings(
        name,
        urls,
        sha256,
        integrity,
        purl):
    errors = []
    if not name:
        errors.append("name is required")
    if not urls:
        errors.append("at least one url is required")
    if not sha256 and not integrity:
        errors.append("sha256 or integrity must be provided")
    if not purl:
        errors.append("purl is required")
    return errors


def validate_file_settings(
        name,
        urls,
        sha256,
        integrity,
        purl):
    return _validate_common_settings(
        name = name,
        urls = urls,
        sha256 = sha256,
        integrity = integrity,
        purl = purl,
    )


def validate_archive_settings(
        name,
        urls,
        sha256,
        integrity,
        archive_type,
        extract,
        strip_prefix,
        purl):
    errors = _validate_common_settings(
        name = name,
        urls = urls,
        sha256 = sha256,
        integrity = integrity,
        purl = purl,
    )
    if not archive_type:
        errors.append("archive_type is required")
    elif archive_type not in _ARCHIVE_TYPES:
        errors.append("archive_type must be one of {}".format(", ".join(_ARCHIVE_TYPES)))
    if strip_prefix and not extract:
        errors.append("strip_prefix requires extract = True")
    return errors


def validate_artifact_settings(
        name,
        urls,
        sha256,
        integrity,
        archive_type,
        extract,
        strip_prefix,
        purl):
    errors = _validate_common_settings(
        name = name,
        urls = urls,
        sha256 = sha256,
        integrity = integrity,
        purl = purl,
    )
    if archive_type:
        if archive_type not in _ARCHIVE_TYPES:
            errors.append("archive_type must be one of {}".format(", ".join(_ARCHIVE_TYPES)))
    else:
        if extract:
            errors.append("extract requires archive_type")
        if strip_prefix:
            errors.append("strip_prefix requires archive_type")
    if strip_prefix and not extract:
        errors.append("strip_prefix requires extract = True")
    return errors
