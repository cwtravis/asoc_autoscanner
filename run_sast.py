import os
import sys
import zipfile
import time
from asoc import ASoC, ALLOW_LIST_EXTENSIONS, ALLOW_LIST_FILES, CONFIG_XML

start_time = time.time()

FULLY_AUTOMATIC = True

required_args = [
    "ASOC_PROJECT_NAME",
    "ASOC_TARGET_DIR",
    "ASOC_API_KEY_ID",
    "ASOC_API_KEY_SECRET",
]

# Check Required Env Vars Exists
for arg in required_args:
    if arg not in os.environ:
        print(f"Required env variable not found: {arg}")
        print("Please specify all required env vars. They are:\n"+", ".join(required_args))
        sys.exit(1)

if "ASOC_ORG_NAME" not in os.environ.keys():
    org_name = "Not Specified"
else:
    org_name = os.environ["ASOC_ORG_NAME"]
project_name = os.environ["ASOC_PROJECT_NAME"]
directory = os.environ["ASOC_TARGET_DIR"]
api_key_id = os.environ["ASOC_API_KEY_ID"]
api_key_secret = os.environ["ASOC_API_KEY_SECRET"]
app_id = None

# Check for proxies
proxies = {}
http_proxy = None
https_proxy = None
if "HTTP_PROXY" in os.environ.keys():
    http_proxy = os.environ["HTTP_PROXY"]
    if "http://" not in http_proxy:
        http_proxy = f"http://{http_proxy}"
        proxies["http"] = http_proxy

if "HTTPS_PROXY" in os.environ.keys():
    https_proxy = os.environ["HTTPS_PROXY"]
    if "https://" not in https_proxy:
        https_proxy = f"https://{https_proxy}"
        proxies["https"] = https_proxy

if len(proxies.keys()) == 0:
    proxies = None
else:
    print("Proxy Info:")
    print(proxies)


print("HCL AppScan on Cloud - Run SAST")
print("------------------------------")
print(f"Org Name: {org_name}")
print(f"Project Name: {project_name}")
print(f"Target Directory: {directory}")
print(f"ASOC API Key: **provided**")

default_scan_name = project_name + "_" + ASoC.getTimeStamp()
scantarget_zip = default_scan_name + ".zip"
cwd = cwd = os.getcwd() 
scantarget_zip_path = os.path.join(cwd, scantarget_zip)

print(f"Zip File: {scantarget_zip_path}")
print("------------------------------")
app_check_time = time.time()
# Check Project Name exists as App
asoc = ASoC(api_key_id, api_key_secret, proxies=proxies)
if asoc.login():
    code, json_obj = asoc.getApps(project_name)
    if code != 200:
        print(f"ASoC API Response Code: {code}")
        print("Could not query ASoC API for App Info")
        sys.exit(1)
    if len(json_obj['Items']) > 0:
        # App Exists Already
        app_id = json_obj['Items'][0]["Id"]
        print(f"App [{project_name}] Exists: [{app_id}]")
    else:
        # Need to create the app
        # ToDo: Find AssetGroupId of Default Asset Group
        code, json_obj = asoc.getAssetGroup(filter_default=True)
        if code != 200:
            print("Could not get Default AssetGroup Id")
            sys.exit(1)
        default_asset_group_id = json_obj[0]["Id"]
        code, json_obj = asoc.createApp(project_name, default_asset_group_id)
        if code >= 300:
            print(f"Could not create application in ASoC: {project_name} in asset_group {default_asset_group_id}")
            print(f"Invalid Status Code: {code}")
            print(json_obj)
            sys.exit(1)
        app_id = json_obj['Id']
        print(f"Created App [{project_name} - {app_id}]")
else:
    print("ASoC API Key Login was unsuccessful. Bad API key?")
    sys.exit(1)

# Check Target Directory Exists
if not os.path.isdir(directory):
    print(f"Target Directory {directory} does not exist.")
    print("Create the directory or specify one that exists.")
    sys.exit(1)

