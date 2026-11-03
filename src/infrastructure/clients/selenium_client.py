from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import time
class SeleniumClient:
    def __init__(self, headless=True):
        options = Options()

        if headless:
            options.add_argument("--headless=new")

        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

        self.driver = webdriver.Chrome(options=options)
    
    def exectute_fetch(self, url, headers=None):
        headers = headers or {}
        script = f"""
        const callback = arguments[arguments.length - 1];
        fetch(
            "{url}",
            {{
                headers: {json.dumps(headers)}
            }}
        )
        .then(r => r.text())
        .then(data => callback(data))
        .catch(err => callback(JSON.stringify({{
            error: err.toString()
        }})));
        """
        return self.driver.execute_async_script(script)
    
    def get_page_source(self, url, sleep_seconds: int = 0):
        self.driver.get(url)
        if sleep_seconds != 0:
            time.sleep(sleep_seconds)
        return self.driver.page_source

    def close(self):
        self.driver.quit()