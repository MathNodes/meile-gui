import requests
from requests.packages.urllib3.util.retry import Retry
from urllib3.exceptions import InsecureRequestWarning
from requests.adapters import HTTPAdapter

DEFAULT_TIMEOUT = 5 # seconds

class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = DEFAULT_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)
    
    

class MakeRequest():
    def __init__(self, TIMEOUT=DEFAULT_TIMEOUT, headers=None):
        self.headers = headers
        self.timeout = TIMEOUT
    def hadapter(self):
        retries = Retry(
            total=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        #adapter = HTTPAdapter(max_retries=retries)
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        http = requests.Session()
        http.headers = self.headers
        http.mount("http://", TimeoutHTTPAdapter(max_retries=retries, timeout=self.timeout))
        http.mount("https://", TimeoutHTTPAdapter(max_retries=retries, timeout=self.timeout))
        return http