from hypie.events import Event

class RemoveTodoEvent(Event):
    id: int

class CancelTodoDeletionEvent(Event):
    pass