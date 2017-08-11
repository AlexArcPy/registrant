'''
The main module to instantiate Geodatabase class, read its objects
and their properties and build an HTML report file
'''

import os
import shutil
import datetime
from functools import partial

from . import _geodatabase as GDB
from . import _build_html
import pandas as pd

from ._data_objects import Table, TableOgr, FeatureClass, FeatureClassOgr
from ._config import REPORT_DATA_FOLDER_PATH, REPORT_FILE_NAME

pd.set_option('display.max_rows', 20)
pd.set_option('display.width', 250)

BOOL_MAPPER = {True: 'Yes', False: 'No'}

try:
    import arcpy
    arcpy_found = True
except:
    arcpy_found = False


#----------------------------------------------------------------------
def map_boolean(df):
    r"""maps data frame boolean columns to get `Yes`\`No` from `True`\`False`"""
    return df.replace({c: BOOL_MAPPER for c in df.select_dtypes([bool])})


#----------------------------------------------------------------------
def report_gdb_as_html(gdb_path,
                       out_report_folder_path,
                       do_report_domains=True,
                       do_report_domains_coded_values=True,
                       do_report_tables=True,
                       do_report_tables_fields=True,
                       do_report_tables_subtypes=True,
                       do_report_tables_indexes=True,
                       do_report_fcs=True,
                       do_report_fcs_fields=True,
                       do_report_fcs_subtypes=True,
                       do_report_fcs_indexes=True):
    r"""report geodatabase properties as an HTML page

    gdb_path: str, path to the input geodatabase
    out_report_folder_path: str, path to a folder where HTML report file along with
    the app files folder will be created

    Example:

        report_gdb_as_html(
        gdb_path=
        r"C:\GIS\MyData.gdb",
        out_report_folder_path=r"C:\GIS\ReportFolder")

    """

    out_report_app_folder = os.path.join(out_report_folder_path,
                                         os.path.basename(REPORT_DATA_FOLDER_PATH))

    if not os.path.exists(out_report_folder_path):
        os.mkdir(out_report_folder_path)

    else:
        if os.path.exists(out_report_app_folder):
            shutil.rmtree(out_report_app_folder)

    shutil.copytree(REPORT_DATA_FOLDER_PATH, out_report_app_folder)

    report_file_path = os.path.join(out_report_app_folder, REPORT_FILE_NAME)

    #remove __init__.py file from the app folder as it is copied along
    for file_name in ['__init__.py', '__init__.pyc']:
        file_path = os.path.join(os.path.join(out_report_app_folder, file_name))
        if os.path.exists(file_path):
            os.remove(file_path)

    gdb = GDB.Geodatabase(gdb_path)

    #write timestamp
    day_time = datetime.datetime.strftime(datetime.datetime.now(), "%d %b %Y %H:%M:%S")
    _build_html.add_timestamp_header(report_path=report_file_path, day_time=day_time)

    #General gdb properties
    df = pd.DataFrame.from_records(gdb.get_pretty_props(), index=[0])
    _build_html.add_div_to_html_page(
        df,
        section_header_id="overview",
        section_title="Overview",
        report_path=report_file_path)

    #------------------------------------------------------------------------------------------------
    #DOMAINS
    #------------------------------------------------------------------------------------------------

    if do_report_domains | do_report_domains_coded_values:
        #Domains properties + coded values domains from Coded values property
        domains = gdb.get_domains()
        if domains:
            df = pd.DataFrame.from_dict(domains).sort_values(by='Name')
            df['Range'].fillna(value='', inplace=True)

            if do_report_domains:
                for domain_name in sorted(
                        df[df['Domain type'] == 'CodedValue']['Name'].values):
                    #TOC generation
                    _build_html.add_li_to_toc(
                        parent_id="tocDomains",
                        section_header_id="dmn" + domain_name,
                        li_text=domain_name,
                        report_path=report_file_path)

                _build_html.add_div_to_html_page(
                    df=df.drop('Coded values', 1),
                    section_header_id="domains",
                    section_title="Domains",
                    report_path=report_file_path)

            if do_report_domains_coded_values:
                df_coded_values = {
                    item['Name']: item['Coded values']
                    for item in df.to_dict(orient='records')
                    if item['Domain type'] == 'CodedValue'
                }

                #Coded values for domains
                for domain_name, coded_values_dict in sorted(
                        df_coded_values.items(), key=lambda i: i[0]):
                    df = pd.DataFrame([{
                        "Code": k,
                        "Value": v
                    } for k, v in coded_values_dict.items()])
                    _build_html.add_div_to_html_page(
                        df,
                        section_header_id="dmn" + domain_name,
                        section_title=domain_name,
                        header_size='h3',
                        report_path=report_file_path)

