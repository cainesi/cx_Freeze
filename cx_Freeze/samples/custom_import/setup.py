# -*- coding: utf-8 -*-

# A script to test finding imports where a package defines a customer importer.
#

from cx_Freeze import setup, Executable

executables = [
    Executable('import_test.py')
]

setup(name='hello',
      version='0.1',
      description='Sample cx_Freeze script',
      executables=executables
      )
