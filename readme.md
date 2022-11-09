[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/AlexArcPy/registrant.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/AlexArcPy/registrant/context:python)

### General

This Python package is used for generating HTML reports about the contents of Esri geodatabases. It supports working with Esri personal/file geodatabases as well as RDBMS enterprise geodatabases (however, it also works with RDBMS databases that were not geodatabase enabled).

Example of report:

![Sample report](https://user-images.githubusercontent.com/7373268/28848206-5eef081e-7712-11e7-90a9-ea882268e928.png)

### Usage guidelines

In order to use this tool, you would need to have *either*:

* ArcGIS Desktop, ArcGIS Server or ArcGIS Pro installed (for `arcpy` package). You will be able to run the tool with ArcGIS Desktop/Server Python 2.7 as well as ArcGIS Pro Python 3.5+.
* GDAL (for `ogr` package). This means you will be able to run the tool without having any Esri software installed. However, only file geodatabases are supported for reporting with GDAL.

The code written is a valid Python 2 as well as Python 3 code, so using the tool in both environments is supported. You will need `pandas` and `beautifulSoup` Python packages which can be installed from `pip` if you are ArcGIS Desktop/Server user or using `conda` if you are ArcGIS Pro or Anaconda user. See [Installing Packages](https://packaging.python.org/tutorials/installing-packages/) in the Python documentation (for ArcGIS Desktop users) and [Install a package](https://conda.io/docs/using/pkgs.html#install-a-package) in the Conda documentation (for ArcGIS Pro and Anaconda users) to get help.

If the package is able to import `arcpy`, then it will use `arcpy` because it provides a more complete view into your geodatabase. The most time is spent in `arcpy` describe and listing functions iterating the datasets and pulling all the relevant information.

If `arcpy` is not found in your system, then the package will try to import `ogr`. The [`OpenFileGDB`](http://www.gdal.org/drv_openfilegdb.html) driver is used to access the key information about the geodatabase and its items. Please keep in mind that when using `ogr`, no information about tables/feature classes indexes and subtypes will be reported and many of the ArcGIS specific properties won't be shown either.

### Output report

After HTML file is generated, you can open it in a web browser. The HTML file uses resources in other folders located in the `app` folder which means you cannot move the HTML file somewhere else without copying its dependency folders. If you would like to move the report somewhere else, you need to copy the whole `app` folder. While having the HTML file shown in a web browser, you can use the links to navigate throughout the page. Keep in mind that since navigation is built using the headers id, you can use the web browser's tools for navigating forward and back as you navigate between different sections of the report.

### Requirements

* arcpy | GDAL 2.1.0
* Python 2.7 | 3.5
* pandas >= 0.20.1
* beautifulsoup4 >= 4.6.0

### Installation

`python setup.py install`

Please keep in mind that `arcpy` and `GDAL` won't be installed when installing the package. The `arcpy` package can be obtained by installing ArcGIS software and GDAL can be installed in many ways, for instance, using [Anaconda Navigator](https://docs.continuum.io/anaconda/navigator/) or using a [binary wheel](http://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal).

### Getting started

When creating a `Reporter` class, you'd need to supply path to your geodatabase and output folder for report data files. Then, calling `Reporter.gdb2html()` would let you optionally specify what information you would like to include into your output HTML report. Depending on the geodatabase size, number of chosen items to include in the report as well as the available system resources, it might take some minutes to run.

The package has convenience functions which can be used to specify what exactly do you want to generate report for. The `gdb2html` function will create a complete report. This function provides you with fine-grained control over what information will be included in the report, so you can use it providing booleans arguments (for instance, you may want to get only list of tables and feature classes without reporting their fields, subtypes, and indexes). However, you can specify if you want to report only domains, only tables, or only feature classes using the `domains2html`, `tables2html`, and `fcs2html` functions respectively.

To generate full geodatabase report:

```python
import registrant
reporter = registrant.Reporter(
    r"C:\GIS\Production.gdb", r"C:\GIS\ReportFolder"
)
reporter.gdb2html()
print(reporter.report_file_path)
```

To generate report listing only tables and feature classes (with no information on fields, subtypes, and indexes):

```python
import registrant
reporter = registrant.Reporter(
    r"C:\GIS\Production.gdb", r"C:\GIS\ReportFolder"
)
reporter.gdb2html(
    do_report_versions=False,
    do_report_replicas=False,
    do_report_domains=False,
    do_report_domains_coded_values=False,
    do_report_relclasses=False,
    do_report_tables=True,
    do_report_tables_fields=False,
    do_report_tables_subtypes=False,
    do_report_tables_indexes=False,
    do_report_fcs=True,
    do_report_fcs_fields=False,
    do_report_fcs_subtypes=False,
    do_report_fcs_indexes=False,
)
print(reporter.report_file_path)

```

To generate report listing only domains and coded values for domains:

```python
import registrant
reporter = registrant.Reporter(
    r"C:\GIS\Production.gdb", r"C:\GIS\ReportFolder"
)
registrant.domains2html()
```

### Architecture

This tool uses `arcpy` package (and if you don't have any ArcGIS software installed - `ogr` package) to read properties of geodatabase into Python dictionaries which are used then to construct `pandas` data frames. The data frames are exported into HTML tables (as large strings) using built-in [`pandas.DataFrame.to_html`](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.to_html.html) method. To merge all the HTML tables into a single page, `beautifulSoup` package is used. The HTML report page is built using the [Bootstrap 3 Dashboard sample](http://getbootstrap.com/examples/dashboard/#). Some extra functionality is added with the help of [Bootstrap 3 DataTables](https://datatables.net/examples/styling/bootstrap.html) extension. Additional navigation items in the table of contents are added to the HTML page on-the-fly while reading geodatabase tables and feature classes.

### FAQ

* Why not just use ArcGIS Diagrammer to generate HTML reports?

    ArcGIS Diagrammer was deprecated at ArcGIS 10.3 which means only users of ArcGIS 10.0-10.2 can use it. If you have ArcGIS 10.3 or above, you can still install it on your machine, but you would need to have the .dll files of ArcObjects SDK for .NET of version 10.2 available.

    The `registrant` package tool is not a replacement of ArcGIS Diagrammer as it can only *report* the information about the geodatabase contents (you cannot *design* a new geodatabase). However, this tool reports a lot of useful information about the contents of  geodatabase as ArcGIS Diagrammer does. This means that you might not need to install ArcGIS Diagrammer if you are only interested in getting the HTML reports about the geodatabase contents.

* I would like to see the information about `X` being reported, but the HTML report doesn't provide any information about it. Can you please add it?

    Feel free to post an issue in this repository and I will see what's possible.

* Why does it take less time for ArcGIS Diagrammer to generate HTML report about my geodatabase?

    ArcGIS Diagrammer was built using fine-grained `ArcObjects` libraries which provides low-level access to the underlying geodatabase datasets and their properties. With this Python package, reading the geodatabase is done using `arcpy` Python package which makes it really easy to write and maintain this package, however there is a price to pay for that; it takes extra time to convert `ArcObjects` COM objects to Python objects and vice versa which results in longer processing time. Reading properties of geodatabase datasets with `ogr` happens much faster than when using `arcpy`, but you don't get all the properties exposed via this interface.

    If you need to produce HTML reports fairly often and performance does matter to you, try to leave out some of the report options to save time. You could, for instance, skip reporting indexes and subtypes for every table and feature class if you have a large number of datasets in your geodatabase.

* I have no Esri software and no GDAL/OGR installed. Can I generate the report of my SQL Server/Oracle/MySQL/PostgreSQL/etc database anyway?

    No, you cannot because the package expects to be able to pull all the information about the tables and columns using either `arcpy` which comes with ArcGIS software or OGR which comes together with GDAL Python bindings. However, there are many other programs that will be able to generate the schema report among many other things. Take a look at [SchemaSpy](http://schemaspy.org/sample/index.html), for instance.

### Report contents

* General geodatabase overview
* Enterprise geodatabase versions
* Enterprise and local geodatabase replicas
* Domains & coded values
* Tables & Feature classes
* Table & Feature class fields
* Table & Feature class subtypes (`arcpy` only)
* Table & Feature class indexes (`arcpy` only)

Added in v0.2:

* Replicas and replicas' datasets (`arcpy` only)

Added in v0.3:

* Versions in SDE geodatabases (`arcpy` only)

Added in v0.4:

* Properties `Attachments enabled` and `Attachments count` for tables and feature classes (`arcpy` only)

Added in v0.5:

* Relationship classes in geodatabases (`arcpy` only)

Added in v0.6:

* Reporting more information for GDAL users using geodatabase XML metadata

Added in v0.7:

* Redesigned architecture with the new public interface

All fields in tables and feature classes have a property showing the order of the field (`UI order`) within the dataset as shown in the dataset properties window in ArcGIS Desktop or Pro that is the order in which the fields were added. This is the order in which fields appear when you open the Feature Class Properties or Table Properties window in ArcGIS Desktop or when you access the Fields window in ArcGIS Pro.

As a note, Unicode characters are supported in geodatabase table names, field aliases and so forth. The web page should be drawn using the `utf-8` encoding. Should any characters appear strange, make sure you are viewing the report page in the proper encoding:

* Firefox: `View > Text Encoding > Unicode`
* IE: `View > Encoding > Unicode (UTF-8)`
* Chrome: auto-detect should do the magic

### Report functionality

* Navigation panel to the left lets you quickly jump between different report sections.

* All columns are sortable (ASC | DESC) with the option to choose a number of entries to show for every data table and use paging. Every section also has the Search panel for text search within the section (e.g., search for the field name in a particular feature class) that will filter out table rows with no matches.

* It is possible to select rows in the data tables (with highlight). Operating system keys such as `Ctrl`/`Shift` can be used for selecting multiple rows. More about [selecting rows in data tables](https://datatables.net/extensions/select/examples/initialisation/blurable.html).

* It is possible to re-order columns in the data tables by dragging them and dropping in the needed place. More about [re-ordering columns in data tables](https://datatables.net/extensions/colreorder/examples/initialisation/simple.html).

* It is possible to enable toggle word break in the data tables cells which can be handy for cells with long words (the checkbox is found in the upper-left corner of the left panel).

* All feature classes have a single default subtype defined for them, so to save the space the information about subtypes will be reported only when there are at least two subtypes (which means at least one subtype has been added by the user).

* By using the `Print` link one can create a printable representation of the report; opening printable report can take some time depending on the number of items in your geodatabase. The report page will be visible in the new browser tab `about:blank`. The generation of printable report works best in Firefox. Please mind that Chrome and IE can choke when the report content is very large.

### New functionality under consideration

Take each domain > list all tables/fcs that use this domain > list all fields that have this domain assigned > count rows using domain value group by code

#### Report design and contents

* Pick what columns to show in each data table using [Buttons](https://datatables.net/extensions/buttons/examples/) extension.

* Add mapping for `arcpy.Field` data types and ArcGIS Desktop (String - Text etc)

### Running tests locally

1. Cd to the `tests` folder and run `coverage run -m unittest discover`. This will create a `.coverage` file which contains the metadata about code coverage.

2. Cd to the `tests` folder and run `coverage html -d coverage_html`. This will generate a nice `.html` report highlighting the covered code. Calls to `arcpy` are excluded in the report thanks to the `.coveragerc` file.

Keep in mind that you need to make sure that `arcpy` is not found when you run tests for OGR as this will make the tests fail.
In Wing IDE, right-click OGR test files > `File Properties` menu > `Testing` tab > choose empty `Custom` for Python path for the Python environments used to run the OGR tests (Anaconda env). This will make sure ArcGIS paths won't be added to the `sys.path`.

You also need to make sure that the right initial diretory used when starting the tests. In Wing IDE, go to the launch configuration properties and under the `Environment` tab, choose `Use default` for the `Initial Directory` property. This is required to be able to find the sample geodatabase files.

### Issues

Did you find a bug? Do you need report to include some other information? Please let me know by submitting an issue.

### Licensing

MIT
