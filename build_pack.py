"""
{Script Name}

{Summary of what the script does}

{How to use the script}
"""

from datetime import datetime
from pathlib import Path
import logging
import re
import sys

try:
    from dir_utils import extract_file_from_zip
    from json_file_utils import read_json_bytes
    from text_file_utils import read_text_file, write_text_file
except ModuleNotFoundError as e:
    print(f"[ERROR] Missing dependency: {e}")
    input("\nPress Enter to exit...")

logger = logging.getLogger(__name__)


def generate_tick_function(ids: list[str], grouping: int, output_file: str | Path) -> None:
    """Generate tick.mcfunction with item functions distributed across timer ticks."""
    if grouping < 1:
        raise ValueError("grouping must be at least 1")

    lines = ["scoreboard players add .Timer OneItemLimit 1", ""]

    for index, item_id in enumerate(ids):
        timer_value = index // grouping + 1
        lines.append(f"execute if score .Timer OneItemLimit matches {timer_value} as @a run function oneitemlimit:clear/{item_id}")

    max_timer = (len(ids) + grouping - 1) // grouping

    if max_timer:
        lines.extend(["", f"execute if score .Timer OneItemLimit matches {max_timer} run scoreboard players set .Timer OneItemLimit 0"])

    write_text_file(output_file, "\n".join(lines) + "\n")
    logger.info("Generated tick function with %s items across %s timer ticks: %s", len(ids), max_timer, output_file)


def generate_item_function(item_id: str, output_folder: str | Path) -> None:
    """Generate the function that clears all but one of the specified item."""
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    content = [
        f"execute store result score @s OneItemLimit run clear @s minecraft:{item_id} 0",
        "scoreboard players operation @s OneItemLimit -= #Remaining OneItemLimit",
        "execute if score @s OneItemLimit matches 1.. store result storage oneitemlimit:macro count int 1 run scoreboard players get @s OneItemLimit",
        f'execute if score @s OneItemLimit matches 1.. run data modify storage oneitemlimit:macro item set value "minecraft:{item_id}"',
        "execute if score @s OneItemLimit matches 1.. run function oneitemlimit:clear_excess with storage oneitemlimit:macro",
    ]

    output_file = output_folder / f"{item_id}.mcfunction"
    write_text_file(output_file, "\n".join(content) + "\n")
    logger.debug("Generated item function: %s", output_file)


def generate_item_functions(ids: list[str], output_folder: str | Path, remove_all_non_defined_ids: bool = False) -> None:
    """Generate all item functions and optionally remove obsolete item functions."""
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    if remove_all_non_defined_ids:
        defined_ids = set(ids)

        for file_path in output_folder.glob("*.mcfunction"):
            if file_path.stem not in defined_ids:
                file_path.unlink()
                logger.info("Removed obsolete item function: %s", file_path)

    for item_id in ids:
        generate_item_function(item_id, output_folder)

    logger.info("Generated %s item functions in %s", len(ids), output_folder)


