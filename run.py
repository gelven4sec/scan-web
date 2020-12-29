#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from urllib.parse import urlparse, urljoin
from urllib.request import urlopen

from bottle import Bottle, run, static_file, request
from requests_html import HTMLSession
from bs4 import BeautifulSoup

app = Bottle()


# send main web page
@app.route('/')
def server_static(filepath="index.html"):
    return static_file(filepath, root='/home/pi/scan-web/public/')


# send static files(css, js, img, etc...)
@app.route('/static/<filepath:path>')
def server_static_file(filepath):
    return static_file(filepath, root='/home/pi/scan-web/public/static/')


# SQLi injection scanner function called from AJAX on client
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
        # check if target is enable
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


@app.post('/process_xss')
def process_xss():
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
        # check if target is enable
        try:
            code = urlopen(url).getcode()
        except:
            return 'Invalid target or offline: Code 2'

    if code != 200:
        return 'Invalid target or offline'

    # initialize an HTTP session
    session = HTMLSession()

    # GET request
    res = session.get(url)

    soup = BeautifulSoup(res.html.html, "html.parser")
    forms = soup.find_all("form")

    # iterate over forms
    for i, form in enumerate(forms, start=1):
        form_details = get_form_details(form)
        # print("=" * 50, f"form #{i}", "=" * 50)
        print(form_details)


def get_form_details(form):
    details = {}
    # get the form action (requested URL)
    action = form.attrs.get("action").lower()
    # get the form method (POST, GET, DELETE, etc)
    # if not specified, GET is the default in HTML
    method = form.attrs.get("method", "get").lower()
    # get all form inputs
    inputs = []
    for input_tag in form.find_all("input"):
        # get type of input form control
        input_type = input_tag.attrs.get("type", "text")
        # get name attribute
        input_name = input_tag.attrs.get("name")
        # get the default value of that input tag
        input_value = input_tag.attrs.get("value", "")
        # add everything to that list
        inputs.append({"type": input_type, "name": input_name, "value": input_value})
    # put everything to the resulting dictionary
    details["action"] = action
    details["method"] = method
    details["inputs"] = inputs
    return details


run(app, host='0.0.0.0', port=2323, debug=True)
