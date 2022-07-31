from app import data_bundles  # noqa

try:
    from ._version import version
except ImportError:
    version = "git"
