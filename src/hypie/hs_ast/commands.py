from typing import Literal, TypedDict, Iterable
from dataclasses import dataclass, field
from textwrap import indent, dedent

from hypie.hs_ast.expressions import *
from hypie.hs_ast.constants import *
from hypie.hs_ast import helpers
from markupsafe import Markup


class Command:
    def render(self):
        pass

    def __html__(self):
        return Markup(self.render())

    # __html__ = __str__
    __str__ = __html__


@dataclass
class Add(Command):
    class_refs: tuple[CSSExpr] = None
    attr_ref: AttrLiteral = None
    to: Expr | None = None
    when: Expr | None = None

    def render(self):
        rendered = "add"
        if self.class_refs:
            for c in self.class_refs:
                rendered += f" {c.render()}"
        else:
            rendered += f" {self.attr_ref.render()}"
        if self.to:
            rendered += f" to {self.to.render()}"
        if self.when:
            rendered += f" {self.when.render()}"
        return rendered


@dataclass
class Call(Command):
    expr: Expr

    def render(self):
        rendered = f"call {self.expr.render()}"
        return rendered


type FetchAs = Literal["HTML", "JSON", "Text", "Stream", "Response"]


class FetchOptions(TypedDict, total=False):
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
    headers: dict[str, str]
    body: str
    credentials: Literal["omit", "same-origin", "include"]
    cache: Literal[
        "default", "no-store", "reload", "no-cache", "force-cache", "only-if-cached"
    ]
    mode: Literal["cors", "no-cors", "same-origin"]
    timeout: str


@dataclass
class Fetch(Command):
    url: str | StringLiteral
    as_: FetchAs = None
    with_: FetchOptions = None
    throw: bool = True

    def render(self):
        rendered = "fetch"
        url_template = VarTemplateString(self.url)
        if not url_template.interpolations:
            url = self.url
        else:
            url = url_template.transform(
                interp_func=lambda x: "${" + x + "}",
                join_func=lambda parts: "`" + "".join(p for p in parts) + "`",
            )
        rendered += f" {url}"
        if self.as_:
            rendered += f" as {self.as_}"
        if self.with_:
            with_ = python_to_hs(self.with_)
            rendered += f" with {with_}"
        if not self.throw:
            rendered += " don't throw"
        return rendered

    # def _default_fetch_options() -> FetchOptions:
    #     return FetchOptions(
    #         method="GET"
    #     )


@dataclass
class HaltEvent(Command):
    halt_bubbling: bool = True
    halt_default: bool = True
    exit_handler: bool = False

    def render(self):
        if self.halt_bubbling and self.halt_default and self.exit_handler:
            return "halt"
        elif self.halt_bubbling and self.halt_default and not self.exit_handler:
            return "halt the event"
        elif self.halt_bubbling and not self.exit_handler:
            return "halt the event's bubbling"
        elif self.halt_bubbling and self.exit_handler:
            return "halt bubbling"
        elif self.halt_default and not self.exit_handler:
            return "halt the event's default"
        else:
            return "halt default"


# has block
@dataclass
class If(Command):
    condition: Expr
    commands: list[Command] = field(default_factory=lambda: [])
    else_commands: list[Command] = field(default_factory=lambda: [])

    def render(self):
        lines = []
        header = f"if {self.condition.render()}"
        lines.append(header)
        for c in self.commands:
            lines.append(indent(c.render(), INDENT, lambda _: True))
        if self.else_commands:
            lines.append("else")
        for c in self.else_commands:
            lines.append(indent(c.render(), INDENT, lambda _: True))
        lines.append("end")
        return "\n".join(lines)

    def __getitem__(self, commands: Command):
        if not isinstance(commands, Iterable):
            commands = (commands,)
        self.commands = [
            c for c in helpers.flatten_iterable(commands) if isinstance(c, Command)
        ]
        return self

    @property
    def else_(self):
        if not self.commands:
            raise ValueError("Can't start an else block without if path")
        if self.else_commands:
            raise ValueError("Can not have two else blocks")
        else_ = _Else(self)
        return else_


@dataclass
class _Else:
    if_cmd: If

    def __getitem__(self, commands):
        if not isinstance(commands, Iterable):
            commands = (commands,)
        self.if_cmd.else_commands = [
            c for c in helpers.flatten_iterable(commands) if isinstance(c, Command)
        ]
        return self.if_cmd