#------------------------------------------------------------------------------------------------
#TABLES
#------------------------------------------------------------------------------------------------

    if (do_report_tables | do_report_tables_fields | do_report_tables_subtypes |
            do_report_tables_indexes):
        tables = gdb.get_tables()
        if tables:
            df = map_boolean(pd.DataFrame.from_dict(tables).sort_values(by='Name'))
            if do_report_tables:
                _build_html.add_div_to_html_page(
                    df,
                    section_header_id="tables",
                    section_title="Tables",
                    report_path=report_file_path)

            for table_name in sorted(df['Name'].values):
                #TOC generation
                _build_html.add_li_to_toc(
                    parent_id="tocTables",
                    section_header_id=table_name,
                    report_path=report_file_path)

                tbl = None
                if do_report_tables_fields:
                    #Tables fields and indexes
                    if arcpy_found:
                        tbl = Table(os.path.join(gdb.path, table_name))
                    else:
                        tbl = TableOgr(gdb.path, table_name)
                    df_fields = map_boolean(pd.DataFrame.from_dict(tbl.get_fields()))
                    #when there is a table with no fields
                    if not df_fields.empty:
                        df_fields['Default value'].fillna(value='', inplace=True)
                    _build_html.add_div_to_html_page(
                        df_fields,
                        section_header_id=table_name,
                        section_title=table_name,
                        header_size='h3',
                        report_path=report_file_path)

                if do_report_tables_subtypes and arcpy_found:
                    if not tbl:
                        tbl = Table(os.path.join(gdb.path, table_name))
                    subtypes = tbl.get_subtypes()
                    if subtypes:
                        df_subtypes = map_boolean(pd.DataFrame.from_dict(subtypes))

                        if do_report_tables_fields:
                            section_title = "Subtypes"
                        else:
                            section_title = "Subtypes ({})".format(table_name)
                        _build_html.add_div_to_html_page(
                            df_subtypes,
                            section_header_id=table_name,
                            section_title=section_title,
                            header_size='h4',
                            report_path=report_file_path)

                if do_report_tables_indexes and arcpy_found:
                    if not tbl:
                        tbl = Table(os.path.join(gdb.path, table_name))
                    indexes = tbl.get_indexes()
                    if indexes:
                        df_indexes = map_boolean(
                            pd.DataFrame.from_dict(indexes).sort_values(by='Name'))

                        if do_report_tables_fields:
                            section_title = "Indexes"
                        else:
                            section_title = "Indexes ({})".format(table_name)
                        _build_html.add_div_to_html_page(
                            df_indexes,
                            section_header_id=table_name,
                            section_title=section_title,
                            header_size='h4',
                            report_path=report_file_path)

