from typing import Type

from discord.ui import Button, Select, Item


class ItemFactory:

    @staticmethod
    def get_item(item_tag: str) -> Type[Item]:
        if item_tag == "button":
            return Button
        elif item_tag == "select":
            return Select

        raise ValueError("Invalid item tag")
