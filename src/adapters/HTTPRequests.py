import requests
from requests.packages.urllib3.util.retry import Retry
from urllib3.exceptions import InsecureRequestWarning
from requests.adapters import HTTPAdapter

DEFAULT_TIMEOUT = 5 # seconds

class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = kwargs.pop("timeout", DEFAULT_TIMEOUT)
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        kwargs["timeout"] = kwargs.get("timeout", self.timeout)
        return super().send(request, **kwargs)



class MakeRequest():
    def __init__(self, TIMEOUT=DEFAULT_TIMEOUT, headers=None):
        self.headers = headers
        self.timeout = TIMEOUT
    def hadapter(self):
        # https://github.com/Tkd-Alex/meile-gui/commit/de3c263c755e7c81e2b72b9ca15d05ad0b92b5f1
        # https://github.com/urllib3/urllib3/blob/main/CHANGES.rst#1260-2020-11-10
        # method_whitelist deprecated

        # We could check the version if urllib3 but I don't want to do another import.

        if 'DEFAULT_METHOD_WHITELIST' in dir(Retry):
            retries = Retry(
                total=2,
                status_forcelist=[429, 500, 502, 503, 504],
                method_whitelist=["HEAD", "GET", "OPTIONS"]
            )
        else:
            # We are on >1.26.0 version, with allowed_methods (Retry.DEFAULT_ALLOWED_METHODS)
            retries = Retry(
                total=2,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS"]
            )

        # adapter = HTTPAdapter(max_retries=retries)
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        http = requests.Session()
        http.headers.update(self.headers or {})
        http.mount("http://", TimeoutHTTPAdapter(max_retries=retries, timeout=self.timeout))
        http.mount("https://", TimeoutHTTPAdapter(max_retries=retries, timeout=self.timeout))
        return http