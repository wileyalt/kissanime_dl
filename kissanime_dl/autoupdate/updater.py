# -*- coding: utf-8 -*-

"""
The MIT License (MIT)
Copyright (c) 2015 Decorater
Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import print_function
import subprocess
import shlex
import warnings

from .errors import (
    LibVerWarning,
)

libvers = '0.3.0'
deslibvers = '0.3.0'

class Updater(object):
    def update(self, module):
        if module is not None:
            cmd = 'pip install --upgrade ' + module
            print(cmd)
            cmdargs = shlex.split(cmd)
            subprocess.Popen(cmdargs, stdout=subprocess.PIPE)
        else:
            print('No module specified Error.')

    def install(self, module):
        if module is not None:
            cmd = 'pip install ' + module
            print(cmd)
            cmdargs = shlex.split(cmd)
            subprocess.Popen(cmdargs, stdout=subprocess.PIPE)
        else:
            print('No module specified Error.')

    def gitplus(self, module, link):
        if module is not None:
            if link is not None:
                cmd = 'pip install git+' + link
                print(cmd)
                cmdargs = shlex.split(cmd)
                subprocess.Popen(cmdargs, stdout=subprocess.PIPE)
            else:
                print('No Git+ link specified Error.')
        else:
            print('No module specified Error.')

    if libvers != deslibvers:
        warnings.warn((
            'You are using a depreciated version of autoupdater. '
            'Be sure to update from ' + libvers + ' to ' + deslibvers + '.'),
            LibVerWarning
        )