def main() -> None:
    jar_path = Path(r"26.3-0.19.5.jar")
    ids_file = Path(r"ids.txt")
    grouping = 93  # Number of item types processed per timer tick
    remove_all_non_defined_ids = True  # Remove .mcfunction files not listed in ids.txt
    excluded_items = [
        "abandoned_campsite_map",
        "acacia_wall_hanging_sign",
        "acacia_wall_sign",
        "ancient_city_map",
        "angler_pottery_shard",
        "archer_pottery_shard",
        "arms_up_pottery_shard",
        "attached_melon_stem",
        "attached_pumpkin_stem",
        "bamboo_sapling",
        "bamboo_wall_hanging_sign",
        "bamboo_wall_sign",
        "beetroots",
        "big_dripleaf_stem",
        "birch_wall_hanging_sign",
        "birch_wall_sign",
        "black_candle_cake",
        "blade_pottery_shard",
        "blue_candle_cake",
        "brain_coral_wall_fan",
        "brewer_pottery_shard",
        "brown_candle_cake",
        "bubble_column",
        "bubble_coral_wall_fan",
        "burn_pottery_shard",
        "candle_cake",
        "carrots",
        "cave_air",
        "cave_vines_plant",
        "cave_vines",
        "chain",
        "cherry_wall_hanging_sign",
        "cherry_wall_sign",
        "cocoa",
        "copper_wall_torch",
        "creeper_wall_head",
        "crimson_wall_hanging_sign",
        "crimson_wall_sign",
        "cyan_candle_cake",
        "danger_pottery_shard",
        "dark_oak_wall_hanging_sign",
        "dark_oak_wall_sign",
        "dead_brain_coral_wall_fan",
        "dead_bubble_coral_wall_fan",
        "dead_fire_coral_wall_fan",
        "dead_horn_coral_wall_fan",
        "dead_tube_coral_wall_fan",
        "dragon_wall_head",
        "end_gateway",
        "end_portal",
        "explorer_pottery_shard",
        "fire_coral_wall_fan",
        "fire",
        "friend_pottery_shard",
        "frosted_ice",
        "grass",
        "gray_candle_cake",
        "green_candle_cake",
        "harness",
        "heart_pottery_shard",
        "heartbreak_pottery_shard",
        "horn_coral_wall_fan",
        "howl_pottery_shard",
        "jungle_explorer_map",
        "jungle_wall_hanging_sign",
        "jungle_wall_sign",
        "kelp_plant",
        "lava_cauldron",
        "lava",
        "light_blue_candle_cake",
        "light_gray_candle_cake",
        "lime_candle_cake",
        "lodestone_compass",
        "magenta_candle_cake",
        "mangrove_wall_hanging_sign",
        "mangrove_wall_sign",
        "melon_stem",
        "miner_pottery_shard",
        "mineshaft_map",
        "mourner_pottery_shard",
        "moving_piston",
        "nether_portal",
        "oak_wall_hanging_sign",
        "oak_wall_sign",
        "ocean_explorer_map",
        "ominous_banner",
        "orange_candle_cake",
        "pale_oak_wall_hanging_sign",
        "pale_oak_wall_sign",
        "piglin_wall_head",
        "pink_candle_cake",
        "piston_head",
        "pitcher_crop",
        "player_wall_head",
        "plenty_pottery_shard",
        "poplar_leaves",
        "poplar_wall_hanging_sign",
        "poplar_wall_sign",
        "potatoes",
        "potted_acacia_sapling",
        "potted_allium",
        "potted_azalea_bush",
        "potted_azure_bluet",
        "potted_bamboo",
        "potted_birch_sapling",
        "potted_blue_orchid",
        "potted_brown_mushroom",
        "potted_cactus",
        "potted_cherry_sapling",
        "potted_closed_eyeblossom",
        "potted_cornflower",
        "potted_crimson_fungus",
        "potted_crimson_roots",
        "potted_dandelion",
        "potted_dark_oak_sapling",
        "potted_dead_bush",
        "potted_fern",
        "potted_flowering_azalea_bush",
        "potted_golden_dandelion",
        "potted_jungle_sapling",
        "potted_lily_of_the_valley",
        "potted_mangrove_propagule",
        "potted_oak_sapling",
        "potted_open_eyeblossom",
        "potted_orange_tulip",
        "potted_oxeye_daisy",
        "potted_pale_oak_sapling",
        "potted_pink_tulip",
        "potted_poplar_sapling",
        "potted_poppy",
        "potted_red_mushroom",
        "potted_red_tulip",
        "potted_spruce_sapling",
        "potted_torchflower",
        "potted_warped_fungus",
        "potted_warped_roots",
        "potted_white_tulip",
        "potted_wither_rose",
        "pottery_shard_archer",
        "pottery_shard_arms_up",
        "pottery_shard_prize",
        "pottery_shard_skull",
        "powder_snow_cauldron",
        "powder_snow",
        "prize_pottery_shard",
        "pumpkin_stem",
        "purple_candle_cake",
        "red_candle_cake",
        "redstone_wall_torch",
        "redstone_wire",
        "scute",
        "set_spawn",
        "sheaf_pottery_shard",
        "shelter_pottery_shard",
        "sign",
        "skeleton_wall_skull",
        "skull_pottery_shard",
        "smithing_template",
        "snort_pottery_shard",
        "soul_fire",
        "soul_wall_torch",
        "spruce_wall_hanging_sign",
        "spruce_wall_sign",
        "swamp_explorer_map",
        "sweet_berry_bush",
        "tall_seagrass",
        "torchflower_crop",
        "trial_explorer_map",
        "tripwire",
        "tube_coral_wall_fan",
        "twisting_vines_plant",
        "void_air",
        "wall_torch",
        "warped_wall_hanging_sign",
        "warped_wall_sign",
        "water_cauldron",
        "water",
        "weeping_vines_plant",
        "white_candle_cake",
        "wither_skeleton_wall_skull",
        "woodland_explorer_map",
        "yellow_candle_cake",
        "zombie_wall_head",
    ]

    json_bytes = extract_file_from_zip(jar_path, "assets/minecraft/lang/en_us.json")
    data = read_json_bytes(json_bytes)
    if not isinstance(data, dict):
        raise TypeError("Data should be a dict")

    item_ids = []
    for key, value in data.items():
        # logger.debug("%s: %s", key, repr(value))

        if not isinstance(key, str):
            continue

        match = re.match(
            r"^(?:item|block)\.minecraft\.([a-z0-9_]+)$",
            key,
        )
        if not match:
            continue

        item_id = match.group(1)
        logger.debug("Found: %s", item_id)
        item_ids.append(item_id)

    for excluded_item in excluded_items:
        if excluded_item in item_ids:
            item_ids.remove(excluded_item)
    item_ids.sort()
    write_text_file(ids_file, item_ids)

    function_folder = Path("data/oneitemlimit/function")
    clear_folder = function_folder / "clear"
    tick_file = function_folder / "tick.mcfunction"

    ids = read_text_file(ids_file, as_list=True)
    ids = [item_id.strip() for item_id in ids if item_id.strip()]

    if not ids:
        raise ValueError(f"No item IDs found in {ids_file}; refusing to generate empty functions")

    invalid_ids = [item_id for item_id in ids if not re.fullmatch(r"[a-z0-9._-]+", item_id)]
    if invalid_ids:
        raise ValueError(f"Invalid item IDs found in {ids_file}: {invalid_ids}")

    if len(ids) != len(set(ids)):
        logger.warning("Duplicate item IDs found; removing duplicates while preserving order")
        ids = list(dict.fromkeys(ids))

    logger.info("Generating datapack functions for %s item IDs with grouping=%s", len(ids), grouping)

    generate_tick_function(ids, grouping, tick_file)
    generate_item_functions(ids, clear_folder, remove_all_non_defined_ids)


