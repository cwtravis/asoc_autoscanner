import requests
import time
import datetime
import os

class ASoC:
    def __init__(self, apikey_id, apikey_secret, proxies=None):
        self.apikey = {
            "KeyId": apikey_id,
            "KeySecret": apikey_secret
        }
        self.token = ""
        self.session = requests.Session()
        if proxies is not None:
            self.session.proxies.update(proxies)
        self.session.headers.update({"Accept": "application/json"})
    
    def login(self):
        resp = self.session.post("https://cloud.appscan.com/api/V2/Account/ApiKeyLogin", json=self.apikey)
        if(resp.status_code == 200):
            jsonObj = resp.json()
            self.token = jsonObj["Token"]
            self.session.headers.update({"Authorization": "Bearer "+self.token})
            return True
        else:
            print(f"Status Code: {resp.status_code}")
            print(resp.text)
            return False
        
    def logout(self):
        resp = self.session.get("https://cloud.appscan.com/api/V2/Account/Logout")
        if(resp.status_code == 200):
            self.token = ""
            return True
        else:
            return False
        
    def checkAuth(self):
        resp = self.session.get("https://cloud.appscan.com/api/V2/Account/TenantInfo")
        return resp.status_code == 200

    def getApps(self, name=None):
        json_obj = None
        data = {
            "$filter": f"Name eq '{name}'"
        }
        if name is not None:
            resp = self.session.get(f"https://cloud.appscan.com/api/V2/Apps/GetAsPage?$select=Id", params=data)
        else:
            resp = self.session.get(f"https://cloud.appscan.com/api/V2/Apps/GetAsPage?$select=Id")
        if resp.status_code >= 200 and resp.status_code < 400:
            json_obj = resp.json()
        return (resp.status_code, json_obj)
    
    def getAssetGroup(self, name=None, filter_default=False):
        json_obj = None
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
        resp = self.session.get("https://cloud.appscan.com/api/V2/AssetGroups", params=data)
        if resp.status_code >= 200 and resp.status_code < 400:
            json_obj = resp.json()
        return (resp.status_code, json_obj)

    def createApp(self, name, asset_group_id):
        app_info = {
            "Name": name,
            "AssetGroupId": asset_group_id
        }
        resp = self.session.post("https://cloud.appscan.com/api/V2/Apps", json=app_info)
        return resp.status_code, resp.json()

    def uploadFile(self, file_path):
        file_name = os.path.basename(file_path)
        files = {"fileToUpload":(file_name, open(file_path, 'rb'), 'application/x-zip-compressed')}
        resp = self.session.post("https://cloud.appscan.com/api/V2/FileUpload?fileType=SourceCodeArchive", files=files)
        return resp.status_code, resp.json()

    def sastScan(self, file_id, app_id, scan_name="SAST Scan", automatic=False):
        data = {
            "ApplicationFileId": file_id,
            "ScanName": scan_name,
            "EnableMailNotification": False,
            "AppId": app_id,
            "FullyAutomatic": automatic
        }
        resp = self.session.post("https://cloud.appscan.com/api/V2/Scans/StaticAnalyzer", data=data)
        return resp.status_code, resp.json()

    def scanDetails(self, scan_id):
        resp = self.session.get(f"https://cloud.appscan.com/api/V2/Scans/{scan_id}")
        return resp.status_code, resp.json()
    
    def scanStatus(self, scan_id):
        try:
            resp = self.session.get(f"https://cloud.appscan.com/api/V2/Scans/{scan_id}")
        except  requests.exceptions.ConnectionError:
            return "Error"
        if resp.status_code == 403:
            return "Cancelled"
        if resp.status_code >= 300:
            return "Error"
        json_obj = resp.json()
        return json_obj["LatestExecution"]["Status"]
    
    @staticmethod
    #Get current system timestamp
    def getTimeStamp():
        ts = time.time()
        return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S')
    
