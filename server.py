#!/usr/bin/env python

from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['POST'])
def get_ans():
    i = 0
    p = Path('./output/ans_booklet.zip')
    while p.exists():
        i += 1
        p = p.with_stem(f"ans_booklet-{i}")
    print(request.files.keys())
    request.files['file'].save(p)
    with ZipFile(p) as zip_ref:
        zip_ref.extractall(p.with_suffix(''))
    return 'ok', 200

if __name__ == '__main__':
    app.run(debug=True)