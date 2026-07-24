import hypie as hp
from .components.TodoItem.events import *
from .components.TodoDeletionModal.TodoDeletionModal import TodoDeletionModalClient
from .components.AddTodoForm.events import *

@hp.behavior
def todo_item_effects():
    return hp.hs(
        # hp.On(CancelTodoDeletionEvent)[hp.remove(hp.q("[data-delete-todo-modal]"))],
        hp.On(RequestRemoveTodoEvent)[
            hp.render(
                TodoDeletionModalClient(RequestRemoveTodoEvent.id, RequestRemoveTodoEvent.title)
            ),
            hp.put(hp.result, "at end of", hp.body),
        ],
        hp.On(ToggleTodoEvent)[
            hp.fetch(
                f"/toggle/{ToggleTodoEvent.id}",
                as_="HTML",
                with_={"method": "PATCH"},
            ),
            hp.morph(
                hp.id(f"#todo-{ToggleTodoEvent.id}"),
                to=hp.result,
            ),
        ],
        hp.On(RemoveTodoEvent.with_spec(from_=hp.body))[
            hp.fetch(f"/{RemoveTodoEvent.id}", as_="HTML", with_={"method": "DELETE"}),
            hp.remove(hp.id(f"todo-{RemoveTodoEvent.id}")),
            hp.remove(hp.q("[data-delete-todo-modal]")),
        ],
    )


@hp.behavior
def add_todo_form_effects(todo_items_container: hp.Expr):
    return hp.On(AddTodoEvent)[
        hp.fetch(
            "/",
            with_={
                "method": "POST",
                "body": hp.as_type({"title": AddTodoEvent.title}, "JSONString"),
                "headers": {"Content-Type": "application/json"},
            },
            as_="HTML",
        ),
        hp.put(
            hp.result,
            "at end of",
            todo_items_container,
        ),
        hp.set_(hp.id("add-todo-input").value, to=""),
    ]