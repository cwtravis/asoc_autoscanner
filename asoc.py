import requests
import time
import datetime
import os

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
    
    def getAssetGroup(self, name=None, filter_default=False):
        json_obj = None
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.token
        }
        if name is not None:
            filter_str = f"name eq '{name}'" 
        else:
            filter_str = ""
        if filter_default:
            if len(filter_str)>0:
                filter_str += " and "
            filter_str += "IsDefault eq true"
        data = {
            "$filter": filter_str
        }
        resp = requests.get("https://cloud.appscan.com/api/V2/AssetGroups", headers=headers, params=data)
        if resp.status_code >= 200 and resp.status_code < 400:
            json_obj = resp.json()
        return (resp.status_code, json_obj)

    def createApp(self, name, asset_group_id):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.token
        }
        app_info = {
            "Name": name,
            "AssetGroupId": asset_group_id
        }
        resp = requests.post("https://cloud.appscan.com/api/V2/Apps", json=app_info, headers=headers)
        return resp.status_code, resp.json()

    def uploadFile(self, file_path):
        file_name = os.path.basename(file_path)
        print(file_name)
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.token
        }
        files = {"fileToUpload":(file_name, open(file_path, 'rb'), 'application/x-zip-compressed')}
        resp = requests.post("https://cloud.appscan.com/api/V2/FileUpload?fileType=SourceCodeArchive", headers=headers, files=files)
        return resp.status_code, resp.json()

    def sastScan(self, file_id, app_id, scan_name="SAST Scan"):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.token
        }
        data = {
            "ApplicationFileId": file_id,
            "ScanName": scan_name,
            "EnableMailNotification": False,
            "AppId": app_id
        }
        resp = requests.post("https://cloud.appscan.com/api/V2/Scans/StaticAnalyzer", headers=headers, data=data)
        return resp.status_code, resp.json()

    def scanDetails(self, scan_id):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.token
        }
        resp = requests.get(f"https://cloud.appscan.com/api/V2/Scans/{scan_id}", headers=headers)
        return resp.status_code, resp.json()
    
    def scanStatus(self, scan_id):
        code, json_obj = self.scanDetails(scan_id)
        if code == 403:
            return "Cancelled"
        if code >= 300:
            return "Error"
        return json_obj["LatestExecution"]["Status"]
    
    @staticmethod
    #Get current system timestamp
    def getTimeStamp():
        ts = time.time()
        return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S')