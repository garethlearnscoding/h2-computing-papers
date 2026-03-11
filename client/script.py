#!/usr/bin/env python
"""
Usage: [WORKING_NAME].py <command> [<arguments>...]

<Commands>
  h  help      : Print this help message
  d  download  : Download files
  u  upload    : Upload files

<Arguments>
 -p  --path <path> : Specify the path in which to upload/download the file
"""

import sys
import requests
import zipfile
import shutil
import tempfile
from pathlib import Path
from io import BytesIO

class Env:
    UPLOAD_PATH: Path = Path('ans_booklet')
    UPLOAD_URI: str = 'http://127.0.0.1:5000/upload'
    DOWNLOAD_URI: str = 'http://127.0.0.1:5000/download'
    DOWNLOAD_PATH: str | None = None

try:
    _, cmd, *args = sys.argv
except ValueError:
    sys.exit(__doc__)

env = Env()
no_args = len(args)

# To accomodate users using --help
if cmd.lower() in ('-h', '--help', 'h', 'help'):
    mode = 'help'
elif cmd.lower() in ('download', 'd'):
    mode = 'download'
    i = 0
    while i < no_args:
        if args[i] in ('-p', '--path') and i+1 < no_args:
            env.DOWNLOAD_PATH = args[i + 1]
            i += 1
        ...
        i += 1
elif cmd.lower() in ('upload', 'u'):
    mode = 'upload'
    i = 0
    while i < no_args:
        if args[i] in ('-p', '--path') and i+1 < no_args:
            env.UPLOAD_PATH = Path(args[i + 1])
            i += 1
        ...
        i += 1
else:
    print(f"Unknown command: '{cmd}'")
    sys.exit(__doc__)

def help_doc(env: Env):
    print(__doc__)
    sys.exit(0)

def download(env: Env):
    try:
        r = requests.get(env.DOWNLOAD_URI, params={})
    except requests.exceptions.ConnectionError:
        sys.exit("Error with connection, check that you are connected to the internet.")
    if r.status_code == 200:
        with zipfile.ZipFile(BytesIO(r.content), 'r') as zip_ref:
            zip_ref.extractall(path=env.DOWNLOAD_PATH)
    else:
        sys.exit(f"Error occured when downloading file (got status code {r.status_code})")

def upload(env: Env):
    try:
        temp_ans = tempfile.NamedTemporaryFile(prefix=env.UPLOAD_PATH.stem, suffix='.zip', delete=False)
        shutil.make_archive(temp_ans.name[:-4], 'zip', env.UPLOAD_PATH)
    except FileNotFoundError as e:
        sys.exit(f"No directory '{e.filename}' found")
    r = requests.post(env.UPLOAD_URI, files={'file': ('ans_booklet.zip', temp_ans, 'application/zip')})
    print(r.text)

match mode:
    case "help": help_doc(env)
    case "download": download(env)
    case "upload": upload(env)
