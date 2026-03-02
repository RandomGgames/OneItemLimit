
# logger = logging.getLogger(__name__)


# def read_toml(file_path: typing.Union[str, pathlib.Path]) -> dict:
#     """
#     Read configuration settings from the TOML file.
#     """
#     file_path = pathlib.Path(file_path)
#     if not file_path.exists():
#         raise FileNotFoundError(f'File not found: "{file_path}"')
#     config = toml.load(file_path)
#     return config


# def generate_item_clear_contents(item_id: str) -> str:
#     string = f'# Debug Message\ntellraw @a[tag=DebugMessages] [{{"text":"oneitemlimit:items/{item_id}","color":"gray"}}]\n\nexecute store result score @s OneItemLimit run clear @s minecraft:{item_id} 0\nexecute if score @s OneItemLimit matches 2.. run clear @s minecraft:{item_id} 1\nexecute if score @s OneItemLimit matches 3.. run function oneitemlimit:items/{item_id}'
#     return string

# def generate_clear_items_function(item_ids: typing.List[str]) -> str:
#     string = f'# Debug Message\ntellraw @a[tag=DebugMessages] [{{"text":"oneitemlimit:clear_items","color":"gray"}}]\n\n'
#     for item_id in item_ids:
#         item_string = f'execute as @s run function oneitemlimit:items/{item_id}\n'
#         string += item_string
#     return string

# def main() -> None:
#     pass


# def format_duration_long(duration_seconds: float) -> str:
#     """
#     Format duration in a human-friendly way, showing only the two largest non-zero units.
#     For durations >= 1s, do not show microseconds or nanoseconds.
#     For durations >= 1m, do not show milliseconds.
#     """
#     ns = int(duration_seconds * 1_000_000_000)
#     units = [
#         ('y', 365 * 24 * 60 * 60 * 1_000_000_000),
#         ('mo', 30 * 24 * 60 * 60 * 1_000_000_000),
#         ('d', 24 * 60 * 60 * 1_000_000_000),
#         ('h', 60 * 60 * 1_000_000_000),
#         ('m', 60 * 1_000_000_000),
#         ('s', 1_000_000_000),
#         ('ms', 1_000_000),
#         ('us', 1_000),
#         ('ns', 1),
#     ]
#     parts = []
#     for name, factor in units:
#         value, ns = divmod(ns, factor)
#         if value:
#             parts.append(f'{value}{name}')
#         if len(parts) == 2:
#             break
#     if not parts:
#         return "0s"
#     return "".join(parts)


# def enforce_max_folder_size(log_dir: pathlib.Path, max_bytes: int) -> None:
#     """
#     Enforce a maximum total size for all logs in the folder.
#     Deletes oldest logs until below limit.
#     """
#     if max_bytes is None:
#         return

#     files = sorted(
#         [f for f in log_dir.glob("*.log*") if f.is_file()],
#         key=lambda f: f.stat().st_mtime
#     )

#     total_size = sum(f.stat().st_size for f in files)

#     while total_size > max_bytes and files:
#         oldest = files.pop(0)
#         try:
#             size = oldest.stat().st_size
#             oldest.unlink()
#             logger.debug(f'Deleted "{oldest}"')
#             total_size -= size
#         except Exception:
#             logger.error(f'Failed to delete "{oldest}"', exc_info=True)
#             continue


# def setup_logging(
#         logger: logging.Logger,
#         log_file_path: typing.Union[str, pathlib.Path],
#         max_folder_size_bytes: typing.Union[int, None] = None,
#         console_logging_level: int = logging.DEBUG,
#         file_logging_level: int = logging.DEBUG,
#         log_message_format: str = "%(asctime)s.%(msecs)03d %(levelname)s [%(funcName)s]: %(message)s",
#         date_format: str = "%Y-%m-%d %H:%M:%S"
# ) -> None:

#     log_file_path = pathlib.Path(log_file_path)
#     log_dir = log_file_path.parent
#     log_dir.mkdir(parents=True, exist_ok=True)

#     logger.handlers.clear()
#     logger.setLevel(file_logging_level)

#     formatter = logging.Formatter(log_message_format, datefmt=date_format)

