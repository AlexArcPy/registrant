# -*- coding: UTF-8 -*-
"""Basic tests generating html files for a geodatabase with a single domain.

This test case is supposed to be run with a Python installation
present either in ArcGIS Desktop or ArcGIS Pro.
"""
from __future__ import print_function
import os
import unittest
import pkgutil

from context import (
    registrant,
    prepare_test,
    PYTHON_VERSION,
    NO_ARCPY_ENV_MESSAGE,
)
import html_parsers


########################################################################
class SimpleGeodatabase(unittest.TestCase):
    """Basic test case for a simple geodatabase with one domain."""

    # ----------------------------------------------------------------------
    def setUp(self):
        """Set up the test.

        Create a file geodatabase from .xml schema file and
        load .json look-up data.
        """
        arcpy_loader = pkgutil.find_loader('arcpy')
        if not arcpy_loader:
            self.skipTest(NO_ARCPY_ENV_MESSAGE)

        self.in_gdb, self.out_report_folder, self.json_results = prepare_test(
            'Basic')

    # ----------------------------------------------------------------------
    def test_domain(self):
        """Test geodatabase report for domains."""
        test_name = self.id().split('.')[-1]
        reporter = registrant.Reporter(
            gdb_path=self.in_gdb,
            out_report_folder_path=os.path.join(self.out_report_folder,
                                                test_name + PYTHON_VERSION),
        )
        reporter.gdb2html()

        print(reporter.report_file_path)

        self.assertEqual(
            html_parsers.parse_domains_from_html(
                html_file=reporter.report_file_path,
                json_file=self.json_results,
            ), (True, True))


if __name__ == '__main__':
    unittest.main()