@dataclass
class Log(Command):
    exprs: tuple[Expr]

    def render(self):
        rendered_exprs = ", ".join(
            [wrap_if_not_literal(e).render() for e in self.exprs]
        )
        return f"log {rendered_exprs}"

    def _wrap_as_template(self, string: str):
        return f"`{string}`"


@dataclass
class Remove(Command):
    class_refs: tuple[CSSExpr] = None
    attr_ref: AttrLiteral = None
    from_: Expr | None = None
    when: Expr | None = None

    def render(self):
        rendered = "remove"
        if self.class_refs:
            for c in self.class_refs:
                rendered += f" {c.render()}"
        else:
            rendered += f" {self.attr_ref.render()}"
        if self.from_:
            rendered += f" from {self.from_.render()}"
        if self.when:
            rendered += f" {self.when.render()}"
        return rendered


@dataclass
class Take(Command):
    class_refs: tuple[CSSExpr]
    # with_: CSSExpr = None
    from_: Expr = None
    giving: Expr = None
    for_: Expr = None

    def render(self):
        # print(self.giving)
        rendered = "take"
        for c in self.class_refs:
            rendered += f" {c.render()}"
        if self.from_:
            rendered += f" from {self.from_.render()}"
        if self.giving is not None:
            rendered += f" giving {coerce_python_type_to_hs(self.giving).render()}"
        if self.for_:
            rendered += f" for {self.for_.render()}"
        return rendered


@dataclass
class SendEvent(Command):
    kind: Literal["send", "trigger"]
    event: EventLiteral
    target: Expr = None

    def render(self):
        if self.kind == "send":
            rendered = f"send {self.event.render()}"
            if self.target:
                rendered += f" to {self.target.render()}"
        else:
            rendered = f"trigger {self.event.render()}"
            if self.target:
                rendered += f" on {self.target.render()}"
        return rendered


type SCROLL_DIRS = Literal["up", "down", "left", "right"]
type SCROLL_TO_V_DIRS = Literal["top", "middle", "bottom"]
type SCROLL_TO_H_DIRS = Literal["left", "center", "right"]
type SCROLL_TRANSITIONS = Literal["smoothly", "instantly"]


@dataclass
class Scroll(Command):
    by: int
    target: Expr = None
    direction: SCROLL_DIRS = None
    transition: SCROLL_TRANSITIONS = None

    def render(self):
        rendered = "scroll"
        if self.target:
            rendered += f" {self.target.render()}"
        if self.direction:
            rendered += f" {self.direction}"
        rendered += f" by {self.by}px"
        if self.transition:
            rendered += f" {self.transition}"
        return rendered


@dataclass
class ScrollTo(Command):
    to: Expr
    vertical_direction: SCROLL_TO_V_DIRS = None
    horizontal_direction: SCROLL_TO_H_DIRS = None
    offset: int = None
    in_: Expr = None
    transition: Literal["smoothly", "instantly"] = None

    def render(self):
        rendered = "scroll to"
        if self.vertical_direction:
            rendered += f" {self.vertical_direction}"
        if self.horizontal_direction:
            rendered += f" {self.horizontal_direction}"
        if self.vertical_direction or self.horizontal_direction:
            rendered += " of"
        rendered += f" {self.to.render()}"
        if self.offset:
            sign = "+"
            if self.offset <= 0:
                sign = "-"
            rendered += f" {sign} {abs(self.offset)}px"
        if self.in_:
            rendered += f" in {self.in_.render()}"
        if self.transition:
            rendered += f" {self.transition}"
        return rendered


@dataclass
class Toggle(Command):
    class_refs: tuple[ClassDOMLiteral] = None

    # TODO: ...
    attr_ref: AttrLiteral = None
    on: Expr = None

    def render(self):
        # print(self.class_refs)
        if self.class_refs:
            rendered = "toggle " + " ".join(c.render() for c in self.class_refs)
        else:
            rendered = f"toggle {self.attr.render()}"
        if self.on:
            rendered += f" on {self.on.render()}"
        return rendered


@dataclass
class ToggleBetween(Command): ...


@dataclass
class Set(Command):
    set_expr: Expr
    to_expr: Expr

    def render(self):
        return f"set {self.set_expr.render()} to {self.to_expr.render()}"


