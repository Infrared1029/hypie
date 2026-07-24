from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, get_args
import json
from functools import wraps

from textwrap import indent

import re


def python_to_hs(obj):
    if isinstance(obj, Expr):
        return obj.render()
    if isinstance(obj, bool):
        return "true" if obj else "false"
    elif obj is None:
        return "null"
    elif isinstance(obj, (int, float)):
        return f"{obj}"
    elif isinstance(obj, str):
        exp_template = VarTemplateString(obj)
        if not exp_template.interpolations:
            return repr(obj)
        return exp_template.transform(
            interp_func=lambda x: "${" + x + "}",
            join_func=lambda parts: "`" + "".join(parts) + "`",
        )
    elif isinstance(obj, dict):
        lines = []
        for k, v in obj.items():
            l = f"{k}: {python_to_hs(v)}"
            lines.append(indent(l, "  ", lambda _: True))
        return "{\n" + ",\n".join(lines) + "\n}"
    elif isinstance(obj, list):
        lines = []
        for v in obj:
            l = python_to_hs(v)
            lines.append(indent(l, "  ", lambda _: True))
        return "[\n" + ",\n".join(lines) + "\n]"
    else:
        return python_to_hs(str(obj))


def coerce_python_type_to_hs(v):
    match v:
        case bool():
            return BooleanLiteral(v)
        case int() | float():
            return NumberLiteral(v)
        case str():
            return StringLiteral(v)
        case list():
            return ListLiteral(v)
        case dict():
            return ObjectLiteral(v)
        case None:
            return NullLiteral()
        case _:
            return v


