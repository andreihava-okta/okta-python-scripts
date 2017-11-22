import requests
import json
import re
import sys
import csv
import time

orgName = ""
apiKey = ""
attributeName = u"userStatus"
triggerValue = "inactive"

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

def DeactivateUser(userId):
    response = requests.request("POST", "https://" + orgName + ".com/api/v1/users/" + userId + "/lifecycle/deactivate", headers=headers)

def DownloadUsers():
    url = "https://" + orgName + ".com/api/v1/users"
    responseJSON = GetPaginatedResponse(url)

    if responseJSON != "Error":
        callCounter = 1
        userFile = open("Deactivated-Users.csv", "wb")
        writer = csv.writer(userFile)
        writer.writerow(["userId", "firstName", "lastName", "email", "login", "userStatus"])
        deactivatedUserCount = 0
        
        for user in responseJSON:
            if callCounter > 9750:
                print ("Hit the cap of 9750 calls. Waiting 60 seconds...")
                time.sleep(60)
                callCounter = 0

            userId = user[u"id"]
            firstName  = user[u"profile"][u"firstName"]
            lastName = user[u"profile"][u"lastName"]
            email = user[u"profile"][u"email"]
            login = user[u"profile"][u"login"]
            
            if user[u"profile"].has_key(attributeName):
                userStatus = user[u"profile"][attributeName]
            
            callCounter = callCounter+1
    
            if userStatus == triggerValue:
                writer.writerow([userId, firstName, lastName, email, login, userStatus])
                print ("Deactivating " + email)
                DeactivateUser(userId)
                callCounter = callCounter+1
                deactivatedUserCount = deactivatedUserCount+1
                userStatus = ""
            
        print ("Deactivated " + str(deactivatedUserCount) + " users.")

if __name__ == "__main__":
    print ("Deactivating all users with " + attributeName + " set to '" + triggerValue + "' from https://" + orgName + ".com/")
    DownloadUsers()
