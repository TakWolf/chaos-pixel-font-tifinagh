from pathlib import Path

from tools.config import path_define

MAPPING_FILE_PATHS: list[Path] = [
    path_define.CONFIGS_MAPPINGS_DIR.joinpath('0080-00FF Latin-1 Supplement.yaml'),
]

KERNING_TEMPLATE_FILE_PATH = path_define.CONFIGS_KERNING_DIR.joinpath('default.yaml')
