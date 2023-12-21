from __future__ import annotations

from functools import cached_property, wraps, lru_cache
from typing import Tuple, List, Optional, Callable, TypeVar

import discord

from qalib.translators.element.embed import EmbedData, render
from qalib.translators.element.types.embed import Field, EmbedBaseAdapter, Footer

__all__ = "ExpansiveEmbedAdapter", "expand"

MAX_FIELD_LENGTH = 1_024


class ExpansiveEmbedAdapter(EmbedBaseAdapter):

    @cached_property
    def field(self) -> Field:
        raise NotImplementedError

    @cached_property
    def page_number_key(self) -> Optional[str]:
        raise NotImplementedError


def _split_field(field: Field) -> List[Field]:
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
        if sum(map(len, lines[start: i + 1])) >= MAX_FIELD_LENGTH:
            values.append(compile_field(i))
            start = i

    values.append(compile_field())
    return values


_T = TypeVar("_T")


def _page_key_guard(
        func: Callable[[ExpansiveEmbedAdapter, _T, int], Optional[_T]]
) -> Callable[[ExpansiveEmbedAdapter, _T, int], Optional[_T]]:
    """A decorator that guards a function so that it only runs if the embed proxy has a page key.

    Args:
        func (Callable[[ExpansiveEmbedProxy, _T, int], Optional[_T]]): The function to guard.

    Returns:
        Callable[[ExpansiveEmbedProxy, _T, int], Optional[_T]]: The guarded function.
    """

    @wraps(func)
    def wrapper(embed_adapter: ExpansiveEmbedAdapter, replaceable: _T, page: int) -> Optional[_T]:
        if not embed_adapter.page_number_key:
            return None
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

    return {
        "text": embed_adapter.footer['text'].replace(embed_adapter.page_number_key, str(page)),
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

    return {
        "name": field["name"],
        "value": field["value"].replace(embed_adapter.page_number_key, str(page)),
        "inline": field["inline"]
    }


@_page_key_guard
def replace(embed_adapter: ExpansiveEmbedAdapter, value: str, page: int) -> str:
    return value.replace(embed_adapter.page_number_key, str(page))


def expand(embed_adapter: ExpansiveEmbedAdapter) -> List[discord.Embed]:
    """Render the desired templated embed in discord.Embed instance.

    Args:
        embed_adapter (ExpansiveEmbedAdapter): The embed proxy to render.

    Returns:
        Embed: Embed Object, discord compatible.
    """

    return [
        render(EmbedData(
            title=replace(embed_adapter, embed_adapter.title, page + 1),
            colour=embed_adapter.colour,
            type=embed_adapter.type,
            description=replace(embed_adapter, embed_adapter.description, page + 1),
            timestamp=embed_adapter.timestamp,
            fields=[field],
            footer=_replace_footer_with_page_key(embed_adapter, embed_adapter.footer, page + 1),
            thumbnail=embed_adapter.thumbnail,
            image=embed_adapter.image,
            author=embed_adapter.author
        )) for page, field in enumerate(_split_field(embed_adapter.field))
    ]
