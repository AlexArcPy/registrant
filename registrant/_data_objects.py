'''
Classes for data objects representing items stored in a geodatabase
'''
from collections import OrderedDict
import arcpy

from ._util_mappings import (GDB_TABLE_FIELD_PROPS, GDB_TABLE_INDEX_PROPS, GDB_FC_PROPS,
                             GDB_TABLE_SUBTYPE_PROPS)


########################################################################
class Describe(object):
    """Describe object returned from arcpy.Describe function"""

    def __init__(self, path):
        """Constructor"""
        self.path = path
        self._desc = arcpy.Describe(self.path)
        self.catalogPath = self._desc.catalogPath
        self.name = self._desc.name


########################################################################
class Dataset(Describe):
    """General dataset object stored in a geodatabase"""

    def __init__(self, path):
        """Constructor"""
        Describe.__init__(self, path)
        self.path = path
        self.datasetType = getattr(self._desc, 'datasetType', '')
        self.changeTracked = getattr(self._desc, 'changeTracked', '')


########################################################################
class Table(Dataset):
    """Table object stored in a geodatabase"""

    def __init__(self, path):
        """Constructor"""
        Dataset.__init__(self, path)
        self.aliasName = getattr(self._desc, 'aliasName', '')
        self.OIDFieldName = getattr(self._desc, 'OIDFieldName', '')
        self.globalIDFieldName = getattr(self._desc, 'globalIDFieldName', '')

    #----------------------------------------------------------------------
    def get_fields(self):
        """return geodatabase table fields props as ordered dicts"""
        fields = []
        for field_order, field in enumerate(arcpy.ListFields(self.path), 1):
            od = OrderedDict()
            od['UI order'] = field_order
            for k, v in GDB_TABLE_FIELD_PROPS.items():
                od[v] = getattr(field, k, '')
            fields.append(od)
        return fields

    #----------------------------------------------------------------------
    def get_subtypes(self):
        """return geodatabase table subtypes as ordered dicts"""
        subtypes = []
        subtypes_dict = arcpy.da.ListSubtypes(self.path)
        if any(subtypes_dict):
            for subtype_code, subtype_obj in subtypes_dict.items():
                od = OrderedDict()
                od['Code'] = subtype_code
                for k, v in GDB_TABLE_SUBTYPE_PROPS.items():
                    od[v] = subtype_obj.get(k, '')
                subtypes.append(od)
        return subtypes

    #----------------------------------------------------------------------
    def get_indexes(self):
        """return geodatabase table indexes as ordered dicts"""
        indexes = []
        for index in arcpy.ListIndexes(self.path):
            od = OrderedDict()
            for k, v in GDB_TABLE_INDEX_PROPS.items():
                if k == 'fields':
                    od[v] = ", ".join(sorted([f.name for f in getattr(index, k, '')]))
                else:
                    od[v] = getattr(index, k, '')
            indexes.append(od)
        return indexes

    #----------------------------------------------------------------------
    def _get_row_count(self):
        """return number of rows in geodatabase table"""
        return int(arcpy.GetCount_management(self.path).getOutput(0))


########################################################################
class FeatureClass(Table):
    """Feature class object stored in a geodatabase"""

    #----------------------------------------------------------------------
    def __init__(self, path):
        """Constructor"""
        Table.__init__(self, path)
        self.featureType = getattr(self._desc, 'featureType', '')
        self.shapeType = getattr(self._desc, 'shapeType', '')
        self.hasM = getattr(self._desc, 'hasM', '')
        self.hasZ = getattr(self._desc, 'hasZ', '')
        self.hasSpatialIndex = getattr(self._desc, 'hasSpatialIndex', '')
        self.shapeFieldName = getattr(self._desc, 'shapeFieldName', '')
        self.spatialReference = getattr(self._desc, 'spatialReference.name', '')
        self.areaFieldName = getattr(self._desc, 'areaFieldName', '')
        self.geometryStorage = getattr(self._desc, 'geometryStorage', '')
        self.lengthFieldName = getattr(self._desc, 'lengthFieldName', '')
