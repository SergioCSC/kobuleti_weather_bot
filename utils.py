from urllib.request import Request, urlopen
import http


def get(url: str) -> http.client.HTTPResponse:
    req = Request(url, headers={'User-Agent': 'AWS Lambda'})
    return urlopen(req)