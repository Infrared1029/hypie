from typing import Annotated

import htpy
from hypie.experimental.components import Component
from hypie.experimental.templates import Template
from hypie.literals import Expr
import hypie.literals as hp_literals
from hypie.commands import (
    fetch,
    put,
    remove,
    set_,
    render,
    halt_event,
    morph,
)
from hypie.features import On


class Layout(Component):
    def template(self):
        return htpy.fragment[
            htpy.link(rel="stylesheet", href="/static/tw_styles.css"),
            htpy.title["Todos"],
            # _hyperscript
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
            _=On("click")[remove(hp_literals.q("[data-delete-todo-modal]"))],
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
                        _=On("click")[
                            fetch(
                                f"/{self.todo_id}",
                                as_="HTML",
                                with_={"method": "DELETE"},
                            ),
                            remove(hp_literals.id(f"#todo-{self.todo_id}")),
                            remove(hp_literals.q("[data-delete-todo-modal]")),
                        ],
                        class_="w-3xs cursor-pointer bg-red-500 p-1 rounded-sm text-white",
                    )["Yes"],
                    htpy.button(
                        _=On("click")[
                            remove(hp_literals.q("[data-delete-todo-modal]")),
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
                _=On("click")[
                    fetch(
                        f"/toggle/{self.id}",
                        as_="HTML",
                        with_={"method": "PATCH"},
                    ),
                    morph(
                        hp_literals.id(f"#todo-{self.id}"),
                        to=hp_literals.result,
                    ),
                ],
            )["Toggle"],
            htpy.a(
                class_="text-red-500 cursor-pointer select-none",
                _=On("click")[
                    render(TodoDeleteModalTemplate(self.id, self.title)),
                    put(hp_literals.result, "at end of", hp_literals.body),
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
                    fetch(
                        "/",
                        with_={
                            "method": "POST",
                            "body": hp_literals.as_type(
                                {"title": hp_literals.id("add-todo-input").value},
                                "JSONString",
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
            )["Save"],
        ]
