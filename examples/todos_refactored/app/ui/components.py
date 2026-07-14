from typing import Annotated

import htpy
from hypie.experimental.components import Component
from hypie.experimental.templates import Template
from hypie.experimental.hyperscript import HyperScript
from hypie.literals import Expr
import hypie.literals as hp_literals
from hypie.commands import (
    fetch,
    put,
    remove,
    trigger,
    set_,
    render,
    halt_event,
    morph,
)
from hypie.features import On
from hypie.events import Event
from hypie import hs


class ToggleTodoEvent(Event):
    id: int


class RequestRemoveTodoEvent(Event):
    id: int
    title: str


class RemoveTodoEvent(Event):
    id: int


class AddTodoEvent(Event):
    title: str


class CancelTodoDeletionEvent(Event):
    pass


class Layout(Component):
    def template(self):
        return htpy.fragment[
            htpy.link(rel="stylesheet", href="/static/tw_styles.css"),
            htpy.title["Todos"],
            # _hyperscript
            htpy.script(type="text/hyperscript", src="/static/_hypie_hyperscript._hs"),
            htpy.script(src="https://cdn.jsdelivr.net/npm/hyperscript.org@0.9.93"),
            htpy.body(class_="flex flex-col gap-2 p-2")[self.children],
        ]


class TodosPageHeader(Component):
    def template(self):
        return htpy.h1(class_="text-4xl")["Todos"]


class TodoDeleteModalTemplate(Template):
    todo_id: Annotated[int, Expr]
    title: Annotated[str, Expr]

    def template(self):
        return htpy.div(
            _=On("click")[trigger(CancelTodoDeletionEvent)],
            data_delete_todo_modal=True,
            class_="flex flex-col justify-center items-center w-screen h-screen fixed left-0 top-0 bg-black/80",
        )[
            htpy.div(
                _=On("click")[halt_event(halt_bubbling=True)],
                class_="text-black bg-white rounded-sm p-1 flex flex-col justify-center items-center gap-2 z-99",
            )[
                htpy.div[f"Are you sure you would like to delete todo: {self.title}"],
                htpy.div(class_="flex gap-2")[
                    htpy.button(
                        _=On("click")[trigger(RemoveTodoEvent(self.todo_id))],
                        class_="w-3xs cursor-pointer bg-red-500 p-1 rounded-sm text-white",
                    )["Yes"],
                    htpy.button(
                        _=On("click")[
                            trigger(CancelTodoDeletionEvent())
                        ],
                        class_="w-3xs cursor-pointer bg-gray-500 p-1 rounded-sm",
                    )["Cancel"],
                ],
            ]
        ]


class TodoItem(Component):
    id: int
    title: str
    done: bool

    def template(self):
        return htpy.li(id=f"todo-{self.id}", class_="flex gap-2")[
            htpy.a(
                class_="text-sky-600 cursor-pointer select-none",
                _=On("click")[trigger(ToggleTodoEvent(id=self.id))],
            )["Toggle"],
            htpy.a(
                class_="text-red-500 cursor-pointer select-none",
                _=On("click")[
                    trigger(RequestRemoveTodoEvent(id=self.id, title=self.title))
                ],
            )["Delete"],
            htpy.span[self.title + (" ✅" if self.done else "")],
        ]


class AddTodoForm(Component):
    def template(self):
        return htpy.div(class_="flex gap-1")[
            htpy.input(
                id="add-todo-input",
                class_="p-1 border-1 border-gray-500 rounded-sm",
                placeholder="Add New Todo",
            ),
            htpy.button(
                class_="bg-cyan-700 text-white p-1 rounded-sm cursor-pointer",
                _=On("click")[
                    trigger(AddTodoEvent(title=hp_literals.id("add-todo-input").value))
                ],
            )["Save"],
        ]


class TodoEventHandler(HyperScript):
    @classmethod
    def script(cls):
        return hs(
            # this comes from the body
            On(CancelTodoDeletionEvent)[
                remove(hp_literals.q("[data-delete-todo-modal]"))
            ],
            On(RequestRemoveTodoEvent)[
                render(
                    TodoDeleteModalTemplate(
                        RequestRemoveTodoEvent.id, RequestRemoveTodoEvent.title
                    )
                ),
                put(hp_literals.result, "at end of", hp_literals.body),
            ],
            On(ToggleTodoEvent)[
                fetch(
                    f"/toggle/{ToggleTodoEvent.id}",
                    as_="HTML",
                    with_={"method": "PATCH"},
                ),
                morph(
                    hp_literals.id(f"#todo-{ToggleTodoEvent.id}"),
                    to=hp_literals.result,
                ),
            ],
            On(RemoveTodoEvent)[
                fetch(f"/{RemoveTodoEvent.id}", as_="HTML", with_={"method": "DELETE"}),
                remove(hp_literals.id(f"todo-{RemoveTodoEvent.id}")),
                remove(hp_literals.q("[data-delete-todo-modal]")),
            ],
            On(AddTodoEvent)[
                fetch(
                    "/",
                    with_={
                        "method": "POST",
                        "body": hp_literals.as_type(
                            {"title": AddTodoEvent.title}, "JSONString"
                        ),
                        "headers": {"Content-Type": "application/json"},
                    },
                    as_="HTML",
                ),
                put(
                    hp_literals.result,
                    "at end of",
                    hp_literals.id("todo-items-container"),
                ),
                set_(hp_literals.id("add-todo-input").value, to=""),
            ],
        )
