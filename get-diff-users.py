import requests
import json
import re
import sys
import csv
import time

orgName = ""
apiKey = ""
groupId = ""

api_token = "SSWS " + apiKey
headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': api_token}


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

        headerLink = response.headers["Link"]

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
            headerLink = response.headers["Link"]

        returnJSON = json.dumps(returnResponseList)
        return returnResponseList

def DownloadUsers():
    url = "https://" + orgName + ".com/api/v1/users?filter=status eq \"ACTIVE\""
    responseJSON = GetPaginatedResponse(url)

    userList = []
    userCount = 0

    if responseJSON != "Error":
        for user in responseJSON:
            userList.append(user[u"id"])
            userCount += 1

        print ("Downloaded " + str(userCount) + " users in the ACTIVE status.")
        return userList

    return "Error"

def DownloadMembers():
    url = "https://" + orgName + ".com/api/v1/groups/" + groupId + "/users"
    responseJSON = GetPaginatedResponse(url)

    memberList = []
    memberCount = 0

    if responseJSON != "Error":
        for member in responseJSON:
            memberList.append(member[u"id"])
            memberCount += 1

        print ("Downloaded " + str(memberCount) + " members from group ID " + groupId)
        return memberList

    return "Error"

def ProcessDifferences(memberList, userList):
    if userList != "Error":
        if memberList != "Error":
            diffList = []
            diffCount = 0
            current = 0

            for user in userList:
                for member in memberList:
                    if user == member:
                        current = 1

                if current == 0:
                    diffList.append(user)
                    diffCount += 1
                    current = 0

            if diffCount > 0:
                print ("Found " + str(diffCount) + " differences between the master user list and the group member list")
                return diffList
            else:
                print ("Found no differences between the master user list and the group member list")
                return "Empty"

        print ("Error was returned when getting group members")
        return "Empty"

    print ("Error was returned when getting master group list")
    return "Empty"


def WriteDifferences(diffList):
    if diffList != "Empty":
        diffFile = open("Diff-Users.csv", "wb")
        writer = csv.writer(diffFile)
        writer.writerow(["userId"])

        for diff in diffList:
            writer.writerow([diff])

        print ("Wrote all differences to Diff-Users.csv")

if __name__ == "__main__":
    print ("Downloading all differences between the master user list and the group memberships of " + groupId + " from https://" + orgName + ".com/")

    userList = DownloadUsers()
    memberList = DownloadMembers()
    diffList = ProcessDifferences(memberList, userList)
    WriteDifferences(diffList)