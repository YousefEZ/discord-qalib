# Usage

Here we will be talking about how to use the interface of the QalibContext

## :zap: Basic Usage

This is a simple XML file that contains a barebones embed

```xml

<discord>
    <message key="test_key">
        <embed>
            <title>Hello World</title>
            <colour>cyan</colour>
            <fields>
                <field>
                    <name>Field 1</name>
                    <value>The first field is mandatory</value>
                </field>
            </fields>
        </embed>
    </message>
</discord>
```

Lets dissect this, piece by piece. First off, we have the ``<discord>`` tag which is the container (ElementTree) for all
the ``<message>`` and ``<menu>`` elements. We can have a variable number of ``<message>`` and ``<menu>`` elements and
they are uniquely identified by their ``key`` attribute such as ``<message key="test_key">``
or ``<menu key="test_key2">``, which is used to identify this embed, in this case ``test_key`` uniquely identifies the
message, and ``test_key2`` uniquely identifies the menu.

In the menu element, we have ``<message>`` tags which uniquely identify the messages that are associated with the menu.

The ``<message>`` tag has a ``key`` attribute which is used to identify the message, and various tags. You can use the
``<embed>`` tag to create a custom embed that is attached to the message as seen above.

There are other tags that allow you to control how the message is used, such as the ``<tts>true</tts>`` tag which is
a boolean value that determines whether the message is sent as text-to-speech or not, and the
``<delete_after>15.0</delete_after>`` tag which is a float value that deletes the message after the specified number
of seconds. The full list can be seen [here](../simple-usage/#all-message-options)

### Components of Embed Tag

We then use the the components of the embed tag, so the 3 mandatory elements of an embed that is required to render it
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

You can view how to write them in different file formats, such as [xml](../qalib/deserializers/xml.md)
and [json](../qalib/deserializers/json.md)

So an example of fully using all the features an embed could offer is as such:

```xml

<discord>
    <message key="test_key">
        <embed>
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
    </message>
</discord>
```

---

## :art: Rendering Values

You can choose your ``TemplateEngine``. The ones that are currently defined is ``Formatter`` which uses python's format
method, and the ``Jinja2`` template engine, which is an adapter over Jinja2. The ``TemplateEngine``
is used in the form of a Dependency Injection into the ``Renderer`` instance via its constructor. The ``Renderer``
templates and deserializes the files into a ``Display``. The ``Renderer`` instance is injected into the ``QalibContext``
which extends the ``discord.ext.commands.Context``.

You can use the ``qalib_context`` decorator over a ``bot.command`` so that it overrides
the ``discord.ext.commands.Context``
with its subclass [``QalibContext``](../qalib/context.md).

```xml

<discord>
    <message key="bank">
        <embed>
            <title>Balance {player.name}</title>
            <colour>cyan</colour>
            <fields>
                <field>
                    <name>{player.bank_name}</name>
                    <value>Has 💵{player.funds} EGP in the bank</value>
                </field>
            </fields>
        </embed>
    </message>
</discord>
```

---

## :crystal_ball: QalibContext

so if we have this sample file called ``player.xml`` that is in the ``templates/`` directory:

```xml

<discord>
    <message key="army">
        <embed>
            <title>Army of {player.name}</title>
            <colour>cyan</colour>
            <fields>
                <field>
                    <name>{player.army_name}</name>
                    <value>Has 💂{player.soldiers} defending the nation</value>
                </field>
            </fields>
        </embed>
    </message>
    <message key="bank">
        <embed>
            <title>Hello {player.name}</title>
            <colour>cyan</colour>
            <fields>
                <field>
                    <name>{player.bank_name}</name>
                    <value>Has 💵{player.funds} EGP in the bank</value>
                </field>
            </fields>
        </embed>
    </message>
</discord>
```

the ``Renderer`` class uses it to render the template, and form a message that can be sent using the QalibContext
instance.

```py
from dataclasses import dataclass
from typing import Literal

import discord
from discord.ext import commands

import qalib
from qalib.template_engines.formatter import Formatter

bot = commands.AutoShardedBot(command_prefix="!", intents=discord.Intents.all())

Messages = Literal["army", "bank"]

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
@qalib.qalib_context(Formatter(), "templates/player.xml")
async def test(ctx: qalib.QalibContext[Messages], name: str):
    await ctx.rendered_send("army", keywords={
        "player": fetch_player(name)
    })
```

---

## :money_with_wings: QalibInteraction

There is also a ``QalibInteraction``, so that it extends the ``discord.Interaction`` instance. Using the same ``.xml``
file as the previous section we are able to use the ``QalibInteraction`` with a slash command as such:

```py
from dataclasses import dataclass
from typing import Literal

import discord
from discord.ext import commands

import qalib
from qalib.template_engines.formatter import Formatter

bot = commands.AutoShardedBot(command_prefix="!", intents=discord.Intents.all())

Messages = Literal["army", "bank"]

@dataclass
class Player:
    name: str
    bank: str
    funds: float
    army_name: str
    soldiers: int


def fetch_player(name: str) -> Player:
    ...


@bot.tree.command(name="test")
@discord.app_commands.describe(player_name="What is the name of the player?")
@qalib.qalib_interaction(Formatter(), "templates/player.xml")
async def test(interaction: qalib.QalibInteraction[Messages], player_name: str):
    await interaction.rendered_send("army", keywords={
        "player": fetch_player(player_name)
    })

@bot.event
async def on_ready():
    await bot.tree.sync()

```

``QalibInteractions`` are also able to render Modals from their documents using
the ``.respond_with_modal(key, methods, keywords)`` method.


---

## :paintbrush: Using Views

We also support the rendering of views, and the different UI Components for each embed.

```xml

<discord>
    <message key="welcome">
        <embed>
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
    </message>
</discord>
```

_This is stored as ``templates/button.xml``_

There are other components that can be rendered, and is shown in
the [XML View Section](https://github.com/YousefEZ/discord-qalib/wiki/2.-XML-Rendering/#%EF%B8%8F-views)

and then can be rendered using the EmbedManager

```py
from typing import Literal

import discord
from discord.ext import commands

import qalib
from qalib.template_engines.formatter import Formatter

bot = commands.AutoShardedBot(command_prefix="!", intents=discord.Intents.all())

Messages = Literal["welcome"]

async def acknowledged(interaction: discord.Interaction):
    await interaction.response.send_message("Acknowledged", ephemeral=True)


@bot.command()
@qalib.qalib_context(Formatter(), "templates/button.xml")
async def greet(ctx: qalib.QalibContext[Messages]):
    await ctx.rendered_send("welcome", callables={"greet": acknowledged})
```

---

## :on: Menus

There is also in-built menus, that you can make easily. You just have to define the embeds in a ``<menu>`` tag, with a
unique ``key`` attribute, and you can use that to make a sequential menu (order appears as defined).

```xml 

<discord>
    <menu key="menu1">
        <pages>
            <message key="1">
                <embed>
                    <title>Page 1</title>
                    <colour>magenta</colour>
                    <fields>
                        <field>
                            <name>This is the first page</name>
                            <value>Lorem ipsum dolor sit amet, consectetur.</value>
                        </field>
                    </fields>
                </embed>
            </message>
            <message key="2">
                <embed>
                    <title>Page 2</title>
                    <colour>magenta</colour>
                    <fields>
                        <field>
                            <name>This is the second page</name>
                            <value>tempor incididunt ut labore et dolore magna.</value>
                        </field>
                    </fields>
                </embed>
            </message>
            <message key="3">
                <embed>
                    <title>Page 3</title>
                    <colour>magenta</colour>
                    <fields>
                        <field>
                            <name>This is the third page</name>
                            <value>Eu non diam phasellus vestibulum lorem sed.</value>
                        </field>
                    </fields>
                </embed>
            </message>
        </pages>
    </menu>
</discord>
```

To render the menu you have to use [.rendered_send()](../qalib/context.md) method with the key as the first argument, 
and that will render the menu.

```py
from typing import Literal

import discord
from discord.ext import commands

import qalib
from qalib.template_engines.formatter import Formatter

bot = commands.AutoShardedBot(command_prefix="!", intents=discord.Intents.all())

Messages = Literal["menu1"]


@bot.command()
@qalib.qalib_context(Formatter(), "templates/player.xml")
async def test(ctx: qalib.QalibContext[Messages]):
    await ctx.rendered_send("menu1")
```

or you can manually define it as so:

```py
from typing import Literal

import discord
from discord.ext import commands

import qalib
from qalib.template_engines.formatter import Formatter

bot = commands.AutoShardedBot(command_prefix="!", intents=discord.Intents.all())

Messages = Literal["menu1"]


@bot.command()
async def test(ctx):
    context: qalib.QalibContext[Messages] = qalib.QalibContext(ctx, qalib.Renderer(Formatter(), "templates/player.xml"))
    await context.rendered_send("menu1")
```

---

## :toolbox: All Message Options

you can read about all the
options [here](https://discordpy.readthedocs.io/en/stable/api.html?highlight=send#discord.abc.Messageable.send)

- embed

```xml

<embed>
    <title>Page 1</title>
    <colour>magenta</colour>
    <fields>
        <field>
            <name>This is the first page</name>
            <value>Lorem ipsum dolor sit amet, consectetur.</value>
        </field>
    </fields>
</embed> 
```

- embeds

```xml
<embeds>
    <embed>
        <title>Page 1</title>
        <colour>magenta</colour>
        <fields>
            <field>
                <name>This is the first page</name>
                <value>Lorem ipsum dolor sit amet, consectetur.</value>
            </field>
        </fields>
    </embed>
    <embed>
        <title>Page 2</title>
        <colour>magenta</colour>
        <fields>
            <field>
                <name>This is the second page</name>
                <value>tempor incididunt ut labore et dolore magna.</value>
            </field>
        </fields>
    </embed>
</embeds>
```

- content

```xml

<content>Lorem ipsum dolor sit amet, consectetur.</content> 
```

- tts

```xml

<tts>true</tts>
```

- nonce

```xml

<nonce>123456789</nonce>
```

- delete_after

```xml

<delete_after>15.0</delete_after>
```

- suppress_embeds

```xml

<suppress_embeds>true</suppress_embeds>
```

- file

```xml

<file>
    <filename>tests/routes/complete_messages.xml</filename>
    <description>Test 1</description>
    <spoilers>False</spoilers>
</file>
```

- files

```xml

<files>
    <file>
        <filename>tests/routes/complete_messages.xml</filename>
        <description>Test 1</description>
        <spoilers>False</spoilers>
    </file>
    <file>
        <filename>tests/routes/full_embeds.xml</filename>
        <description>Test 2</description>
        <spoilers>False</spoilers>
    </file>
</files>
```

- allowed_mentions

```xml

<allowed_mentions>
    <everyone mention="false"/>
    <users>
        <user>
            123456789012345678
        </user>
    </users>
    <roles>
        <role>
            123456789012345678
        </role>
    </roles>
</allowed_mentions>
```

- reference

```xml

<reference>
    <message_id>3445347859384389</message_id>
    <channel_id>234234324324</channel_id>
</reference>
```

- mention_author

```xml

<mention_author>true</mention_author>
```

- view

```xml

<view>
    <button key="button1">
        <style>primary</style>
        <emoji>
            <name>🦺</name>
        </emoji>
        <label>Test Button</label>
        <url>https://www.discord.com</url>
    </button>
</view> 
```

