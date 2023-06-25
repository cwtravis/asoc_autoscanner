import os
import sys
import zipfile
from asoc import ASoC

# for testing set the env vars
os.environ["ASOC_ORG_NAME"] = "Altoro Mutual"
os.environ["ASOC_PROJECT_NAME"] = "Juice Shop2"
os.environ["ASOC_TARGET_DIR"] = "C:\Sample Applications\juice-shop"
os.environ["ASOC_API_KEY_ID"] = "d959529f-ee86-6e53-8574-3a1928c8cda8"
os.environ["ASOC_API_KEY_SECRET"] = "eC6ErNsfXpdsKnjDPlJpepDq5U9PsEq9sknhcvRWeR8="

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
        print("Please specify all required env variabls. They are:\n"+", ".join(required_args))
        sys.exit(1)

org_name = os.environ["ASOC_ORG_NAME"]
project_name = os.environ["ASOC_PROJECT_NAME"]
directory = os.environ["ASOC_TARGET_DIR"]
api_key_id = os.environ["ASOC_API_KEY_ID"]
api_key_secret = os.environ["ASOC_API_KEY_SECRET"]
app_id = None
scantarget_zip = "scantarget.zip"

print(f"Org Name: {org_name}")
print(f"Project Name: {project_name}")
print(f"Target Directory: {directory}")
print(f"ASOC API Key: **provided**")

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
        asoc.createApp(project_name)
    asoc.logout()
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