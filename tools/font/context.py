import math
from collections.abc import Sequence
from datetime import datetime

from loguru import logger
from pixel_font_builder import FontBuilder, WeightName, SerifStyle, SlantStyle, WidthStyle, Glyph, opentype
from pixel_font_knife.cmap.context import CmapContext
from pixel_font_knife.cmap.kerning.template import CmapKerningTemplate
from pixel_font_knife.cmap.mapping.mapping import CmapMapping
from pixel_font_knife.named.context import NamedContext
from pixel_font_knife.named.file import NamedGlyphFile

from tools.config import path_define, project
from tools.config.font import FontConfig
from tools.config.glyph.metric import GlyphMetricRules
from tools.config.options import FontFormat


class FontBuildContext:
    @staticmethod
    def load(
            font_config: FontConfig,
            glyph_metric_rules: GlyphMetricRules,
            mappings: Sequence[CmapMapping],
            kerning_template: CmapKerningTemplate,
    ) -> FontBuildContext:
        font_size = font_config.font_size

        notdef_glyph_file = NamedGlyphFile.load_notdef(path_define.GLYPHS_DIR.joinpath(str(font_size), 'notdef.png'))

        cmap_context = CmapContext().merge_by_code_point(
            CmapContext.load(path_define.GLYPHS_DIR.joinpath(str(font_size), 'cmap', 'common')),
            CmapContext.load(path_define.GLYPHS_DIR.joinpath(str(font_size), 'cmap', 'proportional')),
        ).apply_mapping_by_flavor(*mappings)

        named_context = NamedContext().merge_by_name_key(
            NamedContext.load(path_define.GLYPHS_DIR.joinpath(str(font_size), 'named', 'common')),
            NamedContext.load(path_define.GLYPHS_DIR.joinpath(str(font_size), 'named', 'proportional')),
        )

        return FontBuildContext(
            font_config,
            glyph_metric_rules,
            notdef_glyph_file,
            cmap_context,
            named_context,
            kerning_template,
        )

    font_config: FontConfig
    glyph_metric_rules: GlyphMetricRules
    notdef_glyph_file: NamedGlyphFile
    cmap_context: CmapContext
    named_context: NamedContext
    kerning_template: CmapKerningTemplate

    def __init__(
            self,
            font_config: FontConfig,
            glyph_metric_rules: GlyphMetricRules,
            notdef_glyph_file: NamedGlyphFile,
            cmap_context: CmapContext,
            named_context: NamedContext,
            kerning_template: CmapKerningTemplate,
    ) -> None:
        self.font_config = font_config
        self.glyph_metric_rules = glyph_metric_rules
        self.notdef_glyph_file = notdef_glyph_file
        self.cmap_context = cmap_context
        self.named_context = named_context
        self.kerning_template = kerning_template

    @property
    def font_size(self) -> int:
        return self.font_config.font_size

    def get_alphabet(self) -> Sequence[str]:
        return [chr(code_point) for code_point in sorted(self.cmap_context.get_character_mapping().keys())]

    def create_builder(self) -> FontBuilder:
        builder = FontBuilder()
        builder.font_metric.font_size = self.font_size
        builder.font_metric.horizontal_layout.ascent = self.font_config.ascent
        builder.font_metric.horizontal_layout.descent = self.font_config.descent
        builder.font_metric.vertical_layout.ascent = math.ceil(self.font_config.line_height / 2)
        builder.font_metric.vertical_layout.descent = -math.floor(self.font_config.line_height / 2)
        builder.font_metric.x_height = self.font_config.x_height
        builder.font_metric.cap_height = self.font_config.cap_height
        builder.font_metric.underline_position = self.font_config.underline_position
        builder.font_metric.underline_thickness = 1
        builder.font_metric.strikeout_position = self.font_config.strikeout_position
        builder.font_metric.strikeout_thickness = 1

        builder.meta_info.version = project.VERSION
        builder.meta_info.created_time = datetime.fromisoformat(f'{project.VERSION.replace('.', '-')}T00:00:00Z')
        builder.meta_info.modified_time = builder.meta_info.created_time
        builder.meta_info.family_name = f'{project.FONT_BRAND} {project.FONT_LANGUAGE} {self.font_size}px'
        builder.meta_info.weight_name = WeightName.REGULAR
        builder.meta_info.serif_style = SerifStyle.SANS_SERIF
        builder.meta_info.slant_style = SlantStyle.NORMAL
        builder.meta_info.width_style = WidthStyle.PROPORTIONAL
        builder.meta_info.manufacturer = project.MANUFACTURER
        builder.meta_info.designer = project.DESIGNER
        builder.meta_info.description = project.DESCRIPTION
        builder.meta_info.copyright_info = project.COPYRIGHT_INFO
        builder.meta_info.license_info = project.LICENSE_INFO
        builder.meta_info.vendor_url = project.HOMEPAGE_URL
        builder.meta_info.designer_url = project.DESIGNER_URL
        builder.meta_info.license_url = project.LICENSE_URL

        glyph_sequence = [self.notdef_glyph_file] + self.cmap_context.get_glyph_sequence() + self.named_context.get_glyph_sequence()
        for glyph_file in glyph_sequence:
            horizontal_offset_x, horizontal_offset_y = glyph_file.suggest_horizontal_offset(self.font_size, self.font_config.baseline)
            advance_width = glyph_file.suggest_advance_width()

            vertical_offset_x, vertical_offset_y = glyph_file.suggest_vertical_offset(self.font_size)
            if self.glyph_metric_rules.should_adjust_vertical_offset_y(glyph_file):
                vertical_offset_y -= 1
            advance_height = glyph_file.suggest_advance_height(self.font_size)

            builder.glyphs.append(Glyph(
                name=glyph_file.glyph_name,
                horizontal_offset=(horizontal_offset_x, horizontal_offset_y),
                advance_width=advance_width,
                vertical_offset=(vertical_offset_x, vertical_offset_y),
                advance_height=advance_height,
                bitmap=glyph_file.suggest_bitmap(),
            ))

        character_mapping = self.cmap_context.get_character_mapping()
        builder.character_mapping.update(character_mapping)

        kerning_values = self.kerning_template.calculate_kerning_values(self.cmap_context)
        builder.kerning_values.update(kerning_values)

        builder.opentype_config.field_overrides.head_y_max = self.font_config.ascent
        builder.opentype_config.field_overrides.head_y_min = self.font_config.descent

        builder.opentype_config.features = opentype.FeatureProgram([
            opentype.FeatureFile(
                path_define.CONFIGS_FEATURES_DIR.joinpath('calt.fea'),
                include_dir=path_define.CONFIGS_FEATURES_DIR,
            ),
        ])

        return builder

    def make_fonts(self, font_formats: Sequence[FontFormat]) -> None:
        path_define.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

        if len(font_formats) > 0:
            builder = self.create_builder()
            for font_format in font_formats:
                file_path = path_define.OUTPUTS_DIR.joinpath(f'{project.FILE_NAME_PREFIX}-{project.FONT_LANGUAGE.lower()}-{self.font_size}px.{font_format}')
                getattr(builder, f'save_{font_format.replace('.', '_')}')(file_path)
                logger.info('Make font: {!r}', str(file_path))
