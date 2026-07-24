import htpy
import hypie as hp
from ..widgets.TodoAppWidget import TodoAppWidget
from ..widgets.components.TodoDeletionModal.TodoDeletionModal import TodoDeletionModalClient


class TodoAppPage(hp.ServerComponent):
    todos: list[dict]

    def template(self):
        return htpy.fragment[
            htpy.link(rel="stylesheet", href="/static/tw_styles.css"),
            htpy.title["Todos"],
            # _hyperscript
            htpy.script(type="text/hyperscript", src="/static/_hypie_hyperscript._hs"),
            htpy.link(href="/static/tw_styles.css", rel="stylesheet"),
            htpy.script(src="https://cdn.jsdelivr.net/npm/hyperscript.org@0.9.93"),
            TodoDeletionModalClient.register_template(),
            htpy.body(
                class_="flex flex-col gap-2 p-2",
            )[
                TodoAppWidget(self.todos)
            ],
        ]
