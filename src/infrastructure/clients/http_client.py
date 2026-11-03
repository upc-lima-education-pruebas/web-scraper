import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class HttpClient:
    def __init__(self):
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://",adapter)
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/137.0.0.0 Safari/537.36"
            )
        }

    def get_json(self, url, headers=None):
        if not headers:
            headers = self.headers
        response = self.session.get(
            url,
            headers=headers,
            timeout=20
        )
        response.raise_for_status()
        return response.json()
    
    def get_text(self, url):
        response = self.session.get(
            url,
            headers=self.headers,
            timeout=20
        )
        response.raise_for_status()
        return response.text
    
    def post(self, url, headers = None, payload = None):
        if not headers:
            headers = self.headers
        response = self.session.post(
            url,
            headers=headers,
            json=payload,
            timeout=20
        )
        response.raise_for_status()
        return response.json()