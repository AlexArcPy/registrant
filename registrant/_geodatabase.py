# -*- coding: UTF-8 -*-
"""Geodatabase class representing an Esri geodatabase."""
from __future__ import print_function
import os
import datetime
import tempfile
import pkgutil

from xml.etree import ElementTree
from collections import OrderedDict, defaultdict

arcpy_loader = pkgutil.find_loader('arcpy')
if arcpy_loader:
    import arcpy
    arcpy.env.overwriteOutput = True
    arcpy_found = True
else:
    arcpy_found = False
    import ogr
    import json

from registrant._data_objects import (
    Table,
    TableOgr,
    FeatureClass,
    FeatureClassOgr,
)
from registrant._util_mappings import (
    GDB_RELEASE,
    GDB_WKSPC_TYPE,
    GDB_PROPS,
    GDB_DOMAIN_PROPS,
    GDB_REPLICA_PROPS,
    GDB_VERSION_PROPS,
    GDB_TABLE_PROPS,
    GDB_FC_PROPS,
    OGR_GDB_DOMAIN_PROPS,
    OGR_DOMAIN_PROPS_MAPPINGS,
    GDB_RELATIONSHIP_CLASS_PROPS,
)
from registrant._config import ESRI_GDB_REPLICA_INF_DATE


########################################################################
class Geodatabase(object):
    """Geodatabase object."""

    def __init__(self, path):
        """Initialize `Geodatabase` object with basic properties."""
        self.arcpy_found = arcpy_found
        self.path = path
        self.ds = self._get_gdb_ds()
        self.metadata = self._get_ogr_metadata_full()
        self.release = self._get_release()
        self.wkspc_type = self._get_wkspc_type()
        self.is_gdb_enabled = True if self.release else False

    # ----------------------------------------------------------------------
    def get_pretty_props(self):
        """Get pretty properties as ordered dict."""
        od = OrderedDict()
        for k, v in GDB_PROPS.items():
            od[v] = self.__dict__[k]
        return od

    # ----------------------------------------------------------------------
    def get_replicas(self):
        """Get geodatabase replicas as ordered dict."""
        replicas_props = []
        if self.arcpy_found and self.is_gdb_enabled:
            # due to bug in arcpy, cannot use da.ListReplicas date properties
            # `lastSend` and `lastReceive` for file/personal geodatabases
            # because it crashes the Python process
            for replica in arcpy.da.ListReplicas(self.path):
                od = OrderedDict()
                for k, v in GDB_REPLICA_PROPS.items():
                    if (self.wkspc_type != 'Enterprise geodatabase') and (k in (
                            'lastReceive', 'lastSend')):
                        od[v] = 'Not available'
                    else:
                        prop_value = getattr(replica, k, '')
                        if isinstance(
                                prop_value, datetime.datetime
                        ) and prop_value.year == ESRI_GDB_REPLICA_INF_DATE:
                            od[v] = ''
                        else:
                            if prop_value is not None:
                                od[v] = prop_value
                            else:
                                od[v] = ''

                # need at least Standard license of ArcGIS Desktop
                # to run this GP tool
                if arcpy.ProductInfo() in ('ArcEditor', 'ArcInfo'):
                    if not hasattr(arcpy, 'ExportReplicaSchema_management'):
                        # ArcGIS Pro at 1.2 did not have this GP tool
                        return
                    replica_schema_xml = os.path.join(tempfile.gettempdir(),
                                                      'ReplicaSchema.xml')
                    arcpy.ExportReplicaSchema_management(
                        in_geodatabase=self.path,
                        output_replica_schema_file=replica_schema_xml,
                        in_replica=replica.name,
                    )
                    with open(replica_schema_xml, 'r') as fh:
                        schema_xml_data = fh.readlines()[0]
                    try:
                        os.remove(replica_schema_xml)
                    except Exception:
                        pass
                    xml = ElementTree.fromstring(schema_xml_data)
                    od['Creation date'] = xml.find('WorkspaceDefinition').find(
                        'GPReplica').find('CreationDate').text.replace(
                            'T', ' ')

                    datasets = xml.find('WorkspaceDefinition').find(
                        'GPReplica').find('GPReplicaDescription').find(
                            'GPReplicaDatasets')
                    datasets_pairs = sorted(
                        ((d.find('DatasetName').text, d.find('TargetName').text)
                         for d in datasets.getchildren()),
                        key=lambda pair: pair[0].lower())

                    od['Datasets'] = '<br>'.join([
                        '{0} -> {1}'.format(i[0], i[1]) for i in datasets_pairs
                    ])

                replicas_props.append(od)
        return replicas_props

    # ----------------------------------------------------------------------
    def get_versions(self):
        """Get ArcSDE geodatabase version objects as ordered dict."""
        versions_props = []
        if (self.arcpy_found and self.wkspc_type == 'Enterprise geodatabase'
                and self.is_gdb_enabled):
            for version in arcpy.da.ListVersions(self.path):
                od = OrderedDict()
                for k, v in GDB_VERSION_PROPS.items():
                    if k in ('ancestors', 'children'):
                        prop_value = ', '.join(
                            [s.name for s in getattr(version, k) if s])
                        od[v] = prop_value
                    else:
                        prop_value = getattr(version, k, '')
                        if prop_value is not None:
                            od[v] = prop_value
                        else:
                            od[v] = ''
                versions_props.append(od)

        return versions_props

    # ----------------------------------------------------------------------
    def get_relationship_classes(self):
        """Get geodatabase relationship classes objects as ordered dict."""
        rc_props = []
        if self.arcpy_found and self.is_gdb_enabled:
            for gdb_path, _fd, rcs in arcpy.da.Walk(
                    self.path, datatype='RelationshipClass'):
                for rc in rcs:
                    rc_desc = arcpy.Describe(os.path.join(gdb_path, rc))

                    od = OrderedDict()
                    od['Name'] = rc
                    if os.path.basename(gdb_path) != os.path.basename(
                            self.path):
                        # rc is inside a feature dataset
                        od['Feature dataset'] = os.path.basename(gdb_path)
                    else:
                        od['Feature dataset'] = ''

                    for k, v in GDB_RELATIONSHIP_CLASS_PROPS.items():
                        prop_value = getattr(rc_desc, k, '')
                        if prop_value or isinstance(prop_value, bool):
                            if isinstance(prop_value, list):
                                if isinstance(prop_value[0], tuple):
                                    od[v] = prop_value
                                else:
                                    od[v] = ', '.join(prop_value)
                            else:
                                od[v] = prop_value
                        else:
                            od[v] = ''
                    rc_props.append(od)

        return rc_props

    # ----------------------------------------------------------------------
    def get_domains(self):
        """Get geodatabase domains as ordered dict."""
        domains_props = []
        if self.is_gdb_enabled:
            if self.arcpy_found:
                for domain in arcpy.da.ListDomains(self.path):
                    od = OrderedDict()
                    for k, v in GDB_DOMAIN_PROPS.items():
                        od[v] = getattr(domain, k, '')
                    domains_props.append(od)

            else:
                gdb_domains = self._ogr_get_domains()
                for domain_type, domains in gdb_domains.items():
                    for domain in domains:
                        od = OrderedDict()
                        for k, v in OGR_GDB_DOMAIN_PROPS.items():
                            if k == 'domainType':
                                od[v] = OGR_DOMAIN_PROPS_MAPPINGS[domain_type]

                            # describing domain range
                            elif k == 'range':
                                try:
                                    od[v] = (
                                        float(domain.find('MinValue').text),
                                        float(domain.find('MaxValue').text),
                                    )
                                except AttributeError:
                                    od[v] = ''

                            # describing domain coded values
                            elif k == 'codedValues':
                                try:
                                    cvs = domain.find('CodedValues').findall(
                                        'CodedValue')
                                    od[v] = {
                                        cv.find('Code').text:
                                        cv.find('Name').text
                                        for cv in cvs
                                    }
                                except AttributeError:
                                    od[v] = ''
                            else:
                                try:
                                    if domain.find(k).text:
                                        od[v] = OGR_DOMAIN_PROPS_MAPPINGS.get(
                                            domain.find(k).text,
                                            domain.find(k).text)
                                    else:
                                        od[v] = ''
                                except AttributeError:
                                    od[v] = ''
                        domains_props.append(od)

        return domains_props

    # ----------------------------------------------------------------------
    def get_tables(self):
        """Get geodatabase tables as `Table` class instances."""
        tables = []
        if self.arcpy_found:
            arcpy.env.workspace = self.path
            for tbl in arcpy.ListTables():
                try:
                    tbl_instance = Table(arcpy.Describe(tbl).catalogPath)
                    if tbl_instance.OIDFieldName == 'ATTACHMENTID':
                        continue
                    od = OrderedDict()
                    for k, v in GDB_TABLE_PROPS.items():
                        od[v] = getattr(tbl_instance, k, '')

                    # custom props
                    od['Row count'] = tbl_instance.get_row_count()
                    num_attachments = tbl_instance.get_attachments_count()

                    if num_attachments is not None:
                        od['Attachments enabled'] = True
                        od['Attachments count'] = num_attachments
                    else:
                        od['Attachments enabled'] = False
                        od['Attachments count'] = ''

                    tables.append(od)
                except Exception as e:
                    print('Error. Could not read table', tbl, '. Reason: ', e)

        else:
            table_names = [
                self.ds.GetLayerByIndex(i).GetName()
                for i in range(0, self.ds.GetLayerCount())
                if not self.ds.GetLayerByIndex(i).GetGeometryColumn()
            ]
            for table_name in table_names:
                try:
                    tbl_instance = TableOgr(self, table_name)
                    od = OrderedDict()
                    for k, v in GDB_TABLE_PROPS.items():
                        od[v] = getattr(tbl_instance, k, '')

                    # custom props
                    od['Row count'] = tbl_instance.get_row_count()
                    tables.append(od)
                except Exception as e:
                    print(e)
        return tables

    # ----------------------------------------------------------------------
    def get_feature_classes(self):
        """Get geodatabase feature classes as ordered dicts."""
        fcs = []
        if self.arcpy_found:
            arcpy.env.workspace = self.path
            # iterate feature classes within feature datasets
            fds = [fd for fd in arcpy.ListDatasets(feature_type='feature')]
            if fds:
                for fd in fds:
                    arcpy.env.workspace = os.path.join(self.path, fd)
                    for fc in arcpy.ListFeatureClasses():
                        od = self._get_fc_props(fc)
                        od['Feature dataset'] = fd
                        fcs.append(od)

            # iterate feature classes in the geodatabase root
            arcpy.env.workspace = self.path
            for fc in arcpy.ListFeatureClasses():
                od = self._get_fc_props(fc)
                fcs.append(od)

        else:
            ds = ogr.Open(self.path, 0)
            fcs_names = [
                ds.GetLayerByIndex(i).GetName()
                for i in range(0, ds.GetLayerCount())
                if ds.GetLayerByIndex(i).GetGeometryColumn()
            ]
            for fc_name in fcs_names:
                try:
                    fc_instance = FeatureClassOgr(self, fc_name)
                    od = OrderedDict()
                    for k, v in GDB_FC_PROPS.items():
                        od[v] = getattr(fc_instance, k, '')
                    # custom props
                    od['Row count'] = fc_instance.get_row_count()
                    fcs.append(od)
                except Exception as e:
                    print(e)
        return fcs

    # ----------------------------------------------------------------------
    def _get_gdb_ds(self):
        """Get the geodatabase OGR data source object."""
        if not self.arcpy_found:
            return ogr.Open(self.path, 0)

    # ----------------------------------------------------------------------
    def _get_ogr_metadata_full(self):
        """Get the full geodatabase metadata as a list of xml objects."""
        metadata = None
        if not self.arcpy_found:
            res = self.ds.ExecuteSQL('select * from GDB_Items')
            res.CommitTransaction()
            metadata = []
            for _i in range(0, res.GetFeatureCount()):
                item = json.loads(res.GetNextFeature().
                                  ExportToJson())['properties']['Definition']
                if item:
                    xml = ElementTree.fromstring(item)
                    metadata.append(xml)
        return metadata

    # ----------------------------------------------------------------------
    def _ogr_get_geodatabase(self):
        """Return an xml object with the metadata of geodatabase repository."""
        for item in self.metadata:
            if item.tag == 'DEWorkspace':
                return item

        # ----------------------------------------------------------------------
    def _ogr_get_domains(self):
        """Get an xml object with the geodatase domains metadata."""
        domains = defaultdict(list)
        for item in self.metadata:
            if item.tag in ('GPCodedValueDomain2', 'GPRangeDomain2'):
                domains[item.tag].append(item)
        return domains

    # ----------------------------------------------------------------------
    @staticmethod
    def _get_fc_props(fc):
        """Get single geodatabase feature class props as ordered dict."""
        fc_instance = FeatureClass(arcpy.Describe(fc).catalogPath)
        od = OrderedDict()

        passed_first_column = False
        for k, v in GDB_FC_PROPS.items():
            od[v] = getattr(fc_instance, k, '')
            if not passed_first_column:
                od['Feature dataset'] = ''
                passed_first_column = True
        # custom props
        od['Row count'] = fc_instance.get_row_count()
        num_attachments = fc_instance.get_attachments_count()

        if num_attachments is not None:
            od['Attachments enabled'] = True
            od['Attachments count'] = num_attachments
        else:
            od['Attachments enabled'] = False
            od['Attachments count'] = ''

        return od

    # ----------------------------------------------------------------------
    def _get_release(self):
        """Get geodatabase release version."""
        if self.arcpy_found:
            return GDB_RELEASE.get(arcpy.Describe(self.path).release, '')
        else:
            xml = self._ogr_get_geodatabase()
            return GDB_RELEASE.get(
                ','.join([
                    xml.find('MajorVersion').text,
                    xml.find('MinorVersion').text,
                    xml.find('BugfixVersion').text,
                ]), '')

    # ----------------------------------------------------------------------
    def _get_wkspc_type(self):
        """Get geodatabase workspace type."""
        if self.arcpy_found:
            return [
                value for key, value in GDB_WKSPC_TYPE.items() if key.lower() in
                arcpy.Describe(self.path).workspaceFactoryProgID.lower()
            ][0]
        else:
            return 'File geodatabase'
