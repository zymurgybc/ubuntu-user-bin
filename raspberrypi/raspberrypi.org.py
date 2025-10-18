#!/usr/bin/env /usr/local/bin/python3.6
# -*- coding: utf-8 -*- 

import sys
import os
import glob
import json
import codecs
from tee import StdoutTee, StderrTee

from six.moves import urllib
from bs4 import BeautifulSoup

# Change these!
TRANSMISSION_HOST = 'localhost'
NAME_COLON_PASSWORD = 'transmission:<password>'
#NAME_COLON_PASSWORD = None

def AppendToFile(outputFile, html):
    if isinstance(html, list):
        for item in html:
            AppendToFile(outputFile, item)
    else: 
        outputFile.write(html)
        outputFile.write("\n\n### ==================================================== ###\n\n")

def DumpToFile(outputName, htmlPages):
    print("          Saving content to \"{}\"".format(outputName))
    outputFile = codecs.open(outputName,mode="w", encoding="UTF-8") 
    try:
        AppendToFile(outputFile, htmlPages)         
    except:  # catch *all* exceptions
        print("            Error while saving content to \"{}\"".format(outputName))
        for err in sys.exc_info():
            print("            ### === Exception: {}".format(err))
    outputFile.close()

def GetConfigFiles(rootFolder, scriptName):
    result = glob.glob("{}/{}.d/*.json".format(rootFolder, scriptName))
    configFileName = "{}/{}.json".format(rootFolder, scriptName)
    if os.path.exists(configFileName):
        result.append(configFileName)
    print("Found {} files.".format(len(result)))
    return result
    
def load_config(configFile):
    # read file
    print( "  Loading config file {}".format(configFile))
    with open(configFile, 'r') as myfile:
        data=myfile.read()
        # parse file
        return json.loads(data)

def ProcessConfigFile(configFile):
    config = load_config(configFile)
    try:
        #print(config)
        if config["subscriptions"] :
            for sub in config["subscriptions"]:
                html = []
                html.append(GetPageContent(sub))
                html.append( RecursivePageContents(sub, html[0]))
                DumpToFile("{}/{}.html".format(tmpFolder, sub["name"]), html)
                if html:
                    torrentPages = FindTorrents(html)
                    if torrentPages:
                        for page in torrentPages:
                            magnetLink = FindMagnetLink(sub, page)
    except: # catch *all* exceptions
        print("            Exception in ProcessConfigFile(...)")
        for err in sys.exc_info():
            print("            ### === Exception: {}".format(err))

def RecursivePageContents(sub, htmlPage):
    result = []
    aSub = sub
    soup = BeautifulSoup(htmlPage, 'html.parser')
    iframes = soup.find_all('iframe')
    for item in iframes:
        if "src" in item:
            aSub["url"] = item["src"]           
            page = GetPageConntent( aSub )
            result.append(page)
    return result

def GetPageContent(sub):
    print( "      Found Subscription Url {} -- {}".format(sub["name"], sub["url"]))

    if "parameters" in sub or "referrer" in sub:
        # parameters are option, and using them makes a POST
        if "parameters" in sub:
            params = urllib.parse.urlencode(sub["parameters"])
        else:
            params = urllib.parse.urlencode({})

        headers = {}
        if "referrer" in sub:
            headers["referrer"] = sub["referrer"]

        try:
            req = urllib.request.Request(sub["url"], params.encode("UTF-8"), headers)
            with urllib.request.urlopen(req) as response:
                page = response.read()
        except: # catch *all* exceptions
            print("            Exception in GetPageContent(...)[POST]")
            for err in sys.exc_info():
                print("            ### === Exception: {}".format(err))
    else:
        try:
            #req = urllib.request.Request(sub["url"])
            #with urllib.request.urlopen(req) as response:
            with urllib.request.urlopen(sub["url"]) as response:
                page = response.read()            
            
        except: # catch *all* exceptions
            print("            Exception in GetPageContent(...)[GET]")
            for err in sys.exc_info():
                print("            ### === Exception: {}".format(err))
    return page.decode("UTF-8")


def FindTorrents(html):
    result = []
    print("            Read {} bytes from the URL".format(len(html)))
    try:
        soup = BeautifulSoup(html, 'html.parser')
        anchors = soup.find_all('a')
        if isinstance(anchors, list):
            for a in anchors:
                if "href" in a:
                    print("             anchor -- {}".format(a["href"]))
                    if "class" in a and a["class"] == 'detName':
                        # this looks like a torrent link
                        result.append("{}".Format(a))
    except: # catch *all* exceptions
        print("            Exception in Find_Torrents(...)")
        for err in sys.exc_info():
            print("            ### === Exception: {}".format(err))

    print("           Found {} torrent anchors.".format(len(result)))
    return result

def FindMagnetLink(sub, page):
    result = []
    try: 
        if not page:
           return result
        soup = BeautifulSoup(page, 'html.parser')
        anchors = soup.find_all('a')
        for a in anchors:
            if a['href'].startswith('magnet:'):
                # this looks like a torrent link
                print( "      magnet link {} => {}".format(a.Text, a['href']))
                result.append(a)
    except: # catch *all* exceptions
        print("            Exception in FindMagnetLink(...)")
        for err in sys.exc_info():
            print("            ### === Exception: {}".format(err))
    return result

def AddMagnetLink(sub, link):
    http = urllib.Http(".cache")
    http.add_credentials(username, password)
    resp, content = http.request(url, "GET")

    headers = { "X-Transmission-Session-Id": resp['x-transmission-session-id'] }
    body = dumps( { "method": "torrent-add", "arguments": { "filename": argv[1] } } )

    response, content = http.request(url, 'POST', headers=headers, body=body)


# ====================================================

scriptName = os.path.basename(os.path.splitext(os.path.abspath(__file__))[0])
sourceFolder = os.path.dirname(os.path.abspath(__file__)) # /a/b/c/d/e
os.chdir(sourceFolder)

tmpFolder = "{}/tmp".format(os.environ["HOME"])
if ( not os.path.exists(tmpFolder)):
    os.mkdir(tmpFolder)

with StdoutTee("{}/{}.log".format(tmpFolder, scriptName), mode="a", buff=1024), \
    StderrTee("{}/{}.error".format(tmpFolder, scriptName), mode="a", buff=1024):

    print("{}/{}.py -- Finding config files...".format(sourceFolder, scriptName))
    for configFile in GetConfigFiles(sourceFolder, scriptName):
        ProcessConfigFile(configFile)

    # Handle some cleanup steps
    print("Finished.")
