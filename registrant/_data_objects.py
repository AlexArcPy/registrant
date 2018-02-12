'''
Classes for data objects representing items stored in a geodatabase
'''
import os
import operator
from collections import OrderedDict

try:
    import arcpy
    arcpy_found = True
except:
    import ogr
    arcpy_found = False

from ._util_mappings import (GDB_TABLE_FIELD_PROPS, GDB_TABLE_INDEX_PROPS,
                             GDB_TABLE_SUBTYPE_PROPS, OGR_GEOMETRY_TYPES,
                             STRING_TO_BOOLEAN, BOOL_TO_YESNO_MAPPER)


########################################################################
class Describe(object):
    """Describe object returned from arcpy.Describe function"""

    def __init__(self, path):
        """Constructor"""
        self.path = path
        self._desc = arcpy.Describe(self.path)
        self.catalogPath = self._desc.catalogPath
        self.name = self._desc.name
        self.root = os.path.dirname(self.catalogPath)

        if hasattr(arcpy.Describe(self.root), 'datasetType'):  # 'FeatureDataset':
            self.wkspc = os.path.dirname(self.root)
        else:  #FeatureClass
            self.wkspc = self.root

        if 'Remote' in arcpy.Describe(self.wkspc).workspaceType:
            self.name = '.'.join(self.name.split('.')[1:])


########################################################################
class Dataset(Describe):
    """General dataset object stored in a geodatabase"""

    def __init__(self, path):
        """Constructor"""
        Describe.__init__(self, path)
        self.path = path
        self.changeTracked = getattr(self._desc, 'changeTracked', '')


########################################################################
class TableOgr(object):
    """Table object stored in a file geodatabase accessible through OGR.
    Initialized from a geodatabase path and table name"""

    #----------------------------------------------------------------------
    def __init__(self, gdb_path, table_name):
        """Constructor"""
        self.ds = ogr.Open(gdb_path, 0)
        self.layer = self.ds.GetLayerByName(table_name)
        self.aliasName = ''
        self.name = self.layer.GetName()
        self.OIDFieldName = self.layer.GetFIDColumn()
        self.globalIDFieldName = ''

    #----------------------------------------------------------------------
    def get_row_count(self):
        """return number of rows in geodatabase table"""
        return self.layer.GetFeatureCount()

    #----------------------------------------------------------------------
    def get_fields(self):
        """return geodatabase table fields props as ordered dicts"""
        fields = []
        for field_order, field in enumerate(self.layer.schema, 1):
            od = OrderedDict()
            od['UI order'] = field_order
            for k, v in GDB_TABLE_FIELD_PROPS.items():
                if k == 'type':
                    od[v] = field.GetTypeName()
                elif k == 'defaultValue':
                    od[v] = field.GetDefault()
                elif k == 'length':
                    od[v] = field.width
                elif k == 'isNullable':
                    od[v] = {0: False, 1: True}.get(field.IsNullable())
                else:
                    od[v] = getattr(field, k, '')
            fields.append(od)
        return fields


########################################################################
class Table(Dataset):
    """Table object stored in a geodatabase"""

    def __init__(self, path):
        """Constructor"""
        Dataset.__init__(self, path)
        self.aliasName = getattr(self._desc, 'aliasName', '')
        self.OIDFieldName = getattr(self._desc, 'OIDFieldName', '')
        self.globalIDFieldName = getattr(self._desc, 'globalIDFieldName', '')
        self.isVersioned = getattr(self._desc, 'isVersioned', False)
        self.isArchived = getattr(self._desc, 'isArchived', False)

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
    def get_attachments_count(self):
        """return number of attachments stored for a table/feature class"""
        rel_classes = [
            os.path.join(self.root, rc)
            for rc in getattr(self._desc, 'relationshipClassNames', [''])
        ]
        for rc in rel_classes:
            rc_desc = arcpy.Describe(rc)
            if rc_desc.isAttachmentRelationship:
                return int(
                    arcpy.GetCount_management(
                        os.path.join(self.root, rc_desc.destinationClassNames[0]))
                    .getOutput(0))

    #----------------------------------------------------------------------
    def get_row_count(self):
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
        self.spatialReference = operator.attrgetter('spatialReference.factoryCode')(
            self._desc)
        self.areaFieldName = getattr(self._desc, 'areaFieldName', '')
        self.geometryStorage = getattr(self._desc, 'geometryStorage', '')
        self.lengthFieldName = getattr(self._desc, 'lengthFieldName', '')


########################################################################
class FeatureClassOgr(TableOgr):
    """Feature class object stored in a geodatabase accessible through OGR.
    Initialized from a geodatabase path and feature class name"""

    #----------------------------------------------------------------------
    def __init__(self, gdb_path, fc_name):
        """Constructor"""
        TableOgr.__init__(self, gdb_path, fc_name)
        self.ds = ogr.Open(gdb_path, 0)
        self.layer = self.ds.GetLayerByName(fc_name)
        self.featureType = ''
        self.shapeType = OGR_GEOMETRY_TYPES.get(self.layer.GetGeomType(), 'Unknown')
        self.hasM = ''
        self.hasZ = ''
        self.hasSpatialIndex = ''
        self.shapeFieldName = self.layer.GetGeometryColumn()
        self.spatialReference = self.layer.GetSpatialRef().GetAttrValue(
            'projcs') if self.layer.GetSpatialRef().IsProjected(
            ) else self.layer.GetSpatialRef().GetAttrValue('geogcs')
        self.areaFieldName = ''
        self.geometryStorage = ''
        self.lengthFieldName = ''
