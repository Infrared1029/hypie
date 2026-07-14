from dataclasses import dataclass, is_dataclass
from typing import dataclass_transform
from textwrap import indent

import htpy
from markupsafe import Markup

from hypie.hs_ast.helpers import kebab_case_name, htpy_to_tree, tree_to_htpy


def transform_root(el: dict, component_name: str):
    if not isinstance(el, dict):
        return el
    k, v = next(iter(el.items()))
    if k == "_fragment":
        return {
            k: {
                "children": [transform_root(c, component_name) for c in v["children"]],
                "attrs": v["attrs"],
            }
        }
    if "data-hypie-component" in v["attrs"]:
        return el
    return {
        k: {
            "children": v["children"],
            "attrs": v["attrs"] + f' data-hypie-component="{component_name}"',
        }
    }


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


class ComponentMeta(type):
    def __getitem__(cls, children):
        instance = Component.__new__(cls)
        instance.children = children
        return instance


@dataclass_transform()
class Component(metaclass=ComponentMeta):
    children = None

    def __new__(cls, *args, **kwargs):
        dataclass_cls = cls
        if not is_dataclass(cls):
            dataclass_cls = dataclass(cls)
        instance = object.__new__(dataclass_cls)
        return instance

    def __init_subclass__(cls, as_fragment=False, hidden=False, contents=False):
        cls._hs_dsl_component = True
        cls.as_fragment = as_fragment
        cls.hidden = hidden
        cls.contents = contents
        cls.component_name = kebab_case_name(cls.__name__)
        cls.tag = f"div[data-hypie-component='{cls.component_name}']"

    def __html__(self):
        el = self.template()
        new_el = tree_to_htpy(transform_root(htpy_to_tree(el), self.component_name))
        # print(new_el)
        return new_el

    def __getitem__(self, children):
        if hasattr(self, "children") and self.children:
            raise Exception("Can not reassign children twice")
        self.children = children
        return self

    def template(self):
        return htpy.fragment[self.children]

    @staticmethod
    def style() -> dict:
        pass

    @classmethod
    def generate_style(cls, with_style_tags=True):
        output_style = cls.style()
        if output_style:
            css = generate_scoped_css(cls.tag, cls.style())
            if with_style_tags:
                return htpy.style[Markup(css)]
            return Markup(css)

    def encode(self, encoding: str = "utf-8", errors: str = "strict") -> bytes:
        return str(self).encode(encoding, errors)

    def __str__(self):
        return str(self.__html__())
