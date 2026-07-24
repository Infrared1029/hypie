import htpy
import hypie as hp

from .components.AddTodoForm.AddTodoForm import AddTodoForm
from .components.TodoPageHeader import TodoPageHeader
from .components.TodoItem.TodoItem import TodoItem
from .effects import todo_item_effects, add_todo_form_effects

class TodoAppWidget(hp.ServerComponent):
    todos: list[dict]

    def template(self):
        return htpy.div(_=hp.Install(
                    todo_item_effects,
                    add_todo_form_effects(
                        todo_items_container=hp.id("todo-items-container")
                    ),
                ),
                class_="flex flex-col gap-2 p-2",
            )[
                TodoPageHeader,
                AddTodoForm,
                htpy.ul(id="todo-items-container")[
                    [TodoItem(**t) for t in self.todos]
                ],
            ]