from __future__ import annotations

import dataclasses
from typing import List, Union, Protocol

import discord

from qalib.translators.element.types.embed import Field, EmbedBaseAdapter, EmbedBaseData

__all__ = "EmbedAdapter", "EmbedData", "render"


class EmbedAdapter(EmbedBaseAdapter, Protocol):
    @property
    def fields(self) -> List[Field]:
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class EmbedData(EmbedBaseData):
    fields: List[Field] = dataclasses.field(default_factory=list)


def render(embed_data: Union[EmbedData, EmbedAdapter]) -> discord.Embed:
    embed = discord.Embed(
        title=embed_data.title,
        colour=embed_data.colour,
        type=embed_data.type,
        description=embed_data.description,
        timestamp=embed_data.timestamp,
    )

    for field in embed_data.fields:
        embed.add_field(**field)

    if (footer := embed_data.footer) is not None:
        embed.set_footer(**footer)

    embed.set_thumbnail(url=embed_data.thumbnail)
    embed.set_image(url=embed_data.image)

    if (author := embed_data.author) is not None:
        embed.set_author(**author)

    return embed
