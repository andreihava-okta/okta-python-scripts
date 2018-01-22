import requests
import json
import re
import sys
import csv
import time

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
        if "/appLinks" in url:
            return returnResponseList

        headerLink= response.headers["Link"]
        
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
            response = requests.request("GET", url, headers=headers)
            responseJSON = json.dumps(response.json())
            responseList = json.loads(responseJSON)
            returnResponseList = returnResponseList + responseList
            headerLink= response.headers["Link"]
        
        returnJSON = json.dumps(returnResponseList)
        return returnResponseList

def DownloadUsers():
    url = "https://" + orgName + ".com/api/v1/users?filter=status eq \"STAGED\""
    responseJSON = GetPaginatedResponse(url)

    if responseJSON != "Error":
        userFile = open("Staged-Users.csv", "wb")
        writer = csv.writer(userFile)
        writer.writerow(["userId", "firstName", "lastName", "email", "login", "created", "lastUpdated"])
        userCount = 0
        
        for user in responseJSON:
            userCount = userCount + 1
            userId = user[u"id"]
            firstName  = user[u"profile"][u"firstName"]
            lastName = user[u"profile"][u"lastName"]
            email = user[u"profile"][u"email"]
            login = user[u"profile"][u"login"]
            created = user[u"created"]
            lastUpdated = user[u"lastUpdated"]
            writer.writerow([userId, firstName, lastName, email, login, created, lastUpdated])
            
        print ("Downloaded " + str(userCount) + " users in the STAGED status.")

if __name__ == "__main__":
    print "Downloading all staged users from https://" + orgName + ".com/"
    DownloadUsers()