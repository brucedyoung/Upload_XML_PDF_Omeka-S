import requests
import json
import pprint
import time

import credential
#credental file is 
# key_identity = 'vsvvwvwvdv'
# key_credential = 'wwevwrarr'
# loads credential.key_identity, credential.key_credential

install_location = "http://emergingtrends.stanford.edu"
key_identity = credential.key_identity
key_credential = credential.key_credential
endpoint = "{}/api/items?key_identity={}&key_credential={}"
postdata = {}
final_uri = endpoint.format(install_location, key_identity, key_credential)

#from bs4 import BeautifulSoup#not needed?
import cgi
from lxml import etree
from lxml.etree import tostring 
# get title from metadata
from PyPDF2 import PdfFileReader


def getrecord_idfromidentifer(originaldict):
    #convert json to dict
    record_id=0
    dictfromlist = originaldict[0]
    record_id = list(dictfromlist.values())[3]
    return(record_id)

#GET /api/:api_resource/:id
def getrecord(identifier):
    endpoint = "{}/api/items?key_identity={}&key_credential={}&property[0][property]=10&property[0][type]=in&property[0][text]={}" #- Search by identifier number
    #endpoint = "{}/api/items/{}?key_identity={}&key_credential={}" - Search by record ID
    get_uri = endpoint.format(install_location, key_identity, key_credential, identifier)
    jsonString = requests.get(get_uri)#get record json from website
    originaljsonlist = json.loads(jsonString.text) #you will append to original dict and resend back to modify record
    if originaljsonlist:
        record_id=getrecord_idfromidentifer(originaljsonlist)
    else:
        print('endpint '+get_uri)

    originaljsondict = originaljsonlist[0]
    return record_id, originaljsondict;

def gethreflinks(xmlfilename):
    item_payload={}#emty dict
    bibo_uri_list=[]
    parser = etree.XMLParser(load_dtd=True,
                         no_network=False)

    tree = etree.parse(xmlfilename, parser=parser)
    root = tree.getroot()
    links=root.findall(".//*[.='Related Essays']") # have to find child first, because XML files sometimes exclude type='relatedArticles'
    parent = links[0].getparent()
    listofhref=(parent[1][0])
    for link in listofhref.getchildren():
        xmllink=(link[0].get("href"))
        xmltext=(''.join(link[0].itertext()))
        identifier= (xmllink[-9:]) #example identifier etrds0154
        record_id, originaljson = getrecord(identifier)
        xmllink_URL=install_location+"/s/emergingtrends/item/"+str(record_id)
        bibo_uri_list.append({   
                                "property_id": 121, 
                                "property_label": 'uri',
                                "@id":xmllink_URL,
                                "type" : "uri",
                                "o:label" : xmltext,
                                
                            })
    if len(bibo_uri_list):
        item_payload["bibo:uri"] = bibo_uri_list
       
    #print (item_payload)
    return (item_payload)

def sendpayload(record_id,item_payload):
    endpoint = "{}/api/items/{}?key_identity={}&key_credential={}"
    put_uri = endpoint.format(install_location, record_id, key_identity, key_credential)
    r = requests.patch(put_uri, json=item_payload)#put JSON back
    return(r)

def Merge(dict1, dict2):
    res = {**dict1, **dict2}
    return res

def traversefolders():
        # Import the os module, for the os.walk function
    item_payload={}
    import os
    from os import listdir
    from os.path import isfile, join
   
    #walk through current directory, looking for pdf and XML files
    directory_list= [f for f in os.listdir(".") if os.path.isdir(os.path.join(".", f))]
    for directory in directory_list:
        fileList = [f for f in listdir(directory) if isfile(join(directory, f))] 
        for file in fileList:
            #Get record from website using identifier from XML, example etrds0386
            if file[-3:] =="pdf":#process PDF
                pdf_file_path=directory+"/"+file
                # Important!
                # The Omeka-S API Patch does NOT just modify the components being changed.
                # It will blank all the components that are missing in the requests.patch  
                # https://omeka.org/s/docs/developer/api/rest_api/#partial-update-patch 
                # so you must retrieve the original data as JSON, append as in this example, or you can edit, and then send the combined JSON back.
                record_id, originaljson=getrecord(file[:-4]) #get record_id and originaljson
                print ('trying to update'+str(record_id))
                hrefjson=gethreflinks(directory+"/"+file[:-4]+".xml")
                dict3 = Merge(originaljson, hrefjson)#combine old and new dict, then send as JSON
                response=sendpayload(record_id,dict3)
                print (response)


if __name__ == '__main__': 
    #functions are in traverse folders
    traversefolders()