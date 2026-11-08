# -*- coding: UTF-8 -*-
"""WebGrep package information.

"""
import os
from datetime import datetime

__y = str(datetime.now().year)
__s = "2017"

__author__     = "Alexandre D'Hondt"
__email__      = "alexandre.dhondt@gmail.com"
__copyright__  = "© {} A. D'Hondt".format([__y, __s + "-" + __y][__y != __s])
__license__    = """License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law."""
__repository__ = "https://github.com/dhondta/webgrep"

with open(os.path.join(os.path.dirname(__file__), "VERSION.txt")) as f:
    __version__ = f.read().strip()
