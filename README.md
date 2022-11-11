# discord-qalib

Discord templating engine built on discord.py, to help separate text of embeds from the source code. 
Inspired by Django and Jinja.

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

Sample XML file:
```xml
<embed key="test_key">
    <title>Test</title>
    <description>Test Description</description>
    <colour>magenta</colour>
    <timestamp>{date}</timestamp>
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
```

using the above xml file:
```python
from qalib import EmbedManager

import datetime

# ...

@app.command()
async def test(ctx):
    embedManager = EmbedManager(ctx, client, "test.xml")
    await embedManager.send("test_key", time=datetime.datetime.now())
```