#------------------------------------------------------------------------------------------------
#FEATURE CLASSES
#------------------------------------------------------------------------------------------------
    if (do_report_fcs | do_report_fcs_fields | do_report_fcs_subtypes |
            do_report_fcs_indexes):
        fcs = gdb.get_feature_classes()
        if fcs:
            df = map_boolean(pd.DataFrame.from_dict(fcs).sort_values(by='Name'))
            if do_report_fcs:
                _build_html.add_div_to_html_page(
                    df,
                    section_header_id="fcs",
                    section_title="Feature classes",
                    report_path=report_file_path)

            for fc_name in sorted(df['Name'].values):
                #TOC generation
                _build_html.add_li_to_toc(
                    parent_id="tocFcs",
                    section_header_id=fc_name,
                    report_path=report_file_path)

                fc = None
                if do_report_fcs_fields:
                    if arcpy_found:
                        fc = FeatureClass(os.path.join(gdb.path, fc_name))
                    else:
                        fc = FeatureClassOgr(gdb.path, fc_name)
                    df_fields = map_boolean(pd.DataFrame.from_dict(fc.get_fields()))

                    #when there is a feature class with no fields
                    if not df_fields.empty:
                        df_fields['Default value'].fillna(value='', inplace=True)
                    _build_html.add_div_to_html_page(
                        df_fields,
                        section_header_id=fc_name,
                        section_title=fc_name,
                        header_size='h3',
                        report_path=report_file_path)

                if do_report_fcs_subtypes and arcpy_found:
                    if not fc:
                        fc = FeatureClass(os.path.join(gdb.path, fc_name))
                    subtypes = fc.get_subtypes()
                    if subtypes:
                        df_subtypes = map_boolean(pd.DataFrame.from_dict(subtypes))

                        if do_report_fcs_fields:
                            section_title = "Subtypes"
                        else:
                            section_title = "Subtypes ({})".format(fc_name)
                        _build_html.add_div_to_html_page(
                            df_subtypes,
                            section_header_id=fc_name,
                            section_title=section_title,
                            header_size='h4',
                            report_path=report_file_path)

                if do_report_fcs_indexes and arcpy_found:
                    if not fc:
                        fc = FeatureClass(os.path.join(gdb.path, fc_name))
                    indexes = fc.get_indexes()
                    if indexes:
                        df_indexes = map_boolean(
                            pd.DataFrame.from_dict(indexes).sort_values(by='Name'))

                        if do_report_fcs_fields:
                            section_title = "Indexes"
                        else:
                            section_title = "Indexes ({})".format(fc_name)
                        _build_html.add_div_to_html_page(
                            df_indexes,
                            section_header_id=fc_name,
                            section_title=section_title,
                            header_size='h4',
                            report_path=report_file_path)

    #add CC-BY license text in the end of the page
    _build_html.add_license_footer(report_path=report_file_path)

    return report_file_path

gdb2html = partial(
    report_gdb_as_html,
    do_report_domains=True,
    do_report_domains_coded_values=True,
    do_report_tables=True,
    do_report_tables_fields=True,
    do_report_tables_subtypes=True,
    do_report_tables_indexes=True,
    do_report_fcs=True,
    do_report_fcs_fields=True,
    do_report_fcs_subtypes=True,
    do_report_fcs_indexes=True)

domains2html = partial(
    report_gdb_as_html,
    do_report_domains=True,
    do_report_domains_coded_values=True,
    do_report_tables=False,
    do_report_tables_fields=False,
    do_report_tables_subtypes=False,
    do_report_tables_indexes=False,
    do_report_fcs=False,
    do_report_fcs_fields=False,
    do_report_fcs_subtypes=False,
    do_report_fcs_indexes=False)

tables2html = partial(
    report_gdb_as_html,
    do_report_domains=False,
    do_report_domains_coded_values=False,
    do_report_tables=True,
    do_report_tables_fields=True,
    do_report_tables_subtypes=True,
    do_report_tables_indexes=True,
    do_report_fcs=False,
    do_report_fcs_fields=False,
    do_report_fcs_subtypes=False,
    do_report_fcs_indexes=False)

fcs2html = partial(
    report_gdb_as_html,
    do_report_domains=False,
    do_report_domains_coded_values=False,
    do_report_tables=False,
    do_report_tables_fields=False,
    do_report_tables_subtypes=False,
    do_report_tables_indexes=False,
    do_report_fcs=True,
    do_report_fcs_fields=True,
    do_report_fcs_subtypes=True,
    do_report_fcs_indexes=True)
