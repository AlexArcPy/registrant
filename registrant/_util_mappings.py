'''
Mappings for arcpy.Describe and dataset properties to human readable values
that are used for columns in tables in the HTML report file
'''
from collections import OrderedDict

GDB_RELEASE = {
    '2,2,0': 'ArcGIS Desktop 9.2',
    '2,3,0': 'ArcGIS Desktop 9.3, 9.3.1',
    '3,0,0': 'ArcGIS Desktop 10.0+, ArcGIS Pro 1.2+'
}

#in_memory wkspc is not supported
GDB_WKSPC_TYPE = {
    'esriDataSourcesGDB.FileGDBWorkspaceFactory': 'File geodatabase',
    'esriDataSourcesGDB.AccessWorkspaceFactory': 'Personal geodatabase',
    'esriDataSourcesGDB.SdeWorkspaceFactory': 'Enterprise geodatabase'
}

GDB_PROPS = OrderedDict([('path', 'Path'), ('release', 'Release'), ('wkspc_type',
                                                                    'Workspace type')])

GDB_DOMAIN_PROPS = OrderedDict(
    [('owner', 'Owner'), ('name', 'Name'), ('domainType', 'Domain type'),
     ('description', 'Description'), ('codedValues', 'Coded values'), ('mergePolicy',
                                                                       'Merge policy'),
     ('splitPolicy', 'Split policy'), ('range', 'Range'), ('type', 'Data type')])

GDB_TABLE_PROPS = OrderedDict(
    [('name', 'Name'), ('aliasName', 'Alias'), ('OIDFieldName', 'ObjectID'),
     ('globalIDFieldName', 'GlobalID'), ('changeTracked', 'Is change tracked')])

GDB_TABLE_FIELD_PROPS = OrderedDict(
    [('name', 'Name'), ('type', 'Type'), ('aliasName', 'Alias'),
     ('baseName', 'Base name'), ('defaultValue', 'Default value'), ('length', 'Length'),
     ('domain', 'Domain'), ('editable', 'Is editable'), ('isNullable', 'Is nullable'),
     ('precision', 'Precision'), ('required', 'Required'), ('scale', 'Scale')])

GDB_TABLE_INDEX_PROPS = OrderedDict([('name', 'Name'), ('fields', 'Fields'),
                                     ('isAscending', 'Is ascending'), ('isUnique',
                                                                       'Is unique')])

GDB_TABLE_SUBTYPE_PROPS = OrderedDict([('Name', 'Name'), ('SubtypeField', 'SubtypeField'),
                                       ('Default', 'Default')])

GDB_FC_PROPS = OrderedDict(
    [('name', 'Name'), ('featureType', 'Feature type'), ('shapeType', 'Shape type'),
     ('hasM', 'Has M values'), ('hasZ', 'Has Z values'), ('hasSpatialIndex',
                                                          'Has spatial index'),
     ('shapeFieldName', 'Shape field name'), ('spatialReference', 'Spatial reference'),
     ('areaFieldName', 'Area field'), ('lengthFieldName',
                                       'Length field'), ('geometryStorage',
                                                         'Geometry storage')])
