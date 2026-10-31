"""
Selenium proxy diagnostic (Chrome).

This example uses IP allowlisting. It configures proxy endpoints only and
does not implement HTTP proxy username/password authentication.
"""

import os
import sys
from urllib.parse import urlparse

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.ui import WebDriverWait


IP_CHECK_URL = os.getenv("IP_CHECK_URL", "https://api.ipify.org?format=json")
PROXY_SERVER = os.getenv("PROXY_SERVER", "").strip()
TARGET_URL = os.getenv("TARGET_URL", "").strip()
PAGE_LOAD_TIMEOUT = int(os.getenv("PAGE_LOAD_TIMEOUT", "45"))
ELEMENT_WAIT_TIMEOUT = int(os.getenv("ELEMENT_WAIT_TIMEOUT", "15"))


def validate_url(value: str, name: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError(f"{name} must be a valid http:// or https:// URL")


def build_driver() -> webdriver.Chrome:
    proxy = Proxy()
    proxy.proxy_type = ProxyType.MANUAL
    proxy.http_proxy = PROXY_SERVER
    proxy.ssl_proxy = PROXY_SERVER

    options = webdriver.ChromeOptions()
    options.proxy = proxy
    # Uncomment if you need headless mode:
    # options.add_argument("--headless")

    return webdriver.Chrome(options=options)


def main() -> int:
    if not PROXY_SERVER:
        print("Missing PROXY_SERVER. Set it to your proxy host:port.")
        return 2
    if not TARGET_URL:
        print("Missing TARGET_URL. Set it to a website you own or may test.")
        return 2

    validate_url(IP_CHECK_URL, "IP_CHECK_URL")
    validate_url(TARGET_URL, "TARGET_URL")

    driver = None
    stage = "WebDriver startup"

    try:
        print("[1/3] Starting Chrome WebDriver...")
        driver = build_driver()
        driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
        print("WebDriver started.")

        stage = "Proxy route / IP-check"
        print("[2/3] Opening IP-check endpoint...")
        driver.get(IP_CHECK_URL)
        ip_result = WebDriverWait(driver, ELEMENT_WAIT_TIMEOUT).until(
            lambda browser: browser.find_element("tag name", "body").text.strip()
        )
        if not ip_result:
            raise RuntimeError("The IP-check page loaded but returned an empty body.")
        print(f"IP-check response: {ip_result}")

        stage = "Target website access"
        print("[3/3] Opening target website...")
        driver.get(TARGET_URL)
        WebDriverWait(driver, ELEMENT_WAIT_TIMEOUT).until(
            lambda browser: browser.execute_script("return document.readyState")
            in ("interactive", "complete")
        )
        print(f"Target page loaded: {driver.current_url}")
        print("Result: PASSED")
        return 0

    except TimeoutException as exc:
        print("Result: FAILED")
        print(f"Stage: {stage}")
        print("Exception: TimeoutException")
        print(f"Details: {exc}")
        print(
            "A timeout does not prove proxy authentication failed. "
            "Check the failing stage and inspect proxy/provider logs for an actual 407."
        )
        return 1

    except WebDriverException as exc:
        print("Result: FAILED")
        print(f"Stage: {stage}")
        print(f"Exception: {type(exc).__name__}")
        print(f"Details: {exc}")
        print(
            "This WebDriver error does not, by itself, confirm an HTTP 407 response. "
            "Check browser logs and proxy/provider logs."
        )
        return 1

    except Exception as exc:
        print("Result: FAILED")
        print(f"Stage: {stage}")
        print(f"Exception: {type(exc).__name__}")
        print(f"Details: {exc}")
        return 1

    finally:
        if driver is not None:
            driver.quit()


if __name__ == "__main__":
    sys.exit(main())
