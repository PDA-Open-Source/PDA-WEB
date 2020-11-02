from decouple import UndefinedValueError, config
import mimetypes
mimetypes.add_type("text/css", ".css", True)

try:
    if config('SETTINGS') == 'PRODUCTION':
        from .production import *
    else:
        from .development import *
except UndefinedValueError:
    from .production import *
