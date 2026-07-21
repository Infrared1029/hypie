from __future__ import annotations

import inspect

from hypie.hs_ast.features import *
from hypie.commands import set_
from hypie.events import Event



def hs(*features):
    return Hs(features)



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

def behavior(func):
    sig = inspect.signature(func)
    args = [a for a in sig.parameters.keys()]
    features = func(**{a:VariableLiteral(a) for a in args})
    b = BehaviorF(func.__name__, param_list=args)[
        features
    ]
    def wrapped(*args, **kwargs):
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        named_args = bound_args.arguments
        return BoundedBehavior(name=func.__name__, named_args=named_args)
    wrapped._behavior = b
    wrapped._hs_behavior = True
    return wrapped

def Install(*bounded_behaviors: BoundedBehavior):
    _bounded_behaviors = []
    for b in bounded_behaviors:
        if not isinstance(b, BoundedBehavior) and getattr(b, "_hs_behavior", False) == True:
            _bounded_behaviors.append(b())
        else:
            _bounded_behaviors.append(b)
    return Hs([
        InstallF(b.name,b.named_args) for b in _bounded_behaviors
    ])