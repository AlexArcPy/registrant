# -*- coding: UTF-8 -*-
"""Initialize modules on import of registrant."""
__version__ = '0.7'
from registrant._reporter import Reporter  # noqa: F401
from registrant import (  # noqa: F401
    _util_mappings, _geodatabase, _build_html, _data_objects, _config,
)
