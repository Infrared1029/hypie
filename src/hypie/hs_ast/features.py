from __future__ import annotations

from typing import Iterable, Literal
from textwrap import indent, dedent
from dataclasses import dataclass

from hypie.hs_ast.constants import INDENT
from hypie.hs_ast.commands import Command, Set
from hypie.hs_ast.expressions import *
from hypie.hs_ast import helpers
from markupsafe import Markup


class Feature:
    def render(self): ...
    def __html__(self):
        return self.render()

    # __html__ = __str__
    __str__ = __html__

@dataclass
class Hs:
    features: tuple[Feature] = field(default_factory=lambda: [])

    def render(self):
        return "\n".join(f.render() for f in self.features)

    def add_features(self, *feats: Hs | Feature):
        features = []

        for f in feats:
            if isinstance(f, Hs):
                features.extend(f.features)
            elif isinstance(f, (Feature, Set)):
                features.append(f)
        self.features = tuple([*self.features, *features])
        return self

    def __str__(self):
        return Markup("\n" + self.render() + "\n")

    __html__ = __str__


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

# TODO: potentially use __getitem__ for the JS to align it with JS command
@dataclass
class JsF(Feature):
    javascript: str

    def render(self):
        header = "js"
        end = "end"
        js = dedent(re.sub(r"\A[\n]+|[\s\n]+\Z", "", self.javascript))

        return "\n".join([header, indent(js, INDENT, lambda _: True), end])

@dataclass
class BehaviorF(Feature):
    name: str
    param_list: list[str] = field(default_factory=lambda: [])
    features: list[Feature] = field(default_factory=lambda: Hs())

    def __getitem__(self, features):
        self.features = Hs()
        if not isinstance(features, Iterable):
            features = (features,)
        features = helpers.flatten_iterable(features)
        for f in features:
            if isinstance(f, Feature):
                self.features.add_features(f)
            elif isinstance(f, Hs):
                self.features.add_features(f)
        return self
    
    def render(self):
        header = f"behavior {self.name}"
        if self.param_list:
            header += f"({', '.join(self.param_list)})"
        body = indent(self.features.render(), INDENT, lambda _: True)
        footer = "end"
        return "\n".join([header, body, footer])

@dataclass
class BoundedBehavior:
    name: str
    named_args: dict[list, Expr]

@dataclass
class InstallF(Feature):
    name: str
    named_args: dict[str, Expr] = field(default_factory={})

    def render(self):
        rendered = f"install {self.name}"
        _named_args = ""
        if self.named_args:
            _named_args = "(" + ", ".join([f"{k}: {python_to_hs(v)}" for k,v in self.named_args.items()]) + ")"
        return rendered + _named_args