ALLOW_LIST_EXTENSIONS = [
    ".java",
    ".cls",
    ".page",
    ".c",
    ".cpp",
    ".mm",
    ".h",
    ".h++",
    ".hh",
    ".hxx",
    ".hpp",
    ".H",
    ".ii",
    ".ixx",
    ".ipp",
    ".inl",
    ".txx",
    ".tpp",
    ".tpl",
    ".c+",
    ".cc",
    ".cxx",
    ".C",
    ".cob",
    ".cbl",
    ".ws",
    ".sqb",
    ".cfc",
    ".cfm",
    ".dart",
    ".bat",
    ".sh",
    ".yaml",
    ".yml",
    ".tf",
    ".tf.json",
    ".properties",
    ".curl",
    ".ini",
    ".conf",
    ".js",
    ".hbs",
    ".htm",
    ".html",
    ".rhtml",
    ".xhtml",
    ".cshtml",
    ".vbhtml",
    ".jsf",
    ".jsx",
    ".jsp",
    ".jspx",
    ".jspi",
    ".aspx",
    ".ascx",
    ".asp",
    ".asax",
    ".asa",
    ".inc",
    ".php",
    ".php3",
    ".php4",
    ".php5",
    ".phtm",
    ".phps",
    ".rjs",
    ".wlapp",
    ".ts",
    ".tsx",
    ".svg",
    ".vue",
    ".kt",
    ".m",
    ".mm",
    ".java",
    ".jsp",
    ".jspx",
    ".jspf",
    ".pl",
    ".pm",
    ".cgi",
    ".t",
    ".ctp",
    ".html",
    ".php",
    ".php4",
    ".php3",
    ".php5",
    ".php6",
    ".php7",
    ".phtm",
    ".phps",
    ".inc",
    ".htaccess",
    ".module",
    ".yaml",
    ".yml",
    ".xml",
    ".py",
    ".pyt",
    ".pyw",
    ".rpg",
    ".rpgl",
    ".rpgle",
    ".rb",
    ".rhtml",
    ".rjs",
    ".erb",
    ".abap",
    ".swift",
    ".plist",
    ".sql",
    ".lst",
    ".dbf",
    ".rdo",
    ".arc",
    ".pls",
    ".plb",
    ".pks",
    ".pkb",
    ".pck",
    ".tst",
    ".sp",
    ".sf",
    ".spb",
    ".sps",
    ".sql",
    ".lst",
    ".dbf",
    ".rdo",
    ".arc",
    ".dll",
    ".exe",
    ".asp",
    ".asa",
    ".inc",
    ".bas",
    ".cls",
    ".frm",
    ".jsp",
    ".jspx",
    ".jspi",
    ".htm",
    ".html",
    ".xml",
    ".java",
    ".class",
    ".jar",
    ".wsdl",
    ".smap",
    ".tld",
    ".tag",
    ".war",
    ".ear",
    ".rar",
    ".js",
    ".cpp",
    ".c",
    ".C",
    ".cc",
    ".cxx",
    ".CPP",
    ".CC",
    ".CXX",
    ".h",
    ".hpp",
    ".H",
    ".HPP",
    ".HH",
    ".hh",
    ".i",
    ".inl",
    ".txt",
    ".sql",
    ".ico",
    ".rc",
    ".ICO",
    ".RC",
    ".cur",
    ".rc2",
    ".RC2",
    ".bmp",
    ".aspx",
    ".cs",
    ".vb",
    ".vjs",
    ".master",
    ".xml",
    ".ico",
    ".config",
    ".xsd",
    ".xss",
    ".sql",
    ".mdf",
    ".ldf",
    ".ashx",
    ".css",
    ".ascx",
    ".htm",
    ".txt",
    ".html",
    ".asax",
    ".gif",
    ".jpg",
    ".sitemap",
    ".bmp",
    ".js",
    ".dll",
    ".disco",
    ".vsdisco",
    ".wsdl",
    ".map",
    ".resx",
    ".png",
    ".mdb",
    ".cshtml",
    ".vbhtml",
    ".aspx",
    ".cs",
    ".vb",
    ".vjs",
    ".master",
    ".xml",
    ".ico",
    ".config",
    ".xsd",
    ".xss",
    ".sql",
    ".mdf",
    ".ldf",
    ".ashx",
    ".css",
    ".ascx",
    ".htm",
    ".txt",
    ".html",
    ".asax",
    ".gif",
    ".jpg",
    ".sitemap",
    ".bmp",
    ".js",
    ".dll",
    ".disco",
    ".vsdisco",
    ".wsdl",
    ".map",
    ".resx",
    ".png",
    ".mdb",
    ".cshtml",
    ".vbhtml",
    ".aspx",
    ".ascx",
    ".cs",
    ".cs",
    ".vb",
    ".vbs",
    ".vb",
    ".vbs",
    ".wsdl",
    ".xsd",
    ".go",
    ".scala",
    ".sc",
    ".groovy",
    ".gsh",
    ".gsp",
    ".gvy",
    ".gy",
    ".ts",
    ".tsx",
    ".cs",
    ".rs",
    ".json",
    ".toml",
    ".json5"
]

ALLOW_LIST_FILES = [
    "androidmanifest.xml",
    "web.config",
    "dockerfile",
    "docker-compose",
    "config.xml",
    "androidmanifest.xml",
    "php.ini",
    "httpd.conf"
]

CONFIG_XML = """<Configuration sourceCodeOnly="true" staticAnalysisOnly="true">
    <Targets>
        <Target path="." />
    </Targets>
</Configuration>
"""