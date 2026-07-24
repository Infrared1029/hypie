from dataclasses import dataclass, is_dataclass
from typing import dataclass_transform
from textwrap import indent

import htpy
from markupsafe import Markup

from hypie.hs_ast.helpers import kebab_case_name, htpy_to_tree, tree_to_htpy, transform_root



class ServerComponentMeta(type):
    def __getitem__(cls, children):
        instance = ServerComponent.__new__(cls)
        instance.children = children
        return instance


@dataclass_transform()
class ServerComponent(metaclass=ServerComponentMeta):
    children = None

    def __new__(cls, *args, **kwargs):
        dataclass_cls = cls
        if not is_dataclass(cls):
            dataclass_cls = dataclass(cls)
        instance = object.__new__(dataclass_cls)
        return instance

    def __init_subclass__(cls):
        # cls._hs_dsl_component = True
        cls._hypie_server_component = True
        # cls.component_name = kebab_case_name(cls.__name__)
        cls._component_name = kebab_case_name(cls.__name__)
        cls._tag = f"div[data-hypie-component='{cls._component_name}']"

    def __html__(self):
        el = self.template()
        new_el = tree_to_htpy(transform_root(htpy_to_tree(el), self._component_name))
        # print(new_el)
        return new_el

    def __getitem__(self, children):
        if hasattr(self, "children") and self.children:
            raise Exception("Can not reassign children twice")
        self.children = children
        return self

    def template(self):
        return htpy.fragment[self.children]

    def encode(self, encoding: str = "utf-8", errors: str = "strict") -> bytes:
        return str(self).encode(encoding, errors)

    def __str__(self):
        return str(self.__html__())
