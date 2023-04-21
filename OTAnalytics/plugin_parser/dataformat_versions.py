"""
OTAnalytics version module to set version numbers of output formats.
"""

__OTEVENT_VERSION = "0.0"
"""
Represents the current version of the OTEvent file format. This version is hard coded
and has to be updated manually on format changes.
"""
__OTSECTION_VERSION = "0.0"
"""
Represents the current version of the OTSection file format. This version is hard coded
and has to be updated manually on output changes.
"""


def otevent_version() -> str:
    return __OTEVENT_VERSION


def otsection_version() -> str:
    return __OTSECTION_VERSION
