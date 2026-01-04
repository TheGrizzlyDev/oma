"""Label helpers for OMA data artifacts."""


def repo_name(module_name, artifact_name):
    return "oma_data_{}_{}".format(module_name, artifact_name)


def artifact_label(module_name, artifact_name):
    return "@{}//:artifact".format(repo_name(module_name, artifact_name))


def archive_label(module_name, artifact_name):
    return "@{}//:archive".format(repo_name(module_name, artifact_name))


def extracted_label(module_name, artifact_name):
    return "@{}//:extracted".format(repo_name(module_name, artifact_name))


def metadata_label(module_name, artifact_name):
    return "@{}//:package_metadata".format(repo_name(module_name, artifact_name))


def _repo(module_name):
    return lambda name: repo_name(module_name, name)


def _artifact(module_name):
    return lambda name: artifact_label(module_name, name)


def _archive(module_name):
    return lambda name: archive_label(module_name, name)


def _extracted(module_name):
    return lambda name: extracted_label(module_name, name)


def _metadata(module_name):
    return lambda name: metadata_label(module_name, name)


def helpers(module_name):
    return struct(
        repo = _repo(module_name),
        artifact = _artifact(module_name),
        archive = _archive(module_name),
        extracted = _extracted(module_name),
        metadata = _metadata(module_name),
    )
