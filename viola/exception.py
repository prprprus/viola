"""Custom exception for viola"""


class ViolaEventException(Exception):
    """Event does not exists"""
    pass


class ViolaHTTPMethodException(Exception):
    """HTTP method does not exists"""
    pass


class ViolaHTTPVersionException(Exception):
    """HTTP version does not exists"""
    pass


class ViolaSendDataTypeException(Exception):
    """Socket `send()` data does not support"""
    pass
