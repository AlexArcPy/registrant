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


########################################################################
class FullGeodatabase(object):
    """Full test case with a complete geodatabase that has various domains,
    tables, and feature classes."""

    #----------------------------------------------------------------------
    def setUp(self):
        self.in_gdb, self.out_report_folder, self.json_results = prepare_test('Advanced')

    #----------------------------------------------------------------------
    def test_domains(self):
        """test geodatabase report for domains"""
        test_name = self.id().split('.')[-1]
        report_file_path = registrant.domains2html(self.in_gdb,
                                                   os.path.join(
                                                       self.out_report_folder,
                                                       test_name + PYTHON_VERSION))
        print(CONSOLE_MESSAGE, report_file_path)

        self.assertTupleEqual(
            helpers.parse_domains_from_html(
                html_file=report_file_path, json_file=self.json_results), (True, True))

    #----------------------------------------------------------------------
    def test_tables(self):
        """test geodatabase report for tables"""
        test_name = self.id().split('.')[-1]
        report_file_path = registrant.tables2html(
            self.in_gdb, os.path.join(self.out_report_folder, test_name + PYTHON_VERSION))
        print(CONSOLE_MESSAGE, report_file_path)

        self.assertTupleEqual(
            helpers.parse_tables_from_html(
                html_file=report_file_path, json_file=self.json_results), (True, True))

    #----------------------------------------------------------------------
    def test_fcs(self):
        """test geodatabase report for feature classes"""
        test_name = self.id().split('.')[-1]
        report_file_path = registrant.fcs2html(self.in_gdb,
                                               os.path.join(self.out_report_folder,
                                                            test_name + PYTHON_VERSION))
        print(CONSOLE_MESSAGE, report_file_path)

        self.assertTupleEqual(
            helpers.parse_fcs_from_html(
                html_file=report_file_path, json_file=self.json_results), (True, True))
