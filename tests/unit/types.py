from typing import Literal

SimpleEmbeds = Literal["Launch", "Launch2"]
FullEmbeds = Literal["Launch", "test_key", "test_key2", "test_key3"]
SelectEmbeds = Literal["Launch"]
CompleteEmbeds = Literal[
    "multi_line_content_test",
    "empty_content_test",
    "content_test",
    "tts_test",
    "file_test",
    "allowed_mentions_test",
    "message_reference_test",
    "message_reference_test2",
    "message_reference_test3",
]

ErrorEmbeds = Literal["test1", "test2", "menu_type", "unknown_type"]
JinjaEmbeds = Literal["test1", "test2", "test3", "test4", "test5"]
Menus = Literal["Menu1", "Menu2", "Menu3", "Menu4"]
Modals = Literal["modal1", "modal2"]
CompleteJSONMessages = Literal[
    "content_test", "multi_embeds", "tts_test", "file_test", "allowed_mentions_test", "menu4", "menu5"
]
