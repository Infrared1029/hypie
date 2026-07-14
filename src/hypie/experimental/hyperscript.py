import dataclasses

from hypie.literals import var
from hypie.commands import set_
from hypie import hs


class HyperScript:
    def __new__(cls, *args, **kwargs):
        raise Exception("HyperScript class is not meant to be instantiated.")

    def __init_subclass__(cls):
        if not dataclasses.is_dataclass(cls):
            dataclasses.dataclass(cls, init=False)
        cls._hs_dsl_hyperscript = True
        cls._vars_script = hs()
        for f in dataclasses.fields(cls):
            setattr(cls, f.name, var(f"${cls.__name__}__{f.name}"))
            cls._vars_script.add_features(
                set_(
                    var(f"${cls.__name__}__{f.name}"),
                    to=f.default if f.default != dataclasses.MISSING else None,
                )
            )

    @classmethod
    def script(cls):
        return hs()

    @classmethod
    def register_hyperscript(cls):
        _hs = hs()
        _hs.add_features(cls._vars_script)
        _hs.add_features(cls.script())
        return _hs
