import platform
from .buspirate import *
if not platform.system() is "Windows":
    from .linuxdevice import *
from .mock import *
