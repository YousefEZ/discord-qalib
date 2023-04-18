# Welcome to Discord-Qalib

Qalib (Arabic: قالب), which means template in Arabic, is the official name of this library.

## What is :black_joker: Discord-Qalib?

Discord-Qalib is an extension that wraps around and extends [discord.py](https://github.com/Rapptz/discord.py) Context
instance, allowing for templated responses so that front-end facing text is separated from the source code and placed in
a file in a structured manner (i.e. ``.xml``, ``.json``).

## :joystick: Simple Usage

A simple example ``.xml`` file would be

```xml

<discord>
    <message key="balance">
        <embed>
            <title>Hello {player.name}</title>
            <colour>cyan</colour>
            <fields>
                <field>
                    <title>Balance Remaining</title>
                    <value>£ {player.balance}</value>
                </field>
            </fields>
        </embed>
    </message>
</discord>
```

_stored as ``balance.xml`` in the templates directory_

and can be used in the source code as such

```py
from dataclasses import dataclass
from typing import Literal

import discord
from discord.ext import commands

import qalib
from qalib.template_engines.formatter import Formatter

bot = commands.AutoShardedBot(command_prefix="!", intents=discord.Intents.all())

Messages = Literal["balance"]

@dataclass
class Player:
    name: str
    balance: float


@bot.command()
@qalib.qalib_context(Formatter(), "templates/balance.xml")
def balance(ctx: qalib.QalibContext[Messages], name: str):
    await ctx.rendered_send("balance", keywords={"player": Player(name, 1000.0)})

```

