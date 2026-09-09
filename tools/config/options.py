from typing import Literal, get_args

type FontSize = Literal[
    12,
]
FONT_SIZES = list[FontSize](get_args(FontSize.__value__))

type GlyphScope = Literal[
    'common',
    'proportional',
]
GLYPH_SCOPES = list[GlyphScope](get_args(GlyphScope.__value__))

type FontFormat = Literal[
    'otf',
    'otf.woff',
    'otf.woff2',
    'ttf',
    'ttf.woff',
    'ttf.woff2',
]
FONT_FORMATS = list[FontFormat](get_args(FontFormat.__value__))
