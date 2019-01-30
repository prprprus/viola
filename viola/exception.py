
class ViolaEventException(Exception):
    """Event does not match"""
    pass


class ViolaReadBlockingIOError(BlockingIOError):
    """BlockingIOError"""
    pass


class ViolaReadConnectionResetError(ConnectionResetError):
    """ConnectionResetError. Exception for client"""
    pass


class ViolaWriteBlockingIOError(BlockingIOError):
    """BlockingIOError"""
    pass


class ViolaWriteConnectionResetError(ConnectionResetError):
    """ConnectionResetError. Exception for client"""
    pass


class ViolaBrokenPipeError(BrokenPipeError):
    """BrokenPipeError. Exception for client"""
    pass
