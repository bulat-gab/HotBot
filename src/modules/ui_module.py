import os
from typing import Optional

from src.services import SeleniumBrowser
from src.utils import get_logger
from src.bots import HotBotBrowser
from src.config import settings
from src.utils import proxy_utils

logger = get_logger()

def _create_session(session_name: str):
    try:
        full_session_path = os.path.join(os.getcwd(), "sessions", session_name)
        
        proxy = None
        try:
            proxy = proxy_utils.get_proxy_from_file(os.path.join(full_session_path, "proxy.txt"))
        except FileNotFoundError:
            logger.warning(f"Proxy file not found. Starting session without proxy")
            pass

        settings.HEADLESS = False
        browser = SeleniumBrowser(full_session_path, HotBotBrowser.HOT_URL, proxy)
        input("Waiting for the user... Press enter to close browser")
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.critical(f"{type(e).__name__} occured during create session. {e}")
    finally:
        if browser:
            browser.quit()

def _exist(session) -> bool:
    existing = os.listdir("./sessions")
    return session in existing

def run(session_name: Optional[str] = None, proxy: Optional[str] = None) -> None:
    if not session_name:
        session_name = input("Enter session name (example 'HOT_tg001'): ")
    
    if _exist(session_name):
        logger.info(f"Found existing session '{session_name}'. Starting it.")
        _create_session(session_name)
        return

    logger.info(f"Session '{session_name}' not found. Creating a new one.")
    os.makedirs(f"./sessions/{session_name}")

    if not proxy:
        proxy = input("Enter proxy url (example 'socks5://user123:password123@100.100.100.170:5050') or type 'no' to continue without proxy: ")

    if proxy == "no":
        logger.warning("Proceeding without proxy.")
        _create_session(session_name)
        return

    proxy_utils.ensure_valid_proxy(proxy)
    proxy_path = os.path.join("./sessions", session_name, "proxy.txt")
    proxy_utils.save_proxy_to_file(proxy_path, proxy)
    _create_session(session_name)
