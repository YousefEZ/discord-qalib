from typing import Type, Union

from discord.ui import Button, Select, TextInput

ItemType = Type[Union[Button, Select, TextInput]]

class ItemFactory:

    @staticmethod
    def get_item(item_tag: str) -> ItemType:
        if item_tag == "button":
            return Button
        elif item_tag == "textinput":
            return TextInput

        raise ValueError("Invalid item tag")
