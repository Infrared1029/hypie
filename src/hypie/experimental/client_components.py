import dataclasses
from typing import dataclass_transform

import htpy

from hypie import hs
from hypie.literals import var
from hypie.hs_ast.helpers import (
    kebab_case_name,
    htpy_to_tree,
    tranform_tree,
    tree_to_htpy,
)
from hypie.hs_ast.expressions import VarTemplateString, python_to_hs
from hypie.commands import set_


@dataclass_transform()
class ClientComponent:
    field_names = None

    def __init_subclass__(cls):
        dataclasses.dataclass(cls)
        cls._hs_dsl_client_component = True
        for f in dataclasses.fields(cls):
            setattr(cls, f.name, var(f"^{f.name}"))
        setattr(cls, "field_names", [f.name for f in dataclasses.fields(cls)])
        cls.component_name = kebab_case_name(cls.__name__)
        if "-" not in cls.component_name:
            cls.component_name += "-view"
        cls.script = hs()
        for f in dataclasses.fields(cls):
            cls.script.add_features(set_(var(f"^{f.name}"), to=var(f"attrs.{f.name}")))

    @classmethod
    def template(cls):
        pass

    @classmethod
    def register_template(cls):
        template = cls.template()
        tree = htpy_to_tree(template)
        transformed_tree = tranform_tree(tree, rules={"text": cls.handle_text_nodes})
        transformed_htpy = tree_to_htpy(transformed_tree)
        return htpy.script(
            type="text/hyperscript-template", component=cls.component_name, _=cls.script
        )[transformed_htpy]

    @staticmethod
    def handle_text_nodes(text):
        # print(text)
        exp_template = VarTemplateString(text)
        if not exp_template.interpolations:
            return text
        return exp_template.transform(interp_func=lambda x: "${" + x + "}")

    def __html__(self):
        attrs = {f: python_to_hs(getattr(self, f)) for f in self.field_names}
        # print(attrs)
        return htpy.Element(name=self.component_name)(**attrs)

    def encode(self, encoding: str = "utf-8", errors: str = "strict") -> bytes:
        return str(self).encode(encoding, errors)

    def __str__(self):
        return str(self.__html__())


class Modal(ClientComponent):
    message: str = "some test"
    todo_id: int = 1

    @classmethod
    def template(cls):
        return htpy.div[
            # "hello",
            cls.todo_id
        ]
