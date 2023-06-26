import os
import sys
import zipfile
import time
from asoc import ASoC

# for testing set the env vars
os.environ["ASOC_ORG_NAME"] = "Altoro Mutual"
os.environ["ASOC_PROJECT_NAME"] = "Juice Shop5"
os.environ["ASOC_TARGET_DIR"] = "C:\Sample Applications\SAP ABAP Code"

required_args = [
    "ASOC_ORG_NAME",
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

org_name = os.environ["ASOC_ORG_NAME"]
project_name = os.environ["ASOC_PROJECT_NAME"]
directory = os.environ["ASOC_TARGET_DIR"]
api_key_id = os.environ["ASOC_API_KEY_ID"]
api_key_secret = os.environ["ASOC_API_KEY_SECRET"]
app_id = None

print(f"Org Name: {org_name}")
print(f"Project Name: {project_name}")
print(f"Target Directory: {directory}")
print(f"ASOC API Key: **provided**")

scantarget_zip = project_name + "_" + ASoC.getTimeStamp() + ".zip"
print(f"Target Zip File: {scantarget_zip}")

# Check Project Name exists as App
asoc = ASoC(api_key_id, api_key_secret)
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
    print(f"Target Direcotry {directory} does not exist.")
    print("Create the directory or specify one that exists.")
    sys.exit(1)

print("Zipping Target Directory")

with zipfile.ZipFile(scantarget_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(directory):
        for file in files:
            zipf.write(os.path.join(root, file), 
                os.path.relpath(os.path.join(root, file), 
                os.path.join(directory, '..')))

file_size = os.path.getsize(scantarget_zip)
print("File Size is :", file_size, "bytes")

print("Uploading zip to ASoC")
code, json_obj = asoc.uploadFile(scantarget_zip)
if code >= 300:
    print("Error uploading zip file.")
    print(f"Invalid Response Code: {code}")
    print(json_obj)
    sys.exit(1)

file_id = json_obj["FileId"]
print(f"Zip file uploaded - FileId: {file_id}")
print("Creating SAST Scan")
code, json_obj = asoc.sastScan(file_id, app_id, scantarget_zip)
if code >= 300:
    print("Error creating scan.")
    print(f"Invalid Response Code: {code}")
    print(json_obj)
    sys.exit(1)

scan_id = json_obj["Id"]
print(f"Scan Created: Id [{scan_id}]")
print("waiting for the scan to complete")

# Wait for scan to complete
old_status = ""
status = asoc.scanStatus(scan_id)
while status not in ["Paused", "Ready", "Failed"]:
    if old_status != status :
        print(f"Status: {status}")
        old_status = status
    time.sleep(15)
    status = asoc.scanStatus(scan_id)

print("Scan Complete")
code, json_obj = asoc.scanDetails(scan_id)
if code >= 300:
    print("Error getting scan details")
    print(json_obj)
    sys.exit(1)

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
