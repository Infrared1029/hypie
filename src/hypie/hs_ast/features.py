from typing import Iterable, Literal
from textwrap import indent, dedent
from dataclasses import dataclass

from hypie.hs_ast.constants import INDENT
from hypie.hs_ast.commands import Command
from hypie.hs_ast.expressions import *
from hypie.hs_ast import helpers


class Feature:
    def render(self): ...
    def __html__(self):
        return self.render()

    # __html__ = __str__
    __str__ = __html__


@dataclass
class InitF(Feature):
    commands: tuple[Command] = None
    immediately: bool = False

    def __getitem__(self, commands):
        if not isinstance(commands, Iterable):
            commands = (commands,)
        # self.commands = commands
        return InitF(
            commands=[
                c for c in helpers.flatten_iterable(commands) if isinstance(c, Command)
            ],
            immediately=self.immediately,
        )

    def render(self):
        lines = []
        header = "init" + (" immediately" if self.immediately else "")
        lines.append(header)
        end = "end"
        for c in self.commands:
            lines.append(indent(c.render(), INDENT, lambda _: True))
        lines.append(end)
        return "\n".join(lines)

    def __call__(self, immediately: bool = False):
        return InitF(immediately=immediately)


type ON_QUEUE = Literal["none", "all", "first", "last", "concurrent"]


@dataclass
class OnF(Feature):
    event_specs: tuple[str | EventSpecLiteral]
    queue: ON_QUEUE = None
    commands: tuple[Command] = None
    finally_commands: tuple[Command] = None

    def __getitem__(self, commands):
        if not isinstance(commands, Iterable):
            commands = (commands,)
        self.commands = [
            c for c in helpers.flatten_iterable(commands) if isinstance(c, Command)
        ]
        # print("ON FEATURE GOT COMMANDS: ", self.commands)
        return self

    def render(self):
        header = "on"
        events = []
        for e in self.event_specs:
            events.append(e.render() if isinstance(e, Expr) else e)
        header += f" {'\nor '.join(events)}"
        if self.queue == "concurrent":
            header = "every " + header
        elif self.queue:
            header += f"\nqueue {self.queue}"
        lines = []
        lines.append(header)
        # print("LOOPING OVER: ", self.commands)
        for c in self.commands:
            lines.append(indent(c.render(), INDENT, lambda _: True))
        if self.finally_commands:
            lines.append("finally")
            for c in self.finally_commands:
                lines.append(indent(c.render(), INDENT, lambda _: True))
        lines.append("end")
        return "\n".join(lines)

    @property
    def Finally(self):
        return _Finally(self)


@dataclass
class _Finally:
    feature: Feature

    def __getitem__(self, commands):
        if not isinstance(commands, Iterable):
            commands = (commands,)
        self.feature.finally_commands = [
            c for c in helpers.flatten_iterable(commands) if isinstance(c, Command)
        ]
        return self.feature


@dataclass
class LiveF(Feature):
    commands: tuple[Command] = None

    def __getitem__(self, commands):
        if not isinstance(commands, Iterable):
            commands = (commands,)
        # self.commands = commands
        return LiveF(
            commands=[
                c for c in helpers.flatten_iterable(commands) if isinstance(c, Command)
            ]
        )

    def render(self):
        lines = []
        header = "live"
        lines.append(header)
        end = "end"
        for c in self.commands:
            lines.append(indent(c.render(), INDENT, lambda _: True))
        lines.append(end)
        return "\n".join(lines)

    def __call__(self):
        return LiveF()


@dataclass
class WhenF(Feature):
    exprs: tuple[Expr] = None
    commands: tuple[Command] = None

    def __getitem__(self, commands):
        if not isinstance(commands, Iterable):
            commands = (commands,)
        self.commands = [
            c for c in helpers.flatten_iterable(commands) if isinstance(c, Command)
        ]
        return self

    def render(self):
        header = "when"
        parts = []
        for e in self.exprs:
            parts.append(e.render())
        header += " " + "\nor ".join(parts) + " changes"
        lines = [header]
        for c in self.commands:
            lines.append(indent(c.render(), INDENT, lambda _: True))
        lines.append("end")
        return "\n".join(lines)


@dataclass
class BindF(Feature):
    exprA: Expr
    exprB: Expr

    def render(self):
        return f"bind {self.exprA.render()} to {self.exprB.render()}"


@dataclass
class JsF(Feature):
    javascript: str

    def render(self):
        header = "js"
        end = "end"
        js = dedent(self.javascript.strip("\n"))

        return "\n".join([header, indent(js, INDENT, lambda _: True), end])
