::: qalib.translators.json.JSONDeserializer
    :docstring:
    :members:
    option:
        show_source: False

---

# :toolbox: Working with JSON

This is the alternative way to use 🃏 Qalib.You use the keys to the embed as the 

You can then have multiple embeds which are each contained in a JSON object, and it's key needs to uniquely identifies them among the other embed keys, and is written as ``{"test_key": { ... }, "test_key2": { ... }}`` 

To render values dynamically, simply put them in between braces, and the renderer will format it when you use the context's ``rendered_send()`` method, as seen in the next section. 

It is safe to skip any non-mandatory fields that an embed would not require, they will simply use their default values.

# 🧩 Sample
```json
{
  "test_key": {
    "title": "Test",
    "description": "Test Description",
    "type": "rich",
    "colour": "55,55,55",
    "timestamp": {
      "date": "{todays_date}"
    },
    "url": "https://www.discord.com",
    "fields": [
      {
        "name": "Test Field",
        "text": "Test Text"
      }
    ],
    "footer": {
      "text": "Test Footer",
      "icon": "https://cdn.discordapp.com/embed/avatars/0.png"
    },
    "thumbnail": "https://cdn.discordapp.com/embed/avatars/0.png",
    "image": "https://cdn.discordapp.com/embed/avatars/0.png",
    "author": {
      "name": "{author_name}",
      "icon": "https://cdn.discordapp.com/embed/avatars/0.png",
      "url": "https://discordapp.com"
    }
  },
  "test_key2": {
    "title": "Test",
    "colour": "magenta",
    "fields": [
      {
        "name": "Test Field",
        "text": "Test Text"
      }
    ]
  }
}
```

# 🖌️ Views

The main components are rendered and instantiate the mapped component/item in [discord.py](https://discordpy.readthedocs.io/en/stable/interactions/api.html?highlight=component#item). The limit to the number of components/items that you can use in one embed is [capped at 25](https://discordpy.readthedocs.io/en/stable/interactions/api.html#discord.ui.View.add_item).


For each example we will write how the component should look like. Components/Items should be written in the view section, where the comment is.

```json
{
  "test_key2": {
    "title": "Test2",
    "description": "Test Description",
    "colour": "magenta",
    "fields": [
      {
        "name": "Test Field",
        "text": "Test Text"
      }
    ],
    "view": {
      "components go here": ""
    }
  }
}

```

## 🆗 Button
Rendering a [Button](https://discordpy.readthedocs.io/en/stable/interactions/api.html?highlight=component#discord.ui.Button) in ``.json``.

```json
"button_key": {
  "type": "button",
  "label": "Click Me!",
  "style": "success",
  "custom_id": "{custom_id}",
  "disabled": true,
  "url": "https://github.com/YousefEZ/discord-qalib",
  "emoji": {
    "name": "joy"
  }
}
```

## 🏴 Select
Rendering a [Select](https://discordpy.readthedocs.io/en/stable/interactions/api.html?highlight=component#discord.ui.Select) in ``.json``
```json
"select_key": {
  "placeholder": "Select An Option",
  "custom_id": "{custom_id}",
  "min_values": 1,
  "max_values": 3,
  "disabled": false
  "options": [
    {
      "label": "Amman"
      "value": 0,
      "description": "The capital city of Jordan",
      "emoji": {
        "name": "Petra",
        "id": 217348923789,
        "animated": false
      }
    },
    {
      "label": "Baghdad"
    },
    {
      "label": "Cairo"
    },
    {
      "label": "Damascus"
    }
  ]
}
```

## 📣 Channel Select
Rendering a [Channel Select](https://discordpy.readthedocs.io/en/stable/interactions/api.html?highlight=component#channelselect) in ``.json``
```json
"channel_key": {
  "type": "channel_select",
  "placeholder": "Select A Channel",
  "channel_types": ["text", "private"],
  "min_values": 1,
  "max_values": 2,
  "disabled": false,
}
```

## 🏷️ Mentionable Select
Rendering a [Mentionable Select](https://discordpy.readthedocs.io/en/stable/interactions/api.html?highlight=component#mentionableselect) in ``.json``
```json
"mentionable_key": {
  "type": "mentionable_select",
  "placeholder": "Select Something to Mention",
  "min_values": 1,
  "max_values": 2,
  "disabled": false,
}
```

## 🥷 User Select
Rendering a [User Select](https://discordpy.readthedocs.io/en/stable/interactions/api.html?highlight=component#userselect) in ``.json``

```json
"user_key": {
  "type": "user_select",
  "placeholder": "Select A User",
  "min_values": 1,
  "max_values": 2,
  "disabled": false,
}
```

## 🎭 Role Select
Rendering a [Role Select](https://discordpy.readthedocs.io/en/stable/interactions/api.html?highlight=component#roleselect) in ``.json``

```json
"role_key": {
  "type": "role_select",
  "placeholder": "Select A Role",
  "min_values": 1,
  "max_values": 2,
  "disabled": false,
}
```

## 💬 Text Input
Rendering a [Text Input](https://discordpy.readthedocs.io/en/stable/interactions/api.html?highlight=component#discord.ui.TextInput) in ``.json``

```json
"text_select": {
  "label": "What do you think?",
  "style": "short",
  "placeholder": "Write your response...",
  "default": "N/A",
  "min_length": 0,
  "max_length": 150
}
```

# 📝 Modal

Modals can be rendered, simply by using the key to Modal as the key to ``JSON`` object. They also need to be passed the methods using their method names as their keys. A Sample document containing Modals can be seen here


```json
{
  "modal1": {
    "title": "Modal 1",
    "components": {
      "name": {
        "type": "text_input",
        "label": "What is your name?",
        "placeholder": "Enter your name"
      },
      "age": {
        "type": "text_input",
        "label": "What is your age?",
        "placeholder": "Enter your age"
      }
    }
  }
}
```