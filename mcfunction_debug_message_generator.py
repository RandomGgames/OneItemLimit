"""
mcfunction_debug_message_generator

Automatically scans all .mcfunction files in the current working directory and its subdirectories,
and ensures that each file has a standardized debug header at the top. The header includes:
1. A comment line "# Debug Message"
2. A tellraw command that broadcasts the namespace and function path to players with the DebugMessages tag
3. A blank line separating the header from the rest of the file

If the header is missing, it will be added. If the header exists but is outdated, it will be updated.
All other content in the file is left unchanged. Files that already have the correct header remain unmodified.

Usage:
- Configure the script using the Config dataclass if needed
- Run the script in the directory containing your Minecraft datapacks
- The script will log each file processed, indicating whether the header was added, updated, or unchanged
"""

import json
import logging
import re
import send2trash
import socket
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Iterator, Iterable

logger = logging.getLogger(__name__)

__version__ = "2.0.0"  # Major.Minor.Patch


@dataclass
class ScriptConfig:
    file_extension = r"\.mcfunction$"
    excluded_files = [
        "tick.mcfunction",
        "load.mcfunction",
    ]


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
    script: ScriptConfig = field(default_factory=ScriptConfig)
    generate_config_if_missing: bool = False
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    exit_behavior: ExitBehaviorConfig = field(default_factory=ExitBehaviorConfig)


def iter_files_regex(
    pattern: str,
    exclude_names: Iterable[str] | None = None,
) -> Iterator[Path]:
    """
    Recursively yield files in the current working directory whose
    *filename* matches the given regex pattern, excluding any exact
    filenames listed in exclude_names.

    Args:
        pattern: Regex pattern applied to the file name (not full path).
        exclude_names: Iterable of exact filenames to exclude.

    Yields:
        Path objects, one at a time.
    """
    compiled = re.compile(pattern, re.IGNORECASE)
    excluded = {name.lower() for name in exclude_names or []}

    for path in Path.cwd().rglob("*"):
        if not path.is_file():
            continue

        name = path.name
        if name.lower() in excluded:
            continue

        if compiled.search(name):
            yield path


def update_debug_header(file_path: Path) -> None:
    """
    Ensure the .mcfunction file has the correct debug header.
    Directly logs whether the header was added, updated, or unchanged.
    """

    original_text = file_path.read_text(encoding="utf-8")
    lines = original_text.splitlines()

    # --- Extract namespace (folder after "data")
    parts = file_path.parts
    try:
        data_index = parts.index("data")
        namespace = parts[data_index + 1]
    except (ValueError, IndexError):
        logger.warning(f"Cannot determine namespace from: {file_path}")
        return

    # --- Extract function path (after "function")
    try:
        func_index = parts.index("function")
        relative_parts = parts[func_index + 1:]
    except ValueError:
        logger.warning(f"Cannot determine function path from: {file_path}")
        return

    relative_parts = list(relative_parts)
    relative_parts[-1] = Path(relative_parts[-1]).stem
    function_path = "/".join(relative_parts)

    expected_tellraw = (
        f'tellraw @a[tag=DebugMessages] '
        f'[{{"text":"{namespace}:{function_path}","color":"gray"}}]'
    )

    expected_header = [
        "# Debug Message",
        expected_tellraw,
        "",
    ]

    # --- Detect existing header
    has_header = len(lines) >= 1 and lines[0].startswith("# Debug Message")

    if has_header:
        current_header = lines[:3]
        if current_header == expected_header:
            logger.debug(f"[UNCHANGED] {file_path}")
            return

        # Something differs → update
        changes = []
        if len(lines) >= 2 and lines[1] != expected_tellraw:
            changes.append(f'tellraw changed from "{lines[1]}" to "{expected_tellraw}"')

        new_content = "\n".join(expected_header + lines[3:]) + "\n"
        file_path.write_text(new_content, encoding="utf-8")
        logger.info(f"[UPDATED] {file_path}")

    else:
        # No header → add
        new_content = "\n".join(expected_header + lines) + "\n"
        file_path.write_text(new_content, encoding="utf-8")
        logger.info(f"[ADDED] {file_path}")


def main(Config: Config):
    for f in iter_files_regex(pattern=Config.script.file_extension, exclude_names=Config.script.excluded_files):
        update_debug_header(f)


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