def coerce_arguments(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        new_args = []
        for a in args:
            new_args.append(coerce_python_type_to_hs(a))
        new_kwargs = {}
        for k, v in kwargs.items():
            new_kwargs[k] = coerce_python_type_to_hs(v)
        return func(*new_args, **new_kwargs)

    return wrapped


def wrap_if_not_literal(v):
    if isinstance(v, TemplatedVariableLiteral):
        v = v.symbol
    if isinstance(v, Expr) and not isinstance(v, get_args(Literals.__value__)):
        return Parentheses(v)
    return v

def wrap_expressions(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        new_args = []
        for a in args:
            new_args.append(wrap_if_not_literal(a))
        new_kwargs = {}
        for k, v in kwargs.items():
            new_kwargs[k] = wrap_if_not_literal(v)
        out = func(*new_args, **new_kwargs)
        if all([isinstance(a, TemplatedVariableLiteral) for a in args]) and all(isinstance(v, TemplatedVariableLiteral) for v in kwargs.values()):
            return TemplatedVariableLiteral(out)
        return out

    return wrapped


PATTERN = re.compile(r"\?VAR:<(.*?)>\?")


class VarTemplateString:
    def __init__(self, source: str, pattern = None):
        self.pattern = pattern or PATTERN
        self.source = source
        self.strings = []
        self.interpolations = []
        matches = re.finditer(self.pattern, self.source)
        last_idx = 0
        if matches:
            for m in matches:
                end_idx = m.span()[0]
                s = self.source[last_idx:end_idx]
                self.strings.append(s)
                self.interpolations.append(m.group(1))
                last_idx = m.span()[1]
            # print(last_idx, len(source), print(source[last_idx]))
            # if last_idx <= len(source) - 1:
            self.strings.append(self.source[last_idx:])

        else:
            self.strings = source

    def transform(
        self,
        string_func=lambda x: x,
        interp_func=lambda x: x,
        join_func=lambda parts: "".join(p for p in parts if p != ""),
    ):
        parts = [string_func(self.strings[0])]
        for i, inter in enumerate(self.interpolations):
            parts.append(interp_func(inter))
            parts.append(string_func(self.strings[i + 1]))
        return join_func(parts)

    def __str__(self):
        return f"VarTemplateString(strings={self.strings}, interpolations={self.interpolations})"

    __repr__ = __str__


class Expr:
    _is_template = False
    def __html__(self):
        if self._is_template: return self.render()
        return "${" + self.render() + "}"

    def __str__(self):
        if self._is_template: return self.render()
        return f"?VAR:<{self.render()}>?"

    # __html__ = __str__

    def render(self):
        pass

    # def __format__(self, spec):
    #     return "${" + self.render() + "}"

    # property access
    def __getattr__(self, name: str):
        # htpy attempts to check for this, which makes __html__ fail
        if name == "iter_chunks":
            raise AttributeError()
        if isinstance(self, TemplatedVariableLiteral):
            return TemplatedVariableLiteral(PropertyAccess(self.symbol, property=name))
        return PropertyAccess(self, property=name)

    def prop(self, name: str):
        if isinstance(self, TemplatedVariableLiteral):
            return TemplatedVariableLiteral(PropertyAccess(self.symbol, property=name))
        return PropertyAccess(self, property=name)

    def __getitem__(self, name: str | Expr):
        if isinstance(self, TemplatedVariableLiteral):
            return TemplatedVariableLiteral(PropertyAccessBrackets(self.symbol, property=name))
        return PropertyAccessBrackets(self, property=name)

    # binary
    @coerce_arguments
    @wrap_expressions
    def __add__(self, other: Expr):
        return BinaryOp(kind="add", left=self, right=other)

    @coerce_arguments
    @wrap_expressions
    def __sub__(self, other: Expr):
        return BinaryOp(kind="subtract", left=self, right=other)

    @coerce_arguments
    @wrap_expressions
    def __mul__(self, other: Expr):
        return BinaryOp(kind="multiply", left=self, right=other)

    @coerce_arguments
    @wrap_expressions
    def __mod__(self, other: Expr):
        return BinaryOp(kind="mod", left=self, right=other)

    @coerce_arguments
    @wrap_expressions
    def __gt__(self, other):
        return BinaryOp(kind="gt", left=self, right=other)

    @coerce_arguments
    @wrap_expressions
    def __ge__(self, other):
        return BinaryOp(kind="gte", left=self, right=other)

    @coerce_arguments
    @wrap_expressions
    def __lt__(self, other):
        return BinaryOp(kind="lt", left=self, right=other)

    @coerce_arguments
    @wrap_expressions
    def __le__(self, other):
        return BinaryOp(kind="lte", left=self, right=other)

    @coerce_arguments
    @wrap_expressions
    def __ne__(self, other):
        return BinaryOp(kind="ne", left=self, right=other)
    
    @coerce_arguments
    @wrap_expressions
    def __eq__(self, other):
        return BinaryOp(kind="eq", left=self, right=other)

    @coerce_arguments
    @wrap_expressions
    def and_(self, other: Expr):
        return BinaryOp(kind="and", left=self, right=other)

    @coerce_arguments
    @wrap_expressions
    def or_(self, other: Expr):
        return BinaryOp(kind="or", left=self, right=other)

    @coerce_arguments
    @wrap_expressions
    def matches(self, other: Expr):
        return BinaryOp(kind="matches", left=self, right=other)

    @coerce_arguments
    @wrap_expressions
    def does_not_match(self, other: Expr):
        return BinaryOp(kind="does not match", left=self, right=other)

    @coerce_arguments
    @wrap_expressions
    # collection
    def where(self, condition: Expr):
        return Where(collection=self, condition=condition)

    @coerce_arguments
    @wrap_expressions
    def first(self):
        return PositionalCollection(kind="first", collection=self)

    @coerce_arguments
    @wrap_expressions
    def random(self):
        return PositionalCollection(kind="random", collection=self)

    @coerce_arguments
    @wrap_expressions
    def last(self):
        return PositionalCollection(kind="last", collection=self)

    @wrap_expressions
    def __or__(self, type: Literal["JSON", "JSONString"]):
        return TypeConversion(coerce_python_type_to_hs(self), type)

    @wrap_expressions
    def __ror__(type, self: Literal["JSON", "JSONString"]):
        return TypeConversion(coerce_python_type_to_hs(self), type)

    # @coerce_arguments
    @wrap_expressions
    def as_(self, type: Literal["JSON", "JSONString"]):
        return TypeConversion(self, type)


################## BASIC TYPES ##################


@dataclass(eq=False)
class StringLiteral(Expr):
    value: str

    def render(self):
        return python_to_hs(self.value)


@dataclass(eq=False)

class TemplateLiteral(Expr):
    value: str

    def render(self):
        return f"`{self.value}`"


@dataclass(eq=False)

class NumberLiteral(Expr):
    value: int | float

    def render(self):
        return python_to_hs(self.value)


@dataclass(eq=False)

class BooleanLiteral(Expr):
    value: Literal[True, False]

    def render(self):
        return python_to_hs(self.value)


@dataclass(eq=False)
class NullLiteral(Expr):
    def render(self):
        return python_to_hs(self.value)


@dataclass(eq=False)
class ListLiteral(Expr):
    value: list

    def render(self):
        return python_to_hs(self.value)


@dataclass(eq=False)
class ObjectLiteral(Expr):
    value: dict

    def render(self):
        return python_to_hs(self.value)


################## DOM ##################
# class
@dataclass(eq=False)
class ClassDOMLiteral(Expr):
    class_: str

    def render(self):
        exp_template = VarTemplateString(self.class_)
        if not exp_template.interpolations:
            return f".{self.class_}"
        out = exp_template.transform(
            string_func=lambda x: repr(x),
            join_func=lambda parts: ".{"
            + " + ".join(p for p in parts if p != repr(""))
            + "}",
        )
        # print(exp_template)
        # print(out)
        return out

    def in_(self, other: Expr):
        return InDOM(self, other)


# query
@dataclass(eq=False)
class QueryDOMLiteral(Expr):
    query: str

    def render(self):
        exp_template = VarTemplateString(self.query)
        # print(exp_template)
        if not exp_template.interpolations:
            return f"<{self.query}/>"
        out = exp_template.transform(
            string_func=lambda x: x,
            interp_func=lambda x: "${" + x + "}",
            join_func=lambda parts: "<" + "".join(parts) + "/>",
        )
        # print(exp_template)
        # print(out)
        return out

    def in_(self, other: Expr):
        return InDOM(self, other)


# id
@dataclass(eq=False)
class IdDOMLiteral(Expr):
    id_: str

    def render(self):
        exp_template = VarTemplateString(self.id_)
        if not exp_template.interpolations:
            return f"#{self.id_}"
        out = exp_template.transform(
            string_func=lambda x: repr(x),
            join_func=lambda parts: "#{"
            + " + ".join(p for p in parts if p != repr(""))
            + "}",
        )
        # print(exp_template)
        # print(out)
        return out

    def in_(self, other: Expr):
        return InDOM(self, other)


@dataclass(eq=False)
class AttrLiteral(Expr):
    attr_name: str
    attr_value: str = None

    def render(self):
        rendered = f"@{self.attr_name}"
        if self.attr_value:
            rendered += f"='{json.dumps(self.attr_value)}'"
        return rendered


type CSSExpr = IdDOMLiteral | QueryDOMLiteral | ClassDOMLiteral


################## VARIABLE ##################
@dataclass(eq=False)
class VariableLiteral(Expr):
    symbol: str

    def render(self):
        return f"{self.symbol}"


@dataclass(eq=False)
class TemplatedVariableLiteral(Expr):
    symbol: Expr | str

    def render(self):
        _symbol = self.symbol
        if isinstance(self.symbol, str):
            _symbol = VariableLiteral(self.symbol)
        
        return "${" + _symbol.render() + "}"

    def __html__(self):
        return self.render()

    def __str__(self):
        return self.render()


################## Time ##################
type TIME_RES = Literal["s", "ms"]


@dataclass(eq=False)
class TimeLiteral(Expr):
    time: int
    resolution: TIME_RES = "ms"

    def render(self):
        return f"{self.time}{self.resolution}"


################## Event ##################
@dataclass(eq=False)
class EventLiteral(Expr):
    event_name: str
    bind: dict[str, Expr] = field(default_factory=lambda: {})

    def render(self):
        rendered = f"{self.event_name}"
        if self.bind:
            rendered += "("
            parts = []
            for k, v in self.bind.items():
                parts.append(f"{k}:{coerce_python_type_to_hs(v).render()}")
            rendered += ", ".join(parts) + ")"
        return rendered


@dataclass(eq=False)
class EventSpecLiteral(Expr):
    event_name: str
    args: list[str] = field(default_factory=lambda: [])
    filter: Expr = None
    count: int | tuple = None
    from_: Expr | Literal["elsewhere"] = None
    in_: Expr = None
    debounce: TimeLiteral = None
    throttle: TimeLiteral = None

    def render(self):
        rendered = f"{self.event_name}"
        if self.args:
            rendered += "("
            parts = []
            for a in self.args:
                parts.append(a)
            rendered += ", ".join(parts)
            rendered += ")"
        if self.filter:
            rendered += f"[{self.filter.render()}]"
        if self.count:
            rendered += f" {self.count}"
        if self.from_:
            from_ = self.from_.render() if isinstance(self.from_, Expr) else self.from_
            rendered += f" from {from_}"
        if self.in_:
            rendered += f" in {self.in_.render()}"
        if self.debounce:
            rendered += f" debounced at {self.debounce.render()}"
        elif self.throttle:
            rendered += f" throttled at {self.throttle.render()}"
        return rendered


################## DOM POSITONING ##################
@dataclass(eq=False)
class InDOM(Expr):
    css_selector: CSSExpr
    target: CSSExpr

    def render(self):
        return f"{self.css_selector.render()} in {self.target.render()}"


@dataclass(eq=False)
class RelativetDOM(Expr):
    kind: Literal["next", "previous"]
    css_selector: CSSExpr
    from_: Expr | None = None
    within: Expr | None = None
    with_wrapping: bool = False

    def render(self):
        rendered = f"{self.kind} {self.css_selector.render()}"
        if self.from_:
            rendered += f" from {self.from_.render()}"
        if self.within:
            rendered += f" within {self.within.render()}"
        if self.with_wrapping:
            rendered += " with wrapping"
        return rendered


@dataclass(eq=False)
class ClosestDOM(Expr):
    kind: Literal["closest", "closest parent"]
    css_selector: CSSExpr
    to: Expr | None = None

    def render(self):
        rendered = f"{self.kind} {self.css_selector.render()}"
        if self.to:
            rendered += f" {self.to.render()}"
        return rendered


type Literals = (
    VariableLiteral
    | CSSExpr.__value__
    | ObjectLiteral
    | ListLiteral
    | NumberLiteral
    | StringLiteral
    | BooleanLiteral
    | NullLiteral
    | TemplateLiteral
    | EventLiteral
    | AttrLiteral
    | Parentheses
    | PropertyAccess
    | PropertyAccessBrackets
    | AsType
    # | TemplatedVariableLiteral
)


################## COLLECTIONS ##################
@dataclass(eq=False)
class PositionalCollection(Expr):
    kind: Literal["first", "last", "random"]
    collection: Expr
    # preposition: Literal["in", "of", "from"] = "in"

    def render(self):
        return f"{self.kind} {self.collection.render()}"


@dataclass(eq=False)
class Where(Expr):
    collection: Expr
    condition: Expr

    def render(self):
        return f"{self.collection.render()} where {self.condition.render()}"


@dataclass(eq=False)
class MappedTo(Expr):
    collection: Expr
    expr: Expr

    def render(self):
        return f"{self.collection.render()} mapped to {self.expr.render()}"


################## PROPERTY ACCESS ##################
@dataclass(eq=False)
class PropertyAccess(Expr):
    expr: Expr
    property: str

    def render(self):
        if isinstance(self.expr, VariableLiteral) and self.expr.symbol == "me":
            return f"my {self.property}"
        if isinstance(self.expr, PropertyAccessBrackets):
            return f"{self.expr.render()}.{self.property}"
        return f"{self.expr.render()}'s {self.property}"


@dataclass(eq=False)
class PropertyAccessBrackets(Expr):
    expr: Expr
    property: Expr | str

    def render(self):
        rendered_property = (
            self.property.render()
            if isinstance(self.property, Expr)
            else repr(self.property)
        )
        return f"{self.expr.render()}[{rendered_property}]"


################## OPS ##################

type MATH_BINARY_OPS = Literal["add", "subtract", "multiply", "divide", "mod"]
type LOGICAL_BINARY_OPS = Literal["and", "or"]
type BOOL_BINARY_OPS = Literal[
    "eq",
    "ne",
    "gt",
    "gte",
    "lt",
    "lte",
    "matches",
    "does not match",
    "is",
    "is not",
    "is really",
    "is not really",
    "contains",
    "does not contain",
    "starts with",
    "ends with",
    "precedes",
    "does not precede",
    "follows",
    "does not follow",
    "in",  # this can be used as a location restrictor for DOM literals
]


@dataclass(eq=False)
class BinaryOp(Expr):
    kind: MATH_BINARY_OPS | LOGICAL_BINARY_OPS | BOOL_BINARY_OPS
    left: Expr
    right: Expr

    def __post_init__(self):
        if isinstance(self.left, TemplatedVariableLiteral) and isinstance(self.right, TemplatedVariableLiteral):
            self._is_template = True

    def render(self):
        op = None
        match self.kind:
            case "add":
                op = "+"
            case "subtract":
                op = "-"
            case "multiply":
                op = "*"
            case "lt":
                op = "<"
            case "lte":
                op = "<="
            case "gt":
                op = ">"
            case "gte":
                op = ">="
            case "eq":
                op = "=="
            case "ne":
                op = "!="
            case _:
                op = self.kind
        if self._is_template:
            return TemplatedVariableLiteral(f"{self.left.symbol} {op} {self.right.symbol}").render()
        return f"{self.left.render()} {op} {self.right.render()}"


# MATH_Unary_OPS = ...
LOGICAL_Unary_OPS = ...
BOOL_Unary_OPS = Literal[
    "ignoring case", "exists", "does not exist", "is empty", "is not empty"
]


@dataclass(eq=False)
class UnaryOp(Expr):
    pass


################## PARENTHESES ##################


@dataclass(eq=False)
class Parentheses(Expr):
    expr: Expr

    def render(self):
        return f"({self.expr.render()})"


################## TYPE CONVERSION ##################
@dataclass(eq=False)
class TypeConversion(Expr):
    expr: Expr
    type: Literal["JSON", "JSONString"] | Expr

    def render(self):
        return f"{self.expr.render()} as {self.type.render() if isinstance(self.type, Expr) else self.type}"


@dataclass(eq=False)
class AsType(Expr):
    expr: Expr
    type: Literal["JSON", "JSONString"]

    def render(self):
        return f"{python_to_hs(self.expr)} as {self.type}"
