# Usage

Here we will be talking about how to use the interface of the QalibContext

## :zap: Basic Usage

This is a simple XML file that contains a barebones embed

```xml
<discord>
    <embed key="test_key">
        <title>Hello World</title>
        <colour>cyan</colour>
        <fields>
            <field>
                <name>Field 1</name>
                <value>The first field is mandatory</value>
            </field>
        </fields>
    </embed>
</discord>
```

Lets dissect this, piece by piece. First off, we have the ``<discord>`` tag which is the container (ElementTree) for all
the ``<embed>`` elements. We can have a variable number of ``<embed>`` elements and they are uniquely identified by
their ``key`` attribute such as ``<embed key="test_key">``, which is used to identify this embed, in this
case ``test_key`` uniquely identifies this embed.

We then use the the components of the embed class, so the 3 mandatory elements of an embed that is required to render it
is the ``<title>``, ``<colour>``/``<color>``, and at least one ``<field>`` in the ``<fields>`` container, which contain
a ``<name>``, and a ``<value>``.

Using more of the attributes that can associated with an embed

Each embed can be extended to leverage more the things that an embed can offer such as:
<ol>
  <li>Description</li>
  <li>Type</li>
  <li>Timestamp (with format attribute defaulting to "%Y-%m-%d %H:%M:%S.%f")</li>
  <li>Url</li>
  <li>Footer</li>
  <ol>
    <li>Text</li>
    <li>Icon</li>
  </ol>
  <li>Thumbnail</li>
  <li>Image</li>
  <li>Author</li>
  <ol>
    <li>Name</li>
    <li>Icon</li>
    <li>Url</li>
  </ol>
</ol>

So an example of fully using all the features an embed could offer is as such:

```xml
<discord>
    <embed key="test_key">
        <title>Test</title>
        <description>Test Description</description>
        <type>rich</type>
        <colour>magenta</colour>
        <timestamp format="%d-%m%-Y">22-04-2023</timestamp>
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

---

## :art: Rendering Values

If you are using the EmbedManager as a wrapper (QalibContext with a EmbedProxy) over the default context, then any value
within braces ``{}`` will be treated as an object (will apply ``.format()``). If you are using the JinjaManager then
anything within a double braces ``{{ }}`` will be evaluated as well as all the features that Jinja utilises such as for
loops. Simple example of this with the EmbedManager (so ``{}`` for formatting) will be

```xml
<discord>
    <embed key="bank">
        <title>Balance {player.name}</title>
        <colour>cyan</colour>
        <fields>
            <field>
                <name>{player.bank_name}</name>
                <value>Has 💵{player.funds} EGP in the bank</value>
            </field>
        </fields>
    </embed>
</discord>
```

---

## :crystal_ball: Embed Manager

so if we have this sample file called ``player.xml`` that is in the ``templates/`` directory:

```xml
<discord>
    <embed key="army">
        <title>Army of {player.name}</title>
        <colour>cyan</colour>
        <fields>
            <field>
                <name>{player.army_name}</name>
                <value>Has 💂{player.soldiers} defending the nation</value>
            </field>
        </fields>
    </embed>
    <embed key="bank">
        <title>Hello {player.name}</title>
        <colour>cyan</colour>
        <fields>
            <field>
                <name>{player.bank_name}</name>
                <value>Has 💵{player.funds} EGP in the bank</value>
            </field>
        </fields>
    </embed>
</discord>
```

and then can be used by an ``EmbedManager`` instance

```py
from dataclasses import dataclass

import discord
from discord.ext import commands

import qalib

bot = commands.AutoShardedBot(command_prefix="!", intents=discord.Intents.all())

@dataclass
class Player:
    name: str
    bank: str
    funds: float
    army_name: str
    soldiers: int
    
def fetch_player(name: str) -> Player:
    ...

@bot.command()
@qalib.embed_manager("templates/player.xml")
async def test(ctx):
    await ctx.rendered_send("army", keywords={
        "player": fetch_player(name)
    })
```

---

## :paintbrush: Using Views

We also support the rendering of views, and the different UI Components for each embed.

```xml
<discord>
    <embed key="welcome">
        <title>Greet</title>
        <colour>cyan</colour>
        <fields>
            <field>
                <name>Hello!</name>
                <value>Welcome!</value>
            </field>
        </fields>
        <view>
            <button key="greet">
                <label>Click Me!</label>
                <style>success</style>
            </button>
        </view>
    </embed>
</discord>
```

_This is stored as ``templates/button.xml``_

There are other components that can be rendered, and is shown in
the [XML View Section](https://github.com/YousefEZ/discord-qalib/wiki/2.-XML-Rendering/#%EF%B8%8F-views)

and then can be rendered using the EmbedManager

```py
import discord
from discord.ext import commands

import qalib

bot = commands.AutoShardedBot(command_prefix="!", intents=discord.Intents.all())

async def acknowledged(interaction: discord.Interaction):
    await interaction.response.send_message("Acknowledged", ephemeral=True)

@bot.command()
@qalib.embed_manager("templates/button.xml")
async def greet(ctx):
    await ctx.rendered_send("welcome", callables={"greet":acknowledged})
```

---

## :on: Menus

There is also in-built menus, that you can make easily. You just have to define the embeds in a ``<menu>`` tag, with a
unique ``key`` attribute, and you can use that to make a sequential menu (order appears as defined).

```xml 
<discord>
    <menu key="menu1">
        <embed key="1"> 
            <title>Page 1</title>
            <colour>magenta</colour>
            <fields>
                <field>
                    <name>This is the first page</name>
                    <value>Lorem ipsum dolor sit amet, consectetur.</value>
                </field>
            </fields>
        </embed>
        <embed key="2"> 
            <title>Page 2</title>
            <colour>magenta</colour>
            <fields>
                <field>
                    <name>This is the second page</name>
                    <value>tempor incididunt ut labore et dolore magna.</value>
                </field>
            </fields>
        </embed>
        <embed key="3"> 
            <title>Page 3</title>
            <colour>magenta</colour>
            <fields>
                <field>
                    <name>This is the third page</name>
                    <value> Eu non diam phasellus vestibulum lorem sed.</value>
                </field>
            </fields>
        </embed>
    </menu>
</discord>
```

Then you can use them in two ways. The first is passing the key menu key as the second argument to the embed manger, and
it will automatically set that menu as the root.

```py
import discord
from discord.ext import commands

import qalib


bot = commands.AutoShardedBot(command_prefix="!", intents=discord.Intents.all())

@bot.command()
@qalib.embed_manager("templates/player.xml", "menu1")
async def test(ctx):
    await ctx.menu()
```

or you can manually define it as so:

```py
import discord
from discord.ext import commands

import qalib


bot = commands.AutoShardedBot(command_prefix="!", intents=discord.Intents.all())

@bot.command()
async def test(ctx):
    manager = EmbedManager(ctx, "templates/player.xml", "menu1")
    await manager.menu()
```

its also possible to set the menu, by using the ``set_root`` method which sets the root to a menu (instead of the
default ``<discord>`` tag).