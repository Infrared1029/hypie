from textwrap import indent

from hypie.experimental.client_component import ClientComponent
from hypie.experimental.server_component import ServerComponent


SPACES = " " * 2


def parse_css_dict(k, v: dict):
    parts = [f"{k} {{"]
    for sub_k, sub_v in v.items():
        if sub_k.strip() == "@apply":
            if isinstance(sub_v, list):
                parts.append(
                    indent(
                        f"@apply {' '.join(sub_v)};",
                        prefix=SPACES,
                        predicate=lambda _: True,
                    )
                )
            else:
                parts.append(
                    indent(f"@apply {sub_v};", prefix=SPACES, predicate=lambda _: True)
                )
        elif isinstance(sub_v, str):
            parts.append(
                indent(f"{sub_k}: {sub_v};", prefix=SPACES, predicate=lambda _: True)
            )
        elif isinstance(sub_v, dict):
            parts.append(
                indent(
                    parse_css_dict(sub_k, sub_v),
                    prefix=SPACES,
                    predicate=lambda _: True,
                )
            )
    parts.append("}")
    return "\n".join(parts)


def generate_scoped_css(component_name, css_dict):
    css_parts = [f"@scope ({component_name}) {{"]
    for k, v in css_dict.items():
        css_parts.append(
            indent(parse_css_dict(k, v), prefix=SPACES, predicate=lambda _: True)
        )
    css_parts.append("}")
    return "\n\n".join(css_parts)


def style(*components: ClientComponent | ServerComponent):
    def wrapper(func):
        def wrapped(*args, **kwargs):
            if args or kwargs:
                raise Exception("style function expects no arguments.")
            return func()
        wrapped._hypie_style = True
        wrapped._style = func()
        wrapped._components = set([f"[data-hypie-component='{c._component_name}']" for c in components])
        return wrapped
    return wrapper