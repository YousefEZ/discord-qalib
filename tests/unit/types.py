from typing import Literal

SimpleEmbeds = Literal["Launch", "Launch2"]
FullEmbeds = Literal["Launch", "test_key", "test_key2", "test_key3"]
SelectEmbeds = Literal["Launch"]
CompleteEmbeds = Literal[
    "content_test", "tts_test", "file_test", "allowed_mentions_test",
    "message_reference_test", "message_reference_test2", "message_reference_test3"
]

ErrorEmbeds = Literal["test1", "test2"]
JinjaEmbeds = Literal["test1", "test2"]
Menus = Literal["Menu1"]
Modals = Literal["modal1"]
CompleteJSONMessages = Literal["content_test", "tts_test", "file_test", "allowed_mentions_test"]