import requests
import time
import datetime
import json

class ASoC:
    def __init__(self, apikey_id, apikey_secret):
        self.apikey = {
            "KeyId": apikey_id,
            "KeySecret": apikey_secret
        }
        self.token = ""
    
    def login(self):
        resp = requests.post("https://cloud.appscan.com/api/V2/Account/ApiKeyLogin", json=self.apikey)
        if(resp.status_code == 200):
            jsonObj = resp.json()
            self.token = jsonObj["Token"]
            return True
        else:
            return False
        
    def logout(self):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.token
        }
        resp = requests.get("https://cloud.appscan.com/api/V2/Account/Logout", headers=headers)
        if(resp.status_code == 200):
            self.token = ""
            return True
        else:
            return False
        
    def checkAuth(self):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.token
        }
        resp = requests.get("https://cloud.appscan.com/api/V2/Account/TenantInfo", headers=headers)
        return resp.status_code == 200

    def getApps(self, name=None):
        json_obj = None
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.token
        }
        data = {
            "$filter": f"Name eq '{name}'"
        }
        if name is not None:
            resp = requests.get(f"https://cloud.appscan.com/api/V2/Apps/GetAsPage", params=data, headers=headers)
        else:
            resp = requests.get(f"https://cloud.appscan.com/api/V2/Apps/GetAsPage", headers=headers)
        if resp.status_code >= 200 and resp.status_code < 400:
            json_obj = resp.json()
        return (resp.status_code, json_obj)
    
    def getAssetGroup(self, name="Default"):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.token
        }
        app_info = {
            "Name": name,
            "AssetGroupId": "8a38b653-1695-e711-80ba-002324b5f40c"
        }
        resp = requests.post("https://cloud.appscan.com/api/V2/Apps", json=app_info, headers=headers)
        print(resp.status_code)
        print(resp.text)

    def createApp(self, name):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.token
        }
        app_info = {
            "Name": name,
            "AssetGroupId": "8a38b653-1695-e711-80ba-002324b5f40c"
        }
        resp = requests.post("https://cloud.appscan.com/api/V2/Apps", json=app_info, headers=headers)
        print(resp.status_code)
        print(resp.text)

    @staticmethod
    #Get current system timestamp
    def getTimeStamp():
        ts = time.time()
        return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S')