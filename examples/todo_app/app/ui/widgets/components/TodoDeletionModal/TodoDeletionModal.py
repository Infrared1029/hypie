from typing import Annotated

import htpy
import hypie as hp

from .events import *

class TodoDeletionModalClient(hp.ClientComponent):
    todo_id: Annotated[int, hp.Expr]
    title: Annotated[str, hp.Expr]

    def template(self):
        return htpy.div(
            _=hp.On("click", CancelTodoDeletionEvent)[hp.remove(hp.me)],
            data_delete_todo_modal=True,
            class_="flex flex-col justify-center items-center w-screen h-screen fixed left-0 top-0 bg-black/80",
        )[
            htpy.div(
                _=hp.On("click")[hp.halt_event(halt_bubbling=True)],
                class_="text-black bg-white rounded-sm p-1 flex flex-col justify-center items-center gap-2 z-99",
            )[
                htpy.div[f"Are you sure you would like to delete todo: {self.title}"],
                htpy.div(class_="flex gap-2")[
                    htpy.button(
                        _=hp.On("click")[hp.trigger(RemoveTodoEvent(self.todo_id))],
                        class_="w-3xs cursor-pointer bg-red-500 p-1 rounded-sm text-white",
                    )["Yes"],
                    htpy.button(
                        _=hp.On("click")[hp.trigger(CancelTodoDeletionEvent())],
                        class_="w-3xs cursor-pointer bg-gray-500 p-1 rounded-sm",
                    )["Cancel"],
                ],
            ]
        ]