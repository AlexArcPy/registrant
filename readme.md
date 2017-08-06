### General

This Python package is used for generating HTML reports about the contents of Esri geodatabases. It supports working with Esri personal/file geodatabases as well as RDBMS enterprise geodatabases (however, it also works with RDBMS databases that were not geodatabase enabled).

Example of report:

![Sample report](https://user-images.githubusercontent.com/7373268/28848206-5eef081e-7712-11e7-90a9-ea882268e928.png)

### Usage guidelines

In order to use this tool, you would need to have ArcGIS Desktop, ArcGIS Server or ArcGIS Pro installed (for `arcpy` package). The code written is a valid Python 2 as well as Python 3 code which means you will be able to run against ArcGIS Desktop/Server Python 2.7 as well as ArcGIS Pro Python 3.5+. You will also need `pandas` and `beatifulSoup` Python packages which can be installed from `pip` if you are ArcGIS Desktop/Server user or using `conda` if you are ArcGIS Pro user. See [Installing Packages ](https://packaging.python.org/tutorials/installing-packages/) in the Python documentation (for ArcGIS Desktop users) and [Install a package](https://conda.io/docs/using/pkgs.html#install-a-package) in the Conda documentation (for ArcGIS Pro users) to get help.

When calling the reporting function, you'd need to supply path to your geodatabase and output folder for report data files, and optionally specify what information you would like to include into your output HTML report. Depending on the geodatabase size, number of chosen items to include in the report as well as the available system resources, it might take some minutes to run. The most time is spent in `arcpy` describe and listing functions iterating the datasets and pulling all the relevant information.

After HTML file is generated, you can open it in a web browser. The HTML file uses resources in other folders located in the `app` folder which means you cannot move the HTML file somewhere else without copying its dependency folders. If you would like to move the report somewhere else, you need to copy the whole `app` folder. While having the HTML file shown in a web browser, you can use the links to navigate throughout the page. Keep in mind that since navigation is built using the headers id, you can use the web browser's tools for navigating forward and back as you navigate between different sections of the report. 

### Requirements

* arcpy
* Python 2.7 / 3.5
* pandas >= 0.19.0
* beautifulsoup4 >= 4.6.0

### Installation

`python setup.py install`

### Getting started

The package has convenience functions which can be used to specify what exactly do you want to generate report for. The `gdb2html` function will create a complete report. However, you can specify if you want to report only domains, only tables, or only feature classes using the `domains2html`, `tables2html`, and `fcs2html` functions respectively. If you would like to have a fine-grained control over what information will be included in the report, you can use `report_gdb_as_html` function which has a few booleans you can set (for instance, you may want to get only list of tables and feature classes without reporting their fields, subtypes, and indexes). 

To generate full geodatabase report:

```
import registrant
registrant.gdb2html(r"C:\GIS\Production.gdb", r"C:\GIS\ReportFolder")
```

To generate report listing only tables and feature classes (with no information on fields, subtypes, and indexes):

```
import registrant
registrant.report_gdb_as_html(r"C:\GIS\Production.gdb",
                            r"C:\GIS\ReportFolderTablesFcs",
                            do_report_domains=False,
                            do_report_domains_coded_values=False,
                            do_report_tables=True,
                            do_report_tables_fields=False,
                            do_report_tables_subtypes=False,
                            do_report_tables_indexes=False,
                            do_report_fcs=True,
                            do_report_fcs_fields=False,
                            do_report_fcs_subtypes=False,
                            do_report_fcs_indexes=False)
```

To generate report listing only domains and coded values for domains:

```
import registrant
registrant.domains2html(r"C:\GIS\Production.gdb", r"C:\GIS\ReportFolderDomains")
```

### Architecture

This tool uses `arcpy` package to read properties of geodatabase into Python dictionaries which are used then to construct `pandas` data frames. The data frames are exported into HTML tables (as large strings) using built-in [`pandas.DataFrame.to_html`](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.to_html.html) method. To merge all the HTML tables into a single page, `beatifulSoup` package is used. The HTML report page is built using the [Bootstrap 3 Dashboard sample](http://getbootstrap.com/examples/dashboard/#). Some extra functionality is added with the help of [Bootstrap 3 DataTables](https://datatables.net/examples/styling/bootstrap.html) extension. Additional navigation items in the table of contents are added to the HTML page on-the-fly while reading geodatabase tables and feature classes.

### FAQ

* Why not just use ArcGIS Diagrammer to generate HTML reports?

    ArcGIS Diagrammer was deprecated at ArcGIS 10.3 which means only users of ArcGIS 10.0-10.2 can use it. If you have ArcGIS 10.3 or above, you can still install it on your machine, but you would need to have the .dll files of ArcObjects SDK for .NET of version 10.2 available.

    The `registrant` package tool is not a replacement of ArcGIS Diagrammer as it can only *report* the information about the geodatabase contents (you cannot *design* a new geodatabase). However, this tool reports a lot of useful information about the contents of  geodatabase as ArcGIS Diagrammer does. This means that you might not need to install ArcGIS Diagrammer if you are only interested in getting the HTML reports about the geodatabase contents. 

* I would like to see the information about `X` being reported, but the HTML report doesn't provide any information about it. Can you please add it?

    Feel free to post an issue in this repository and I will see what's possible.

* Why does it take less time for ArcGIS Diagrammer to generate HTML report about my geodatabase?

    ArcGIS Diagrammer was built using fine-grained `ArcObjects` libraries which provides low-level access to the underlying geodatabase datasets and their properties. With this Python package, reading the geodatabase is done using `arcpy` Python package which makes it really easy to write and maintain this package, however there is a price to pay for that; it takes extra time to convert `ArcObjects` COM objects to Python objects and vice versa which results in longer processing time.

    If you need to produce HTML reports fairly often and performance does matter to you, try to leave out some of the report options to save time. You could, for instance, skip reporting indexes and subtypes for every table and feature class if you have a large number of datasets in your geodatabase.

### Report contents

* General geodatabase overview
* Domains & coded values
* Tables & Feature classes
* Table & Feature class fields
* Table & Feature class subtypes
* Table & Feature class indexes

All fields in tables and feature classes have a property showing the order of the field (`UI order`) within the dataset as shown in the dataset properties window in ArcGIS Desktop or Pro that is the order in which the fields were added. This is the order in which fields appear when you open the Feature Class Properties or Table Properties window in ArcGIS Desktop or when you access the Fields window in ArcGIS Pro.

As a note, Unicode characters are supported in geodatabase table names, field aliases and so forth. The web page should be drawn using the `utf-8` encoding. Should any characters appear strange, make sure you are viewing the report page in the proper encoding:

* Firefox: `View > Text Encoding > Unicode`
* IE: `View > Encoding > Unicode (UTF-8)`
* Chrome: auto-detect should do the magic

### Report functionality

* Navigation panel to the left lets you quickly jump between different report sections.

* All columns are sortable (ASC | DESC) with the option to choose a number of entries to show for every data table and use paging. Every section also has the Search panel for text search within the section (e.g., search for the field name in a particular feature class) that will filter out table rows with no matches.

* All feature classes have a single default subtype defined for them, so to save the space the information about subtypes will be reported only when there are at least two subtypes (which means at least one subtype has been added by the user).

* By using the `Print` link one can create a printable representation of the report; opening printable report can take some time depending on the number of items in your geodatabase. The report page will be visible in the new browser tab `about:blank`. The generation of printable report works best in Firefox. Please mind that Chrome and IE can choke when the report content is very large.

### New functionality under consideration

#### Report design
* Reorder columns within the data tables https://datatables.net/extensions/colreorder/

#### Report contents
* Add mapping for `arcpy.Field` data types and ArcGIS Desktop (String - Text etc)

* Use ogr / file gdb api to read as much as info as possible if `arcpy` is not present

### Running tests locally

1. Cd to the `tests` folder and run `coverage run -m unittest discover`. This will create a `.coverage` file which contains the metadata about code coverage.

2. Cd to the `tests` folder and run `coverage html -d coverage_html --omit "C:\Program Files (x86)\ArcGIS\Desktop10.5\*"`. This will generate a nice `.html` report highlighting the covered code. The `--omit` flag is used to exclude calls to `arcpy` in the report.

### Issues

Did you find a bug? Do you need report to include some other information? Please let me know by submitting an issue.

### Licensing

MIT