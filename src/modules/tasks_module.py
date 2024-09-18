import json
import multiprocessing
import os
import time

from src.exceptions import HotWalletException
from src.services.report import produce_report
from src.services import SeleniumBrowser
from src.utils import get_logger
from src.bots import HotBotBrowser
from src.config import settings
from src.utils import proxy_utils

logger = get_logger()

"""This module will use existing sessions from ./sessions folder.
Accounts must be logged in already.
"""


def _get_sessions() -> list[str]:
    dirs = os.listdir("./sessions")
    logger.info(f"Found {len(dirs)} sessions.")
    return sorted(dirs)

def _process_session(session_name: str):
    session_logger = logger.bind(session_name=session_name)
    session_logger.info(f"Start processing session")
    
    bot = None
    try:
        full_session_path = os.path.join(os.getcwd(), "sessions", session_name)

        proxy = None

        try:
            proxy = proxy_utils.get_proxy_from_file(os.path.join(full_session_path, "proxy.txt"))
        except FileNotFoundError:
            session_logger.warning(f"Proxy file not found. Starting session without proxy")
            pass

        browser = SeleniumBrowser(full_session_path, HotBotBrowser.HOT_URL, proxy)
        bot = HotBotBrowser(browser)
        bot.run_tasks()
    except HotWalletException as e:
        session_logger.error(f"Session {session_name} has failed. {e}")
    except Exception as e:
        session_logger.error(f"Session {session_name} has failed. {e}")
    finally:
        if browser:
            browser.quit()

        _status = None
        if bot:
            _status = bot.status()
            return _status


def run(sessions_to_run) -> None:
    start_time = time.time()
    logger.info("Starting tasks module")

    sessions = _get_sessions()
    
    if not sessions_to_run:
         sessions_to_run = sessions
    else:
         sessions_to_run = list(set(sessions) & set(sessions_to_run)) # run only specified sessions (if they exist in the ./sesions path)

    logger.info(f"{len(sessions_to_run)} will be processed.")

    tasks = []
    with multiprocessing.Pool(processes=settings.ACTIVE_SESSIONS) as pool:
        for s in sessions_to_run:
            r = pool.apply_async(_process_session, args=(s,))
            tasks.append(r)

        pool.close()
        pool.join()

    result_list = [t.get() for t in tasks]
    produce_report(result_list)

    elapsed_seconds = int(time.time() - start_time)
    logger.info(f"Tasks module finished. Elapsed time: {elapsed_seconds} seconds")
    return


