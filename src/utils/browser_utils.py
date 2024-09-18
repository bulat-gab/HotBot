from selenium.webdriver.chromium.options import ChromiumOptions

def add_default_chrome_options(chrome_options: ChromiumOptions) -> ChromiumOptions:
    chrome_options.add_argument("--no-sandbox")  # disables the sandbox for Chrome
    chrome_options.add_argument("--disable-dev-shm-usage")  # disables the use of /dev/shm, useful for Docker
    chrome_options.add_argument('--log-level=1')  # log only WARNING level logs and above
    chrome_options.add_argument("--disable-blink-features=AutomationControlled") # Prevents detection of Selenium
    chrome_options.add_argument("--ignore-certificate-errors") # disables SSL certificate warnings
    chrome_options.add_argument("--allow-running-insecure-content") #  allows HTTP content on HTTPS pages
    chrome_options.add_argument("--test-type") # bypass unnecessary warnings
    return chrome_options

def get_selenium_wire_proxy_options(proxy_url: str) -> dict[str, dict[str, str]]:
    seleniumwire_options = {
        "proxy": {
            "http": f"{proxy_url}",
            "https": f"{proxy_url}"
        },
    }

    return seleniumwire_options
                