import requests
import json
import re
import sys
import csv

orgName = ""
apiKey = ""
appId = ""

api_token = "SSWS "+ apiKey
headers = {'Accept':'application/json', 'Content-Type':'application/json', 'Authorization':api_token}

def GetPaginatedResponse(url, multiple):
    response = requests.request("GET", url, headers=headers)
    returnResponseList = []
    responseJSON = json.dumps(response.json())
    responseList = json.loads(responseJSON)
    
    if "errorCode" in responseJSON:
        print "\nYou encountered following Error: \n"
        print responseJSON
        print "\n"
        return "Error"

    else:
        if multiple == 0:
            return responseList
        
        returnResponseList = returnResponseList + responseList
        
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
    url = "https://" + orgName + ".com/api/v1/apps/" + appId + "/users"
    responseJSON = GetPaginatedResponse(url, 1)
    userCount = 0
    
    if responseJSON != "Error":
        responseFile = open("Assigned-Users-" + appId + ".csv", "wb")
        writer = csv.writer(responseFile)
        writer.writerow(["userId", "userEmail", "appUsername"])
        
        for user in responseJSON:
            if user[u"status"] == "ACTIVE":
                userCount = userCount + 1

                userId = user[u"id"]
                appUsername = user[u"credentials"][u"userName"]

                userUrl = user[u"_links"][u"user"][u"href"]

                print (userUrl)
                
                userJSON = GetPaginatedResponse(userUrl, 0)

                if userJSON != "Error":
                    userEmail = userJSON[u"profile"][u"email"]
                
                writer.writerow([userId, userEmail, appUsername])

        print ("Downloaded " + str(userCount) + " users assigned to " + appId)

if __name__ == "__main__":
    print ("Downloading all active users assigned to " + appId + " from https://" + orgName + ".com/")
    UDOperation()
