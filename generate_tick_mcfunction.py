# input_file = "ids.txt"  # Change this to your input file path
# output_file = "data\\oneitemlimit\\function\\tick.mcfunction"  # Change this to your output file path

# def main():
#     try:
#         with open(input_file, 'r') as f:
#             ids = [line.strip() for line in f if line.strip()]

#         with open(output_file, 'w') as f:
#             for item_id in ids:
#                 f.write(f"execute as @a store result score @s OneItemLimit run clear @s minecraft:{item_id} 0\n")
#                 f.write(f"execute as @a if score @s OneItemLimit matches 2.. run clear @s minecraft:{item_id} 1\n\n")

#         print(f"tick.mcfunction generated successfully with {len(ids)} IDs.")
#     except Exception as e:
#         print(f"Error: {e}")

# if __name__ == "__main__":
#     main()
#     input("Press Enter to exit...")  # Keeps the window open after running

import json
import logging
import pathlib
import sys
import time
import traceback
import typing
from datetime import datetime

logger = logging.getLogger(__name__)

"""
Python Script Template
"""


def read_text_file_lines(file_path: typing.Union[str, pathlib.Path]) -> typing.List[str]:
    """
    Reads a text file and returns a list of strings with the \n characters at the end of each line removed.
    Includes error checking and logging.

    Args:
    file_path (typing.Union[str, pathlib.Path]): The file path of the text file to read.

    Returns:
    typing.List[str]: A list of strings with the \n characters at the end of each line removed.
    """
    try:
        with open(file_path, 'r') as f:
            lines = [line.strip() for line in f]
        logger.info(f"Successfully read {file_path}")
        return lines
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return []


def read_text_file(file_path: typing.Union[str, pathlib.Path]) -> str:
    """
    Reads a text file and returns its entire contents as a single string.
    Includes error checking and logging.

    Args:
    file_path (typing.Union[str, pathlib.Path]): The file path of the text file to read.

    Returns:
    str: The entire contents of the text file as a single string.
    """
    try:
        with open(file_path, 'r') as f:
            text = f.read()
        logger.info(f"Successfully read {file_path}")
        return text
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return ""


def write_text_file(file_path: typing.Union[str, pathlib.Path], text: str) -> None:
    """
    Writes a string to a text file. Includes error checking and logging.

    Args:
    file_path (typing.Union[str, pathlib.Path]): The file path of the text file to write.
    text (str): A string to write to the text file.
    """
    try:
        with open(file_path, 'w') as f:
            f.write(text)
        logger.info(f"Successfully wrote {file_path}")
    except Exception as e:
        logger.error(f"Error writing {file_path}: {e}")


def write_json_file(data: typing.Union[dict, list], file_path: typing.Union[str, pathlib.Path]) -> None:
    """
    Writes a dictionary or list to a json file. Includes error checking and logging.

    Args:
    data (typing.Union[dict, list]): The data to write to the json file.
    file_path (typing.Union[str, pathlib.Path]): The file path of the json file to write.

    Returns:
    None
    """
    try:
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)
            logger.info(f"Successfully wrote json file: '{file_path}'")
    except IOError:
        logger.error(f"Error writing json file: '{file_path}'")
        raise


def generate_predicate(id):
    if id.startswith("minecraft:"):
        id = id[10:]
    data = {"condition": "minecraft:any_of", "terms": [{"condition": "minecraft:entity_properties", "entity": "this", "predicate": {"slots": {"hotbar.*": {"items": id, "count": {"min": 2}}}}}, {"condition": "minecraft:entity_properties", "entity": "this", "predicate": {"slots": {"inventory.*": {"items": id, "count": {"min": 2}}}}}, {"condition": "minecraft:entity_properties", "entity": "this", "predicate": {"slots": {"weapon.offhand": {"items": id, "count": {"min": 2}}}}}]}
    write_json_file(data, f"data\\oneitemlimit\\predicate\\{id}.json")


def generate_function(id):
    if id.startswith("minecraft:"):
        id = id[10:]
    data = f"clear @s {id} 1\n\nexecute as @s if predicate oneitemlimit:{id} run function oneitemlimit:{id}"
    write_text_file(f"data\\oneitemlimit\\function\\{id}.mcfunction", data)


def main() -> None:
    ids = read_text_file_lines("ids.txt")
    logger.debug(f"{ids=}")

    tickdotmcfunction = ""
    for id in ids:
        generate_predicate(id)
        generate_function(id)
        tickdotmcfunction += f"execute as @a if predicate oneitemlimit:{id} run function oneitemlimit:{id}\n"

    write_text_file("data\\oneitemlimit\\function\\tick.mcfunction", tickdotmcfunction)


def setup_logging(
        logger: logging.Logger,
        log_file_path: typing.Union[str, pathlib.Path],
        console_logging_level: int = logging.DEBUG,
        file_logging_level: int = logging.DEBUG,
        log_message_format: str = "%(asctime)s.%(msecs)03d %(levelname)s [%(funcName)s] [%(name)s]: %(message)s",
        date_format: str = "%Y-%m-%d %H:%M:%S") -> None:
    logger.setLevel(file_logging_level)  # Set the overall logging level

    # File Handler for script-named log file (overwrite each run)
    file_handler = logging.FileHandler(log_file_path, encoding="utf-8", mode="w")
    file_handler.setLevel(file_logging_level)
    file_handler.setFormatter(logging.Formatter(log_message_format, datefmt=date_format))
    logger.addHandler(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_logging_level)
    console_handler.setFormatter(logging.Formatter(log_message_format, datefmt=date_format))
    logger.addHandler(console_handler)

    # Set specific logging levels if needed
    # logging.getLogger("requests").setLevel(logging.INFO)


if __name__ == "__main__":
    script_name = pathlib.Path(__file__).stem
    log_file_name = f"{script_name}.log"
    log_file_path = pathlib.Path(log_file_name)
    setup_logging(logger, log_file_path, log_message_format="%(asctime)s.%(msecs)03d %(levelname)s [%(funcName)s]: %(message)s")

    error = 0
    try:
        start_time = time.perf_counter()
        logger.info("Starting operation...")
        main()
        end_time = time.perf_counter()
        duration = end_time - start_time
        logger.info(f"Completed operation in {duration:.4f}s.")
    except Exception as e:
        logger.warning(f"A fatal error has occurred: {repr(e)}\n{traceback.format_exc()}")
        error = 1
    finally:
        sys.exit(error)
