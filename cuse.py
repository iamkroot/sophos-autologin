import urllib.parse as up
import requests
import time
import json
from bs4 import BeautifulSoup
import re
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

BASE_URL = 'https://172.16.0.30:4443/corporate/'


def make_heads(cookie, query_len):
    USERAGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                 '(KHTML, like Gecko) Chrome/65.0.3325.183 Safari/537.36')

    control_headers = {
        'Accept': 'text/plain, */*; q=0.01',
        'Host': '172.16.0.30:4443',
        'Connection': 'keep-alive',
        'Content-Length': str(query_len),
        'Origin': 'https://172.16.0.30:4443',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': USERAGENT,
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Referer': BASE_URL + 'webpages/login.jsp?webclient=myaccount&fref=gc',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cookie': 'JSESSIONID=' + cookie
    }

    acc_headers = {
        'Accept': '*/*',
        'Host': '172.16.0.30:4443',
        'Connection': 'keep-alive',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': USERAGENT,
        'Referer': BASE_URL + 'webpages/myaccount/index.jsp',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cookie': 'JSESSIONID=' + cookie
    }

    return control_headers, acc_headers


def get_rem_data(un, pwd):
    """Retreive the remaining data from cyberoam site."""
    TIME_FORMAT = '%a %b %d %Y %H:%M:%S GMT 0530 (India Standard Time)'
    login_url = BASE_URL + 'webpages/login.jsp?webclient=myaccount&fref=gc'
    control_url = BASE_URL + 'Controller'
    acc_url = BASE_URL + 'webpages/myaccount/AccountStatus.jsp'

    sess = requests.Session()

    rl = sess.get(login_url, verify=False)  # get cookie
    cookie = rl.cookies['JSESSIONID']
    data = {
        'username': un,
        'password': pwd,
        'languageid': '1',
        'browser': 'Chrome_65'
    }
    payload = {
        'mode': '451',
        'json': json.dumps(data),
        '_RequestType': 'ajax',
        't': time.strftime(TIME_FORMAT, time.localtime())
    }
    query = up.urlencode(payload)
    c_head, a_head = make_heads(cookie, len(query))

    sess.post(control_url, payload, headers=c_head)

    params = {
        'popup': '0',
        't': time.strftime(TIME_FORMAT, time.localtime())
    }
    ra = sess.get(acc_url, params=params, headers=a_head)

    soup = BeautifulSoup(ra.text, 'html.parser')
    data = soup.find_all('td', {'class': 'tabletext'})[-1].text.strip()
    value = re.search(r'(?P<rem>[0-9\.]+).*', data)['rem']
    return float(value)
