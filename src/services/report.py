from datetime import datetime
import os
import json
import shutil
from typing import Any

from src.utils import get_logger


PATH = "./output"

logger = get_logger()

def produce_report(data: list[dict[str, Any]]):
    file_name = f"report.json"
    file_path = os.path.join(PATH, file_name)

    converted_data = {}
    for item in data:
        converted_data.update(item)

    if not os.path.exists(file_path):
        logger.info(f"Creating a new report file: {file_path}")
        _save_to_file(file_path, converted_data)
        return

    _update_existing(file_path, converted_data)


def _update_existing(file_path: str, new_data: dict[str, Any]):
    logger.info(f"Updating an existing report file: {file_path}")

    with open(file_path, "r") as file:
        try:
            existing_data: dict[str, Any] = json.load(file)
        except json.JSONDecodeError as e:
            logger.error(f"Reports file {file_path} corrupted. str{e}.")
            logger.error(f"Copying its content to a new file.")
            shutil.copy(file_path, f"{file_path}.corrupted")
            
            _save_to_file(file_path, new_data)
            return

        for session_name, session_data in new_data.items():
            existing_data[session_name] = session_data
    
    _save_to_file(file_path, existing_data)


def _save_to_file(file_path: str, data: dict[str, Any]):
    sorted_data = dict(sorted(data.items()))
    
    with open(file_path, "w") as file:
        json.dump(sorted_data, file, indent=4)
        logger.success(f"Report '{file_path}' generated.")
