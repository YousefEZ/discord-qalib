class MessageMocked:

    def __init__(self, content=None, embed=None):
        self.content = content
        self.embed = embed

    def edit(self, embed=None):
        self.embed = embed


class BotMocked:
    pass


class ContextMocked:

    def __init__(self):
        self.message = None
        self.bot = BotMocked()

    async def send(self, embed=None) -> MessageMocked:
        self.message = MessageMocked(embed=embed)
        return self.message
