import htpy
import hypie as hp

from .events import *


class AddTodoForm(hp.ServerComponent):
    def template(self):
        return htpy.div(class_="flex gap-1")[
            htpy.input(
                id="add-todo-input",
                class_="p-1 border-1 border-gray-500 rounded-sm",
                placeholder="Add New Todo",
            ),
            htpy.button(
                class_="bg-cyan-700 text-white p-1 rounded-sm cursor-pointer",
                _=hp.On("click")[
                    hp.trigger(AddTodoEvent(title=hp.id("add-todo-input").value))
                ],
            )["Save"],
        ]