@dataclass
class Repeat(Command):
    commands: tuple[Command] = None
    loop_var: VariableLiteral = None
    index_var: VariableLiteral = None
    loop_expression: Expr = None
    while_condition: Expr = None
    until_condition: Expr = None
    number_times: NumberLiteral = None
    forever_condition: bool = None
    at_least_once: bool = False

    def __getitem__(self, commands: Command):
        if not isinstance(commands, Iterable):
            commands = (commands,)
        self.commands = helpers.flatten_iterable(commands)
        return self

    def render(self):
        lines = []
        header = ""
        end = ""
        cond = self.while_condition or self.until_condition
        stop = "stop " if isinstance(cond, EventLiteral) else ""

        if self.loop_expression:
            if self.loop_var:
                header = f"repeat for {self.loop_var.render()} in {self.loop_expression.render()}"
            else:
                header = f"repeat in {self.loop_expression.render()}"
        elif self.while_condition:
            if self.at_least_once:
                header = "repeat"
                end = f"while {stop}{self.while_condition.render()}"
            else:
                header = f"repeat while {stop}{self.while_condition.render()}"
        elif self.until_condition:
            if self.at_least_once:
                header = "repeat"
                end = f"until {stop}{self.until_condition.render()}"
            else:
                header = f"repeat until {stop}{self.until_condition.render()}"
        elif self.forever_condition:
            header = "repeat forever"
        elif self.number_times:
            header = f"repeat {self.number_times} times"
        # not bottom-tested check
        if self.index_var and not self.at_least_once:
            header += f" index {self.index_var.render()}"

        lines.append(header)
        for c in self.commands:
            lines.append(indent(c.render(), INDENT, lambda _: True))
        if end:
            lines.append(end)
        lines.append("end")
        # print(lines)
        return "\n".join(lines)


class Continue(Command):
    def render(self):
        return "continue"


class Break(Command):
    def render(self):
        return "break"


class Exit(Command):
    def render(self):
        return "exit"


type PUT_PLACEMENTS = Literal["into", "before", "at start of", "at end of", "after"]


@dataclass
class Put(Command):
    expr: Expr
    placement: PUT_PLACEMENTS
    target: Expr

    def render(self):
        return f"put {coerce_python_type_to_hs(self.expr).render()} {self.placement} {self.target.render()}"


@dataclass
class Morph(Command):
    expr: Expr
    to: Expr

    def render(self):
        return f"morph {self.expr.render()} to {coerce_python_type_to_hs(self.to).render()}"


@dataclass
class Wait(Command):
    # events: list[EventSpecLiteral | str] = None
    time: TimeLiteral = None

    def render(self):
        return f"wait {self.time.render()}"


@dataclass
class Focus(Command):
    expr: Expr = None

    def render(self):
        rendered = "focus"
        if self.expr:
            rendered += f" {self.expr.render()}"
        return rendered


@dataclass
class Make(Command):
    object_name: str | Expr
    from_: Iterable[Expr] = None
    called: str = None

    def render(self):
        rendered = f"make a {self.object_name.render() if isinstance(self.object_name, Expr) else self.object_name}"
        if self.from_:
            from_ = self.from_
            rendered += f" from {', '.join(coerce_python_type_to_hs(e).render() for e in from_)}"
        if self.called:
            rendered += f" called {self.called}"
        return rendered


@dataclass
class Render(Command):
    template_id: str
    with_: dict = None

    def render(self):
        rendered = f"render #{self.template_id}"
        if self.with_:
            values = ", ".join(
                [f"{k}: {python_to_hs(v)}" for k, v in self.with_.items()]
            )
            rendered += f" with {values}"
        return rendered


@dataclass
class Append(Command):
    expr: Expr
    to: Expr

    def render(self):
        expr = python_to_hs(self.expr)
        to = python_to_hs(self.to)
        return f"append {expr} to {to}"


@dataclass
class Js(Command):
    vars: list[str]
    javascript: str = None

    def __getitem__(self, javascript: str):
        if not isinstance(javascript, str):
            raise Exception("js command only accepts a single javascript string")
        self.javascript = dedent(re.sub(r"\A[\n]+|[\s\n]+\Z", "", javascript))
        return self
    
    def render(self):
        if not self.javascript:
            raise Exception("No javascript was provided to Js command")
        header = "js" + f"({', '.join(self.vars)})"
        body = indent(self.javascript, INDENT, lambda _: True)
        footer = "end"
        return "\n".join([header, body, footer])
