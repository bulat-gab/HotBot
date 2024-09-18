import random
import json
import time
from typing import Optional

from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import (
    NoSuchElementException, 
    TimeoutException, 
    StaleElementReferenceException, 
    ElementClickInterceptedException)
from selenium.webdriver.chrome.options import Options

from src.exceptions import HotWalletException
from src.utils import proxy_utils
from src.config import settings
from src import utils
from src.utils.user_agents import get_random_chrome_user_agent

class SeleniumBrowser:
    def __init__(self, session_path: str, url: str, proxy_url: str = None) -> None:
        self.session_path = session_path
        self.session = session_path.split("/")[-1]
       
        self.start_url = url

        if proxy_url:
            proxy_utils.ensure_valid_proxy(proxy_url)
        self.proxy_url = proxy_url

        self.logger = utils.get_logger(self.session)

        self._driver = self._setup_driver()

    def success(self, log):
        self.logger.success(log)

    def info(self, log):
        self.logger.info(log)
    
    def error(self, log):
        self.logger.error(log)

    def debug(self, log):
        self.logger.debug(log)

    def warning(self, log):
        self.logger.warning(log)

    def critical(self, log):
        self.logger.critical(log)

    def quit(self) -> None:
        if self._driver:
            self._driver.quit()

    def refresh(self):
        self._driver.refresh()

    def wait_until_disappears(self, xpath, wait_time = 10, action_description = "") -> bool:
        if not action_description:
             action_description = xpath

        wait = WebDriverWait(self._driver, wait_time)
        target_element = wait.until(EC.invisibility_of_element_located((By.XPATH, xpath)))
        if target_element:
            self.debug(f"Element {xpath} is still present.")
            return False
        
        return True

    def click_element(self, xpath, timeout=30, action_description="") -> bool:
        try:
            wait = WebDriverWait(self._driver, timeout)
            element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

            action = ActionChains(self._driver)
            action.move_to_element(element).perform()
            time.sleep(random.uniform(0.5, 1.5))  # Small delay before clicking
            element.click()
            
            return True
        
        except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e:
            self.error(f"'{type(e).__name__}' occured during {action_description}. {str(e)}")
            return False
    
    def move_and_click(self, xpath: str, 
                       wait_time: int = 10, 
                       action_description: str = None,
                       log_level: str = "DEBUG") -> Optional[WebElement]:
        return self.get_element(xpath, wait_time=wait_time, action_description=action_description, click=True, log_level=log_level)

    def get_element(self, xpath: str, 
                    wait_time: int = 10, 
                    action_description: str = None, 
                    click: bool = False, 
                    log_level="DEBUG") -> Optional[WebElement]:
        if not self.page_has_loaded():
            time.sleep(5) # extra delay
        
        if not action_description:
            action_description = xpath

        self.logger.log(log_level, action_description)
        time.sleep(random.uniform(1, 3)) # random delay

        wait = WebDriverWait(self._driver, wait_time)
        try:
            target_element = wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))

            if target_element is None:
                self.debug(f"Element not found for action: {action_description}")
                return None

            self.scroll_to_element(target_element)

            if click:
                self.debug(f"click element {xpath}.")
                if self.click_element(xpath, action_description=action_description):
                    self.debug(f"Clicked successfully {action_description}")
                    return target_element
            else:
                return target_element

        
        except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
            self.debug(f"{type(e).__name__} occured during {action_description}")
            raise
        except Exception as e:
            self.debug(f"{type(e).__name__} occured during {action_description}. {str(e)}")
            raise

    def select_iframe(self, xpath) -> bool:
        try:
            wait = WebDriverWait(self._driver, 20)

            iframe = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            self._driver.switch_to.frame(iframe)

            self.debug(f"Successfully switched to iframe '{xpath}'.")
            return True
        except Exception as e:
            self.error(f"Could not switch to app's iFrame. {str(e)}")
            return False

    def select_iframe_and_wait(self, xpath, element_inside_iframe_xpath, wait_time=30) -> bool:
        try:
            wait = WebDriverWait(self._driver, wait_time)
            iframe = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            self._driver.switch_to.frame(iframe)

            # Wait for a specific element inside the iframe to ensure the content is fully loaded
            wait.until(EC.visibility_of_element_located((By.XPATH, element_inside_iframe_xpath)))

            self.debug(f"Successfully switched to iframe and waited for element within '{xpath}'.")
            return True
        except Exception as e:
            self.error(f"Could not switch to iframe or wait for element. {e}")
            return False

    def scroll_to_element(self, element: WebElement) -> bool:
        """
            Scroll element into view if it's not visible. Telegram mini apps have limited size windows.
            Clicking/selecting an element when it's not in a viewport will not work.

            @returns whether the element is in a viewport or not.
        """

        is_in_viewport = self._driver.execute_script("""
            var elem = arguments[0], box = elem.getBoundingClientRect();
            if (!(box.top >= 0 && box.left >= 0 &&
                box.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                box.right <= (window.innerWidth || document.documentElement.clientWidth))) {
                elem.scrollIntoView({block: 'center'});
                return false;
            }
            return true;
        """, element)

        return is_in_viewport
    
    def close_tab(self, action_description = None) -> None:
        if not action_description:
            action_description = "Trying to close tab"

        tabs =  self._driver.window_handles
        self.debug(f"{action_description}. {len(tabs)} tabs are currently open.")
        if len(tabs) == 1:
            return

        current_tab = tabs[0]

        self.debug(f"Closing the last tab")
        self._driver.switch_to.window(tabs[-1])
        self._driver.close()
        self._driver.switch_to.window(current_tab)
    
    def page_has_loaded(self) -> bool:
        return self._driver.execute_script("return document.readyState;") == "complete"

    def wait_for_page(self, wait_time = 30) -> bool:
        try:
            self.info(f"Wait {wait_time} seconds for the page to load.")
            result = WebDriverWait(self._driver, wait_time).until(lambda d: self.page_has_loaded())
            return True
        except TimeoutException:
            self.error(f"Page was not loaded after {wait_time} seconds")
            return False

    def _setup_driver(self) -> webdriver.Chrome:
        chrome_options = Options()
        chrome_options = utils.add_default_chrome_options(chrome_options)        
        chrome_options.add_argument(f"--user-data-dir={self.session_path}")  # Use a specific user data directory
        chrome_options.add_argument(f"--user-agent={get_random_chrome_user_agent()}")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--start-maximized") # HTML elements are not properly located otherwise.

        if settings.CHROME_PATH:
            chrome_options.binary_location = settings.CHROME_PATH

        if settings.HEADLESS:
            chrome_options.add_argument("--headless")  # no UI mode

        try:
            self.info(f"Setting up Selenium Chrome Driver. Proxy url: {self.proxy_url}")
            selenium_wire_options = None if not self.proxy_url else utils.get_selenium_wire_proxy_options(self.proxy_url)
      
            if settings.DISABLE_WEBRTC:
                chrome_options.add_argument(f"--load-extension={settings.WEBRTC_EXTENSION_PATH}")

            if settings.CHROME_DRIVER_PATH:
                service = Service(settings.CHROME_DRIVER_PATH)

                self._driver = webdriver.Chrome(
                    service=service,
                    seleniumwire_options=selenium_wire_options,
                    options=chrome_options)
            else:
                self._driver = webdriver.Chrome(seleniumwire_options=selenium_wire_options, options=chrome_options)
            
            # Save proxy url to file
            if self.proxy_url:
                proxy_utils.save_proxy_to_file(f"{self.session_path}/proxy.txt", self.proxy_url)

             # TODO: add timezones
            tz_params = {'timezoneId': 'Europe/Amsterdam'} # Browser timezone
            self._driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)

            ua = self._driver.execute_script("return navigator.userAgent")
            self.info(f"Browser started. User-Agent: {ua}")
            
            if settings.DISABLE_WEBRTC:
                self._disable_webrtc()

            if settings.VERIFY_PROXY:
                self._verify_proxy()

            self._driver.get(self.start_url)
            return self._driver
        
        except Exception as e:
            self.error(f"ChromeDriver setup failed: {str(e)}")
            raise HotWalletException()

    def _verify_proxy(self) -> bool:
        try:
            if not self.proxy_url:
                msg = f"Proxy url was not provided."
                self.critical(msg)
                raise HotWalletException(msg)

            self._driver.get("https://httpbin.io/ip")
            content = self._driver.find_element(By.TAG_NAME, "pre").text
            origin = json.loads(content).get("origin")

            real_ip_addr = proxy_utils.extract_ip(origin)
            my_ip = proxy_utils.extract_ip(self.proxy_url)

            if real_ip_addr != my_ip:
                msg = f"Proxy did not work. Expected IP address: '{my_ip}'. Real IP address: '{real_ip_addr}' (from ifconfig.me)."
                self.critical(msg)
                raise HotWalletException(msg)

            self.info(f"Proxy check was successful. Your IP: {real_ip_addr}")
            return True
        except Exception as e:
            msg = f"IP check failed. {str(e)}"
            self.critical(msg)
            raise HotWalletException(msg)

    def _disable_webrtc(self):
        """Prevent real IP address leak when using Proxy

        Uses WebRTC Network Limiter extension: https://chromewebstore.google.com/detail/webrtc-network-limiter/npeicpdbkakmehahjeeohfdhnlpdklia
        The extension configuration must be set to 'disable_non_proxied_udp', other options will not prevent the IP leak

        Make sure self.driver is created
        """
        try:
            extension_options_page = "chrome-extension://npeicpdbkakmehahjeeohfdhnlpdklia/options.html"
            self._driver.get(extension_options_page)

            label_id = "for_disable_non_proxied_udp"
            target_element = self._driver.find_element(By.ID, label_id)
            target_element.click()
            self.info(f"WebRTC disabled.")
        except Exception as e:
            msg = f"Could not disable web rtc. {str(e)}"
            self.critical(msg)
            raise HotWalletException(msg)
        