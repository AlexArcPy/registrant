# -*- coding: UTF-8 -*-
"""Parsing output report html files.

Verifying that they contain correct information written by the reporter class
"""

import json
from bs4 import BeautifulSoup
from registrant._config import HTML_PARSER


# ----------------------------------------------------------------------
def parse_relclasses_from_html(html_file, json_file):
    """Parse html file and return basic information about relationship classes.

    Return information about objects based on the input parameters
    from the passed json file.
    """
    with open(html_file, 'r') as fh:
        page = BeautifulSoup(fh, HTML_PARSER)

    relclasses_table = page.findAll(name='table')[1]

    with open(json_file) as lookup:
        relclasses_info = json.load(lookup)['relclasses']
        headers = relclasses_info.keys()

    # test headers of the html table
    html_headers = relclasses_table.findChildren(['th'])
    headers_match = set(headers) == {
        th.string
        for th in [html_headers[0], html_headers[2], html_headers[3]]
    }

    # test row values of the html table
    name, origin, destination = (
        relclasses_info['Name'],
        relclasses_info['Origin class names'],
        relclasses_info['Destination class names'],
    )

    for relclass in relclasses_table.findChildren(['td']):
        if relclass.text == name:
            idx = relclasses_table.findChildren(['td']).index(relclass)
            html_name = relclasses_table.findChildren(['td'])[idx].string
            html_origin = relclasses_table.findChildren(['td'])[idx + 2].string
            html_destination = relclasses_table.findChildren(
                ['td'])[idx + 4].string
            break

    row_values_match = all([
        name == html_name,
        origin == html_origin,
        destination == html_destination,
    ])

    return (headers_match, row_values_match)


# ----------------------------------------------------------------------
def parse_domains_from_html(html_file, json_file):
    """Parse html file and return basic information about domains.

    Return information about objects based on the input parameters
    from the passed json file.
    """
    with open(html_file, 'r') as fh:
        page = BeautifulSoup(fh, HTML_PARSER)

    domains_table = page.findAll(name='table')[1]

    with open(json_file) as lookup:
        domains_info = json.load(lookup)['domains']
        headers = domains_info.keys()

    # test headers of the html table
    headers_match = set(headers) == {
        th.string
        for th in domains_table.findChildren(['th'])[1:4]
    }

    # test row values of the html table
    name, dtype, desc = (
        domains_info['Name'],
        domains_info['Domain type'],
        domains_info['Description'],
    )
    row_values_match = all([
        name == domains_table.findChildren(['td'])[1].string,
        dtype == domains_table.findChildren(['td'])[2].string,
        desc == domains_table.findChildren(['td'])[3].string,
    ])
    return (headers_match, row_values_match)


# ----------------------------------------------------------------------
def parse_tables_from_html(html_file, json_file):
    """Parse html file and return basic information about tables.

    Return information about objects based on the input parameters
    from the passed json file.
    """
    with open(html_file, 'r') as fh:
        page = BeautifulSoup(fh, HTML_PARSER)

    gdbtables_table = page.findAll(name='table')[1]

    with open(json_file) as lookup:
        tables_info = json.load(lookup)['tables']
        headers = tables_info.keys()

    # test headers of the html table
    headers_match = set(headers) == {
        th.string
        for th in gdbtables_table.findChildren(['th'])[0:3]
    }

    # test row values of the html table
    name, alias, oid = (
        tables_info['Name'],
        tables_info['Alias'],
        tables_info['ObjectID'],
    )
    row_values_match = all([
        name == gdbtables_table.findChildren(['td'])[0].string,
        alias == gdbtables_table.findChildren(['td'])[1].string,
        oid == gdbtables_table.findChildren(['td'])[2].string,
    ])
    return (headers_match, row_values_match)


# ----------------------------------------------------------------------
def parse_fcs_from_html(html_file, json_file):
    """Parse html file and return basic information about feature classes.

    Return information about objects based on the input parameters
    from the passed json file.
    """
    with open(html_file, 'r') as fh:
        page = BeautifulSoup(fh, HTML_PARSER)

    fcs_table = page.findAll(name='table')[1]

    with open(json_file) as lookup:
        fcs_info = json.load(lookup)['fcs']
        headers = fcs_info.keys()

    # test headers of the html table
    html_headers = fcs_table.findChildren(['th'])
    string_headers = [th.string for th in html_headers]

    if 'Feature dataset' not in string_headers:  # ogr test
        headers_match = set(headers) == {
            th.string
            for th in [html_headers[0], html_headers[2], html_headers[3]]
        }
    else:  # arcpy test
        headers_match = set(headers) == {
            th.string
            for th in [html_headers[0], html_headers[3], html_headers[4]]
        }

    # test row values of the html table
    name, feat_type, shape_type = (
        fcs_info['Name'],
        fcs_info['Feature type'],
        fcs_info['Shape type'],
    )

    if 'Feature dataset' not in string_headers:  # ogr test
        row_values_match = all([
            name == fcs_table.findChildren(['td'])[0].string,
            feat_type == fcs_table.findChildren(['td'])[2].string,
            shape_type == fcs_table.findChildren(['td'])[3].string,
        ])
    else:  # arcpy test
        row_values_match = all([
            name == fcs_table.findChildren(['td'])[0].string,
            feat_type == fcs_table.findChildren(['td'])[3].string,
            shape_type == fcs_table.findChildren(['td'])[4].string,
        ])
    return (headers_match, row_values_match)
