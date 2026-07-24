import re
import dataclasses
from textwrap import indent

import htpy


from markupsafe import Markup
# from hypie.literals import var
from hypie.hs_ast.expressions import TemplatedVariableLiteral, VariableLiteral
from hypie.hs_ast.helpers import (
    kebab_case_name,
    htpy_to_tree,
    # tranform_tree,
    tree_to_htpy,
    transform_root
)
from hypie.hs_ast.expressions import VarTemplateString
from typing import dataclass_transform


def tranform_tree(tree: dict, rules: dict):
    # print(tree)
    if isinstance(tree, str):
        # print(tree)
        if rules.get("text"):
            tree = rules["text"](tree)
        return Markup(tree)
    elif not isinstance(tree, dict):
        return tree
    new_tree = {}
    k, v = next(iter(tree.items()))
    # print("ATTRS:", v["attrs"])
    new_tree[k] = {
        "attrs": v["attrs"] if not isinstance(v["attrs"], str) else Markup(ClientComponent.handle_text_nodes(v["attrs"], re.compile(r"\?VAR:&lt;(.*?)&gt;\?"))).unescape(),
        "children": [tranform_tree(c, rules) for c in v["children"]],
    }
    return new_tree


@dataclass_transform()
class ClientComponent:
    field_names = None

    def __init_subclass__(cls):
        dataclasses.dataclass(cls)
        cls._hs_dsl_template = True
        for f in dataclasses.fields(cls):
            setattr(cls, f.name, TemplatedVariableLiteral(VariableLiteral(f.name)))
        setattr(cls, "field_names", [f.name for f in dataclasses.fields(cls)])
        # cls.__post_init__ = lambda s: print(s)
        cls._component_name = kebab_case_name(cls.__name__)
        cls._template_id = cls._component_name + "-hypie-template"
    
    def __post_init__(self):
        for f in self.field_names:
            if not isinstance(getattr(self, f), TemplatedVariableLiteral):
                setattr(self, f, TemplatedVariableLiteral(getattr(self, f)))

    # @classmethod
    def template(self):
        return htpy.fragment

    def __html__(self):
        el = self.template()
        new_el = tree_to_htpy(transform_root(htpy_to_tree(el), self._component_name))
        return new_el
        

    @classmethod
    def register_template(cls):
        template = cls(
            **{f: TemplatedVariableLiteral(VariableLiteral(f)) for f in cls.field_names}
        ).__html__()
        tree = htpy_to_tree(template)
        transformed_tree = tranform_tree(tree, rules={"text": cls.handle_text_nodes})
        transformed_htpy = tree_to_htpy(transformed_tree)
        return htpy.script(type="text/hyperscript-template", id=cls._template_id)[
            transformed_htpy
        ]

    @staticmethod
    def handle_text_nodes(text, pattern=None):
        # print(text)
        exp_template = VarTemplateString(text, pattern=pattern)
        if not exp_template.interpolations:
            return text
        return Markup(exp_template.transform(interp_func=lambda x: "${" + x + "}"))

class For:
    def __init__(self, loop_var, in_):
        self.loop_var = loop_var
        if isinstance(self.loop_var, TemplatedVariableLiteral):
            self.loop_var = loop_var.symbol
        
        self.in_ = in_
        if isinstance(self.in_, TemplatedVariableLiteral):
            self.in_ = self.in_.symbol
        self.body = []    
    
    def __getitem__(self, body):
        if not isinstance(body, (list, tuple)):
            self.body = [body]
        else:
            self.body = body
        return self
    
    def __html__(self):
        header = f"\n#for {self.loop_var.render()} in {self.in_.render()}"
        body = []
        for b in self.body:
            # if isinstance(b, (htpy.Element, For)):
            #     body.append(indent(b.__html__(), 4 *" ", lambda _: True))
            # else:
            #     body.append(b)
            body.append(indent(str(b), 4 *" ", lambda _: True))
        footer = "#end\n"
        return "\n".join([header, *body, footer])
    
    __str__ = __html__
