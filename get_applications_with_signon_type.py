import requests
import json
import re
import sys
import csv

orgName = "vulcan.okta"
apiKey = "00LQYNhFYR-Gzwlwz5-wIiXIuiUbmjFLvcK2-nTr-4"

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

def UDOperation():
    url = "https://" + orgName + ".com/api/v1/apps"
    responseJSON = GetPaginatedResponse(url)
    appCount = 0
    
    if responseJSON != "Error":
        responseFile = open("Applications-With-Signon-Type.csv", "wb")
        writer = csv.writer(responseFile)
        writer.writerow(["label", "name", "signOnMode"])
        
        for app in responseJSON:
            if app[u"status"] == "ACTIVE":
                appCount = appCount + 1
                label = app[u"label"]
                name = app[u"name"]
                signOnMode = app[u"signOnMode"]
                writer.writerow([label, name, signOnMode])

        print ("Downloaded " + str(appCount) + " applications with their signon types.")

if __name__ == "__main__":
    print ("Downloading all active applications and their signon types from https://" + orgName + ".com/")
    UDOperation()
