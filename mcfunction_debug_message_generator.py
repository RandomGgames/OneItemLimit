import logging
import os
import pathlib
import re
import socket
import sys
import time
import toml
import traceback
import typing
from datetime import datetime

logger = logging.getLogger(__name__)

"""
Python Script Template

Template includes:
- Configurable logging via config file
- Script run time at the end of execution
- Error handling and cleanup
"""

__version__ = "1.0.1"  # Major.Minor.Patch


def read_toml(file_path: typing.Union[str, pathlib.Path]) -> dict:
    """
    Read configuration settings from the TOML file.
    """
    file_path = pathlib.Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    config = toml.load(file_path)
    return config


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


def write_text_file_lines(file_path: typing.Union[str, pathlib.Path], lines: typing.List[str]) -> None:
    """
    Writes a list of strings to a text file, with each string on a new line.
    Includes error checking and logging.

    Args:
    file_path (typing.Union[str, pathlib.Path]): The file path of the text file to write.
    lines (typing.List[str]): A list of strings to write to the text file.

    Returns:
    None
    """
    try:
        with open(file_path, 'w') as f:
            for line in lines:
                f.write(line + '\n')
        logger.info(f"Successfully wrote {file_path}")
    except Exception as e:
        logger.error(f"Error writing {file_path}: {e}")


def iter_matching_files(root_path, regex_patterns):
    """
    Generator that yields file paths under root_path
    matching any regex in regex_patterns.

    Parameters:
        root_path (str): Base directory to search.
        regex_patterns (list[str]): List of regex strings.
        logger (logging.Logger, optional): Logger instance.

    Yields:
        str: Full path to each matching file.
    """
    compiled = [re.compile(p) for p in regex_patterns]

    logger.info("Starting search in: %s", root_path)
    logger.debug("Patterns: %s", regex_patterns)

    for dirpath, _, filenames in os.walk(root_path):
        logger.debug("Scanning directory: %s", dirpath)
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            normalized = full_path.replace("\\", "/")
            if any(r.search(normalized) for r in compiled):
                logger.debug("Matched file: %s", normalized)
                yield full_path

    logger.info("Finished iterating in: %s", root_path)


def generate_mcfunction_debug_line(mcfunction_path: typing.Union[str, pathlib.Path]) -> str:
    """
    Generates a tellraw line for a Minecraft function file showing its pack and relative path.
    Automatically extracts the pack name from the path.

    Args:
        mcfunction_path: Full path to the mcfunction file.

    Returns:
        str: A tellraw command that prints the function identifier in gray text.
    """
    mcfunction_path = pathlib.Path(mcfunction_path).resolve()
    parts = mcfunction_path.parts

    # Find "data/<namespace>/function/"
    try:
        data_index = parts.index("data")
        namespace = parts[data_index + 1]  # This is the "map" part
        if parts[data_index + 2] != "function":
            raise ValueError(f"Expected 'function' after namespace in {mcfunction_path}")
        relative_parts = parts[data_index + 3:]  # Everything after 'data/<namespace>/function/'
        relative_path = "/".join(relative_parts).removesuffix(".mcfunction")
    except ValueError as e:
        raise ValueError(f"Could not determine function relative path for {mcfunction_path}: {e}")

    return f'tellraw @a[tag=DebugMessages] [{{"text":"{namespace}:{relative_path}","color":"gray"}}]'


def add_or_update_debug_message(mcfunction_path: pathlib.Path) -> None:
    """
    Ensures the mcfunction file starts with a debug message header.

    - Adds a comment line "# Debug Message" if missing.
    - Adds or updates the tellraw line immediately after the comment.

    Args:
        mcfunction_path: Full path to the mcfunction file.

    Returns:
        None
    """
    mcfunction_path = mcfunction_path.resolve()

    # Read existing lines
    lines = read_text_file_lines(mcfunction_path)

    try:
        tellraw_line = generate_mcfunction_debug_line(mcfunction_path)
    except ValueError as e:
        logger.error(f"Could not generate tellraw line for {mcfunction_path}: {e}")
        return

    # Case 1: File empty or first line is not the debug comment
    if not lines or not lines[0].startswith("# Debug Message"):
        new_lines = ["# Debug Message", tellraw_line] + lines
        write_text_file_lines(mcfunction_path, new_lines)
        logger.info(f"Added debug header to {mcfunction_path}")
        return

    # Case 2: First line is debug comment, check the second line
    if len(lines) < 2 or lines[1] != tellraw_line:
        lines[1:2] = [tellraw_line]  # Replace or insert the tellraw line
        write_text_file_lines(mcfunction_path, lines)
        logger.info(f"Updated debug tellraw line in {mcfunction_path}")
        return

    # Case 3: Header already correct, do nothing
    logger.debug(f"{mcfunction_path} debug header already correct. Skipping.")


