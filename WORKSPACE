# Only needed if using the packaging rules.
load("@bazel_tools//tools/build_defs/repo:git.bzl", "git_repository")
git_repository(
    name = "rules_python",
    remote = "https://github.com/bazelbuild/rules_python.git",
    commit = "748aa53d7701e71101dfd15d800e100f6ff8e5d1",
)
load("@rules_python//python:pip.bzl", "pip_repositories")
pip_repositories()

load("@rules_python//python:pip.bzl", "pip_import")
pip_import(
	name = "global_deps",
	requirements = "//:requirements.txt"
)

load("@global_deps//:requirements.bzl", "pip_install")
pip_install()


