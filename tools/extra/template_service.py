from collections.abc import Mapping

from jinja2 import Environment, FileSystemLoader
from loguru import logger

from tools.config import path_define, project, options

_environment = Environment(
    trim_blocks=True,
    lstrip_blocks=True,
    loader=FileSystemLoader(path_define.TEMPLATES_DIR),
)


def _make_html(template_name: str, file_name: str, params: Mapping[str, object] | None = None) -> None:
    params = dict(params) if params is not None else {}
    params['project'] = project
    params['options'] = options

    html = _environment.get_template(template_name).render(params)

    path_define.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    file_path = path_define.OUTPUTS_DIR.joinpath(file_name)
    file_path.write_text(html, 'utf-8')
    logger.info('Make html: {!r}', str(file_path))


def make_playground_html() -> None:
    _make_html('playground.html', 'playground.html')
