from typing import Any

import yaml
from pixel_font_knife.glyph.file import GlyphFile
from pixel_font_knife.named.file import NamedGlyphFile

from tools.config import path_define


class NamedGlyphMetricRules:
    @staticmethod
    def parse(data: Any) -> NamedGlyphMetricRules:
        no_vertical_offset_y_adjustment = set(data['no-vertical-offset-y-adjustment'])
        return NamedGlyphMetricRules(
            no_vertical_offset_y_adjustment,
        )

    no_vertical_offset_y_adjustment: set[str]

    def __init__(
            self,
            no_vertical_offset_y_adjustment: set[str],
    ) -> None:
        self.no_vertical_offset_y_adjustment = no_vertical_offset_y_adjustment


class GlyphMetricRules:
    @staticmethod
    def load() -> GlyphMetricRules:
        data = yaml.safe_load(path_define.CONFIGS_GLYPHS_DIR.joinpath('metrics.yaml').read_bytes())
        named_rules = NamedGlyphMetricRules.parse(data['named'])
        return GlyphMetricRules(
            named_rules,
        )

    named_rules: NamedGlyphMetricRules

    def __init__(
            self,
            named_rules: NamedGlyphMetricRules,
    ) -> None:
        self.named_rules = named_rules

    def should_adjust_vertical_offset_y(self, glyph_file: GlyphFile) -> bool:
        if glyph_file.canvas.is_blank:
            return False

        if isinstance(glyph_file, NamedGlyphFile):
            if glyph_file.name_key not in self.named_rules.no_vertical_offset_y_adjustment:
                return True

        return False