def main() -> None:
    for mcfunction_path in iter_matching_files(".", [r".*\/(?!tick|load)\w+\.mcfunction$"]):
        mcfunction_path = pathlib.Path(mcfunction_path).resolve()
        logger.debug(f"Processing {mcfunction_path}")
        add_or_update_debug_message(mcfunction_path)


def format_duration_long(duration_seconds: float) -> str:
    """
    Format duration in a human-friendly way, showing only the two largest non-zero units.
    For durations >= 1s, do not show microseconds or nanoseconds.
    For durations >= 1m, do not show milliseconds.
    """
    ns = int(duration_seconds * 1_000_000_000)
    units = [
        ('y', 365 * 24 * 60 * 60 * 1_000_000_000),
        ('mo', 30 * 24 * 60 * 60 * 1_000_000_000),
        ('d', 24 * 60 * 60 * 1_000_000_000),
        ('h', 60 * 60 * 1_000_000_000),
        ('m', 60 * 1_000_000_000),
        ('s', 1_000_000_000),
        ('ms', 1_000_000),
        ('us', 1_000),
        ('ns', 1),
    ]
    parts = []
    for name, factor in units:
        value, ns = divmod(ns, factor)
        if value:
            parts.append(f"{value}{name}")
        # Stop after two largest non-zero units
        if len(parts) == 2:
            break
    if not parts:
        return "0s"
    return "".join(parts)


def setup_logging(
        logger: logging.Logger,
        log_file_path: typing.Union[str, pathlib.Path],
        number_of_logs_to_keep: typing.Union[int, None] = None,
        console_logging_level: int = logging.DEBUG,
        file_logging_level: int = logging.DEBUG,
        log_message_format: str = "%(asctime)s.%(msecs)03d %(levelname)s [%(funcName)s] [%(name)s]: %(message)s",
        date_format: str = "%Y-%m-%d %H:%M:%S") -> None:
    log_file_path = pathlib.Path(log_file_path)
    log_dir = log_file_path.parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # Limit # of logs in logs folder
    if number_of_logs_to_keep is not None:
        log_files = sorted([f for f in log_dir.glob("*.log")], key=lambda f: f.stat().st_mtime)
        if len(log_files) > number_of_logs_to_keep:
            for file in log_files[:-number_of_logs_to_keep]:
                file.unlink()

    # Clear old handlers to avoid duplication
    logger.handlers.clear()
    logger.setLevel(file_logging_level)

    formatter = logging.Formatter(log_message_format, datefmt=date_format)

    # File Handler
    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setLevel(file_logging_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_logging_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


if __name__ == "__main__":
    config_path = pathlib.Path("config.toml")
    if not config_path.exists():
        raise FileNotFoundError(f"Missing {config_path}")
    global config
    config = read_toml(config_path)

    console_logging_level = getattr(logging, config.get("logging", {}).get("console_logging_level", "INFO").upper(), logging.DEBUG)
    file_logging_level = getattr(logging, config.get("logging", {}).get("file_logging_level", "INFO").upper(), logging.DEBUG)
    logs_file_path = config.get("logging", {}).get("logs_file_path", "logs")
    use_logs_folder = config.get("logging", {}).get("use_logs_folder", True)
    number_of_logs_to_keep = config.get("logging", {}).get("number_of_logs_to_keep", 10)
    log_message_format = config.get("logging", {}).get(
        "log_message_format",
        "%(asctime)s.%(msecs)03d %(levelname)s [%(funcName)s]: %(message)s"
    )

    script_name = pathlib.Path(__file__).stem
    pc_name = socket.gethostname()
    if use_logs_folder:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_dir = pathlib.Path(f"{logs_file_path}/{script_name}")
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file_name = f"{timestamp}_{script_name}_{pc_name}.log"
        log_file_path = log_dir / log_file_name
    else:
        log_file_path = pathlib.Path(f"{script_name}_{pc_name}.log")

    setup_logging(
        logger,
        log_file_path,
        console_logging_level=console_logging_level,
        file_logging_level=file_logging_level,
        number_of_logs_to_keep=number_of_logs_to_keep,
        log_message_format=log_message_format
    )

    error = 0
    try:
        start_time = time.perf_counter_ns()
        logger.info(f"Script: {script_name} | Version: {__version__} | Host: {pc_name}")

        main()
        end_time = time.perf_counter_ns()
        duration = end_time - start_time
        duration = format_duration_long(duration / 1e9)
        logger.info(f"Execution completed in {duration}.")
    except KeyboardInterrupt:
        logger.warning("Operation interrupted by user.")
        error = 130
    except Exception as e:
        logger.warning(f"A fatal error has occurred: {repr(e)}\n{traceback.format_exc()}")
        error = 1
    finally:
        for handler in logger.handlers:
            handler.close()
        logger.handlers.clear()
        sys.exit(error)
