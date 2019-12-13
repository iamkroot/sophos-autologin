#! /usr/bin/python3
import json
import re
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

BASE_URL = 'https://172.16.0.30/userportal/'
LOGIN_URL = urljoin(BASE_URL, 'Controller')
ACC_URL = urljoin(BASE_URL, 'webpages/myaccount/AccountStatus.jsp')
INDEX_URL = urljoin(BASE_URL, "webpages/myaccount/index.jsp")


def get_rem_data(un, pwd):
    """Retreive the remaining data from cyberoam site."""
    sess = requests.Session()

    login_data = {
        'username': un,
        'password': pwd,
        'languageid': '1',
    }

    payload = {
        'mode': '451',
        'json': json.dumps(login_data),
    }

    sess.post(LOGIN_URL, payload, verify=False, timeout=5)
    r = sess.get(INDEX_URL)
    csrf_match = re.search(r"'([0-9a-z]*)'", r.text[r.text.find('c$rFt'):])
    heads = {
        "Referer": INDEX_URL,
        "X-CSRF-Token": csrf_match.group(1),
        "X-Requested-With": "XMLHttpRequest",
    }
    resp = sess.get(ACC_URL, params={'popup': '0'}, headers=heads, timeout=5)
    soup = BeautifulSoup(resp.text, 'html.parser')
    data = soup.find_all('td', {'class': 'tabletext'})[-1].text.strip()
    value = re.search(r'(?P<rem>[0-9\.]+).*', data)['rem']
    return float(value)
