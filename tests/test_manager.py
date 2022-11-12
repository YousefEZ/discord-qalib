import unittest

from qalib.embed_manager import EmbedManager
from tests.mocked_classes import ContextMocked


class MyTestCase(unittest.TestCase):

    async def test_embed_manager(self):
        ctx = ContextMocked()
        embed_manager = EmbedManager(ctx, "tests/routes/simple_embeds.xml")
        await embed_manager.display("test")
        self.assertEqual(ctx.message.embed.title, "Test")


if __name__ == '__main__':
    unittest.main()
