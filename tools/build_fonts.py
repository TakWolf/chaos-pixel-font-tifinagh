import shutil

from cyclopts import App, Parameter
from loguru import logger
from pixel_font_knife.cmap.kerning.template import CmapKerningTemplate
from pixel_font_knife.cmap.mapping.mapping import CmapMapping

from tools.config import path_define, project, manifest, options
from tools.config.font import FontConfig
from tools.config.glyph.metric import GlyphMetricRules
from tools.config.options import FontSize, FontFormat
from tools.extra import publish_service, info_service
from tools.font.context import FontBuildContext

app = App(
    version=project.VERSION,
    default_parameter=Parameter(consume_multiple=True),
)


@app.default
def main(
        cleanup: bool = False,
        font_sizes: set[FontSize] | None = None,
        font_formats: set[FontFormat] | None = None,
) -> None:
    font_sizes = sorted(font_sizes, key=lambda x: options.FONT_SIZES.index(x)) if font_sizes is not None else options.FONT_SIZES
    font_formats = sorted(font_formats, key=lambda x: options.FONT_FORMATS.index(x)) if font_formats is not None else options.FONT_FORMATS

    logger.info('cleanup = {}', cleanup)
    logger.info('font_sizes = {}', font_sizes)
    logger.info('font_formats = {}', font_formats)

    if cleanup and path_define.BUILD_DIR.exists():
        shutil.rmtree(path_define.BUILD_DIR)
        logger.info('Delete dir: {!r}', str(path_define.BUILD_DIR))

    glyph_metric_rules = GlyphMetricRules.load()

    mappings = [
        CmapMapping.load_yaml(file_path)
        for file_path in manifest.MAPPING_FILE_PATHS
    ]

    kerning_template = CmapKerningTemplate.load(manifest.KERNING_TEMPLATE_FILE_PATH)

    for font_size in font_sizes:
        font_config = FontConfig.load(font_size)
        build_context = FontBuildContext.load(font_config, glyph_metric_rules, mappings, kerning_template)

        alphabet = build_context.get_alphabet()

        build_context.make_fonts(font_formats)
        publish_service.make_release_zips(font_size, font_formats)
        info_service.make_info(font_size, alphabet)
        info_service.make_alphabet_txt(font_size, alphabet)


if __name__ == '__main__':
    app()
