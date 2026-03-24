import requests

s = requests.Session()
#BASEURL = 'http://localhost:5000'
#TEAM_NUMBER = '0'
authKey = 'df5c5d634ec16bbe1639a91cddc177de'
TEAM_NUMBER = '11'
BASEURL = 'http://192.168.0.100:5000'
#BASEURL = baseurl for comp

def getMatchInfo():
    r = s.get(f"{BASEURL}/match", params= {'auth': authKey})
    if r.ok:
        return r.json()
    else:
        print('error with match status')

def getFares():
    r = s.get(f"{BASEURL}/fares")
    if r.ok:
        return r.json()
    else:
        print('error with getting fares')

def claimFare(fareidx):
    r = s.get(f"{BASEURL}/fares/claim/{fareidx}", params= {'auth':authKey})
    print(r)
    res = r.json()
    if res['success'] == True:
        return True
    else:
        return False

def checkCurrFare():
    r= s.get(f"{BASEURL}/fares/current/{TEAM_NUMBER}", params= {'auth': authKey})
    if r.ok:
        return r.json()
    else:
        print("chuck curr fair end point issue")
        

def getCurrentLocation():
    r= s.get(f"{BASEURL}/whereami/{TEAM_NUMBER}", params={'auth': authKey})
    if r.ok:
        return r.json()
    else:
        print("issue with getting current position")

def dropFare(fareIndex):
    r = s.get(f"{BASEURL}/fares/drop/{fareIndex}", params = {'auth': authKey})
        


def main():
    print(getMatchInfo())
    print(getCurrentLocation())
    
    print("CHECKING CURRENT FARE")
    curr = checkCurrFare()
    print(curr)

    if checkCurrFare()['fare']['id']:
        print(checkCurrFare()['fare']['id'])
        dropFare(checkCurrFare()['fare']['id'])

if __name__ == "__main__":
    main()
