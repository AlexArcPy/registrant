'''
Running basic tests generating html files for
a dummy geodatabase with a single domain
'''
from __future__ import print_function

import os
import unittest
import webbrowser

from context import (registrant, test_config, console_message, prepare_test)
import helpers


########################################################################
class SimpleGeodatabase(unittest.TestCase):
    """Basic test case for a simple geodatabase with one domain"""

    #----------------------------------------------------------------------
    def setUp(self):
        self.in_gdb, self.out_report_folder, self.json_results = prepare_test('Basic')

    #----------------------------------------------------------------------
    def test_domain(self):
        """test geodatabase report for domains"""
        test_name = self.id().split('.')[-1]
        report_file_path = registrant.gdb2html(self.in_gdb,
                                               os.path.join(self.out_report_folder,
                                                            test_name))

        print(console_message, report_file_path)

        self.assertTupleEqual(
            helpers.parse_domains_from_html(
                html_file=report_file_path, json_file=self.json_results), (True, True))

        webbrowser.open(report_file_path)


if __name__ == '__main__':
    unittest.main()
