import subprocess
import traceback
import os
from sys import platform
import requests


def operating_system():
    try:
        if platform == "linux" or platform == "linux2":
            return "linux"
        elif platform == "darwin":
            return "osx"
        elif platform == "win32":
            return "windows"
    except Exception as err_os:
        raise err_os


def ping(host):
    try:
        command = ['ping', '-c', '1', host]
        if subprocess.call(command) == 0:
            result = True
        else:
            result = False

        return result
    except Exception as err_ping:
        traceback.print_stack()
        raise err_ping


def req(url):
    try:
        res = requests.get(url)
        if res.status_code == 200 or res.status_code == 403:
            return True
        return False
    except Exception as err_req:
        traceback.print_stack()
        raise err_req


def trace_route(url):
    if operating_system() == "windows":
        cmd = f"tracert {0}".format(url)
        result = os.system(cmd)
    else:
        cmd = f"traceroute {0}".format(url)
        result = os.system(cmd)
    return result
