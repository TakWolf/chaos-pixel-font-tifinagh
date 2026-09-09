import yaml

from tools.config import path_define
from tools.config.options import FontSize


class FontConfig:
    @staticmethod
    def load(font_size: FontSize) -> FontConfig:
        data = yaml.safe_load(path_define.CONFIGS_FONTS_DIR.joinpath(f'font-{font_size}px.yaml').read_bytes())
        assert font_size == data['font-size']
        canvas_height = data['canvas-height']
        baseline = data['baseline']
        ascent = data['ascent']
        descent = data['descent']
        x_height = data['x-height']
        cap_height = data['cap-height']
        underline_position = data['underline-position']
        strikeout_position = data['strikeout-position']
        return FontConfig(
            font_size,
            canvas_height,
            baseline,
            ascent,
            descent,
            x_height,
            cap_height,
            underline_position,
            strikeout_position,
        )

    font_size: FontSize
    canvas_height: int
    baseline: int
    ascent: int
    descent: int
    x_height: int
    cap_height: int
    underline_position: int
    strikeout_position: int

    def __init__(
            self,
            font_size: FontSize,
            canvas_height: int,
            baseline: int,
            ascent: int,
            descent: int,
            x_height: int,
            cap_height: int,
            underline_position: int,
            strikeout_position: int,
    ) -> None:
        self.font_size = font_size
        self.canvas_height = canvas_height
        self.baseline = baseline
        self.ascent = ascent
        self.descent = descent
        self.x_height = x_height
        self.cap_height = cap_height
        self.underline_position = underline_position
        self.strikeout_position = strikeout_position

    @property
    def line_height(self) -> int:
        return self.ascent - self.descent
