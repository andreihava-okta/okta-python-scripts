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

def GetAccessNumber(appId, userId):
    url = "https://" + orgName + ".com/api/v1/events?limit=1000&filter=action.objectType eq \"app.auth.sso\" and target.id eq \"" + appId + "\" and target.id eq \"" + userId + "\""
    responseJSON = GetPaginatedResponse(url)

    accessCount = 0

    if responseJSON != "Error":
        for access in responseJSON:
            accessCount = accessCount + 1

    return accessCount

def GetBookmarks():
    url = "https://" + orgName + ".com/api/v1/apps"
    responseJSON = GetPaginatedResponse(url)

    apps = []

    if responseJSON != "Error":
        for app in responseJSON:
            if app[u"status"] == "ACTIVE":
                if app[u"name"] == "bookmark":
                    apps.append(app)

    return apps

def GetActiveUsers():
    url = "https://" + orgName + ".com/api/v1/users?filter=status eq \"ACTIVE\""
    responseJSON = GetPaginatedResponse(url)

    users = []

    if responseJSON != "Error":
        for user in responseJSON:
            users.append(user)

    return users

def UDOperation():
    apps = GetBookmarks()
    users = GetActiveUsers()

    responseFile = open("Bookmarks-With-Usage.csv", "wb")
    writer = csv.writer(responseFile)
    writer.writerow(["appId", "appLabel", "userId", "userName", "numberOfSignons"])

    for app in apps:
        for user in users:
            appId = app[u"id"]
            appLabel = app[u"label"]
            userId = user[u"id"]
            userName = user[u"profile"][u"login"]
            numberOfSignons = GetAccessNumber(appId, userId)

            writer.writerow([appId, appLabel, userId, userName, numberOfSignons])

if __name__ == "__main__":
    print ("Downloading all active bookmarks and their number of signons from https://" + orgName + ".com/")
    UDOperation()
