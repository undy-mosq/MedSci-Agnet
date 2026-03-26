"""题录文本词频（英文停用词 + 简单分词）。"""

import re
from collections import Counter
from typing import Iterable

# 常见英文停用词（精简版，Demo 够用）
_STOP = frozenset(
    """
    a an the and or but if in on at to for of as is was are were be been being
    with from by that this these those it its they them their we our you your
    he she his her has have had do does did not no nor so than then such
    can will may might should could would about into through during before
    after above below between both each few more most other some such only
    same than too very just also using use used new study patients results
    method methods data analysis based cell cells protein gene expression
    significant effect effects model models human disease treatment clinical
    one two first however there which while where when what who how all any
    both each few most other some than that these those this
    """.split(),
)


def _tokenize(text: str) -> Iterable[str]:
    """字母数字片段转小写词条。"""
    for m in re.finditer(r"[A-Za-z][A-Za-z0-9\-]{1,48}", text):
        w = m.group(0).lower()
        if w in _STOP or len(w) < 3:
            continue
        yield w


def build_word_frequencies(
    texts: list[str],
    top_n: int = 100,
) -> list[tuple[str, int]]:
    """合并多段文本，统计词频，返回 Top N。

    Args:
        texts: 标题与摘要等。
        top_n: 最多返回条数。

    Returns:
        (词, 频次) 列表，按频次降序。
    """
    counter: Counter[str] = Counter()
    for t in texts:
        if not t:
            continue
        counter.update(_tokenize(t))
    return counter.most_common(top_n)
