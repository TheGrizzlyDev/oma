# OMA Bazel Data Artifacts

This document describes the Bazel-native approach OMA uses to declare, download, and version external open-data artifacts.

## Why a custom repository rule

Built-in rules like `http_file` and `http_archive` are convenient, but they keep downloaded artifacts and metadata in separate places. OMA needs both the raw artifacts and their supply-chain metadata (license and package identity) to live in the same external repository so downstream rules can depend on them directly. A custom repository rule lets us:

- Keep the downloaded archive/file and its extracted tree together.
- Generate `package_metadata` and `license` targets alongside the artifact.
- Ensure downstream ETL rules can consume metadata via providers, not by parsing files.

## Declaring a new artifact

Add a declaration in `MODULE.bazel` using the `oma` module extension:

```starlark
oma = use_extension("//bazel/data:extension.bzl", "oma")

oma.file(
    name = "my_dataset",
    urls = ["https://example.com/dataset.csv"],
    sha256 = "<sha256>",
    purl = "pkg:generic/oma/my_dataset@2024-01-01",
    license_kind_label = "@package_metadata//licenses/spdx:CC-BY-4.0",
)

use_repo(oma, "oma_data_oma_my_dataset")
```

Every artifact declaration must include:

- `urls` and a `sha256` or `integrity` hash
- `purl` package identity
- License metadata (`license_kind`, `license_name`)

## Archive handling

To declare archives, set `archive_type` and optionally `strip_prefix` and `extract`:

```starlark
oma.archive(
    name = "my_archive",
    urls = ["https://example.com/data.tar.gz"],
    sha256 = "<sha256>",
    archive_type = "tar.gz",
    strip_prefix = "data-1.0",
    extract = True,
    purl = "pkg:generic/oma/my_archive@1.0",
    license_kind_label = "@package_metadata//licenses/spdx:CC-BY-4.0",
)
```

The repository rule always keeps the downloaded archive. If `extract = True`, it also extracts to a deterministic `extracted/` tree.

## Targets exposed to downstream consumers

Each generated repository exposes:

- `:artifact` for single-file downloads (includes `PackageMetadataInfo`)
- `:archive` for archive downloads (includes `PackageMetadataInfo`)
- `:extracted` for extracted archive contents (when `extract = True`, includes `PackageMetadataInfo`)
- `:package_metadata` with supply-chain metadata
- `:license` and `:license_kind`

The `:artifact`, `:archive`, and `:extracted` targets are wrapped to carry `PackageMetadataInfo`, so downstream rules can consume licensing and provenance without parsing files.

## Helper label functions

Use `//bazel/data:labels.bzl` to build workspace names and labels from artifact names:

```starlark
load("//bazel/data:labels.bzl", "archive_label", "artifact_label", "extracted_label", "helpers", "repo_name")

DATA_REPO = repo_name("oma", "test_sample_archive")
ARCHIVE = archive_label("oma", "test_sample_archive")
EXTRACTED = extracted_label("oma", "test_sample_archive")

oma = helpers("oma")
ARTIFACT = oma.artifact("test_sample_file")
```

These helpers expand names like `test_sample_archive` into labels such as `@oma_data_oma_test_sample_archive//:archive`.
