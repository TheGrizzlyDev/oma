"""Integration tests for OMA data repositories."""

load("@bazel_skylib//lib:unittest.bzl", "analysistest", "asserts", "unittest")
load("@package_metadata//providers:package_metadata_info.bzl", "PackageMetadataInfo")


def _artifact_metadata_test_impl(ctx):
    env = analysistest.begin(ctx)
    target = analysistest.target_under_test(env)
    asserts.true(env, PackageMetadataInfo in target, "Expected PackageMetadataInfo provider")
    files = target[DefaultInfo].files.to_list()
    asserts.true(env, files, "Expected files to be present")
    return analysistest.end(env)


artifact_metadata_test = analysistest.make(_artifact_metadata_test_impl)


def oma_data_integration_test_suite(name):
    artifact_metadata_test(
        name = name + "_file_artifact_test",
        target_under_test = "@oma_data_oma_test_sample_file//:artifact",
    )
    artifact_metadata_test(
        name = name + "_archive_artifact_test",
        target_under_test = "@oma_data_oma_test_sample_archive//:archive",
    )
    artifact_metadata_test(
        name = name + "_archive_extracted_test",
        target_under_test = "@oma_data_oma_test_sample_archive//:extracted",
    )
    native.test_suite(
        name = name,
        tests = [
            name + "_file_artifact_test",
            name + "_archive_artifact_test",
            name + "_archive_extracted_test",
        ],
    )
