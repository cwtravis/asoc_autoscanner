# AppScan on Cloud AutoScanner

This script will compress a directory into a zip file and upload to HCL AppScan on Cloud for Static Analysis.

## Environment Variables

Environment variables are used to configure the script. They are specified below.

| Env Var Name  | Description | Required |
| ------------- | ------------- | ------------- |
| ASOC_ORG_NAME  | The name of the organization in ASoC  | No |
| ASOC_PROJECT_NAME  | The name of the project to scan. This will be created in ASoC if it does not exist  | Yes |
| ASOC_TARGET_DIR  | The full path to the directory to be zipped and scanned | Yes |
| ASOC_API_KEY_ID  | The AppScan on Cloud API Key ID  | Yes |
| ASOC_API_KEY_SECRET  | The AppScan on Cloud API Key Secret  | Yes |

Added support for HTTP_PROXY and HTTPS_PROXY environment variables. 

Example: `HTTPS_PROXY=123.123.123.123:4444`

AppScan on Cloud API Key may be generated inside the AppScan on Cloud portal via the menu Tools > API > Generate.

## Running a scan

To execute a scan with this script the above env variables will need to be created. Python and Pip are needed as well. This script was built and tested with Python 3.11.0.

Clone the repo
```bash
git clone https://github.com/cwtravis/asoc_autoscanner.git
cd asoc_autoscanner
```

Install the requirements via Pip
```bash
python3 -m pip install -r requirements.txt
```

Run the scan
```bash
python3 run_sast.py
```
