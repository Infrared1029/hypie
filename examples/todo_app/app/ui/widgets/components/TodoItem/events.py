from hypie.events import Event


class ToggleTodoEvent(Event):
    id: int


class RequestRemoveTodoEvent(Event):
    id: int
    title: str


class RemoveTodoEvent(Event):
    id: int


class CancelTodoDeletionEvent(Event):
    pass