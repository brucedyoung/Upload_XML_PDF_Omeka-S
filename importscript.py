#Extract all pdf and xml from ET Master Content File to temp directory using shell

#IF you don't want to traverse the folders, you can make a unified folder by making a copy.sh file with something like this
#DIR='/ET Master Content File'
#cd "$DIR"
#cp */*.pdf /home/bruce/combinedET
#cp */*.xml /home/bruce/combinedET

import requests
import json
import pprint
import time

import credential
#credental file is 
# key_identity = 'vsvvwvwvdv'
# key_credential = 'wwevwrarr'
# loads credential.key_identity, credential.key_credential

import cgi
from lxml import etree
# get title from metadata
from PyPDF2 import PdfFileReader

def getmetadata(filename):
    #print (filename)
    xmlfilename=filename.replace('pdf', 'xml')

    #important! The DTD or entity list is a link in the XML
    #http://v.wiley.com:3535/dtds/wileyml3g/wiley.ent
    #Tell lxml module to load it online to avoid character problems
    parser = etree.XMLParser(load_dtd=True,
                         no_network=False)

    tree = etree.parse(xmlfilename, parser=parser)
    root = tree.getroot()
    try:
        isbn=(root[0][0][2].text) #ISBN-13
    except:
        isbn="BlankISBN-13" 
    
    try:
        title=(''.join(root[0][4][0][0].itertext()))    
    except:
        title="BlankTitle"
    try:   
        publishdate=(root[0][0][5][0].attrib['date']) #publishedOnlineProduct
    except:
        publishdate="Blankpublishdate" 
    #editors placeholder - not imported
    #subjects (multiple) placeholder - not imported
    
    try:
        type=(root[0][1][0][0].text)    #Type
    except:
        type="BlankType" 
    try:
        subject=(root[0][2][0][0].text)    #Subject
    except:
        subject="BlankSubject" 
    #meta ID placeholder - not imported
    #publisher copywrite placeholder - not imported
    #numbering (number of pages) placeholder - not imported
    
    #get multiple authors
    authors=[]
    try: 
        for element in root[0][4][1]:
            authors.append((element[0][0].text)+" "+(element[0][1].text)) #Author FirstM, last
    except:
         authors.append("MissingAuthor")
    try:
        abstract=(''.join(root[0][4][4][0][1].itertext()))# join flattens any html like italics    
    except:
        abstract="BlankAbstract"


    return([title,authors,abstract,type,subject,isbn,publishdate])#xmlvaluelist
    #Author Biography placeholder -  not imported - in PDF
    #Paper Biography placeholder - not imported - in PDF
    
    #for element in root[1][5][1][0]:
    #    print (root[1][5][1][0][0][0].get("href")) #links
    #relatedArticles (multiple) - need importing

def creators(xmlvaluelist):
    authorslist=[]
    for idx,author in enumerate(xmlvaluelist[1]):
        authorslist.append (
            {      
                "property_id": 2, 
                "property_label": "Creator",
                "@value": author,
                "type" : "literal"
            }
        )

    #item_payload["dcterms:creator"]=authorslist	
    return(authorslist)


# Translated from https://forum.omeka.org/t/example-api-usage-using-curl/8083,
# the work of user 'kgoetz'.  Thanks.

# Begin quote:
# > The API permits anonymous access to public resources (i.e., reading non-private
# > data). To perform actions or view data that only logged-in users can access, 
# > you must authenticate your requests.
# > Authentication requires every request to include two additional GET
# > parameters: key_identity and key_credential. An Omeka S user can create API
# > keys in the "API keys" tab of their user edit page.

install_location = "http://emergingtrends.stanford.edu"

key_identity = credential.key_identity
key_credential = credential.key_credential

endpoint = "{}/api/items?key_identity={}&key_credential={}"
postdata = {}

final_uri = endpoint.format(install_location, key_identity, key_credential)

def traversefolders():
        # Import the os module, for the os.walk function
    item_payload={}
    import os
    from os import listdir
    from os.path import isfile, join
   
    #walk through current directory, looking foir directories
    directory_list= [f for f in os.listdir(".") if os.path.isdir(os.path.join(".", f))]
    for directory in directory_list:
        fileList = [f for f in listdir(directory) if isfile(join(directory, f))] 

        for file in fileList:
            if file[-3:] =="pdf":#process PDF
                creatorstext=''
                pdf_file_path=directory+"/"+file
                print ("pfd_file_path = "+pdf_file_path)
                predefined_item_set_id = 1
                pdf_reader = PdfFileReader(open(pdf_file_path, "rb"),strict=False)
                title=authorfirstname=authorlastname='notfound'
                xmlvaluelist=getmetadata(filename=pdf_file_path)# get the metadata from corresponding XML file in same folder
                try:
                    title=xmlvaluelist[0]
                except:
                    title="aBlank"
                #print (xmlvaluelist)
                authorslist=creators(xmlvaluelist=xmlvaluelist)
             
                #reference http://emergingtrends.stanford.edu/api/properties for property ID
                #save identifier without extension like .pdf
                item_payload = {
                    "dcterms:title": [
                                        {   
                                            "property_id": 1, 
                                            "property_label": xmlvaluelist[0],
                                            "@value":title,
                                            "type" : "literal"
                                        }
                                    ],
                    "dcterms:abstract": [
                        {   
                        "property_id": 19,  
                        "property_label": 'identifier',
                        "@value":xmlvaluelist[2],
                        "type" : "literal"
                    
                    }],
                    "dcterms:type": [
                        {   
                        "property_id": 8,  
                        "property_label": 'identifier',
                        "@value":xmlvaluelist[3],
                        "type" : "literal"
                    
                    }],
                       "bibo:isbn": [
                        {   
                        "property_id": 99,  
                        "property_label": 'identifier',
                        "@value":xmlvaluelist[5],
                        "type" : "literal"
                    
                    }],
                        "dcterms:dcterms:issued": [
                        {   
                        "property_id": 23,  
                        "property_label": 'identifier',
                        "@value":xmlvaluelist[6],
                        "type" : "literal"
                    
                    }],
                    "dcterms:subject": [
                        {   
                        "property_id": 3,  
                        "property_label": 'identifier',
                        "@value":xmlvaluelist[4],
                        "type" : "literal"
                    }
                    ],                
                    "dcterms:creator": authorslist,
                    "dcterms:identifier": [
                        {   
                            "property_id": 10,  
                        "property_label": 'identifier',
                        "@value":file[:-4],
                        "type" : "literal"
                    }
                    ],
                    "o:media": [
                                    {"o:ingester": "upload", "file_index": "0", "o:item": {},"dcterms:title": 
                                    [
                                        {
                                        "property_id": 1,
                                        "property_label": title,
                                        "@value" : title,
                                        "type" : "literal"
                                        }
                                    ],
                           
                                
                                    }
                            

                                ]
                                }

                #item_payload["dcterms:creator"] = [authorslist
                print (json.dumps(item_payload))
                r = requests.post(final_uri, data={'data': json.dumps(item_payload)}, files=[('file[0]', (pdf_file_path, open(pdf_file_path, 'rb'), 'application/pdf'))])
                time.sleep(2) #avoid upload timeout
                print (pdf_file_path)
                if r.ok:
                    #pprint.pprint(r.json())

                    print(r.status_code)
                else:
                    print(r.status_code)
                    print(r.content)
                    pprint.pprint(r.json())
                    #if file[-3:] =="xml":
                    #    print (file)
                    #print (file[0:9])
    return ("completed")

if __name__ == "__main__":
    traversefolders()
