from pathlib import Path

from tools.config import paths

MAPPING_FILE_PATHS: list[Path] = [
    paths.CONFIGS_MAPPINGS_DIR.joinpath('0080-00FF Latin-1 Supplement.yaml'),
]

KERNING_TEMPLATE_FILE_PATH = paths.CONFIGS_KERNING_DIR.joinpath('default.yaml')
