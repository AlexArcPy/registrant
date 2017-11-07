'''
Parsing output report html files and verifying that they contain needed information
'''

import json
from bs4 import BeautifulSoup


#----------------------------------------------------------------------
def parse_domains_from_html(html_file, json_file):
    """parse HTML file and return key information about objects based
    on the input parameters from the passed json file"""

    with open(html_file, 'r') as f:
        page = BeautifulSoup(f, "html.parser")

    domains_table = page.findAll(name='table')[1]

    with open(json_file) as lookup:
        info = json.load(lookup)['domains']
        headers = info.keys()

    #test headers of the html table
    headers_match = set(headers) == set(
        [th.string for th in domains_table.findChildren(['th'])[1:4]])

    #test row values of the html table
    name, dtype, desc = (info['Name'], info['Domain type'], info['Description'])
    row_values_match = all([
        name == domains_table.findChildren(['td'])[1].string,
        dtype == domains_table.findChildren(['td'])[2].string,
        desc == domains_table.findChildren(['td'])[3].string
    ])

    return (headers_match, row_values_match)


#----------------------------------------------------------------------
def parse_tables_from_html(html_file, json_file):
    """parse HTML file and return key information about objects based
    on the input parameters from the passed json file"""

    with open(html_file, 'r') as f:
        page = BeautifulSoup(f, "html.parser")

    gdbtables_table = page.findAll(name='table')[1]

    with open(json_file) as lookup:
        info = json.load(lookup)['tables']
        headers = info.keys()

    #test headers of the html table
    headers_match = set(headers) == set(
        [th.string for th in gdbtables_table.findChildren(['th'])[0:3]])

    #test row values of the html table
    name, alias, oid = (info['Name'], info['Alias'], info['ObjectID'])
    row_values_match = all([
        name == gdbtables_table.findChildren(['td'])[0].string,
        alias == gdbtables_table.findChildren(['td'])[1].string,
        oid == gdbtables_table.findChildren(['td'])[2].string
    ])

    return (headers_match, row_values_match)


#----------------------------------------------------------------------
def parse_fcs_from_html(html_file, json_file):
    """parse HTML file and return key information about objects based
    on the input parameters from the passed json file"""

    with open(html_file, 'r') as f:
        page = BeautifulSoup(f, "html.parser")

    fcs_table = page.findAll(name='table')[1]

    with open(json_file) as lookup:
        info = json.load(lookup)['fcs']
        headers = info.keys()

    #test headers of the html table
    html_headers = fcs_table.findChildren(['th'])
    string_headers = [th.string for th in html_headers]

    if 'Feature dataset' not in string_headers:  # ogr test
        headers_match = set(headers) == set(
            [th.string for th in [html_headers[0], html_headers[2], html_headers[3]]])
    else:  # arcpy test
        headers_match = set(headers) == set(
            [th.string for th in [html_headers[0], html_headers[3], html_headers[4]]])

    #test row values of the html table
    name, feat_type, shape_type = (info['Name'], info['Feature type'], info['Shape type'])

    if 'Feature dataset' not in string_headers:  # ogr test
        row_values_match = all([
            name == fcs_table.findChildren(['td'])[0].string,
            feat_type == fcs_table.findChildren(['td'])[2].string,
            shape_type == fcs_table.findChildren(['td'])[3].string
        ])
    else:  # arcpy test
        row_values_match = all([
            name == fcs_table.findChildren(['td'])[0].string,
            feat_type == fcs_table.findChildren(['td'])[3].string,
            shape_type == fcs_table.findChildren(['td'])[4].string
        ])

    return (headers_match, row_values_match)
