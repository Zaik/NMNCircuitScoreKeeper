import urllib.request
import json
import sys

#Return a tuple (code,response)
#code = 0 if succesfull
#       -1 if there was an error connecting
#       -2 if website returns an error
#response = The resulting string of the request
#           The exception or error code if unsuccesfull
def doWebRequest(url : str):
    try:
        result = urllib.request.urlopen(url)
    except:
        print("Protocol Error on " + url + ", " + str(sys.exc_info()))
        return (-1,sys.exc_info()[0])
    if (result.getcode() < 200 or result.getcode() >= 300):
        print("Bad HTTP answer from " + url + ", " + str(result.getcode()))
        return (-2,result.getcode())
    return (0,result.read().decode(result.info().get_param('charset') or 'utf-8'))

def doJSONRequest(url : str):
    result = doWebRequest(url)
    if (result[0] != 0):
        return result
    jsonresult = json.loads(result[1])
    return (0,jsonresult)

def getPlayerInfo(name : str):
    result = doJSONRequest("http://smashranking.eu/api/smashers/"+name)
    if (result[0] == 0):
        return (0,result[1])
    else:
        return (-1,result[1])

#Takes a players non-slug name, searches for slugs starting with it. finds the one with the highest rank
#returns the proper slug (or an error if SR is down or no slug found)
def getPlayerHighestSlug(name : str):
    rankingresult = doJSONRequest("http://smashranking.eu/api/ranking/")
    if (rankingresult[0] != 0):
        return (-1,rankingresult[1])
    slug = None
    rank = -1
    for entry in rankingresult[1]:
        if (entry["slug"].startswith(name)):
            if (len(entry["slug"]) - len(name) < 3):
                if (entry["eurank"] < rank or rank == -1):
                    slug=entry["slug"]
                    rank=entry["eurank"]
                    break
    if (slug == None):
        return (-1,None)
    return (0,slug)
    
