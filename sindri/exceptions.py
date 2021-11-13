class SindriError(Exception):
    pass

class SindriSupplierError(SindriError):
    pass

class SindriSupplierNotFound(SindriSupplierError):
    pass

class SindriSupplierFailedError(SindriSupplierError):
    pass
