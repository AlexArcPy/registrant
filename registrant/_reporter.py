# -*- coding: UTF-8 -*-
"""
The main module to work with the report.

It can instantiate `Geodatabase` class, read its objects,
and their properties and build an HTML report file.
"""
import os
import shutil
import datetime
import pkgutil
import pandas as pd
from registrant import _util_mappings as utils
from registrant import _geodatabase
from registrant import _build_html

from registrant._data_objects import (
    Table,
    TableOgr,
    FeatureClass,
    FeatureClassOgr,
)
from registrant._config import (
    REPORT_DATA_FOLDER_PATH,
    REPORT_FILE_NAME,
    OGR_GDB_SUPPORT_MESSAGE,
    DATASET_TYPE_FC,
    DATASET_TYPE_TABLE,
)

pd.set_option('display.max_rows', 20)  # noqa: Z432
pd.set_option('display.width', 250)  # noqa: Z432


########################################################################
class Reporter(object):
    """Reporter of geodatabase properties capable of creating .html reports."""

    # ----------------------------------------------------------------------
    def __init__(self, gdb_path, out_report_folder_path):
        """Initialize reporter with basic properties.

        gdb_path: str:
            path to the input geodatabase

        out_report_folder_path: str:
            path to the folder where HTML report file along with
            the template and styling files folder will be created
        """
        self.gdb_path = gdb_path
        arcpy_loader = pkgutil.find_loader('arcpy')
        if arcpy_loader:
            self.arcpy_found = True
        else:
            self.arcpy_found = False

        if not self.arcpy_found and not gdb_path.endswith('.gdb'):
            raise ValueError(OGR_GDB_SUPPORT_MESSAGE)

        self._out_report_folder = os.path.join(
            out_report_folder_path,
            os.path.basename(gdb_path).replace('.', '_'),
            os.path.basename(REPORT_DATA_FOLDER_PATH),
        )

        if not os.path.exists(out_report_folder_path):
            os.mkdir(out_report_folder_path)
        else:
            if os.path.exists(self._out_report_folder):
                shutil.rmtree(self._out_report_folder)

        shutil.copytree(REPORT_DATA_FOLDER_PATH, self._out_report_folder)

        # path to .html file report that will be updated by this class methods
        self.report_file_path = os.path.join(self._out_report_folder,
                                             REPORT_FILE_NAME)

        self.gdb = _geodatabase.Geodatabase(gdb_path)

        self._write_timestamp()
        self._cleanup_report_folder()

        # general gdb properties
        self._gdb_info = pd.DataFrame.from_records(
            self.gdb.get_pretty_props(), index=[0])
        return

    # ----------------------------------------------------------------------
    def gdb2html(
            self,
            do_report_versions=True,
            do_report_replicas=True,
            do_report_domains=True,
            do_report_domains_coded_values=True,
            do_report_relclasses=True,
            do_report_tables=True,
            do_report_tables_fields=True,
            do_report_tables_subtypes=True,
            do_report_tables_indexes=True,
            do_report_fcs=True,
            do_report_fcs_fields=True,
            do_report_fcs_subtypes=True,
            do_report_fcs_indexes=True,
    ):
        r"""Report geodatabase properties as an HTML file.

        do_report_%obj%: bool:
            what type of information should be reported
        """
        self._report_overview()

        if do_report_versions:
            self._report_versions()

        if do_report_replicas:
            self._report_replicas()

        if do_report_domains | do_report_domains_coded_values:
            self._report_domains(do_report_domains,
                                 do_report_domains_coded_values)

        if do_report_relclasses:
            self._report_relclasses()

        if (do_report_tables | do_report_tables_fields
                | do_report_tables_subtypes
                | do_report_tables_indexes):
            self._report_tables(
                do_report_tables,
                do_report_tables_fields,
                do_report_tables_subtypes,
                do_report_tables_indexes,
            )

        if (do_report_fcs | do_report_fcs_fields | do_report_fcs_subtypes
                | do_report_fcs_indexes):
            self._report_fcs(
                do_report_fcs,
                do_report_fcs_fields,
                do_report_fcs_subtypes,
                do_report_fcs_indexes,
            )

        self._write_license_text()
        return

    # ----------------------------------------------------------------------
    def domains2html(
            self,
            do_report_versions=False,
            do_report_replicas=False,
            do_report_domains=True,
            do_report_domains_coded_values=True,
            do_report_relclasses=False,
            do_report_tables=False,
            do_report_tables_fields=False,
            do_report_tables_subtypes=False,
            do_report_tables_indexes=False,
            do_report_fcs=False,
            do_report_fcs_fields=False,
            do_report_fcs_subtypes=False,
            do_report_fcs_indexes=False,
    ):
        """Report geodatabase domains properties only."""
        self.gdb2html(
            do_report_versions=False,
            do_report_replicas=False,
            do_report_domains=True,
            do_report_domains_coded_values=True,
            do_report_relclasses=False,
            do_report_tables=False,
            do_report_tables_fields=False,
            do_report_tables_subtypes=False,
            do_report_tables_indexes=False,
            do_report_fcs=False,
            do_report_fcs_fields=False,
            do_report_fcs_subtypes=False,
            do_report_fcs_indexes=False,
        )

    # ----------------------------------------------------------------------
    def tables2html(
            self,
            do_report_versions=False,
            do_report_replicas=False,
            do_report_domains=False,
            do_report_domains_coded_values=False,
            do_report_relclasses=False,
            do_report_tables=True,
            do_report_tables_fields=True,
            do_report_tables_subtypes=True,
            do_report_tables_indexes=True,
            do_report_fcs=False,
            do_report_fcs_fields=False,
            do_report_fcs_subtypes=False,
            do_report_fcs_indexes=False,
    ):
        """Report geodatabase tables properties only."""
        self.gdb2html(
            do_report_versions=False,
            do_report_replicas=False,
            do_report_domains=False,
            do_report_domains_coded_values=False,
            do_report_relclasses=False,
            do_report_tables=True,
            do_report_tables_fields=True,
            do_report_tables_subtypes=True,
            do_report_tables_indexes=True,
            do_report_fcs=False,
            do_report_fcs_fields=False,
            do_report_fcs_subtypes=False,
            do_report_fcs_indexes=False,
        )

    # ----------------------------------------------------------------------
    def fcs2html(
            self,
            do_report_versions=False,
            do_report_replicas=False,
            do_report_domains=False,
            do_report_domains_coded_values=False,
            do_report_relclasses=False,
            do_report_tables=False,
            do_report_tables_fields=False,
            do_report_tables_subtypes=False,
            do_report_tables_indexes=False,
            do_report_fcs=True,
            do_report_fcs_fields=True,
            do_report_fcs_subtypes=True,
            do_report_fcs_indexes=True,
    ):
        """Report geodatabase feature classes properties only."""
        self.gdb2html(
            do_report_versions=False,
            do_report_replicas=False,
            do_report_domains=False,
            do_report_domains_coded_values=False,
            do_report_relclasses=False,
            do_report_tables=False,
            do_report_tables_fields=False,
            do_report_tables_subtypes=False,
            do_report_tables_indexes=False,
            do_report_fcs=True,
            do_report_fcs_fields=True,
            do_report_fcs_subtypes=True,
            do_report_fcs_indexes=True,
        )

    # ----------------------------------------------------------------------
    def _cleanup_report_folder(self):
        """Remove files that do not belong to the output report folder.

        `__init__.py` and `__init__.pyc` files are copied along from the
        template dir because they are part of the package and should be removed.
        """
        for file_name in ['__init__.py', '__init__.pyc']:
            file_path = os.path.join(
                os.path.join(self._out_report_folder, file_name))
            if os.path.exists(file_path):
                os.remove(file_path)
        return

    # ----------------------------------------------------------------------
    def _write_timestamp(self):
        """Write timestamp to .html report file."""
        day_time = datetime.datetime.strftime(datetime.datetime.now(),
                                              '%d %b %Y %H:%M:%S')
        _build_html.add_timestamp_header(
            report_path=self.report_file_path, day_time=day_time)
        return

    # ----------------------------------------------------------------------
    def _map_boolean(self, df):
        """Map pandas data frame boolean columns.

        Used to get `Yes` from `True` and `No` from `False`.
        """
        return df.replace({
            col: utils.BOOL_TO_YESNO_MAPPER
            for col in df.select_dtypes([bool])
        })

    # ----------------------------------------------------------------------
    def _report_overview(self):
        """Report overview information."""
        _build_html.add_div_to_html_page(
            self._gdb_info,
            section_header_id='overview',
            section_title='Overview',
            report_path=self.report_file_path)
        return

    # ----------------------------------------------------------------------
    def _report_versions(self):
        """Report versions information."""
        versions = self.gdb.get_versions()
        if versions:
            df = self._map_boolean(
                pd.DataFrame.from_dict(versions).sort_values(by='Name'))
            _build_html.add_div_to_html_page(
                df=df,
                section_header_id='versions',
                section_title='Versions',
                report_path=self.report_file_path)
        return

    # ---------------------------------------------------------------------
    def _report_replicas(self):
        """Report replicas information."""
        replicas = self.gdb.get_replicas()
        if replicas:
            df = self._map_boolean(
                pd.DataFrame.from_dict(replicas).sort_values(by='Name'))
            _build_html.add_div_to_html_page(
                df=df,
                section_header_id='replicas',
                section_title='Replicas',
                report_path=self.report_file_path,
                escape=False)
        return

    # ---------------------------------------------------------------------
    def _report_domains(self, do_report_domains,
                        do_report_domains_coded_values):
        """Report domains information."""
        domains = self.gdb.get_domains()
        if not domains:
            return

        df = pd.DataFrame.from_dict(domains).sort_values(by='Name')
        df['Range'].fillna(value='', inplace=True)

        if do_report_domains:
            for domain_name in sorted(
                    df[df['Domain type'] == 'CodedValue']['Name'].values):
                _build_html.add_li_to_toc(
                    parent_id='tocDomains',
                    section_header_id='dmn' + domain_name,
                    li_text=domain_name,
                    report_path=self.report_file_path)

            _build_html.add_div_to_html_page(
                df=df.drop('Coded values', 1),
                section_header_id='domains',
                section_title='Domains',
                report_path=self.report_file_path)

        if do_report_domains_coded_values:
            df_coded_values = {
                item['Name']: item['Coded values']
                for item in df.to_dict(orient='records')
                if item['Domain type'] == 'CodedValue'
            }

            for domain_name, coded_values_dict in sorted(
                    df_coded_values.items(), key=lambda i: i[0]):
                df = pd.DataFrame([{
                    'Code': k,
                    'Value': v,
                } for k, v in coded_values_dict.items()])
                _build_html.add_div_to_html_page(
                    df,
                    section_header_id='dmn' + domain_name,
                    section_title=domain_name,
                    header_size='h3',
                    report_path=self.report_file_path)
        return

    # ----------------------------------------------------------------------
    def _report_relclasses(self):
        """Report relationship classes information."""
        rel_classes = self.gdb.get_relationship_classes()
        if rel_classes:
            df = self._map_boolean(
                pd.DataFrame.from_dict(rel_classes).sort_values(by='Name'))

            _build_html.add_div_to_html_page(
                df=df,
                section_header_id='relclasses',
                section_title='Relationship classes',
                report_path=self.report_file_path,
                escape=False)
        return

    # ----------------------------------------------------------------------
    def _report_tables(
            self,
            do_report_tables,
            do_report_tables_fields,
            do_report_tables_subtypes,
            do_report_tables_indexes,
    ):
        """Report tables information."""
        tables = self.gdb.get_tables()
        if tables:
            tables_info = self._get_tables_info(tables)
            if do_report_tables:
                _build_html.add_div_to_html_page(
                    tables_info,
                    section_header_id='tables',
                    section_title='Tables',
                    report_path=self.report_file_path)

            for table_name in tables_info['Name'].values:
                _build_html.add_li_to_toc(
                    parent_id='tocTables',
                    section_header_id=table_name,
                    report_path=self.report_file_path)

                if do_report_tables_fields:
                    table_fields = self._get_table_fields(table_name)
                    if table_fields is not None:
                        _build_html.add_div_to_html_page(
                            table_fields,
                            section_header_id=table_name,
                            section_title=table_name,
                            header_size='h3',
                            report_path=self.report_file_path)

                if do_report_tables_subtypes and self.arcpy_found:
                    table_subtypes = self._get_table_subtypes(table_name)
                    if table_subtypes is not None:
                        if do_report_tables_fields:
                            section_title = 'Subtypes'
                        else:
                            section_title = 'Subtypes ({0})'.format(table_name)
                        _build_html.add_div_to_html_page(
                            table_subtypes,
                            section_header_id=table_name,
                            section_title=section_title,
                            header_size='h4',
                            report_path=self.report_file_path)

                if do_report_tables_indexes and self.arcpy_found:
                    table_indexes = self._get_table_indexes(table_name)
                    if do_report_tables_fields is not None:
                        section_title = 'Indexes'
                    else:
                        section_title = 'Indexes ({0})'.format(table_name)
                    _build_html.add_div_to_html_page(
                        table_indexes,
                        section_header_id=table_name,
                        section_title=section_title,
                        header_size='h4',
                        report_path=self.report_file_path)
        return

    # ---------------------------------------------------------------------
    def _report_fcs(
            self,
            do_report_fcs,
            do_report_fcs_fields,
            do_report_fcs_subtypes,
            do_report_fcs_indexes,
    ):
        """Report feature classes information."""
        fcs = self.gdb.get_feature_classes()
        if fcs:
            if do_report_fcs:
                fcs_info = self._get_fcs_info(fcs)
                _build_html.add_div_to_html_page(
                    fcs_info,
                    section_header_id='fcs',
                    section_title='Feature classes',
                    report_path=self.report_file_path)

            for fc_name in fcs_info['Name'].values:
                _build_html.add_li_to_toc(
                    parent_id='tocFcs',
                    section_header_id=fc_name,
                    report_path=self.report_file_path)

                if do_report_fcs_fields:
                    fc_fields = self._get_fc_fields(fc_name)
                    if fc_fields is not None:
                        _build_html.add_div_to_html_page(
                            fc_fields,
                            section_header_id=fc_name,
                            section_title=fc_name,
                            header_size='h3',
                            report_path=self.report_file_path)

                if do_report_fcs_subtypes and self.arcpy_found:
                    fc_subtypes = self._get_fc_subtypes(fc_name)
                    if fc_subtypes is not None:
                        if do_report_fcs_fields:
                            section_title = 'Subtypes'
                        else:
                            section_title = 'Subtypes ({0})'.format(fc_name)

                        _build_html.add_div_to_html_page(
                            fc_subtypes,
                            section_header_id=fc_name,
                            section_title=section_title,
                            header_size='h4',
                            report_path=self.report_file_path)

                if do_report_fcs_indexes and self.arcpy_found:
                    fc_indexes = self._get_fc_indexes(fc_name)
                    if fc_indexes is not None:
                        if do_report_fcs_fields:
                            section_title = 'Indexes'
                        else:
                            section_title = 'Indexes ({0})'.format(fc_name)
                        _build_html.add_div_to_html_page(
                            fc_indexes,
                            section_header_id=fc_name,
                            section_title=section_title,
                            header_size='h4',
                            report_path=self.report_file_path)
        return

    # ----------------------------------------------------------------------
    def _get_dataset_info(self, datasets):
        """Get dataset information ready to write into report."""
        df = self._map_boolean(
            pd.DataFrame.from_dict(datasets).sort_values(by='Name'))
        # sort dataset names case insensitive
        df = df.iloc[df.Name.str.lower().argsort()]
        return df

    # ----------------------------------------------------------------------
    def _get_dataset_fields(self, dataset_name, dataset_type):
        """Get fields information for single dataset."""
        if self.arcpy_found:
            if dataset_type == DATASET_TYPE_FC:
                dataset = FeatureClass(
                    os.path.join(self.gdb.path, dataset_name))
            elif dataset_type == DATASET_TYPE_TABLE:
                dataset = Table(os.path.join(self.gdb.path, dataset_name))
        else:
            if dataset_type == DATASET_TYPE_FC:
                dataset = FeatureClassOgr(self.gdb, dataset_name)
            elif dataset_type == DATASET_TYPE_TABLE:
                dataset = TableOgr(self.gdb, dataset_name)

        df_fields = self._map_boolean(
            pd.DataFrame.from_dict(dataset.get_fields()))

        # when there is a dataset with no fields
        if not df_fields.empty:
            df_fields['Default value'].fillna(value='', inplace=True)
        else:
            df_fields = None
        return df_fields

    # ----------------------------------------------------------------------
    def _get_dataset_subtypes(self, dataset_name, dataset_type):
        """Get subtypes information for single dataset."""
        if dataset_type == DATASET_TYPE_FC:
            dataset = FeatureClass(os.path.join(self.gdb.path, dataset_name))
        elif dataset_type == DATASET_TYPE_TABLE:
            dataset = Table(os.path.join(self.gdb.path, dataset_name))
        subtypes = dataset.get_subtypes()
        if subtypes:
            df_subtypes = self._map_boolean(pd.DataFrame.from_dict(subtypes))
            return df_subtypes

    # ----------------------------------------------------------------------
    def _get_dataset_indexes(self, dataset_name, dataset_type):
        """Get indexes information for single feature class."""
        if dataset_type == DATASET_TYPE_FC:
            dataset = FeatureClass(os.path.join(self.gdb.path, dataset_name))
        elif dataset_type == DATASET_TYPE_TABLE:
            dataset = Table(os.path.join(self.gdb.path, dataset_name))

        indexes = dataset.get_indexes()
        if indexes:
            df_indexes = (pd.DataFrame.from_dict(indexes).sort_values(
                by='Name'))
            return df_indexes

    # ----------------------------------------------------------------------
    def _get_fcs_info(self, fcs):
        """Get feature classes information ready to write into report."""
        return self._get_dataset_info(fcs)

    # ---------------------------------------------------------------------
    def _get_fc_fields(self, fc_name):
        """Get fields information for single feature class."""
        return self._get_dataset_fields(
            dataset_name=fc_name, dataset_type=DATASET_TYPE_FC)

    # ----------------------------------------------------------------------
    def _get_fc_subtypes(self, fc_name):
        """Get subtypes information for single feature class."""
        return self._get_dataset_subtypes(
            dataset_name=fc_name, dataset_type=DATASET_TYPE_FC)

    # ----------------------------------------------------------------------
    def _get_fc_indexes(self, fc_name):
        """Get indexes information for single feature class."""
        return self._get_dataset_indexes(
            dataset_name=fc_name, dataset_type=DATASET_TYPE_FC)

    # ----------------------------------------------------------------------
    def _get_tables_info(self, tables):
        """Get tables information ready to write into report."""
        return self._get_dataset_info(tables)

    # ----------------------------------------------------------------------
    def _get_table_fields(self, table_name):
        """Get fields information for single table."""
        return self._get_dataset_fields(
            dataset_name=table_name, dataset_type=DATASET_TYPE_TABLE)

    # ----------------------------------------------------------------------
    def _get_table_subtypes(self, table_name):
        """Get subtypes information for single table."""
        return self._get_dataset_subtypes(
            dataset_name=table_name, dataset_type=DATASET_TYPE_TABLE)

    # ----------------------------------------------------------------------
    def _get_table_indexes(self, table_name):
        """Get indexes information for single table."""
        return self._get_dataset_indexes(
            dataset_name=table_name, dataset_type=DATASET_TYPE_TABLE)

    # ----------------------------------------------------------------------
    def _write_license_text(self):
        """Add CC-BY license text in the end of the .html report."""
        _build_html.add_license_footer(report_path=self.report_file_path)
        return
