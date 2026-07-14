from hypie.literals import var, Expr, TimeLiteral
from typing import Literal, dataclass_transform
from dataclasses import fields, dataclass, is_dataclass


@dataclass
class EventSpec:
    filter: Expr = (None,)
    count: int = (None,)
    from_: Expr | Literal["elsewhere"] = (None,)
    in_: Expr = (None,)
    debounce: TimeLiteral = (None,)
    throttle: TimeLiteral = (None,)


@dataclass_transform()
class Event:
    event_spec: EventSpec = None
    event_name: str = None
    event_args: list = None

    def __init_subclass__(cls):
        if not is_dataclass(cls):
            dataclass_cls = dataclass(cls)
        else:
            dataclass_cls = cls
        dataclass_cls.event_name = cls.__name__
        args = []
        for f in fields(dataclass_cls):
            setattr(cls, f.name, var(f"{cls.event_name}__{f.name}"))
            args.append(f"{cls.event_name}__{f.name}")
        cls.event_args = args

    @property
    def _bounded_args(self):
        # if not TEMPLATE_CONTEXT.get():
        return {
            f"{self.event_name}__{f.name}": getattr(self, f.name) for f in fields(self)
        }
        # template
        # out = {}
        # for f in fields(self):
        #     v = getattr(self, f.name)
        #     if isinstance(v, VariableLiteral):
        #         out[f"{self.event_name}__{f.name}"] = VariableLiteral(f"${{{v.render()}}}")
        #     else:
        #         out[f"{self.event_name}__{f.name}"] = v

        # return out

    @classmethod
    def with_spec(
        cls,
        filter=None,
        count: int = None,
        from_: Expr | Literal["elsewhere"] = None,
        in_: Expr = None,
        debounce: TimeLiteral = None,
        throttle: TimeLiteral = None,
    ):
        spec = EventSpec(
            filter=filter,
            count=count,
            from_=from_,
            in_=in_,
            debounce=debounce,
            throttle=throttle,
        )
        return type(cls)(
            cls.__name__,
            (cls,),
            {
                "event_spec": spec,
                "__qualname__": cls.__qualname__,
                "__module__": cls.__module__,
            },
        )
