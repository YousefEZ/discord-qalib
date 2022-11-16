# discord-qalib

[![Discord-Qalib Tests](https://github.com/YousefEZ/discord-qalib/actions/workflows/discord-qalib.yml/badge.svg)](https://github.com/YousefEZ/discord-qalib/actions/workflows/discord-qalib.yml)
[![codecov](https://codecov.io/gh/YousefEZ/discord-qalib/branch/main/graph/badge.svg?token=3EG4ZF8K3R)](https://codecov.io/gh/YousefEZ/discord-qalib)


Discord templating engine built on discord.py, to help separate text of embeds from the source code. Inspired by Django
and Jinja.

-----
Key Features:

- use of xml files to hold the various template responses
- allows for pagination, in an abstract form simplifying the interface in the source code

-----

## Installing:

Python3.8 or higher is required

# Tests

To run the tests, run the following command in the root directory:

Windows:

```bash
python -m unittest tests -v 
```

Linux:

```bash
python3 -m unittest tests -v
```

# Usage

Wrap expressions that need to evaluated with ``{}``, such as ``{player.name}`` or ``{todays_date}``

Sample XML file:

```xml

<discord>
    <embed key="test_key">
        <title>Test</title>
        <description>Test Description</description>
        <colour>magenta</colour>
        <timestamp format="%Y-%m-%s %H:%M:%S.%f">{todays_date}</timestamp>
        <url>https://www.discord.com</url>
        <fields>
            <field>
                <name>Test Field</name>
                <text>Test Text</text>
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
</discord>
```

using the above xml file, for example, you can create an embed with the following code:

```python
import datetime

import discord
from discord.ext import commands

from qalib import EmbedManager

bot = commands.AutoShardedBot(command_prefix="!", intents=discord.Intents.all())


@bot.command()
async def test(ctx):
    embedManager = EmbedManager(ctx, bot, "test.xml")
    await embedManager.send("test_key", todays_date=datetime.datetime.now())
```
