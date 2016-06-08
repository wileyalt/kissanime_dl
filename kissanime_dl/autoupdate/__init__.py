# -*- coding: utf-8 -*-

"""
autoupdate
~~~~~~~~~~~~~~~~~~~

auto updater for modules that are installed by pip.

:copyright: (c) 2015 Decorater
:license: MIT, see LICENSE for more details.

"""

__title__ = 'autoupdate'
__author__ = 'Decorater'
__license__ = 'MIT'
__copyright__ = 'Copyright 2015 Decorater'
__version__ = '0.1.0'
__build__ = 0x001000

from .updater import Updater
import logging

try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
