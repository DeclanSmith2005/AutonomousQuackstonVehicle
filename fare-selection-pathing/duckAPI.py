import requests

s = requests.Session()
BASEURL = 'http://localhost:5000'
TEAM_NUMBER = '0'
#BASEURL = baseurl for lab
#BASEURL = baseurl for comp

def getMatchInfo():
    r = s.get(f"{BASEURL}/match", params= {'auth': TEAM_NUMBER})
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
    r = s.post(f"{BASEURL}/fares/claim/{fareidx}", params= {'auth':TEAM_NUMBER})
    res = r.json()
    if res['success']:
        return True
    else:
        print (res.message)
        return False

def checkCurrFare():
    r= s.get(f"{BASEURL}/fares/current/{TEAM_NUMBER}", params= {'auth': TEAM_NUMBER})

def getCurrentLocation():
    r= s.get(f"{BASEURL}/whereami/{TEAM_NUMBER}", params={'auth': TEAM_NUMBER})
    if r.ok:
        return r.json()
    else:
        print("issue with getting current position")
        


def main():
    print(getMatchInfo())
    print(getCurrentLocation())
    print(getFares())

if __name__ == "__main__":
    main()
