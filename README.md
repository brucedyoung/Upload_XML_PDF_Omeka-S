omeka_import_pdf_xml
=======

This repo includes two Python scripts designed for use with the Omeka API. 

One adds new items to Omeka from the command line using XML file, and adding an associated media item using an associated PDF.
The other adds the list of related items to the item, after all the items have been imported.
This was intended to create a new Omeka S instance from a set of PDF's and XML files exported from Wiley publishing.
An example PDf and XML file is included in the repo, and the production Omeka-S site with all of the imported data is at: https://emergingtrends.stanford.edu 

The starting point of the useage examples were lifted from kgoetz https://forum.omeka.org/t/example-api-usage-using-curl/8083


Bruce Young, bdyoung@gmail.com


`importscript.py`
============

This script traverses the folders of matching XML and PDF files, imports XML data as field(s) in Omeka-S, and imports the associated PDF. 

`updatelinks.py`
============

This script traverses the folders of the XML and modifies the item metadata to include URL's of related Omeka-S items.
Since all the items have to be imported before the relations can be made, this script is run after the importscript.py


Usage
-----

Edit the parameters of importscript.py, and place in the directory above our group of directories to be imported.
Run python3/importscript.py
After you validate the imported data in Omeka-S interface,
Run python3/updatelinks.py


Issues
======


