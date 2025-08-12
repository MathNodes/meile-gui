import requests
from requests.packages.urllib3.util.retry import Retry
from urllib3.exceptions import InsecureRequestWarning
from requests.adapters import HTTPAdapter

DEFAULT_TIMEOUT = 5  # seconds

class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = kwargs.pop("timeout", DEFAULT_TIMEOUT)
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        kwargs["timeout"] = kwargs.get("timeout", self.timeout)
        return super().send(request, **kwargs)

class TimeoutSession(requests.Session):
    def __init__(self, timeout=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._timeout = timeout or DEFAULT_TIMEOUT

    def request(self, *args, **kwargs):
        kwargs.setdefault("timeout", self._timeout)
        return super().request(*args, **kwargs)

class MakeRequest():
    def __init__(self, TIMEOUT=DEFAULT_TIMEOUT, headers=None):
        self.headers = headers
        self.timeout = TIMEOUT

    def hadapter(self):
        if 'DEFAULT_METHOD_WHITELIST' in dir(Retry):
            retries = Retry(
                total=2,
                status_forcelist=[429, 500, 502, 503, 504],
                method_whitelist=["HEAD", "GET", "OPTIONS"]
            )
        else:
            retries = Retry(
                total=2,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS"]
            )

        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

        http = TimeoutSession(timeout=self.timeout)
        http.headers.update(self.headers or {})
        http.mount("http://", TimeoutHTTPAdapter(max_retries=retries))
        http.mount("https://", TimeoutHTTPAdapter(max_retries=retries))
        return http