#     # File Handler
#     file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
#     file_handler.setLevel(file_logging_level)
#     file_handler.setFormatter(formatter)
#     logger.addHandler(file_handler)

#     # Console Handler
#     console_handler = logging.StreamHandler(sys.stdout)
#     console_handler.setLevel(console_logging_level)
#     console_handler.setFormatter(formatter)
#     logger.addHandler(console_handler)

#     if max_folder_size_bytes is not None:
#         enforce_max_folder_size(log_dir, max_folder_size_bytes)


# def load_config(file_path: typing.Union[str, pathlib.Path]) -> dict:
#     file_path = pathlib.Path(file_path)
#     if not file_path.exists():
#         raise FileNotFoundError(f'File not found: "{file_path}"')
#     config = read_toml(file_path)
#     return config


# if __name__ == "__main__":
#     error = 0
#     try:
#         script_name = pathlib.Path(__file__).stem
#         config_path = pathlib.Path(f'{script_name}_config.toml')
#         # config_path = pathlib.Path("config.toml")
#         config = load_config(config_path)

#         logging_config = config.get("logging", {})
#         console_logging_level = getattr(logging, logging_config.get("console_logging_level", "INFO").upper(), logging.DEBUG)
#         file_logging_level = getattr(logging, logging_config.get("file_logging_level", "INFO").upper(), logging.DEBUG)
#         log_message_format = logging_config.get("log_message_format", "%(asctime)s.%(msecs)03d %(levelname)s [%(funcName)s]: %(message)s")
#         logs_folder_name = logging_config.get("logs_folder_name", "logs")
#         max_folder_size_bytes = logging_config.get("max_folder_size", None)

#         pc_name = socket.gethostname()
#         timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#         log_dir = pathlib.Path(logs_folder_name) / script_name
#         log_dir.mkdir(parents=True, exist_ok=True)
#         log_file_name = f'{timestamp}_{script_name}_{pc_name}.log'
#         log_file_path = log_dir / log_file_name

#         setup_logging(
#             logger,
#             log_file_path,
#             max_folder_size_bytes=max_folder_size_bytes,
#             console_logging_level=console_logging_level,
#             file_logging_level=file_logging_level,
#             log_message_format=log_message_format
#         )
#         start_time = time.perf_counter_ns()
#         logger.info(f'Script: "{script_name}" | Version: {__version__} | Host: "{pc_name}"')
#         main()
#         end_time = time.perf_counter_ns()
#         duration = end_time - start_time
#         duration = format_duration_long(duration / 1e9)
#         logger.info(f'Execution completed in {duration}.')
#     except KeyboardInterrupt:
#         logger.warning("Operation interrupted by user.")
#         error = 130
#     except Exception as e:
#         logger.warning(f'A fatal error has occurred: {repr(e)}\n{traceback.format_exc()}')
#         error = 1
#     finally:
#         for handler in logger.handlers:
#             handler.close()
#         logger.handlers.clear()
#         input("Press Enter to exit...")
#         sys.exit(error)

"""
{Script Name}

{Summary of what the script does}

{How to use the script}
"""

import json
import logging
import pathlib
import re
import send2trash
import socket
import sys
import time
import toml
import traceback
import typing
from dataclasses import dataclass, field, asdict
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

logger = logging.getLogger(__name__)

__version__ = "0.0.0"  # Major.Minor.Patch


@dataclass
class ScriptConfig:
    items_path = Path("ids.txt").resolve()


