from urllib.request import Request, urlopen
import http
import time


last_time = None


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_with_time(s: str) -> None:
    global last_time
    if not last_time:
        last_time = time.time()
    current_time = time.time()
    delta = current_time - last_time
    last_time = current_time

    if delta > 2.0:
        color = bcolors.FAIL
    elif delta > 1.0:
        color = bcolors.OKGREEN
    else:
        color = bcolors.ENDC
        
    print(f'{color}{delta:.1f}s {s}{bcolors.ENDC}')
    

def get(url: str) -> http.client.HTTPResponse:
    req = Request(url, headers={'User-Agent': 'AWS Lambda'})
    return urlopen(req)