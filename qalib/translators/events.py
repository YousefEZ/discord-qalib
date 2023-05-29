from typing import Callable, Union, Dict

from qalib.translators.menu import Menu, MenuEvents
from qalib.translators.modal import ModalEvents, ModalEventsCallbacks
from qalib.translators.view import ViewEvents, ViewEventsCallbacks

Events = Union[ViewEvents, MenuEvents, ModalEvents]
EventCallback = Union[ViewEventsCallbacks, ModalEventsCallbacks, Callable[[Menu], None]]
EventCallbacks = Dict[Events, EventCallback]
