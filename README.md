<p align="center">
  <img src="https://user-images.githubusercontent.com/45167695/210134648-e954d124-a9bd-4d48-9cc1-e51f28241711.png" />
</p>

[![Discord-Qalib Tests](https://github.com/YousefEZ/discord-qalib/actions/workflows/discord-qalib.yml/badge.svg)](https://github.com/YousefEZ/discord-qalib/actions/workflows/discord-qalib.yml)
[![codecov](https://codecov.io/gh/YousefEZ/discord-qalib/branch/main/graph/badge.svg?token=3EG4ZF8K3R)](https://codecov.io/gh/YousefEZ/discord-qalib)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/b6a528f00dc7418c9cd15b0d120d8297)](https://www.codacy.com/gh/YousefEZ/discord-qalib/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=YousefEZ/discord-qalib&amp;utm_campaign=Badge_Grade)
![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-informational)
<a href="https://gitmoji.dev">
<img src="https://img.shields.io/badge/gitmoji-%20😜%20😍-FFDD67.svg?style=flat-square"
alt="Gitmoji"
/>
</a>
<a href="https://pypi.org/project/discord-qalib/"><img alt="PyPI" src="https://img.shields.io/pypi/v/discord-qalib"></a>
<a href="https://pypi.org/project/discord-qalib/"><img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/discord-qalib"></a>

Discord templating engine built on discord.py, to help separate text of embeds from the source code. Inspired by Flask.

-----
Key Features:

- use of xml files to hold the various template responses
- allows for pagination, in an abstract form simplifying the interface in the source code

-----

## :gear: Installing:

Python3.8 or higher is required

## :test_tube: Tests

To run the tests, run the following command in the root directory:

Windows:

```bash
python -m unittest tests -v 
```

Linux:

```bash
python3 -m unittest tests -v
```

## :zap: Usage

_This is explained in more detail in the [wiki](https://github.com/YousefEZ/discord-qalib/wiki)_

Wrap expressions that need to evaluated with ``{}``, such as ``{player.name}`` or ``{todays_date}``

Sample XML file:

```xml

<discord>
    <message key="test_key">
        <embed>
            <title>Test</title>
            <description>Test Description</description>
            <colour>magenta</colour>
            <timestamp format="%Y-%m-%d %H:%M:%S.%f">{todays_date}</timestamp>
            <url>https://www.discord.com</url>
            <fields>
                <field>
                    <name>Test Field</name>
                    <value>Test Text</value>
                </field>
            </fields>
            <footer>
                <text>Test Footer</text>
                <icon>https://cdn.discordapp.com/embed/avatars/0.png</icon>
            </footer>
            <thumbnail>https://cdn.discordapp.com/embed/avatars/0.png</thumbnail>
            <image>https://cdn.discordapp.com/embed/avatars/0.png</image>
            <author>
                <name>Test Author</name>
                <icon>https://cdn.discordapp.com/embed/avatars/0.png</icon>
                <url>https://discordapp.com</url>
            </author>
        </embed>
        <view>
            <button key="understood_button">
                <label>Understood</label>
                <style>success</style>
            </button>
        </view>
    </message>
</discord>
```

using the above xml file, for example, you can create an embed with the following code:

```python
import datetime
from typing import Literal

import discord
from discord.ext import commands

import qalib
from qalib.template_engines import formatter

bot = commands.AutoShardedBot(command_prefix="!", intents=discord.Intents.all())

Messages = Literal["test_key"]

async def acknowledged(interaction: discord.Interaction):
    await interaction.response.send_message("Acknowledged", ephemeral=True)


@bot.command()
@qalib.qalib_context(formatter.Formatter(), "templates/test.xml")
async def test(ctx: qalib.QalibContext[Messages]):
    callables = {"understood_button": acknowledged}

    await ctx.rendered_send("test_key", callables, keywords={
        "todays_date": datetime.datetime.now()
    })
```