app_check_time = round(time.time()-app_check_time)

zip_time = time.time()
print("Zipping Target Directory")
with zipfile.ZipFile(scantarget_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
    zipf.writestr('appscan-config.xml', CONFIG_XML)
    for root, dirs, files in os.walk(directory):
        for file in files:
            f_name, f_ext = os.path.splitext(file)
            if file.lower() in ALLOW_LIST_FILES or f_ext in ALLOW_LIST_EXTENSIONS:
                zipf.write(os.path.join(root, file), 
                    os.path.relpath(os.path.join(root, file), 
                    os.path.join(directory, '..')))
print("Zip Complete")    
file_size = os.path.getsize(scantarget_zip)
file_size_kb = file_size / 1024
file_size_mb = file_size_kb / 1024
print(f"Zip File Size: {round(file_size_mb)} MB")
zip_time = round(time.time()-zip_time)

print("------------------------------")

upload_time = time.time()
print("Uploading zip to ASoC")
code, json_obj = asoc.uploadFile(scantarget_zip)
if code >= 300:
    print("Error uploading zip file.")
    print(f"Invalid Response Code: {code}")
    print(json_obj)
    sys.exit(1)

file_id = json_obj["FileId"]
print(f"Zip file uploaded: FileId [{file_id}]")
upload_time = round(time.time()-upload_time)

print("------------------------------")
scan_time = time.time()

print("Creating SAST Scan")
code, json_obj = asoc.sastScan(file_id, app_id, scantarget_zip, FULLY_AUTOMATIC)
if code >= 300:
    print("Error creating scan")
    print(f"Invalid Response Code: {code}")
    print(json_obj)
    sys.exit(1)

scan_id = json_obj["Id"]
print(f"Scan Created: Id [{scan_id}]")
print("Waiting for Scan to complete...")

# Wait for scan to complete
old_status = ""
status = asoc.scanStatus(scan_id)
error_count = 0
while status not in ["Paused", "Ready", "Failed"]:
    if old_status != status :
        print(f"\tCurrent Status: {status}")
        old_status = status
    if status == "Error":
        error_count += 1
    else:
        error_count = 0
    if error_count >= 6:
        print("Error attempting to get the current scan status")
        sys.exit(1)
    if status == "Cancelled":
        print("API Returned Status Code 403 - Scan may have been cancelled.")
        sys.exit(0)
    time.sleep(15)
    status = asoc.scanStatus(scan_id)

print("Scan Complete")
code, json_obj = asoc.scanDetails(scan_id)
if code >= 300:
    print("Error getting scan details")
    print(json_obj)
    sys.exit(1)
scan_time = round(time.time()-scan_time)
print("------------------------------")

NIssuesFound = json_obj["LatestExecution"]["NIssuesFound"]
NCriticalIssues = json_obj["LatestExecution"]["NCriticalIssues"]
NHighIssues = json_obj["LatestExecution"]["NHighIssues"]
NMediumIssues = json_obj["LatestExecution"]["NMediumIssues"]
NLowIssues = json_obj["LatestExecution"]["NLowIssues"]
NInfoIssues = json_obj["LatestExecution"]["NInfoIssues"]

print("Scan Summary:")
print(f"\tCritical: {NCriticalIssues}")
print(f"\tHigh: {NHighIssues}")
print(f"\tMed: {NMediumIssues}")
print(f"\tLow: {NLowIssues}")
print(f"\tInfo: {NInfoIssues}")
print()
print(f"Total Issues: {NIssuesFound}")

# Logout of ASoC
asoc.logout()

elapsed_time = round(time.time()-start_time)
print(f"Runtime Summary: ")
print(f"\t App Check Time: {app_check_time} sec")
print(f"\t Zip Time: {zip_time} sec")
print(f"\t Upload Time: {upload_time} sec")
print(f"\t Scan Time: {scan_time} sec")
print(f"\t Total Time: {elapsed_time} sec")