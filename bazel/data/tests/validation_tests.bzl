"""Unit tests for OMA data validation helpers."""

load("@bazel_skylib//lib:unittest.bzl", "asserts", "unittest")
load("//bazel/data:validation.bzl", "validate_archive_settings", "validate_file_settings")


def _missing_hash_test(ctx):
    env = unittest.begin(ctx)
    errors = validate_file_settings(
        name = "missing_hash",
        urls = ["https://example.com/data.csv"],
        sha256 = "",
        integrity = "",
        purl = "pkg:generic/oma/missing_hash@1.0",
        license_kind_label = "@package_metadata//licenses/spdx:Apache-2.0",
    )
    asserts.true(env, errors, "Expected validation errors for missing hash")
    return unittest.end(env)


def _strip_prefix_requires_archive_test(ctx):
    env = unittest.begin(ctx)
    errors = validate_archive_settings(
        name = "strip_prefix",
        urls = ["https://example.com/data.csv"],
        sha256 = "abc",
        integrity = "",
        archive_type = "tar.gz",
        extract = False,
        strip_prefix = "data",
        purl = "pkg:generic/oma/strip_prefix@1.0",
        license_kind_label = "@package_metadata//licenses/spdx:Apache-2.0",
    )
    asserts.true(env, errors, "Expected validation errors for strip_prefix without archive")
    return unittest.end(env)


def _valid_archive_test(ctx):
    env = unittest.begin(ctx)
    errors = validate_archive_settings(
        name = "valid_archive",
        urls = ["https://example.com/data.tgz"],
        sha256 = "abc",
        integrity = "",
        archive_type = "tar.gz",
        extract = True,
        strip_prefix = "data",
        purl = "pkg:generic/oma/valid_archive@1.0",
        license_kind_label = "@package_metadata//licenses/spdx:Apache-2.0",
    )
    asserts.equals(env, [], errors)
    return unittest.end(env)


missing_hash_test = unittest.make(_missing_hash_test)
strip_prefix_requires_archive_test = unittest.make(_strip_prefix_requires_archive_test)
valid_archive_test = unittest.make(_valid_archive_test)


def validation_test_suite(name):
    unittest.suite(
        name,
        missing_hash_test,
        strip_prefix_requires_archive_test,
        valid_archive_test,
    )
