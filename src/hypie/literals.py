from enum import Enum

from hypie.hs_ast.expressions import *


def id(id_: str, /):
    return IdDOMLiteral(id_=str(id_).lstrip("#"))


def cls(class_: str, /):
    return ClassDOMLiteral(class_=str(class_).lstrip("."))


def q(query: str, /):
    if query.startswith(">"):
        query = query[1:]
    if query.endswith("/>"):
        query = query[:-2]
    return QueryDOMLiteral(query=query)


def attr(attr_name, attr_value=None, /):
    return AttrLiteral(attr_name=attr_name, attr_value=attr_value)


def var(symbol: str, /):
    return VariableLiteral(symbol=symbol)


def t(value: str, /):
    return TemplateLiteral(value=value)


def time(time: int, resolution: TIME_RES = "ms", /):
    return TimeLiteral(time=time, resolution=resolution)


def event(event_name: str, /, bind: dict[str, Expr] = None):
    return EventLiteral(event_name=event_name, bind=bind)


def event_spec(
    event_name: str,
    args: list[str] = None,
    filter: Expr = None,
    count: int = None,
    from_: Expr | Literal["elsewhere"] = None,
    in_: Expr = None,
    debounce: TimeLiteral = None,
    throttle: TimeLiteral = None,
):
    if isinstance(event_name, Enum):
        event_name = event_name.value
    return EventSpecLiteral(
        event_name=event_name,
        args=args,
        filter=filter,
        count=count,
        from_=from_,
        in_=in_,
        debounce=debounce,
        throttle=throttle,
    )


def as_type(expr: Expr, t: Literal["JSON", "JSONString"], /):
    return AsType(expr, type=t)


# magic values
me = var("me")
I = var("I")
my = var("my")
result = var("result")
it = var("it")
body = var("body")
