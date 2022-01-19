#!/usr/bin/python
import logging
import os
import random
import time
import psutil
import requests
import toml
from requests.exceptions import ConnectionError, SSLError, Timeout
import cuse

with open("config.toml") as f:
    config = toml.load(f)

logging.getLogger("urllib3").setLevel(logging.INFO)
logging.basicConfig(
    level=logging.DEBUG, style="{", format="{asctime} - {levelname} - {message}"
)
PORTAL_URL = config["general"]["portal_url"]
POLL_INTERVAL = config["general"]["poll_interval"]  # in secs
LOGINS_FILE = config["creds"]["logins_file"]
SHUFFLE = config["creds"]["shuffle"]


def read_logins(path):
    """Properly handle reading the logins."""
    if not os.path.isfile(path):
        logging.critical(f"{path} not found! Quitting.")
        exit(1)
    with open(path, "r") as f:
        lines = f.readlines()
        if lines[0].startswith("u"):
            lines = lines[1:]
        logins = list(line.strip().split(",") for line in lines)
    return logins


def login(un, pwd):
    payload = {"mode": 191, "username": un, "password": pwd}
    r = requests.post(PORTAL_URL, payload, timeout=5)
    response = r.text.lower()
    states = (
        ("signed in", "logged in"),
        ("exceeded"),
        ("invalid user"),
        ("maximum login limit"),
    )
    for code, state in enumerate(states, 1):
        if any(status in response for status in state):
            return code
    return r.text


def try_login(logins):
    for account in logins:
        un, pwd = account
        status = login(un, pwd)
        if status == 1:
            logging.info("Logged in as " + un)
            return account
        elif status == 2:
            logging.info("Data limit exceeded for " + un)
        elif status == 3:
            logging.warning("Creds incorrect for " + un)
        elif status == 4:
            logging.info("Maximum login limit reached for " + un)
        else:
            logging.debug(status)
            logging.critical("Unknown error. Quitting!")
            exit(1)
    logging.error("All login IDs exhausted. Quitting.")
    exit(2)


def get_net_used():
    counter = psutil.net_io_counters(nowrap=True)
    return counter.bytes_sent + counter.bytes_recv


def net_accessible(retry_count=5):
    if not retry_count:
        logging.error("Couldn't connect to google")
        return False
    try:
        requests.head("https://google.com", timeout=15)
    except SSLError:
        return False
    except (ConnectionError, Timeout):
        logging.warning("Conn Error")
        return net_accessible(retry_count - 1)
    else:
        return True


def get_used_data(used_data=0):
    prev = get_net_used()
    while True:
        cur = get_net_used()
        used_data += cur - prev
        yield round(used_data / 1e6, 2)
        prev = cur


def main():
    logins = read_logins(LOGINS_FILE)
    if SHUFFLE:
        random.shuffle(logins)
    used_data_gen = get_used_data()
    while True:
        if not net_accessible():
            logging.warning("Net not accessible.")
            un, pwd = try_login(logins)
            try:
                rem_data = cuse.get_rem_data(un, pwd)
            except TimeoutError:
                logging.warning("Failed to retrieve remaining data.")
            else:
                logging.info(f"Remaining data {rem_data} MB")
            used_data_gen = get_used_data()
        used_data = next(used_data_gen)
        logging.debug(f"Used data: {used_data} MB")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Stopped by user. Quitting!")
        exit(0)
