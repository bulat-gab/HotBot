import argparse

from src import utils
from src.modules import tasks_module
from src.modules import ui_module
from src.modules import tasks_with_login_module


action_help = \
"""Action to perform \n
    tasks - Begin solving tasks (e.g., watching videos) for existing sessions. Sessions must already be logged in.\n

    tasks --with-login - Perform login first, then solve tasks for accounts listed in accounts.txt.\n

    ui - Launch a browser with a user interface. If no session exists, a new one will be created. Can be used with the --session <SESSION_NAME> argument.\n
"""

logger = utils.get_logger()

def launch() -> None:
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description=action_help)

    sub = parser.add_subparsers(dest="action", help="Specify 'tasks' or 'ui' as the action")

    tasks_parser = sub.add_parser("tasks", help="Solve tasks for existing sessions")
    tasks_parser.add_argument("--with-login", action='store_true', help="Start tasks with login module. Accounts must be placed in accounts.txt file. Ignores --session argument")

    ui_parser = sub.add_parser("ui", help="Launch a browser with UI")
    ui_parser.add_argument("-p", "--proxy", help="Proxy url to be used for a new session")
    
    for p in [tasks_parser, ui_parser]:
        p.add_argument("-s","--session", nargs="+", help="Session names to run, put whitespace between names")
    

    args = parser.parse_args()
    
    action: str = args.action
    sessions: list[str] = args.session

    if action == "tasks":
        if args.with_login:
            tasks_with_login_module.run()
        else:
            tasks_module.run(sessions)
    elif action == "ui":
        proxy: str = args.proxy
        session_name = None
        if sessions:
            session_name = sessions[0]
        ui_module.run(session_name, proxy)
    else:
        logger.error(f"Action is unknown or not provided: {action}.")
        return
    
    logger.info("Execution finished.")