def setup_logging(log_folder: Path = Path("Logs"), console_level: int = logging.DEBUG, enable_file_logging: bool = True, max_log_files: int | None = 30, file_level: int = logging.DEBUG, date_format: str = "%Y-%m-%dT%H:%M:%S", message_format: str = "%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s") -> Path | None:
    """Configures file and console logging and prunes old logs for this script."""
    if max_log_files is not None and max_log_files < 1:
        raise ValueError("max_log_files must be at least 1 or None.")

    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    logger.propagate = False
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(message_format, datefmt=date_format)

    # Console Handler (always active)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    log_path: Path | None = None

    # Optional File Handler
    if enable_file_logging:
        script_stem = Path(__file__).stem
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")

        log_dir = Path(log_folder).expanduser().resolve()
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / f"{timestamp}_{script_stem}.log"

        file_handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Prune old logs specific to this script
        if max_log_files is not None and log_dir.exists():
            script_logs = sorted(
                [f for f in log_dir.glob("*.log") if f.name.endswith(f"_{script_stem}.log")],
                key=lambda p: p.stat().st_mtime,
            )
            while len(script_logs) > max_log_files:
                oldest = script_logs.pop(0)
                try:
                    oldest.unlink()
                except OSError:
                    pass

    return log_path


if __name__ == "__main__":
    exit_code = 0
    try:
        setup_logging(max_log_files=5)
        # setup_logging(log_folder=Path(f"~/AppData/Local/Temp/{Path(__file__).stem}"), max_log_files=5) # C:\Users\YourName\AppData\Local\Temp\{script_name}
        main()

    except KeyboardInterrupt:
        print()
        logger.warning("Operation interrupted by user.")
        exit_code = 130

    except Exception as e:
        print()
        logger.exception("A fatal error has occurred: %s", e)
        exit_code = 1

    # input("Press Enter to exit...") # Uncomment to keep console open after script run
    sys.exit(exit_code)
