#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from queue import Empty
import random
from urllib.parse import urlparse, urljoin
from urllib.request import urlopen

from bottle import Bottle, run, static_file, request, response
from requests_html import HTMLSession
from bs4 import BeautifulSoup

app = Bottle()

# send main web page
@app.get('/')
def server_static(filepath="index.html"):
    return static_file(filepath, root='public/')


# send static files(css, js, img, etc...)
@app.get('/static/<filepath:path>')
def server_static_file(filepath):
    return static_file(filepath, root='public/static/')


# SQLi injection scanner function called from AJAX on client
@app.post('/process')
def process_scan():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

    # get url from POST method
    url = request.forms.get('url')

    target = verif(url)

    # start scan with sqlmap
    os.system("sqlmap -u \'" + url + "\' --crawl=1 --batch --forms --technique=E")

    # if this fail, sqlmap didn't found a form so it didn't even created the directory
    try:
        f = open(f"{os.path.expanduser('~')}/.local/share/sqlmap/output/{target}/log", 'r')
    except:
        return 'Target not vulnerable to SQL Injection !'

    # save content and close file
    result = f.read()
    f.close()

    # if file content is empty, means no param were injectable
    if len(result) == 0:
        return 'Target not vulnerable to SQL Injection !'

    # clean sqlmap directory to cause result will be saved somewhere else
    os.system("sqlmap --purge")
    return result


@app.post('/process_xss')
def process_xss():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

    # get url from POST method
    url = request.forms.get('url')
    
    target = verif(url)

    # initialize an HTTP session
    session = HTMLSession()

    # GET request
    res = session.get(url)

    soup = BeautifulSoup(res.html.html, "html.parser")

    result_id = []

    for form in soup.find_all("form"):
        form_details = get_form_details(form)

        num = str(random.randint(0, 100))
        # the data body we want to submit
        data = {}
        for input_tag in form_details["inputs"]:
            if input_tag["type"] == "text":
                data[input_tag["name"]] = '<p id="' + num + '">scan_xss:' + num + '</p>'
            elif input_tag["type"] == "hidden":
                data[input_tag["name"]] = input_tag["value"]

        # join the url with the action (form request URL)
        url_target = urljoin(url, form_details["action"])

        if (form_details["method"] == "post"):
            res = session.post(url_target, data=data)
        else :
            res = session.get(url_target, params=data) # ?name=caca&test=davy
        soup = BeautifulSoup(res.content, "html.parser")
        for p in soup.find_all("p"):
            if 'id' in p.attrs:
                if p.attrs["id"] == num:
                    # TODO: retourner la list des id des formulaires vulnérables
                    result_id += form_details["id"]
                    #return "Target VULNERABLE to XSS injection !\r\nThe following tag has been injected:\r\n" + '<p id="' + num + '">scan_xss:' + num + '</p>'

    if (len(result_id) == 0):
        return "Target NOT VULNERABLE to XSS injection !"
    else :
        return "Target VULNERABLE to XSS injection !\r\n" + '\r\n'.join(result_id)

def verif(url):
    # parse input to get hostname
    target = urlparse(url).hostname
    # if value is None means the url input is the exact hostname
    if target is None:
        target = url
        try:
            code = urlopen(f"http://{url}").getcode()
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
    return target

def get_form_details(form):
    details = {}
    id = form.attrs.get("id").lower()
    # get the form action (requested URL)
    action = form.attrs.get("action").lower()
    # get the form method (POST, GET, DELETE, etc)
    if (form.attrs.get("method", "get").lower() == Empty):
        method = form.attrs.get("method", "post").lower()
    else:
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
    details["id"] = id
    return details

if __name__ == "__main__":
    run(app, host='0.0.0.0', port=2323, debug=True)