from typing import overload

from hypie.hs_ast.commands import *
from hypie.hs_ast.expressions import *
from hypie.events import Event
from hypie.experimental.client_component import ClientComponent


@overload
def add(*class_refs, to: Expr = None, when: Expr = None): ...


@overload
def add(*attr_ref, to: Expr = None, when: Expr = None): ...


def add(*exprs: Expr, to: Expr = None, when: Expr = None):
    if len(exprs) == 1 and not isinstance(exprs[0], ClassDOMLiteral):
        return Add(attr_ref=exprs[0], to=to, when=when)
    else:
        return Add(class_refs=exprs, to=to, when=when)


@overload
def remove(*class_refs, from_: Expr = None, when: Expr = None): ...


@overload
def remove(attr_ref, from_: Expr = None, when: Expr = None): ...


def remove(*exprs: Expr, from_: Expr = None, when: Expr = None):
    if len(exprs) == 1 and not isinstance(exprs[0], ClassDOMLiteral):
        return Remove(attr_ref=exprs[0], from_=from_, when=when)
    else:
        return Remove(class_refs=exprs, from_=from_, when=when)


def take(
    *class_refs,
    from_: Expr = None,
    giving: Expr = None,
    for_: Expr = None,
):
    return Take(class_refs=class_refs, from_=from_, giving=giving, for_=for_)


def call(expr: str, /):
    # using variable literal as it puts the expr as is
    return Call(VariableLiteral(expr))


def fetch(
    url: str, /, as_: FetchAs = None, with_: FetchOptions = None, throw: bool = True
):
    # # print(pattern.search(url))
    # if pattern.search(url):
    #     url = f"`{url}`"
    return Fetch(url=str(url), as_=as_, with_=with_, throw=throw)


def halt_event(
    halt_bubbling: bool = True, halt_default: bool = True, exit_handler: bool = False
):
    return HaltEvent(
        halt_bubbling=halt_bubbling,
        halt_default=halt_default,
        exit_handler=exit_handler,
    )


def if_(condition: Expr, /):
    return If(condition=condition)


def log(*exprs):
    return Log(exprs=tuple(coerce_python_type_to_hs(e) for e in exprs))


def send(event_name: str, bind: dict = None, to: Expr = None):
    if isinstance(event_name, Event):
        _event = event_name
        event_name = _event.event_name
        bind = _event._bounded_args
    event = EventLiteral(event_name=event_name, bind=bind)
    return SendEvent(kind="send", event=event, target=to)


def trigger(event_name: str | Event, bind: dict = None, on: Expr = None):
    if isinstance(event_name, type) and issubclass(event_name, Event):
        _event = event_name()
        event_name = _event.event_name
        bind = _event._bounded_args
    elif isinstance(event_name, Event):
        _event = event_name
        event_name = _event.event_name
        bind = _event._bounded_args
    event = EventLiteral(event_name=event_name, bind=bind)
    return SendEvent(kind="trigger", event=event, target=on)


def repeat(
    for_: VariableLiteral = None,
    in_: Expr = None,
    forever: bool = False,
    number_of_times: int = None,
    while_: Expr = None,
    until: Expr = None,
    at_least_once: bool = False,
):
    return Repeat(
        loop_var=for_,
        loop_expression=in_,
        forever_condition=forever,
        while_condition=while_,
        until_condition=until,
        at_least_once=at_least_once,
        number_times=number_of_times,
    )


def set_(set_expr: VariableLiteral, /, to: Expr):
    return Set(
        set_expr=set_expr,
        to_expr=coerce_python_type_to_hs(wrap_if_not_literal(to)),
    )


def put(expr: Expr, /, placement: PUT_PLACEMENTS, target: Expr):
    return Put(expr=expr, placement=placement, target=target)


@overload
def toggle(*class_refs: ClassDOMLiteral, on: Expr = None): ...


@overload
def toggle(attr_ref: AttrLiteral, /, on: Expr = None): ...


def toggle(*exprs: Expr, on: Expr = None):
    if len(exprs) == 1 and not isinstance(exprs[0], ClassDOMLiteral):
        return Toggle(attr_ref=exprs[0], on=on)
    else:
        return Toggle(class_refs=exprs, on=on)


def scroll(
    target: Expr,
    /,
    by: int,
    direction: SCROLL_DIRS = None,
    transition: SCROLL_TRANSITIONS = None,
):
    return Scroll(by=by, target=target, direction=direction, transition=transition)


def scroll_to(
    to: Expr,
    /,
    vertical_direction: SCROLL_TO_V_DIRS = None,
    horizontal_direction: SCROLL_TO_H_DIRS = None,
    offset: int = None,
    in_: Expr = None,
    transition: SCROLL_TRANSITIONS = None,
):
    return ScrollTo(
        to=to,
        vertical_direction=vertical_direction,
        horizontal_direction=horizontal_direction,
        offset=offset,
        in_=in_,
        transition=transition,
    )


def morph(expr: Expr, /, to: Expr):
    return Morph(expr=expr, to=to)


def wait(time: TimeLiteral):
    return Wait(time=time)


def focus(expr: Expr, /):
    return Focus(expr=expr)


def make(object_name: str, /, *from_: Expr | list[Expr], called: str = None):
    return Make(object_name=object_name, from_=from_, called=called)


def render(template: ClientComponent):
    def extract_expr(v):
        if isinstance(v, TemplatedVariableLiteral):
            return v.symbol
    if isinstance(template, (ClientComponent)):
        return Render(
            template_id=template._template_id,
            with_={f: extract_expr(getattr(template, f)) for f in template.field_names},
        )
    raise Exception("render only accepts Client Fragments")

def append(expr: Expr, / , to):
    return Append(expr=expr, to=to)

def js(*vars):
    _vars = []
    for v in vars:
        if isinstance(v, VariableLiteral):
            _vars.append(v.symbol)
        else:
            _vars.append(v)
    return Js(vars=_vars)