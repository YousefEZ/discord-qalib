::: qalib.translators.xml.XMLDeserializer
    :docstring:
    :members:
    option:
        show_source: False

---

# :toolbox: Working with XML

This is the main way to use 🃏 Qalib. You must have a ``<discord>`` tag that spans the entire document, as it is treated as the root of the ElementTree.

You can then have multiple embeds which are each contained in a ``<embed>`` tag, and must have a ``key`` attribute that uniquely identifies them among the other embed keys, and is written as ``<embed key="key_name">``. 

To render values dynamically, simply put them in between braces, and the renderer will format it when you use the context's ``rendered_send()`` method, as seen in the next section. 

It is safe to skip any non-mandatory fields that an embed would not require, they will simply use their default values.

# 🧩 Sample
```xml
<discord>
    <embed key="test_key">
        <title>Test Title</title>
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
            <name>{author_name}</name>
            <icon>https://cdn.discordapp.com/embed/avatars/0.png</icon>
            <url>https://discordapp.com</url>
        </author>
    </embed>
    <embed key="test_key2">
        <title>Test</title>
        <colour>magenta</colour>
        <fields>
            <field>
                <name>Test Field</name>
                <text>Test Text</text>
            </field>
        </fields>
    </embed>
</discord>
```
_For the purpose of this example, we store this file in ``templates/test.xml``_

# 🖌️ Views

The main components are rendered and instantiate the mapped component/item in [discord.py](https://discordpy.readthedocs.io/en/stable/interactions/api.html?highlight=component#item). The limit to the number of components/items that you can use in one embed is [capped at 25](https://discordpy.readthedocs.io/en/stable/interactions/api.html#discord.ui.View.add_item).


For each example we will write how the component should look like. Components/Items should be written in the view section, where the comment is.
```xml

<discord>
    <message key="test">

        <embed>
            <title>This is a Test!</title>
            <colour>cyan</colour>
            <fields>
                <field>
                    <name>Test Field</name>
                    <value>Test Value</value>
                </field>
            </fields>
            <view>
                <components>
                    <!--Each component/item should go here-->
                </components>
            </view>
        </embed>
    </message>
</discord>
```

## 🆗 Button
Rendering a [Button](https://discordpy.readthedocs.io/en/stable/interactions/api.html?highlight=component#discord.ui.Button) in ``.xml``.

```xml
<button key="click_key">
    <label>Click Me!</label>
    <style>success</style>
    <custom_id>{custom_id}</style>
    <disabled>false</disabled>
    <url>https://github.com/YousefEZ/discord-qalib</url>
    <emoji>
        <name>joy</name>
    </emoji>
</button>
```

## 🏴 Select
Rendering a [Select](https://discordpy.readthedocs.io/en/stable/interactions/api.html?highlight=component#discord.ui.Select) in ``.xml``
```xml
<select key="select_key">
    <placeholder>Select An Option</placeholder>
    <custom_id>{custom_id}</custom_id>
    <min_values>1</min_values>
    <max_values>3</max_values>
    <disabled>false</disabled>
    <options>
        <option>
            <label>Amman</label>
            <value>0</value>
            <description>The Capital of Jordan</description>
            <emoji>
                <name>Petra</name>
                <id>217348923789</id>
                <animated>false</false>
            </emoji>
        </option>
        <option>
            <label>Baghdad</label>
        </option>
        <option>
            <label>Cairo</label>
        </option>
        <option>
            <label>Damascus</label>
        </option>
    </options>
</select>
```

## 📣 Channel Select
Rendering a [Channel Select](https://discordpy.readthedocs.io/en/stable/interactions/api.html?highlight=component#channelselect) in ``.xml``
```xml
<channel_select key="channel_select_key">
    <placeholder>Select a Channel</channel_type>
    <channel_types>
        <channel_type>text</channel_type>
        <channel_type>voice</channel_type>
    </channel_types>
    <min_values>1</min_values>
    <max_values>5</max_values>
    <disabled>false</disabled>
</channel_select>
```

## 🏷️ Mentionable Select
Rendering a [Mentionable Select](https://discordpy.readthedocs.io/en/stable/interactions/api.html?highlight=component#mentionableselect) in ``.xml``
```xml
<mentionable_select key="mentionable_key">
    <placeholder>Select Something to Mention</placeholder>
    <min_values>1</min_values>
    <max_values>2</max_values>
    <disabled>false</disabled>
</mentionable_select>
```

## 🥷 User Select
Rendering a [User Select](https://discordpy.readthedocs.io/en/stable/interactions/api.html?highlight=component#userselect) in ``.xml``

```xml
<user_select key="user_key">
    <placeholder>Select a User</placeholder>
    <min_values>1</min_values>
    <max_values>2</max_values>
    <disabled>false</disabled>
</user_select>
```

## 🎭 Role Select
Rendering a [Role Select](https://discordpy.readthedocs.io/en/stable/interactions/api.html?highlight=component#roleselect) in ``.xml``

```xml
<role_select key="role_select_key">
    <placeholder>Select a Role</placeholder>
    <min_values>1</min_values>
    <max_values>2</max_values>
    <disabled>false</disabled>
</role_select>
```

## 💬 Text Input
Rendering a [Text Input](https://discordpy.readthedocs.io/en/stable/interactions/api.html?highlight=component#discord.ui.TextInput) in ``.xml``

```xml
<text_input key="text_input_key">
    <label>What do you think?</label>
    <style>short</style>
    <placeholder>Write your response...</placeholder>
    <default>N/A</default>
    <min_length>0</min_length>
    <max_length>150</max_length>
</text_input>
```

# 📝 Modals

Modals can be rendered by using the ``<modal>``. They also need to be passed the methods using their method names as their keys. A Sample document containing Modals can be seen here

```xml
<discord>
    <modal key="modal1" title="Questionnaire">
        <text_input>
            <label>What is your name?</label>
            <placeholder>Enter your name</placeholder>
            <style>long</style>
        </text_input>
        <text_input>
            <label>What is your age?</label>
            <placeholder>Enter your age</placeholder>
            <style>long</style>
        </text_input>
    </modal>
</discord>
```