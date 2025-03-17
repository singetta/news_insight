import os
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from .utility import print_log


def kill_all_chrome_process():
    try:
        result = subprocess.check_output(["ps", "aux"], text=True)

        for line in result.splitlines():
            if ("chrome" in line or "Chrome" in line) and "grep" not in line:
                parts = line.split()
                pid = parts[1]

                os.kill(int(pid), 9)
                print_log(f"kill {pid}")
        print_log("Complete kill all chrome process")

    except Exception as e:
        print_log(f"Error occurred in kill chrome : {e}")


class BaseCrawler(object):
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--headless=new")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--disable-software-rasterizer")  # 렌더링 문제 해결
        self.options.add_argument("--disable-features=PaintHolding")  # 렌더링 타임아웃 방지
        self.options.add_argument("--window-size=1920x1080")
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        custom_ua = ('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
                     ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
        self.options.add_argument(custom_ua)

        self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument("--remote-debugging-port=9222")  # 디버깅 포트 열기
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(options=self.options, service=service)
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        });
                    '''
        })

        self.driver.execute_cdp_cmd('Network.clearBrowserCache', {})
        self.driver.execute_cdp_cmd('Network.clearBrowserCookies', {})
        self.wait = WebDriverWait(self.driver, 20)

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
        kill_all_chrome_process()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
