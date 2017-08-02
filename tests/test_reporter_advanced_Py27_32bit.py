'''
Running advanced tests generating html files for
geodatabase domains, tables, and feature classes
'''
from __future__ import print_function

import os
import unittest
import webbrowser

from .context import (registrant, TEST_CONFIG, CONSOLE_MESSAGE, prepare_test,
                     PYTHON_VERSION)
from . import helpers
from .reporter_advanced import FullGeodatabase

########################################################################
class FullGeodatabaseChild(unittest.TestCase, FullGeodatabase):
    #----------------------------------------------------------------------
    def setUp(self):
        self.in_gdb, self.out_report_folder, self.json_results = prepare_test('Advanced')

if __name__ == '__main__':
    unittest.main()