@dataclass
class LoggingConfig:
    mode: str = "per_run"  # single_file | per_run | per_day
    # SN: str = field(default_factory=lambda: input("Please input the SN: "))
    logs_folder_name: str = "logs"
    console_logging_level: str = "DEBUG"
    file_logging_level: str = "DEBUG"
    log_message_format: str = "%(asctime)s.%(msecs)03d %(levelname)s [%(funcName)s] - %(message)s"
    max_files: int | None = 10

    def __post_init__(self):
        if hasattr(self, "SN"):
            sn = (self.SN or "").strip().replace(" ", "_").upper()
            sn = re.sub(r'[<>:"/\\|?*]', "", sn)
            self.SN = sn if sn else "Undefined"

    @property
    def log_file_path(self) -> Path:
        """Generate log path based on mode and optional SN folder."""
        # Base folder
        base_folder = Path(self.logs_folder_name)
        if hasattr(self, "SN") and getattr(self, "SN", None) not in ("", None):
            log_folder = base_folder / self.SN
        else:
            log_folder = base_folder
        log_folder.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pc_name = socket.gethostname()
        if hasattr(self, "SN") and getattr(self, "SN", None) not in ("", None):
            script_name = Path(__file__).stem + "_" + self.SN
        else:
            script_name = Path(__file__).stem

        # Filename depends on mode
        if self.mode == "single_file":
            log_file_name = f"{script_name}__{pc_name}.log"
        elif self.mode == "per_day":
            day_stamp = datetime.now().strftime("%Y%m%d")
            log_file_name = f"{day_stamp}__{script_name}__{pc_name}.log"
        else:  # per_run
            log_file_name = f"{timestamp}__{script_name}__{pc_name}.log"

        return log_folder / log_file_name


@dataclass
class ExitBehaviorConfig:
    pause_on_error: bool = True
    always_pause: bool = False


