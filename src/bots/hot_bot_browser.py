from datetime import datetime
import time
from typing import Optional, Union
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException

from src.exceptions import HotWalletException
from src.services import SeleniumBrowser
from src.bots import get_codeword, get_first_line
from src.config import settings

class HotBotBrowser:
    HOT_URL = "https://my.herewallet.app/hot"

    def __init__(self, browser: SeleniumBrowser):
        self.start_app_xpath = "//div[contains(., 'Open Wallet')]"
        self.iframe_xpath = "//iframe[@src='/']"

        self.is_logged_in: Optional[bool] = None

        self.browser = browser
        self.logger = browser.logger

        self.tasks: list[str] = [] # names of tasks
        self.unfinished_tasks: list[str] = []
        self.finished_tasks: list[str] = []

    def _open_app(self):
        if not self.browser.select_iframe(self.iframe_xpath):
            msg = "Could not open Hot Wallet app"
            self.logger.critical(msg)
            raise HotWalletException(msg)
    
    def _open_tasks_page(self) -> bool:
        self.logger.debug("open_tasks_page")

        xpath = "//h4[contains(text(), 'HOT Balance')]"
        target_element = self.browser.move_and_click(xpath, 10, "Click fireplace 'HOT Balance'")
        if not target_element:
            return False
        
        self.is_logged_in = True # If we opened HOT Balance, that means login is successful
        xpath = "//p[contains(text(), 'Missions')]"
        target_element = self.browser.move_and_click(xpath, 10, "Click missions")
        if not target_element:
            return False

        xpath = "//h3[contains(text(), 'Explore crypto')]"
        target_element = self.browser.move_and_click(xpath, 10, "Open 'Explore crypto' mission")
        if not target_element:
            return False

        return True

    def _get_tasks_list(self, only_not_completed: bool = False) -> list[WebElement]:
        xpath = "//div[p[contains(text(), 'Show all videos')]]"
        show_all_videos_button = self.browser.move_and_click(xpath, 10, "Click 'Show all videos'")

        xpath = "//p[contains(text(), 'Watch educational videos')]/following-sibling::div[2]"
        tasks_container = self.browser.get_element(xpath)
        task_divs = tasks_container.find_elements(By.XPATH, "./div")

        task_divs = task_divs[1:] # first element is not a task
        if "Show less videos" in task_divs[-1].text:
            task_divs = task_divs[:-1]

        if only_not_completed:
            return [t for t in task_divs if "Completed" not in t.text]

        return task_divs

    def _solve_task(self, task_div: WebElement) -> bool:
        if not task_div:
            self.logger.error("solve_task() received None instead of task element.")
            return False

        video_name = get_first_line(task_div.text)

        if self._is_mission_completed(task_div):
            self.logger.debug(f"Task '{video_name}' is already completed. Moving to the next one.")
            return True

        self.logger.info(f"Solving task '{video_name}'")

        codeword = get_codeword(video_name)
        self.logger.debug(f"Codeword is '{codeword}'")
        if not codeword:
            self.logger.critical(f"STATUS: Could not find a codeword for the video task '{video_name}'")
            return False

        self.browser.scroll_to_element(task_div)
        task_div.click()

        xpath = "//button[contains(text(), 'Watch the video')]"
        target_element = self.browser.move_and_click(xpath, 15, f"Click 'Watch the video'")
        
        time.sleep(5) # Let the YouTube video open

        self.browser.close_tab() # Close YouTube tab
        self.browser.select_iframe(self.iframe_xpath)

        xpath = "//button[contains(text(), 'Submit password')]"
        target_element = self.browser.move_and_click(xpath, 15,  f"Click 'Submit password'")

        xpath = "//h2[contains(text(), 'Enter the password')]/following-sibling::label"
        elements = self.browser._driver.find_elements(By.XPATH, xpath)
        elements[0].send_keys(codeword)

        xpath = "//button[contains(text(), 'Submit password')]"
        target_element = self.browser.move_and_click(xpath, 15,  f"Click 'Submit password after entering a codeword'")

        xpath = "//h3[contains(text(), 'You got')]/following-sibling::div//div"
        target_element = self.browser.get_element(xpath, settings.TIMEOUT, f"Waiting {settings.TIMEOUT} seconds for the mission to complete.")
        if not target_element:
            self.logger.warning(f"Could not complete mission {video_name}")
            return

        self.logger.success(f"Mission watch video '{video_name}' completed. Reward: {target_element.text}")
        return True

    def _is_mission_completed(self, task_div: WebElement) -> Optional[bool]:
        return task_div and "Completed" in task_div.text

    def _solve_tasks(self):
        task_divs = self._get_tasks_list()

        for div in task_divs:
            task_name = get_first_line(div.text)
            self.tasks.append(task_name)

            if "Completed" in div.text:
                self.finished_tasks.append(task_name)
            else:
                self.unfinished_tasks.append(task_name)

        self.logger.info(f"STATUS: total tasks available: '{len(self.tasks)}'")
        self.logger.info(f"STATUS: unfinished tasks: '{len(self.unfinished_tasks)}'")

        if len(self.tasks) == len(self.finished_tasks):
            self.logger.success(f"STATUS: all tasks finished.")
            return
        
        task_divs = [t for t in task_divs if "Completed" not in t.text] # leave only not completed
        unfinished_count = len(self.unfinished_tasks)
        for i in range(unfinished_count):
            try:
                self.logger.info(f"Processing task {i+1} out of {unfinished_count}.")
                name = get_first_line(task_divs[0].text)

                result = self._solve_task(task_divs[0])
                if result:
                    self.finished_tasks.append(name)
                    self.unfinished_tasks.remove(name)
                
            except Exception as e:
                pass
            
            if len(self.finished_tasks) == len(self.tasks):
                return

             # refresh and start over
            self.browser.refresh()
            self.browser.wait_for_page(3)
            self._open_app()
            self._open_tasks_page()
            task_divs = self._get_tasks_list(only_not_completed=True)
            
    def run_tasks(self, already_opened: bool = False):
        if not already_opened:
            self.logger.info(f"Opening HOT wallet")
            self._open_app()

        self.browser.wait_for_page(settings.TIMEOUT) # Openning HOT Wallet for the first time takes more time
        self.logger.info(f"Opening tasks page")
        opened = self._open_tasks_page()
        if not opened:
            self.logger.error(f"Could not open tasks page")

        self._solve_tasks()

    def login(self, seed_phrase: str) -> bool:
        self.logger.info("Started login process.")

        try:
            import_account_xpath = "//button[p[contains(., 'Import account')]]"

            if not self.browser.select_iframe_and_wait(self.iframe_xpath, import_account_xpath):
                msg = "Could not open Hot Wallet app or it's already logged in."
                self.logger.critical(msg)
                raise HotWalletException(msg)
            
            log_level="INFO"
            target_element = self.browser.move_and_click(import_account_xpath, 20, "Click Import account", log_level=log_level)

            xpath = "//p[contains(text(), 'Seed or private key')]/ancestor-or-self::*/textarea"
            input_field = self.browser.move_and_click(xpath, 10, "Locate seedphrase textbox")
            input_field.send_keys(seed_phrase)

            xpath = "//button[contains(text(), 'Continue')]"
            self.browser.move_and_click(xpath, 30, "Click continue after seedphrase entry", log_level=log_level)

            xpath = "//button[contains(text(), 'Continue')]"
            self.browser.move_and_click(xpath, 180, "Click continue at account selection screen and wait 180s to load.")

            xpath = "//h4[text()='Storage']"
            self.browser.get_element(xpath, 30, "Find 'storage' button. Make sure login was successful", log_level=log_level)

            self.is_logged_in = True
            self.logger.success(f"STATUS: login successful")
            return True
        except Exception as e:
            self.logger.critical(f"STATUS: login failed. {str(e)}")
            self.is_logged_in = False
            return False

    def status(self) -> dict[str, Union[str, int]]:
        result = {}
        _status = {
            self.browser.session: result
        }
        
        if not self.is_logged_in:
            result["login"] = "Error"
            return _status
        else:
            result["login"] = "OK"


        tasks_count = len(self.tasks)
        finished_count = len(self.finished_tasks)

        status = None
        if tasks_count == 0:
            status = "Error"
            self.logger.error(f"STATUS: Tasks count is 0. Must be error during session execution.")
        elif tasks_count == finished_count:
            status = "OK"
            self.logger.success(f"STATUS: All {finished_count} tasks have been completed.")
        else:
            status = "Error"
            self.logger.error(f"STATUS: {finished_count} out of {tasks_count} tasks have been completed.")

        result["Explore crypto"] = {
                "status": status,
                "total_tasks": tasks_count,
                "finished_tasks": finished_count,
                "date": datetime.now().strftime("%d-%b-%Y %H:%M")
        }
        return _status