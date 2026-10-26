from collections.abc import Sequence
from zipfile import ZipFile

from loguru import logger

from tools.config import paths, project
from tools.config.options import FontSize, FontFormat


def make_release_zips(font_size: FontSize, font_formats: Sequence[FontFormat]) -> None:
    paths.RELEASES_DIR.mkdir(parents=True, exist_ok=True)

    for font_format in font_formats:
        zip_file_path = paths.RELEASES_DIR.joinpath(f'{project.FILE_NAME_PREFIX}-font-{project.FONT_LANGUAGE.lower()}-{font_size}px-{font_format}-v{project.VERSION}.zip')
        with ZipFile(zip_file_path, 'w') as file:
            file.write(paths.PROJECT_ROOT_DIR.joinpath('LICENSE-OFL'), 'OFL.txt')

            font_file_path = paths.OUTPUTS_DIR.joinpath(f'{project.FILE_NAME_PREFIX}-{project.FONT_LANGUAGE.lower()}-{font_size}px.{font_format}')
            file.write(font_file_path, font_file_path.name)
        logger.info('Make release zip: {!r}', str(zip_file_path))
