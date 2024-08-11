from __future__ import annotations

from functools import wraps
from typing import List, Optional, Callable, TypeVar

import discord

from qalib.translators.element.embed import EmbedData, render
from qalib.translators.element.types.embed import Field, EmbedBaseAdapter, Footer

__all__ = "ExpansiveEmbedAdapter", "expand"

MAX_FIELD_LENGTH = 1_024


class ExpansiveEmbedAdapter(EmbedBaseAdapter):
    def __init__(self, page_number_key: Optional[str] = None):
        self._page_number_key = page_number_key

    @property
    def field(self) -> Field:
        raise NotImplementedError

    @property
    def page_number_key(self) -> Optional[str]:
        return self._page_number_key


def _split_field(field: Field, key: Optional[str]) -> List[Field]:
    start = 0
    lines = [string.strip() for string in field["value"].strip().split("\n")]

    values: List[Field] = []

    def compile_lines(end: Optional[int] = None) -> str:
        if end is None:
            return "\n".join([string.replace("\\n", "\n") for string in lines[start:]])
        return "\n".join([string.replace("\\n", "\n") for string in lines[start:end]])

    def compile_field(end: Optional[int] = None) -> Field:
        return {
            "name": field["name"].replace(key, str(len(values) + 1)) if key else field["name"],
            "value": compile_lines(end).replace(key, str(len(values) + 1)) if key else compile_lines(end),
            "inline": field.get("inline", True),
        }

    for i in range(len(lines)):
        diff_char = key is not None and len(str(len(values))) - len(key)
        var_char: int = key is not None and lines[start : i + 1].count(key) * diff_char
        if sum(map(len, lines[start : i + 1])) + var_char >= MAX_FIELD_LENGTH:
            values.append(compile_field(i))
            start = i

    values.append(compile_field())
    return values


_T = TypeVar("_T")


def _page_key_guard(func: Callable[[str, _T, int], _T]) -> Callable[[Optional[str], _T, int], _T]:
    """A decorator that guards a function so that it only runs if the embed proxy has a page key.

    Args:
        func (Callable[[ExpansiveEmbedProxy, _T, int], Optional[_T]]): The function to guard.

    Returns:
        Callable[[ExpansiveEmbedProxy, _T, int], Optional[_T]]: The guarded function.
    """

    @wraps(func)
    def wrapper(page_key: Optional[str], replaceable: _T, page: int) -> _T:
        if page_key is None:
            return replaceable
        return func(page_key, replaceable, page)

    return wrapper


@_page_key_guard
def _replace_footer_with_page_key(page_key: str, footer: Optional[Footer], page: int) -> Optional[Footer]:
    """Render the footer, if it exists, with the page key.

    Args:
        page_key (str): the string to replace with the page number
        page (int): The page number to render the footer with.

    Returns:
        Optional[discord.EmbedFooter]: The rendered footer, if it exists.
    """
    if footer is None:
        return None

    if "text" not in footer:
        return footer

    return {"text": footer['text'].replace(page_key, str(page)), "icon_url": footer['icon_url']}


@_page_key_guard
def replace(page_key: str, value: str, page: int) -> str:
    return value.replace(page_key, str(page))


def expand(embed: ExpansiveEmbedAdapter) -> List[discord.Embed]:
    """Render the desired templated embed in discord.Embed instance.

    Args:
        embed (ExpansiveEmbedAdapter): The embed proxy to render.

    Returns:
        Embed: Embed Object, discord compatible.
    """

    return [
        render(
            EmbedData(
                title=replace(embed.page_number_key, embed.title, page + 1),
                colour=embed.colour,
                type=embed.type,
                description=replace(embed.page_number_key, embed.description, page + 1) if embed.description else None,
                timestamp=embed.timestamp,
                fields=[field],
                footer=_replace_footer_with_page_key(embed.page_number_key, embed.footer, page + 1),
                thumbnail=embed.thumbnail,
                image=embed.image,
                author=embed.author,
            )
        )
        for page, field in enumerate(_split_field(embed.field, embed.page_number_key))
    ]
