from typing import Union, Dict

from qalib.translators.menu import MenuEvents, MenuChangeEvent
from qalib.translators.modal import ModalEvents, ModalEventsCallbacks
from qalib.translators.view import ViewEvents, ViewEventsCallbacks

Events = Union[ViewEvents, MenuEvents, ModalEvents]
EventCallback = Union[ViewEventsCallbacks, ModalEventsCallbacks, MenuChangeEvent]
EventCallbacks = Dict[Events, EventCallback]
