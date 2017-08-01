'''
Geodatabase class representing an Esri geodatabase
'''
import os
from collections import OrderedDict
import arcpy

from ._data_objects import Table, FeatureClass
from ._util_mappings import (GDB_RELEASE, GDB_WKSPC_TYPE, GDB_PROPS, GDB_DOMAIN_PROPS,
                             GDB_TABLE_PROPS, GDB_FC_PROPS)


########################################################################
class Geodatabase(object):
    """Geodatabase object"""

    def __init__(self, path):
        """Constructor"""
        self.path = path
        self.release = self._get_release()
        self.wkspc_type = self._get_wkspc_type()

    #----------------------------------------------------------------------
    def get_pretty_props(self):
        """get pretty properties as ordered dict"""
        od = OrderedDict()
        for k, v in GDB_PROPS.items():
            od[v] = self.__dict__[k]
        return od

    #----------------------------------------------------------------------
    def _get_release(self):
        """return geodatabase release version"""
        return GDB_RELEASE[arcpy.Describe(self.path).release]

    #----------------------------------------------------------------------
    def _get_wkspc_type(self):
        """return geodatabase workspace type - personal, file, SDE"""
        return [
            value for key, value in GDB_WKSPC_TYPE.items()
            if key.lower() in arcpy.Describe(self.path).workspaceFactoryProgID.lower()
        ][0]

    #----------------------------------------------------------------------
    def get_domains(self):
        """return geodatabase domains as ordered dict"""
        domains = []
        for domain in arcpy.da.ListDomains(self.path):
            od = OrderedDict()
            for k, v in GDB_DOMAIN_PROPS.items():
                od[v] = getattr(domain, k, '')
            domains.append(od)
        return domains

    #----------------------------------------------------------------------
    def get_tables(self):
        """return geodatabase tables as Table class instances"""
        tables = []
        arcpy.env.workspace = self.path
        for tbl in arcpy.ListTables():
            tbl_instance = Table(arcpy.Describe(tbl).catalogPath)
            od = OrderedDict()
            for k, v in GDB_TABLE_PROPS.items():
                od[v] = getattr(tbl_instance, k, '')

            #custom props
            od['Row count'] = tbl_instance._get_row_count()
            tables.append(od)
        return tables

    #----------------------------------------------------------------------
    def get_feature_classes(self):
        """return geodatabase feature classes as ordered dicts"""
        fcs = []

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
                    od['Row count'] = fc_instance._get_row_count()
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
            od['Row count'] = fc_instance._get_row_count()
            od['Feature dataset'] = ''
            fcs.append(od)
        return fcs
