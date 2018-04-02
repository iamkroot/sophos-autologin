import requests
import random
import cuse
import os
import time

RAND = True
MIN_DATA = 200  # in MB


def read_logins(path='cy_logins.txt'):
    """Properly handle reading the logins."""
    if not os.path.isfile(path):
        print(f'{path} not found! Quitting.')
        exit(0)
    with open(path, 'r') as f:
        data = f.read()
        if not data:  # in case the file is empty
            print(f'{path} is empty. Add some logins first.')
            exit(0)
        return data.split('\n')


def login(un, pwd):
    url = 'http://172.16.0.30:8090/httpclient.html'
    payload = {'mode': 191, 'username': un, 'password': pwd}
    r = requests.post(url, payload)
    response = r.text.lower()
    states = [
        'logged in',
        'exceeded',
        'not log you on',
        'maximum login limit'
    ]
    for code, state in enumerate(states, 1):
        if state in response:
            return code
    return r.text


def try_login(logins: list):
    for creds in logins:
        logins.remove(creds)
        un, pwd = creds.split(' ')
        status = login(un, pwd)
        if status is 1:
            return creds
        elif status is 2:
            print('Data limit exceeded for', un)
        elif status is 3:
            print('Creds incorrect for', un)
        elif status is 4:
            print('Maximum login limit reached for', un)
        else:
            print(status)
            print('Quitting!')
            exit(0)
    print('All login IDs exhausted. Quitting.')


def get_rem_data(un, pwd):
    rem_data = cuse.get_rem_data(un, pwd)
    print('Remaining data:', rem_data, 'MB')
    return rem_data


def start_watching(un, pwd, rem_data):
    while rem_data > MIN_DATA:
        try:
            time.sleep(170)  # update interval of cyberoam site
        except KeyboardInterrupt:
            print('Quitting!')
            exit(0)
        rem_data = get_rem_data(un, pwd)


def main():
    logins = read_logins()
    if RAND:
        logins = random.sample(logins, len(logins))
    while True:
        un, pwd = try_login(logins).split(' ')
        rem_data = get_rem_data(un, pwd)
        if rem_data > MIN_DATA:
            start_watching(un, pwd, rem_data)


if __name__ == '__main__':
    main()
