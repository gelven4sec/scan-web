#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bottle import Bottle, run, route, static_file, request, post
import os
from urllib.request import urlopen
from urllib.parse import urlparse

app = Bottle()


# send main web page
@app.route('/')
def server_static(filepath="index.html"):
    return static_file(filepath, root='/home/pi/scan-web/public/')


# send static files(css, js, img, etc...)
@app.route('/static/<filepath:path>')
def server_static_file(filepath):
    return static_file(filepath, root='/home/pi/scan-web/public/static/')


# sqli injection scanner function called from AJAX on client
@app.post('/process')
def process_scan():
    # get url from POST method
    url = request.forms.get('url')

    # parse input to get hostname
    target = urlparse(url).hostname
    # if value is None means the url input is the exact hostname
    if target is None:
        target = url
        try:
            code = urlopen("http://" + url).getcode()
        except:
            return 'Invalid target or offline : Code 1'
    else:
        # check if target is joinable
        try:
            code = urlopen(url).getcode()
        except:
            return 'Invalid target or offline: Code 2'

    if code != 200:
        return 'Invalid target or offline'

    # start scan with sqlmap
    os.system("sqlmap -u \'" + url + "\' --crawl=1 --batch --forms --technique=BE")

    # if this fail, sqlmap didn't found a form so it didn't even created the directory
    try:
        f = open("/root/.sqlmap/output/" + target + "/log", 'r')
    except:
        return 'Target not vulnerable to SQL Injection ! : Code 3'

    # save content and close file
    result = f.read()
    f.close()

    # clean sqlmap directory
    os.system("sqlmap --purge")

    # if file content is empty, means no param were injectable
    if len(result) == 0:
        return 'Target not vulnerable to SQL Injection ! : Code 4'

    # clean sqlmap directory to cause result will be saved somewhere else
    os.system("sqlmap --purge")
    return result


run(app, host='0.0.0.0', port=2323, debug=True)
