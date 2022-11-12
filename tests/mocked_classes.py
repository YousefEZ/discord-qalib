class MessageMocked:

    def __init__(self, author=None, channel=None, content=None, embed=None):
        self.author = author
        self.channel = channel
        self.content = content
        self.embed = embed


    async def edit(self, embed=None):
        self.embed = embed


class BotMocked:

    def __init__(self):
        self.message = None

    def inject_message(self, message):
        self.message = message

    async def wait_for(self, event, timeout, check):
        message = MessageMocked(content="Hello World") if self.message is None else self.message
        if event == "message" and check(message):
            return message


class ContextMocked:

    def __init__(self):
        self.message = None
        self.bot = BotMocked()

    async def send(self, embed=None) -> MessageMocked:
        self.message = MessageMocked(embed=embed)
        return self.message
