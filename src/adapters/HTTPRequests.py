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
    def hadapter(self):
        retries = Retry(
            total=2,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"]
        )
        #adapter = HTTPAdapter(max_retries=retries)
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        http = requests.Session()
        http.mount("http://", TimeoutHTTPAdapter(max_retries=retries))
        http.mount("https://", TimeoutHTTPAdapter(max_retries=retries))
        return http