'''
Running basic tests generating html files for
a dummy geodatabase with a single domain
'''
from __future__ import print_function

import os
import unittest
import webbrowser

from .context import (registrant, TEST_CONFIG, CONSOLE_MESSAGE, PYTHON_VERSION,
                      prepare_test)
from . import helpers

from .reporter_basic import SimpleGeodatabase


########################################################################
class SimpleGeodatabaseChild(unittest.TestCase, SimpleGeodatabase):
    #----------------------------------------------------------------------
    def setUp(self):
        self.in_gdb, self.out_report_folder, self.json_results = prepare_test('Basic_ogr')


if __name__ == '__main__':
    unittest.main()
