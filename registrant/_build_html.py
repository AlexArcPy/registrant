# -*- coding: UTF-8 -*-
"""Internal worker functions for constructing HTML source code strings."""

from registrant._config import (
    REPORT_TEMPLATE_FILE,
    HTML_PARSER,
    DIV_CSS_CLASS,
    COMMONS_LICENSE_TEXT,
)

import os
import shutil
from codecs import open
from bs4 import BeautifulSoup
import pandas as pd
# to not truncate string content when export pandas DataFrame to HTML
pd.set_option('display.max_colwidth', -1)


# ----------------------------------------------------------------------
def do_copy_report(report_path, report_template_file):
    """Copy report file into the destination folder if it doesn't yet exist."""
    if not os.path.exists(report_path):
        shutil.copy2(report_template_file, report_path)
    return


# ----------------------------------------------------------------------
def add_timestamp_header(report_path, day_time):
    """Append `h1` header to html page with the time of report generation."""
    do_copy_report(report_path, REPORT_TEMPLATE_FILE)

    with open(report_path, 'r', encoding='utf-8') as report:
        soup_page = BeautifulSoup(report, HTML_PARSER)

    soup_main_div = soup_page.find_all('div', {'class': DIV_CSS_CLASS})[0]
    soup_page_header_template = BeautifulSoup(
        """<h1 class="page-header">Report created {day_time}</h1>""".format(
            day_time=day_time), HTML_PARSER)
    soup_main_div.append(soup_page_header_template)

    with open(report_path, 'w', encoding='utf-8') as report:
        report.write(soup_page.decode())
    return


# ----------------------------------------------------------------------
def add_li_to_toc(parent_id, section_header_id, report_path, li_text=None):
    """Update html report with `li` item.

    Append `li` item to the table of contents and
    save the updated HTML object to the `.html` file.
    """
    if not li_text:
        li_text = section_header_id

    do_copy_report(report_path, REPORT_TEMPLATE_FILE)

    with open(report_path, 'r', encoding='utf-8') as report:
        soup_page = BeautifulSoup(report, HTML_PARSER)

    toc_ul = soup_page.find_all('ul', {'id': parent_id})[0]
    soup_li_template = BeautifulSoup(
        u"""<li><a href="#{section_header_id}">{li_text}</a></li>""".format(
            section_header_id=section_header_id, li_text=li_text), HTML_PARSER)
    toc_ul.append(soup_li_template)

    with open(report_path, 'w', encoding='utf-8') as report:
        report.write(soup_page.decode())
    return


# ----------------------------------------------------------------------
def add_div_to_html_page(df,
                         report_path,
                         section_header_id,
                         section_title='New section',
                         header_size='h2',
                         escape=True):
    """
    Update html report with `div` item.

    Append `div` with the data table to the body of the report and
    save the updated the HTML object to the .`html` file.
    """
    html_table = df.to_html(
        index=False,
        classes='table table-striped table-hover',
        border=0,
        escape=escape)

    with open(report_path, 'r', encoding='utf-8') as report:
        soup_page = BeautifulSoup(report, HTML_PARSER)

    soup_main_div = soup_page.find_all('div', {'class': DIV_CSS_CLASS})[0]
    soup_main_div['id'] = 'divDataTables'
    soup_div_template = BeautifulSoup(
        u"""
        <{header_size} class="sub-header"
        id="{section_header_id}">{section_title}</h2>
        <div class="table-responsive">
        </div>
        """.format(
            header_size=header_size,
            section_header_id=section_header_id,
            section_title=section_title,
        ), HTML_PARSER)

    soup_table = BeautifulSoup(html_table, HTML_PARSER)
    soup_div_template.div.append(soup_table)
    soup_main_div.append(soup_div_template)

    with open(report_path, 'w', encoding='utf-8') as report:
        report.write(soup_page.decode())
    return


# ----------------------------------------------------------------------
def add_license_footer(report_path):
    """Add license footer to the end of the `.html` report page."""
    with open(report_path, 'r', encoding='utf-8') as report:
        soup_page = BeautifulSoup(report, HTML_PARSER)

    soup_main_div = soup_page.find_all('div', {'class': DIV_CSS_CLASS})[0]
    soup_main_div['id'] = 'divDataTables'
    soup_div_template = BeautifulSoup(
        '<div class="license-text">{license_text}</div>'.format(
            license_text=COMMONS_LICENSE_TEXT), HTML_PARSER)
    soup_main_div.append(soup_div_template)

    with open(report_path, 'w', encoding='utf-8') as report:
        report.write(soup_page.decode())
    return
