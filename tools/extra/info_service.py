from collections import defaultdict
from collections.abc import Collection, Sequence
from typing import TextIO

import unicodedata2
import unidata_blocks
from loguru import logger
from unidata_blocks import UnicodeBlock

from tools.config import path_define, project
from tools.config.options import FontSize


def _do_we_need_to_create_a_glyph(c: str) -> bool:
    category = unicodedata2.category(c)
    return category[0] in ('L', 'M', 'N', 'P', 'S') or category == 'Zs'


def _get_unicode_chr_count_infos(alphabet: Collection[str]) -> list[tuple[UnicodeBlock, int, int]]:
    in_block_counts = defaultdict(int)
    for c in alphabet:
        block = unidata_blocks.get_block_by_chr(c)
        if 'Private Use Area' not in block.name:
            assert _do_we_need_to_create_a_glyph(c)
        in_block_counts[block.code_start] += 1

    count_infos = []
    for code_start, count in sorted(in_block_counts.items()):
        block = unidata_blocks.get_block_by_code_point(code_start)
        total = 0
        if 'Private Use Area' not in block.name:
            for code_point in range(block.code_start, block.code_end + 1):
                c = chr(code_point)
                if _do_we_need_to_create_a_glyph(c):
                    total += 1
        count_infos.append((block, count, total))
    return count_infos


def _write_unicode_chr_count_infos_table(file: TextIO, infos: Sequence[tuple[UnicodeBlock, int, int]]) -> None:
    file.write('| Block Range | Block Name | Completed | Missing | Progress |\n')
    file.write('|---|---|---:|---:|---:|\n')
    for block, count, total in infos:
        code_point_range = f'{block.code_start:04X} ~ {block.code_end:04X}'
        name = block.name
        missing = total - count if total > 0 else 0
        progress = count / total if total > 0 else 1
        finished_emoji = '🚩' if progress == 1 else '🚧'
        file.write(f'| {code_point_range} | {name} | {count} / {total} | {missing} | {progress:.2%} {finished_emoji} |\n')


def make_info(font_size: FontSize, alphabet: Sequence[str]) -> None:
    alphabet = set(alphabet)

    path_define.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    file_path = path_define.OUTPUTS_DIR.joinpath(f'info-{font_size}px.md')
    with file_path.open('w', encoding='utf-8') as file:
        file.write(f'# {project.FONT_BRAND} {project.FONT_LANGUAGE} {font_size}px\n')
        file.write('\n')
        file.write('## Basic Information\n')
        file.write('\n')
        file.write('| Property | Value |\n')
        file.write('|---|---|\n')
        file.write(f'| Version | {project.VERSION} |\n')
        file.write(f'| Total Characters | {len(alphabet)} |\n')
        file.write('\n')
        file.write('## Unicode Character Statistics\n')
        file.write('\n')
        file.write(f'Unicode Version：{unidata_blocks.unicode_version}\n')
        file.write('\n')
        _write_unicode_chr_count_infos_table(file, _get_unicode_chr_count_infos(alphabet))
    logger.info('Make info: {!r}', str(file_path))


def make_alphabet_txt(font_size: FontSize, alphabet: Sequence[str]) -> None:
    path_define.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    file_path = path_define.OUTPUTS_DIR.joinpath(f'alphabet-{font_size}px.txt')
    file_path.write_text(''.join(alphabet), 'utf-8')
    logger.info('Make alphabet txt: {!r}', str(file_path))
