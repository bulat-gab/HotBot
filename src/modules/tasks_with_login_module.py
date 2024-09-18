import json
import multiprocessing
import os
import shutil
import sys
import time
from typing import Any

from src.exceptions import HotWalletException
from src.services.report import produce_report
from src.services import SeleniumBrowser
from src.utils import get_logger
from src.bots import HotBotBrowser
from src.config import settings
from src.utils import proxy_utils

logger = get_logger()

ACCOUNTS_FILE = "accounts.txt"
SESSIONS_PATH = "./sessions"

def _delete_session(full_path: str):
    try:
        logger.warning(f"Deleting failed session: {full_path}")
        shutil.rmtree(full_path)
    except:
        pass

def _get_existing_sessions() -> list[str]:
    if not os.path.exists(SESSIONS_PATH):
        return []

    dirs = os.listdir(SESSIONS_PATH)
    logger.info(f"Found {len(dirs)} existing sessions.")
    return sorted(dirs)

def _process_session(account: tuple[str, str, str]) -> dict[str, Any]:
    session_name, proxy, seed = account

    session_logger = logger.bind(session_name=session_name)
    session_logger.info(f"Start processing session")
    
    bot = None
    logged_in = False
    full_session_path = os.path.join(os.getcwd(), "sessions", session_name)
    try:
        browser = SeleniumBrowser(full_session_path, HotBotBrowser.HOT_URL, proxy)
        bot = HotBotBrowser(browser)
        logged_in = bot.login(seed)
        if logged_in:
            bot.run_tasks(already_opened=True)

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
        if not logged_in:
            _delete_session(full_session_path)
        
        return _status


def _parse_accounts_file() -> list[tuple[str, str, str]]:
    if not os.path.exists(ACCOUNTS_FILE):
        logger.error(f"File {ACCOUNTS_FILE} not found")
        sys.exit(1)
    
    accounts = []
    with open(ACCOUNTS_FILE, "r") as file:
        for line in file:
            if not line:
                continue
            
            try:
                split = line.split('|')
                session_name = split[0].strip()
                proxy = split[1].strip()
                seed = split[2].strip()

                tup = (session_name, proxy, seed)
                accounts.append(tup)
            except Exception as e:
                logger.error(f"Invalid line: '{line}'. {e}")

        logger.info(f"{ACCOUNTS_FILE} parsed. Found {len(accounts)} accounts.")
        return accounts

def _filter_invalid_accounts(accounts: list[tuple[str, str, str]]) -> list[tuple[str, str, str]]:
    filtered = []

    for i, acc in enumerate(accounts):
        name, proxy, seed = acc

        if " " in name:
            logger.error(f"Line {i+1}. Session name cannot contain whitespace characters: {name}")
            continue
        if proxy and not proxy_utils.is_valid_proxy(proxy):
            logger.error(f"Line {i+1}. Invalid proxy: {proxy}")
            continue
        
        words = seed.split(' ')
        if len(words) != 12:
            logger.error(f"Line {i+1}. Seed must contain 12 words: {seed}")
            continue

        filtered.append((name,proxy,seed))

    logger.info(f"Found {len(filtered)} valid accounts.")
    return filtered

def _remove_existing_sessions(accounts, existing_sessions) -> list[tuple[str, str, str]]:
    filtered = []

    for acc in accounts:
        name, _, _ = acc

        if name in existing_sessions:
            logger.warning(f"Account {name} already exists. It will be skipped")
            continue
        
        filtered.append(acc)

    logger.info(f"After excluding existing accounts: {len(filtered)} accounts left")
    return filtered

def run() -> None:
    start_time = time.time()
    logger.info("Starting tasks with login module")

    accounts = _parse_accounts_file()
    accounts = _filter_invalid_accounts(accounts)
    existing_sessions = _get_existing_sessions()
    accounts = _remove_existing_sessions(accounts, existing_sessions)
    
    tasks = []
    with multiprocessing.Pool(processes=settings.ACTIVE_SESSIONS) as pool:
        for acc in accounts:
            r = pool.apply_async(_process_session, args=(acc,))
            tasks.append(r)

        pool.close()
        pool.join()

    result_list = [t.get() for t in tasks]
    produce_report(result_list)

    elapsed_seconds = int(time.time() - start_time)
    logger.info(f"Tasks --with-login module finished. Elapsed time: {elapsed_seconds} seconds")
    return


