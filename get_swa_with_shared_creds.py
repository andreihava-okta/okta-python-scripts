import requests
import json
import re
import sys
import csv

orgName = ""
apiKey = ""

api_token = "SSWS "+ apiKey
headers = {'Accept':'application/json', 'Content-Type':'application/json', 'Authorization':api_token}

def GetPaginatedResponse(url):
    response = requests.request("GET", url, headers=headers)
    returnResponseList = []
    responseJSON = json.dumps(response.json())
    responseList = json.loads(responseJSON)
    returnResponseList = returnResponseList + responseList

    if "errorCode" in responseJSON:
        print "\nYou encountered following Error: \n"
        print responseJSON
        print "\n"
        return "Error"

    else:
        headerLink= response.headers["Link"]
        count = 1
        
        while str(headerLink).find("rel=\"next\"") > -1:
            linkItems = str(headerLink).split(",")
            nextCursorLink = ""
            
            for link in linkItems:
                if str(link).find("rel=\"next\"") > -1:
                    nextCursorLink = str(link)

            nextLink = str(nextCursorLink.split(";")[0]).strip()
            nextLink = nextLink[1:]
            nextLink = nextLink[:-1]
            url = nextLink
            print "\nCalling Paginated Url " + str(url) + "  " + str(count) +  " \n"
            response = requests.request("GET", url, headers=headers)
            responseJSON = json.dumps(response.json())
            responseList = json.loads(responseJSON)
            returnResponseList = returnResponseList + responseList
            headerLink= response.headers["Link"]
            count += 1
        
        returnJSON = json.dumps(returnResponseList)
        return returnResponseList

def GetSWAApps():
    url = "https://" + orgName + ".com/api/v1/apps"
    responseJSON = GetPaginatedResponse(url)

    apps = []

    if responseJSON != "Error":
        for app in responseJSON:
            if app[u"status"] == "ACTIVE":
                if app[u"signOnMode"] == "AUTO_LOGIN":
                    if app[u"credentials"][u"scheme"] == "SHARED_USERNAME_AND_PASSWORD":
                        apps.append(app)

    return apps

def UDOperation():
    apps = GetSWAApps()

    responseFile = open("SWA-Apps-With-Shared-Creds.csv", "wb")
    writer = csv.writer(responseFile)
    writer.writerow(["appId", "appLabel", "appUserName"])

    for app in apps:
        appId = app[u"id"]
        appLabel = app[u"label"]
        appUserName = app[u"credentials"][u"userName"]

        writer.writerow([appId, appLabel, appUserName])

if __name__ == "__main__":
    print ("Downloading all active SWA apps with their shared username from https://" + orgName + ".com/")
    UDOperation()
