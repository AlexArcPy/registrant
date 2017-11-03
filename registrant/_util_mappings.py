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

GDB_REPLICA_PROPS = OrderedDict(
    [('name', 'Name'), ('owner', 'Owner'), ('role', 'Role'), ('type', 'Type'),
     ('version', 'Version'), ('hasConflicts', 'Has conflicts'), ('isParent', 'Is parent'),
     ('isSender', 'Is sender'), ('lastReceive', 'Last receive'), ('lastSend',
                                                                  'Last send')])

GDB_VERSION_PROPS = OrderedDict(
    [('name', 'Name'), ('parentVersionName', 'Parent version'), ('description',
                                                                 'Description'),
     ('access', 'Access'), ('ancestors', 'Ancestors'), ('children', 'Children'),
     ('isOwner', 'Is owner'), ('created', 'Created'), ('lastModified', 'Last modified')])

GDB_DOMAIN_PROPS = OrderedDict(
    [('owner', 'Owner'), ('name', 'Name'), ('domainType', 'Domain type'),
     ('description', 'Description'), ('codedValues', 'Coded values'), ('mergePolicy',
                                                                       'Merge policy'),
     ('splitPolicy', 'Split policy'), ('range', 'Range'), ('type', 'Data type')])

OGR_GDB_DOMAIN_PROPS = OrderedDict(
    [('Owner', 'Owner'), ('DomainName', 'Name'), ('domainType', 'Domain type'),
     ('Description', 'Description'), ('codedValues', 'Coded values'), ('MergePolicy',
                                                                       'Merge policy'),
     ('SplitPolicy', 'Split policy'), ('range', 'Range'), ('FieldType', 'Data type')])

#http://resources.esri.com/help/9.3/arcgisengine/arcobjects/esriGeodatabase/esriFieldType.htm
OGR_DOMAIN_PROPS_MAPPINGS = {
    'GPCodedValueDomain2': 'CodedValue',
    'GPRangeDomain2': 'Range',
    'esriMPTDefaultValue': 'DefaultValue',
    'esriSPTDefaultValue': 'DefaultValue',
    'esriSPTDuplicate': 'Duplicate',
    'esriMPTSumValues': 'SumValues',
    'esriMPTAreaWeighted': 'AreaWeighted',
    'esriSPTGeometryRatio': 'GeometryRatio',
    'esriFieldTypeInteger': 'Long Integer',
    'esriFieldTypeSmallInteger': 'Integer',
    'esriFieldTypeSingle': 'Float',
    'esriFieldTypeDouble': 'Double',
    'esriFieldTypeString': 'String',
    'esriFieldTypeDate': 'Date',
    'esriFieldTypeGeometry': 'Geometry',
    'esriFieldTypeBlob': 'Blob',
    'esriFieldTypeRaster': 'Raster',
    'esriFieldTypeGUID': 'GUID',
    'esriFieldTypeGlobalID': 'Global ID',
    'esriFieldTypeXML': 'XML'
}

OGR_GEOMETRY_TYPES = {
    0: 'Geometry',
    1: 'Point',
    2: 'Line',
    3: 'Polygon',
    4: 'MultiPoint',
    5: 'MultiLineString',
    6: 'MultiPolygon',
    100: 'No Geometry'
}

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
