from hypie.hs_ast.features import *
from hypie.commands import set_
from hypie.events import Event


# so you can call it as init() or init[] both work
Init = InitF()


def On(*event_specs: EventSpecLiteral | str, queue: ON_QUEUE = None):
    _event_specs = []
    for event in event_specs:
        if isinstance(event, type) and issubclass(event, Event):
            _event_specs.append(
                EventSpecLiteral(
                    event_name=event.event_name,
                    args=event.event_args,
                    filter=event.event_spec and event.event_spec.filter,
                    count=event.event_spec and event.event_spec.count,
                    from_=event.event_spec and event.event_spec.from_,
                    in_=event.event_spec and event.event_spec.in_,
                    debounce=event.event_spec and event.event_spec.debounce,
                    throttle=event.event_spec and event.event_spec.throttle,
                )
            )
        else:
            _event_specs.append(event)
    return OnF(event_specs=_event_specs, queue=queue)


Live = LiveF()


def Bind(exprA: Expr, exprB: Expr, /):
    return BindF(exprA=exprA, exprB=exprB)


Set = set_


def WhenChange(*exprs):
    return WhenF(exprs=exprs)


def Js(javascript: str, /):
    return JsF(javascript)
