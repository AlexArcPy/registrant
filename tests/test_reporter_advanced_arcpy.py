# -*- coding: UTF-8 -*-
"""Advanced tests generating html files for a geodatabase.

Geodatabase contains domains, tables, and feature classes.
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
    """Full test case with a complete geodatabase.

    Geodatabase contains has domains, tables, and feature classes.
    """

    # ---------------------------------------------------------------------
    def setUp(self):
        """Set up the test context.

        Create a file geodatabase from .xml schema file and
        load .json look-up data.
        """
        arcpy_loader = pkgutil.find_loader('arcpy')
        if not arcpy_loader:
            self.skipTest(NO_ARCPY_ENV_MESSAGE)

        self.in_gdb, self.out_report_folder, self.json_results = prepare_test(
            'Advanced')
        return

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
        return

    # ---------------------------------------------------------------------
    def test_relclasses(self):
        """Test geodatabase report for relationship classes."""
        test_name = self.id().split('.')[-1]
        self.reporter = registrant.Reporter(
            gdb_path=self.in_gdb,
            out_report_folder_path=os.path.join(self.out_report_folder,
                                                test_name + PYTHON_VERSION),
        )

        self.reporter.gdb2html(
            do_report_versions=False,
            do_report_replicas=False,
            do_report_domains=False,
            do_report_domains_coded_values=False,
            do_report_relclasses=True,
            do_report_tables=False,
            do_report_tables_fields=False,
            do_report_tables_subtypes=False,
            do_report_tables_indexes=False,
            do_report_fcs=False,
            do_report_fcs_fields=False,
            do_report_fcs_subtypes=False,
            do_report_fcs_indexes=False,
        )
        print(self.reporter.report_file_path)
        self.assertEqual(
            html_parsers.parse_relclasses_from_html(
                html_file=self.reporter.report_file_path,
                json_file=self.json_results,
            ), (True, True))
        return

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
        return

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
        return


if __name__ == '__main__':
    unittest.main()
