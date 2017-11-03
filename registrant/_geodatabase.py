'''
Geodatabase class representing an Esri geodatabase
'''
from __future__ import print_function
import os
import datetime
import tempfile
import xml.etree.ElementTree as ET
from collections import OrderedDict, defaultdict

try:
    import arcpy
    arcpy_found = True
    arcpy.env.overwriteOutput = True
except:
    arcpy_found = False
    import ogr
    import json

from ._data_objects import Table, TableOgr, FeatureClass, FeatureClassOgr
from ._util_mappings import (GDB_RELEASE, GDB_WKSPC_TYPE, GDB_PROPS, GDB_DOMAIN_PROPS,
                             GDB_REPLICA_PROPS, GDB_VERSION_PROPS,
                             GDB_TABLE_PROPS, GDB_FC_PROPS,
                             OGR_GDB_DOMAIN_PROPS, OGR_DOMAIN_PROPS_MAPPINGS)


########################################################################
class Geodatabase(object):
    """Geodatabase object"""

    def __init__(self, path):
        """Constructor"""
        self.path = path
        self.release = self._get_release()
        self.wkspc_type = self._get_wkspc_type()
        self.is_gdb_enabled = True if self.release else False

    #----------------------------------------------------------------------
    def get_pretty_props(self):
        """get pretty properties as ordered dict"""
        od = OrderedDict()
        for k, v in GDB_PROPS.items():
            od[v] = self.__dict__[k]
        return od

    #----------------------------------------------------------------------
    def get_replicas(self):
        """return geodatabase replicas as ordered dict"""
        replicas_props = []
        if arcpy_found and self.is_gdb_enabled:
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
                        if isinstance(prop_value,
                                      datetime.datetime) and prop_value.year == 1899:
                            od[v] = ''
                        else:
                            if prop_value != None:
                                od[v] = prop_value
                            else:
                                od[v] = ''

                # need at least Standard license of ArcGIS Desktop to run this GP tool
                if arcpy.ProductInfo() in ('ArcEditor', 'ArcInfo'):
                    replica_schema_xml = os.path.join(tempfile.gettempdir(),
                                                      'ReplicaSchema.xml')
                    arcpy.ExportReplicaSchema_management(self.path, replica_schema_xml,
                                                         replica.name)
                    with open(replica_schema_xml, 'r') as f:
                        data = f.readlines()[0]
                    try:
                        os.remove(replica_schema_xml)
                    except:
                        pass
                    xml = ET.fromstring(data)
                    od['Creation date'] = xml.find('WorkspaceDefinition').find(
                        'GPReplica').find('CreationDate').text.replace('T', ' ')

                    datasets = xml.find('WorkspaceDefinition').find('GPReplica').find(
                        'GPReplicaDescription').find('GPReplicaDatasets')
                    datasets_pairs = sorted(
                        [(d.find('DatasetName').text, d.find('TargetName').text)
                         for d in datasets.getchildren()],
                        key=lambda pair: pair[0].lower())

                    od['Datasets'] = '<br>'.join(
                        ['{} -> {}'.format(i[0], i[1]) for i in datasets_pairs])

                replicas_props.append(od)
        return replicas_props

    #----------------------------------------------------------------------
    def get_versions(self):
        """return SDE geodatabase version objects as ordered dict"""
        versions_props = []
        if arcpy_found and self.wkspc_type == 'Enterprise geodatabase' and self.is_gdb_enabled:
            for version in arcpy.da.ListVersions(self.path):
                od = OrderedDict()
                for k, v in GDB_VERSION_PROPS.items():
                    if k in ('ancestors', 'children'):
                        prop_value = ', '.join([s.name for s in getattr(version, k) if s])
                    else:
                        prop_value = getattr(version, k, '')
                        if prop_value != None:
                            od[v] = prop_value
                        else:
                            od[v] = ''
                versions_props.append(od)

        return versions_props

    #----------------------------------------------------------------------
    def get_domains(self):
        """return geodatabase domains as ordered dict"""
        domains_props = []
        if self.is_gdb_enabled:
            if arcpy_found:
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

                            #describing domain range
                            elif k == 'range':
                                try:
                                    od[v] = (float(domain.find('MinValue').text),
                                             float(domain.find('MaxValue').text))
                                except AttributeError:
                                    od[v] = ''

                            #describing domain coded values
                            elif k == 'codedValues':
                                try:
                                    cvs = domain.find('CodedValues').findall('CodedValue')
                                    od[v] = {
                                        cv.find('Code').text: cv.find('Name').text
                                        for cv in cvs
                                    }
                                except AttributeError:
                                    od[v] = ''
                            else:
                                try:
                                    if domain.find(k).text:
                                        od[v] = OGR_DOMAIN_PROPS_MAPPINGS.get(
                                            domain.find(k).text, domain.find(k).text)
                                    else:
                                        od[v] = ''
                                except AttributeError:
                                    od[v] = ''
                        domains_props.append(od)

        return domains_props

    #----------------------------------------------------------------------
    def get_tables(self):
        """return geodatabase tables as Table class instances"""
        tables = []
        if arcpy_found:
            arcpy.env.workspace = self.path
            for tbl in arcpy.ListTables():
                try:
                    tbl_instance = Table(arcpy.Describe(tbl).catalogPath)
                    od = OrderedDict()
                    for k, v in GDB_TABLE_PROPS.items():
                        od[v] = getattr(tbl_instance, k, '')

                    #custom props
                    od['Row count'] = tbl_instance.get_row_count()
                    tables.append(od)
                except Exception as e:
                    print("Error. Could not read table", tbl, ". Reason: ", e)

        else:
            ds = ogr.Open(self.path, 0)
            table_names = [
                ds.GetLayerByIndex(i).GetName() for i in range(0, ds.GetLayerCount())
                if not ds.GetLayerByIndex(i).GetGeometryColumn()
            ]
            for table_name in table_names:
                try:
                    tbl_instance = TableOgr(self.path, table_name)
                    od = OrderedDict()
                    for k, v in GDB_TABLE_PROPS.items():
                        od[v] = getattr(tbl_instance, k, '')

                    #custom props
                    od['Row count'] = tbl_instance.get_row_count()
                    tables.append(od)
                except Exception as e:
                    print(e)
        return tables

    #----------------------------------------------------------------------
    def get_feature_classes(self):
        """return geodatabase feature classes as ordered dicts"""
        fcs = []
        if arcpy_found:
            arcpy.env.workspace = self.path
            #iterate feature classes within feature datasets
            fds = [fd for fd in arcpy.ListDatasets(feature_type='feature')]
            if fds:
                for fd in fds:
                    arcpy.env.workspace = os.path.join(self.path, fd)
                    for fc in arcpy.ListFeatureClasses():
                        fc_instance = FeatureClass(arcpy.Describe(fc).catalogPath)
                        od = OrderedDict()
                        for k, v in GDB_FC_PROPS.items():
                            od[v] = getattr(fc_instance, k, '')
                        #custom props
                        od['Row count'] = fc_instance.get_row_count()
                        od['Feature dataset'] = fd
                        fcs.append(od)

            #iterate feature classes in the geodatabase root
            arcpy.env.workspace = self.path
            for fc in arcpy.ListFeatureClasses():
                fc_instance = FeatureClass(arcpy.Describe(fc).catalogPath)
                od = OrderedDict()
                for k, v in GDB_FC_PROPS.items():
                    od[v] = getattr(fc_instance, k, '')
                #custom props
                od['Row count'] = fc_instance.get_row_count()
                od['Feature dataset'] = ''
                fcs.append(od)

        else:
            ds = ogr.Open(self.path, 0)
            fcs_names = [
                ds.GetLayerByIndex(i).GetName() for i in range(0, ds.GetLayerCount())
                if ds.GetLayerByIndex(i).GetGeometryColumn()
            ]
            for fc_name in fcs_names:
                try:
                    fc_instance = FeatureClassOgr(self.path, fc_name)
                    od = OrderedDict()
                    for k, v in GDB_FC_PROPS.items():
                        od[v] = getattr(fc_instance, k, '')
                    #custom props
                    od['Row count'] = fc_instance.get_row_count()
                    fcs.append(od)
                except Exception as e:
                    print(e)
        return fcs

    #----------------------------------------------------------------------
    def _ogr_get_gdb_metadata(self):
        """return an xml object with the geodatabase metadata"""
        ds = ogr.Open(self.path, 0)
        res = ds.ExecuteSQL('select * from GDB_Items')
        res.CommitTransaction()

        for i in xrange(0, res.GetFeatureCount()):
            item = json.loads(
                res.GetNextFeature().ExportToJson())['properties']['Definition']
            if item:
                xml = ET.fromstring(item)
                if xml.tag == 'DEWorkspace':
                    break
        del ds
        return xml

    #----------------------------------------------------------------------
    def _ogr_get_domains(self):
        """return an xml object with the geodatase domains metadata"""
        ds = ogr.Open(self.path, 0)
        res = ds.ExecuteSQL('select * from GDB_Items')
        res.CommitTransaction()

        domains = defaultdict(list)
        for i in xrange(0, res.GetFeatureCount()):
            item = json.loads(
                res.GetNextFeature().ExportToJson())['properties']['Definition']
            if item:
                xml = ET.fromstring(item)
                if xml.tag in ('GPCodedValueDomain2', 'GPRangeDomain2'):
                    domains[xml.tag].append(xml)
        del ds
        return domains

    #----------------------------------------------------------------------
    def _get_release(self):
        """return geodatabase release version"""
        if arcpy_found:
            return GDB_RELEASE.get(arcpy.Describe(self.path).release, '')
        else:
            xml = self._ogr_get_gdb_metadata()
            return GDB_RELEASE.get(','.join([
                xml.find('MajorVersion').text,
                xml.find('MinorVersion').text,
                xml.find('BugfixVersion').text
            ]), '')

    #----------------------------------------------------------------------
    def _get_wkspc_type(self):
        """return geodatabase workspace type - personal, file, SDE"""
        if arcpy_found:
            return [
                value for key, value in GDB_WKSPC_TYPE.items()
                if key.lower() in arcpy.Describe(
                    self.path).workspaceFactoryProgID.lower()
            ][0]
        else:
            return 'File geodatabase'
