import dataclasses
import htpy

# from hypie.literals import var
from hypie.hs_ast.expressions import TemplatedVariableLiteral
from hypie.hs_ast.helpers import (
    kebab_case_name,
    htpy_to_tree,
    tranform_tree,
    tree_to_htpy,
)
from hypie.hs_ast.expressions import VarTemplateString
from typing import dataclass_transform


@dataclass_transform()
class Template:
    field_names = None

    def __init_subclass__(cls):
        dataclasses.dataclass(cls)
        cls._hs_dsl_template = True
        for f in dataclasses.fields(cls):
            setattr(cls, f.name, TemplatedVariableLiteral(f.name))
        setattr(cls, "field_names", [f.name for f in dataclasses.fields(cls)])
        cls.id = kebab_case_name(cls.__name__)

    # @classmethod
    def template(cls):
        pass

    @classmethod
    def register_template(cls):
        template = cls(
            **{f: TemplatedVariableLiteral(f) for f in cls.field_names}
        ).template()
        tree = htpy_to_tree(template)
        transformed_tree = tranform_tree(tree, rules={"text": cls.handle_text_nodes})
        transformed_htpy = tree_to_htpy(transformed_tree)
        return htpy.script(type="text/hyperscript-template", id=cls.id)[
            transformed_htpy
        ]

    @staticmethod
    def handle_text_nodes(text):
        # print(text)
        exp_template = VarTemplateString(text)
        if not exp_template.interpolations:
            return text
        return exp_template.transform(interp_func=lambda x: "${" + x + "}")
