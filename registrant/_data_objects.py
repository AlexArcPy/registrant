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
    def __init__(self, gdb, table_name, object_type='DETableInfo'):
        """Constructor"""
        self.gdb = gdb
        self.table_metadata = [
            item for item in self.gdb.metadata
            if item.tag == object_type and item.find('Name').text == table_name
        ][0]
        self.table_fields_metadata = self.table_metadata.find('GPFieldInfoExs').findall(
            'GPFieldInfoEx')

        self.layer = self.gdb.ds.GetLayerByName(table_name)
        self.name = self.layer.GetName()
        self.aliasName = self._ogr_get_table_property('AliasName')
        self.OIDFieldName = self.layer.GetFIDColumn()
        self.globalIDFieldName = self._ogr_get_table_property('GlobalIDFieldName')
        self.changeTracked = ''

    #----------------------------------------------------------------------
    def get_row_count(self):
        """return number of rows in geodatabase table"""
        return self.layer.GetFeatureCount()

    #----------------------------------------------------------------------
    def get_fields(self):
        """return geodatabase table fields props as ordered dicts"""
        fields = []
        for field_order, field in enumerate(self.layer.schema, 1):
            field_name = field.GetName()
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
                elif k == 'aliasName':
                    od[v] = self._ogr_get_table_field_property(field_name, 'AliasName')
                elif k == 'editable':
                    od[v] = self._ogr_get_table_field_property(field_name, 'Editable',
                                                               True)
                elif k == 'required':
                    od[v] = self._ogr_get_table_field_property(field_name, 'Required',
                                                               True)
                elif k == 'domain':
                    od[v] = self._ogr_get_table_field_property(field_name, 'DomainName')
                else:
                    od[v] = getattr(field, k, '')
            fields.append(od)
        return fields

    #----------------------------------------------------------------------
    def _ogr_get_table_field_property(self, field_name, field_prop_name, is_bool=False):
        """return property of a geodatabase table field"""
        # not all fields are being retrieved from GDB_Items and therefore cannot get
        # all the properties (the XML returned is incomplete for certain geodatabases)
        try:
            field = [
                field for field in self.table_fields_metadata
                if field.find('Name').text == field_name
                ][0]
        except:
            return ''
        item = field.find(field_prop_name)
        if item is not None:
            value = item.text
            return BOOL_TO_YESNO_MAPPER[STRING_TO_BOOLEAN[value]] if is_bool else value
        return ''

    #----------------------------------------------------------------------
    def _ogr_get_table_property(self, prop_name, is_bool=False):
        """return property of a geodatabase table"""
        value = self.table_metadata.find(prop_name).text
        if is_bool:
            return BOOL_TO_YESNO_MAPPER[STRING_TO_BOOLEAN[value]]
        return value if value else ''


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
    def __init__(self, gdb, fc_name):
        """Constructor"""
        TableOgr.__init__(self, gdb, fc_name, object_type='DEFeatureClassInfo')

        self.aliasName = self._ogr_get_table_property('AliasName')
        self.OIDFieldName = self.layer.GetFIDColumn()
        self.globalIDFieldName = self._ogr_get_table_property('GlobalIDFieldName')
        self.featureType = self._ogr_get_table_property('FeatureType').replace(
            'esriFT', '')
        self.shapeType = OGR_GEOMETRY_TYPES.get(self.layer.GetGeomType(), 'Unknown')
        self.hasM = self._ogr_get_table_property('HasM', True)
        self.hasZ = self._ogr_get_table_property('HasZ', True)
        self.hasSpatialIndex = self._ogr_get_table_property('HasSpatialIndex', True)
        self.shapeFieldName = self.layer.GetGeometryColumn()
        self.spatialReference = self.layer.GetSpatialRef().GetAttrValue(
            'projcs') if self.layer.GetSpatialRef().IsProjected(
            ) else self.layer.GetSpatialRef().GetAttrValue('geogcs')
        self.areaFieldName = self._ogr_get_table_property('AreaFieldName')
        self.geometryStorage = ''
        self.lengthFieldName = self._ogr_get_table_property('LengthFieldName')
