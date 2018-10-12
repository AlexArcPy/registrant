# -*- coding: UTF-8 -*-
"""Advanced tests generating html files for a geodatabase.

Geodatabase contains domains, tables, and feature classes.
This test case is supposed to be run with a Python installation
that have GDAL installed because OGR module is being used.
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
import html_parsers


########################################################################
class SimpleGeodatabase(unittest.TestCase):
    """Full test case with a complete geodatabase.

    Geodatabase contains has domains, tables, and feature classes.
    """

    # ---------------------------------------------------------------------
    def setUp(self):
        """Set up the test context.

        Create a file geodatabase from .xml schema file and
        load .json look-up data.
        """
        ogr_loader = pkgutil.find_loader('ogr')
        if not ogr_loader:
            self.skipTest(NO_OGR_ENV_MESSAGE)

        self.in_gdb, self.out_report_folder, self.json_results = prepare_test(
            'Advanced_ogr')

    # ---------------------------------------------------------------------
    def test_domains(self):
        """Test geodatabase report for domains."""
        test_name = self.id().split('.')[-1]
        self.reporter = registrant.Reporter(
            gdb_path=self.in_gdb,
            out_report_folder_path=os.path.join(self.out_report_folder,
                                                test_name + PYTHON_VERSION),
        )

        self.reporter.domains2html()
        print(self.reporter.report_file_path)
        self.assertEqual(
            html_parsers.parse_domains_from_html(
                html_file=self.reporter.report_file_path,
                json_file=self.json_results,
            ), (True, True))

    # ---------------------------------------------------------------------
    def test_tables(self):
        """Test geodatabase report for tables."""
        test_name = self.id().split('.')[-1]
        self.reporter = registrant.Reporter(
            gdb_path=self.in_gdb,
            out_report_folder_path=os.path.join(self.out_report_folder,
                                                test_name + PYTHON_VERSION),
        )
        self.reporter.tables2html()
        print(self.reporter.report_file_path)
        self.assertEqual(
            html_parsers.parse_tables_from_html(
                html_file=self.reporter.report_file_path,
                json_file=self.json_results,
            ), (True, True))

    # ---------------------------------------------------------------------
    def test_fcs(self):
        """Test geodatabase report for feature classes."""
        test_name = self.id().split('.')[-1]
        self.reporter = registrant.Reporter(
            gdb_path=self.in_gdb,
            out_report_folder_path=os.path.join(self.out_report_folder,
                                                test_name + PYTHON_VERSION),
        )
        self.reporter.fcs2html()
        print(self.reporter.report_file_path)
        self.assertEqual(
            html_parsers.parse_fcs_from_html(
                html_file=self.reporter.report_file_path,
                json_file=self.json_results,
            ), (True, True))


if __name__ == '__main__':
    unittest.main()
