import urllib.request
import dataclasses as dc


class DontThrowExceptions(urllib.request.HTTPErrorProcessor):
    http_response = https_response = lambda self, request, response: response
