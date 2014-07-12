#
#   Copyright (c) 2014, Scott J Maddox
#
#   This file is part of Plot Liberator.
#
#   Plot Liberator is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published
#   by the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   Plot Liberator is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with Plot Liberator.  If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

# std lib imports
import sys
import os.path

# third party imports
import glob
from setuptools import setup, find_packages

# read in __version__
exec(open('src/plotliberator/version.py').read())

# If on Mac OS X, build an app bundle using py2app
if sys.platform == 'darwin':
    # extra arguments for mac py2app to associate files
    plist = {
        'CFBundleName': 'Plot Liberator',
        'CFBundleShortVersionString': __version__,
        'CFBundleIdentifier': 'org.python.plotliberator',
        }
    
    py2app_opts = {
                   'argv_emulation': False,
                   'includes' : ['PySide.QtCore', 'PySide.QtGui', 'numpy',
                                 'math'],
#                    'excludes' : [],
                   'plist': plist,
                   #'iconfile': 'icons/plotliberator.icns',
                   }
    extra_options = {
                    'setup_requires': ['py2app'],
                    'app' : ['src/plotliberator/main.py'],
                    'options': { 
                                'py2app': py2app_opts
                                }
                    }
elif sys.platform == 'win32':
    
    extra_options = {
                    'setup_requires': ['py2exe'],
                    'app' : ['src/plotliberator/main.py'],
                    }
else:
    extra_options = {}

setup(name='plotliberator',
      version=__version__,  # read from version.py
      description='A GUI for extracting data from plot images',
      long_description=open('README.rst').read(),
      url='http://scott-maddox.github.io/plotliberator',
      author='Scott J. Maddox',
      author_email='smaddox@utexas.edu',
      license='AGPLv3',
      packages=['plotliberator',
                ],
      package_dir={'plotliberator': 'src/plotliberator'},
      zip_safe=True,
      **extra_options)
