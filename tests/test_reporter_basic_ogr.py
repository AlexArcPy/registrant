# -*- coding: UTF-8 -*-
"""Basic tests generating html files for a geodatabase with a single domain.

These tests should be run using Python installation that has GDAL installed
and no arcpy installed. Such installation is best created using Anaconda.
"""
from __future__ import print_function
import os
import unittest
import pkgutil

from context import (
    registrant,
    prepare_test,
    PYTHON_VERSION,
    NO_OGR_ENV_MESSAGE,
)

from registrant._config import OGR_GDB_SUPPORT_MESSAGE
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
        ogr_loader = pkgutil.find_loader('ogr')
        if not ogr_loader:
            self.skipTest(NO_OGR_ENV_MESSAGE)

        self.in_gdb, self.out_report_folder, self.json_results = prepare_test(
            'Basic_ogr')

    # ----------------------------------------------------------------------
    def test_personal_gdb(self):
        """Test that report personal geodatabase with ogr is not supported."""
        test_name = self.id().split('.')[-1]
        with self.assertRaises(ValueError):
            reporter = registrant.Reporter(
                gdb_path='personal.mdb',
                out_report_folder_path=os.path.join(
                    self.out_report_folder,
                    test_name + PYTHON_VERSION,
                ),
            )
        return

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
        return


if __name__ == '__main__':
    unittest.main()
