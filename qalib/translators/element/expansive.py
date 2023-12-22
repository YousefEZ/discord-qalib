from __future__ import annotations

from functools import cached_property, wraps
from typing import List, Optional, Callable, TypeVar

import discord

from qalib.translators.element.embed import EmbedData, render
from qalib.translators.element.types.embed import Field, EmbedBaseAdapter, Footer

__all__ = "ExpansiveEmbedAdapter", "expand"

MAX_FIELD_LENGTH = 1_024


class ExpansiveEmbedAdapter(EmbedBaseAdapter):

    def __init__(self, page_number_key: Optional[str] = None):
        super().__init__()
        self._page_number_key = page_number_key

    @property
    def field(self) -> Field:
        raise NotImplementedError

    @property
    def page_number_key(self) -> Optional[str]:
        return self._page_number_key


def _split_field(field: Field, with_key: bool) -> List[Field]:
    start = 0
    lines = [string.strip() for string in field["value"].strip().split("\n")]

    values: List[Field] = []

    def compile_lines(end: Optional[int] = None) -> str:
        if end is None:
            return "\n".join([string.replace("\\n", "\n") for string in lines[start:]])
        return "\n".join([string.replace("\\n", "\n") for string in lines[start: end]])

    def compile_field(end: Optional[int] = None) -> Field:
        return {
            "name": field["name"],
            "value": compile_lines(end),
            "inline": field.get("inline", True)
        }

    for i in range(len(lines)):
        if sum(map(len, lines[start: i + 1])) + (len(str(len(values))) * with_key) >= MAX_FIELD_LENGTH:
            values.append(compile_field(i))
            start = i

    values.append(compile_field())
    return values


_T = TypeVar("_T")


def _page_key_guard(
        func: Callable[[ExpansiveEmbedAdapter, _T, int], _T]
) -> Callable[[ExpansiveEmbedAdapter, _T, int], _T]:
    """A decorator that guards a function so that it only runs if the embed proxy has a page key.

    Args:
        func (Callable[[ExpansiveEmbedProxy, _T, int], Optional[_T]]): The function to guard.

    Returns:
        Callable[[ExpansiveEmbedProxy, _T, int], Optional[_T]]: The guarded function.
    """

    @wraps(func)
    def wrapper(embed_adapter: ExpansiveEmbedAdapter, replaceable: _T, page: int) -> _T:
        if embed_adapter.page_number_key is None or replaceable is None:
            return replaceable
        return func(embed_adapter, replaceable, page)

    return wrapper


@_page_key_guard
def _replace_footer_with_page_key(
        embed_adapter: ExpansiveEmbedAdapter,
        footer: Optional[Footer],
        page: int
) -> Optional[Footer]:
    """Render the footer, if it exists, with the page key.

    Args:
        embed_adapter (ExpansiveEmbedAdapter): The embed proxy to render the footer of.
        page (int): The page number to render the footer with.

    Returns:
        Optional[discord.EmbedFooter]: The rendered footer, if it exists.
    """
    if not embed_adapter.footer:
        return None

    if "text" not in embed_adapter.footer:
        return footer

    page_key = embed_adapter.page_number_key
    assert page_key, "page key is None"

    return {
        "text": embed_adapter.footer['text'].replace(page_key, str(page)),
        "icon_url": embed_adapter.footer['icon_url']
    }


@_page_key_guard
def _replace_field_with_page_key(
        embed_adapter: ExpansiveEmbedAdapter,
        field: Field,
        page: int
) -> Field:
    """Render the field, if it exists, with the page key.

    Args:
        embed_adapter (ExpansiveEmbedAdapter): The embed proxy to render the field of.
        page (int): The page number to render the field with.

    Returns (Field): The replaced field, with the key swapped.
    """
    if "value" not in field:
        return field

    page_key = embed_adapter.page_number_key
    assert page_key, "Page Key is Empty"

    return {
        "name": field["name"],
        "value": field["value"].replace(page_key, str(page)),
        "inline": field.get("inline", True)
    }


@_page_key_guard
def replace(embed_adapter: ExpansiveEmbedAdapter, value: str, page: int) -> str:
    page_key = embed_adapter.page_number_key
    assert page_key, "Page Key is Empty"
    return value.replace(page_key, str(page))


def expand(embed: ExpansiveEmbedAdapter) -> List[discord.Embed]:
    """Render the desired templated embed in discord.Embed instance.

    Args:
        embed (ExpansiveEmbedAdapter): The embed proxy to render.

    Returns:
        Embed: Embed Object, discord compatible.
    """

    return [
        render(EmbedData(
            title=replace(embed, embed.title, page + 1),
            colour=embed.colour,
            type=embed.type,
            description=replace(embed, embed.description, page + 1) if embed.description else None,
            timestamp=embed.timestamp,
            fields=[field],
            footer=_replace_footer_with_page_key(embed, embed.footer, page + 1) if embed.footer else None,
            thumbnail=embed.thumbnail,
            image=embed.image,
            author=embed.author
        )) for page, field in enumerate(_split_field(embed.field, embed.page_number_key is not None))
    ]