@dataclass
class Config:
    generate_config_if_missing: bool = False
    script: ScriptConfig = field(default_factory=ScriptConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    exit_behavior: ExitBehaviorConfig = field(default_factory=ExitBehaviorConfig)


def read_text_file_lines(file_path: Path | str) -> list[str]:
    """
    Reads a text file and returns a list of strings with the \n characters at the end of each line removed.
    Includes error checking and logging.

    Args:
    file_path (Path | str): The file path of the text file to read.

    Returns:
    list[str]: A list of strings with the \n characters at the end of each line removed.
    """
    try:
        file_path = Path(file_path)
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created folder: {json.dumps(str(file_path.parent))}")
        with open(file_path, "r", encoding="utf-8") as f:
            text_lines = [line.rstrip("\n\r") for line in f]
        logger.info(f"Successfully read {json.dumps(str(file_path))}")
        return text_lines
    except FileNotFoundError:
        logger.error(f"File not found: {json.dumps(str(file_path))}")
        return []
    except PermissionError:
        logger.error(f"Permission denied: {json.dumps(str(file_path))}")
        return []
    except OSError as e:
        logger.error(f"Error reading {json.dumps(str(file_path))}", e)
        return []


def write_text_file_lines(file_path: Path | str, lines: list[str]) -> None:
    """
    Writes a list of strings to a text file, with each string on a new line.
    Includes error checking and logging.

    Args:
    file_path (Path | str): The file path of the text file to write.
    lines (list[str]): A list of strings to write to the text file.

    Returns:
    None
    """
    try:
        file_path = Path(file_path)
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created folder: {json.dumps(str(file_path.parent))}")
        with open(file_path, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")
        logger.info(f"Successfully wrote {json.dumps(str(file_path))}")
    except FileNotFoundError:
        logger.error(f"File not found: {json.dumps(str(file_path))}")
    except PermissionError:
        logger.error(f"Permission denied: {json.dumps(str(file_path))}")
    except OSError as e:
        logger.error(f"Error writing {json.dumps(str(file_path))}", e)


def main(Config: Config):
    item_ids_path = Config.script.items_path
    item_ids = read_text_file_lines(item_ids_path)
    for item_id in item_ids:
        mcfunction_path = f"data/oneitemlimit/function/items/{item_id}.mcfunction"
        data = [
            f"execute store result score @s OneItemLimit run clear @s minecraft:{item_id} 0",
            "execute store result storage minecraft:oneitemlimit count int 1 run scoreboard players operation @s OneItemLimit -= #Remaining OneItemLimit",
            f"data modify storage oneitemlimit item set value \"minecraft:{item_id}\"",
            "execute if score @s OneItemLimit matches 2.. run function oneitemlimit:clear_all_but_1 with storage minecraft:oneitemlimit",
        ]


def save_default_config(file_path: Path, config: Config):
    """Save JSON config based on dataclass defaults."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(asdict(config), f, indent=4)


def load_config(file_path: Path, generate_if_missing: bool = True) -> Config:
    """
    Load configuration from JSON file.
    If missing and generate_if_missing=True, auto-generate.
    If missing and generate_if_missing=False, use dataclass defaults.
    Any missing keys in existing JSON are filled from dataclass defaults.
    """
    def merge_defaults(dataclass_type, data: dict):
        """Fill missing keys from dataclass defaults."""
        defaults = asdict(dataclass_type())
        merged = {**defaults, **data}  # Python 3.9+ can also use defaults | data
        return dataclass_type(**merged)

    if not file_path.exists():
        config = Config()
        if generate_if_missing:
            save_default_config(file_path, config)
        return config

    with file_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # Merge defaults for each section
    logging_cfg = merge_defaults(LoggingConfig, data.get("logging", {}))
    exit_cfg = merge_defaults(ExitBehaviorConfig, data.get("exit_behavior", {}))

    # ScriptConfig is currently empty; merge if fields are added later
    script_cfg = ScriptConfig()

    config = Config(
        logging=logging_cfg,
        exit_behavior=exit_cfg,
        script=script_cfg,
        generate_config_if_missing=data.get("generate_config_if_missing", True)
    )

    # Optionally overwrite JSON with missing keys filled in
    if generate_if_missing:
        save_default_config(file_path, config)

    return config


def enforce_max_log_count(dir_path: Path | str, max_count: int | None, script_name: str):
    """
    Keep only the N most recent logs for this script.

    Oldest files are deleted first, based on modification time.

    Args:
        dir_path (Path | str): Directory containing log files.
        max_count (int | None): Maximum number of log files to keep. None = no limit.
        script_name (str): Filter logs by this script name.
    """
    if max_count is None or max_count <= 0:
        return

    dir_path = Path(dir_path)
    # Get all matching log files
    files = [f for f in dir_path.glob(f"*{script_name}*.log") if f.is_file()]

    # Sort by modification time (oldest first)
    files.sort(key=lambda f: f.stat().st_mtime)

    # Delete excess files
    if len(files) > max_count:
        to_delete = files[:len(files) - max_count]  # oldest files
        for f in to_delete:
            try:
                send2trash.send2trash(f)
                logger.debug(f"Deleted old log: {f.name}")
            except OSError as e:
                logger.error(f"Failed to delete {f.name}: {e}")


def setup_logging(logger_obj: logging.Logger, config: LoggingConfig) -> Path:
    """Set up file and console logging based on AppConfig."""
    log_path = config.log_file_path

    logger_obj.handlers.clear()
    logger_obj.setLevel(getattr(logging, config.file_logging_level.upper(), logging.INFO))

    formatter = logging.Formatter(
        config.log_message_format,
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    if config.mode == "per_day":
        # Automatic midnight rotation
        file_handler = TimedRotatingFileHandler(
            log_path,
            when="midnight",
            interval=1,
            backupCount=config.max_files if config.max_files else 0,
            encoding="utf-8",
        )
    else:
        # per_run or single_file
        file_mode = "w" if config.mode == "per_run" else "a"
        file_handler = logging.FileHandler(
            log_path,
            mode=file_mode,
            encoding="utf-8",
        )

    file_handler.setLevel(getattr(logging, config.file_logging_level.upper(), logging.INFO))
    file_handler.setFormatter(formatter)
    logger_obj.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, config.console_logging_level.upper(), logging.INFO))
    console_handler.setFormatter(formatter)
    logger_obj.addHandler(console_handler)

    return log_path


def bootstrap():
    exit_code = 0
    try:
        script_path = Path(__file__)
        config_path = script_path.with_name(f"{script_path.stem}_config.json")
        config = load_config(config_path, generate_if_missing=Config.generate_config_if_missing)

        setup_logging(logger, config.logging)  # just pass the logging config

        logger.info(f"Script: {script_path.stem}")
        logger.info(f"Version: {__version__}")
        logger.info(f"Host: {socket.gethostname()}")
        logger.info(f"AppConfig: {config}")

        main(config)

    except KeyboardInterrupt:
        logger.warning("Operation interrupted by user.")
        exit_code = 130
    except Exception as e:
        logger.exception(f"A fatal error has occurred: {e}")
        exit_code = 1
    finally:
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

    if config.exit_behavior.always_pause or (config.exit_behavior.pause_on_error and exit_code != 0):
        input("Press Enter to exit...")

    return exit_code


if __name__ == "__main__":
    sys.exit(bootstrap())
