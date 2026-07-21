import re
from typing import Iterable
import htpy
from hypie.hs_ast.expressions import Expr


def flatten_iterable(iterable):
    if not isinstance(iterable, (list, tuple)):
        return [iterable]
    out = []
    for i in iterable:
        out.extend(flatten_iterable(i))
    return out


def kebab_case_name(name):
    return re.sub(r"(?<!^)([A-Z])", r"-\1", name).lower()



def htpy_to_tree(el):
    from hypie.experimental.components import Component, ServerFragment, ServerFragmentMeta
    from hypie.experimental.templates import Template, ClientFragment, For

    # print()
    if isinstance(el, Expr):
        return el
    elif isinstance(el, (str, float, int)) or el is None:
        return el
    elif isinstance(el, htpy.Fragment):
        element_type = "_fragment"
        nodes = el._node or []
        attrs = ""
    elif isinstance(el, (Component, ServerFragment, ServerFragmentMeta, Template, ClientFragment)):
        try:
            el = el.__html__()
        except TypeError as e: 
            # print(e)
            el = el().__html__()
        return htpy_to_tree(el) 
    elif isinstance(el, For):
        element_type = "_for"
        nodes = el.body or []
        attrs = {"loop_var": el.loop_var, "in_": el.in_}
    elif isinstance(el, htpy.BaseElement): # htpy.Element
        nodes = getattr(el, "_children", [])
        # print("ELEMENT IS!!!!", el, type(el))
        element_type = el._name
        attrs = el._attrs
    else:
        # print("ELEMENT IS", el)
        raise Exception(f"type {type(el)} is not supported.")

    children = []
    tree = {element_type: {"children": children, "attrs": attrs}}
    if isinstance(nodes, (list, tuple)) and len(nodes) == 1 and isinstance(nodes[0], (list, tuple)):
        nodes = nodes[0]
    elif not isinstance(nodes, (list, tuple)):
        nodes = [nodes]
    for c in nodes:
        children.append(htpy_to_tree(c))
    return tree


def tranform_tree(tree: dict, rules: dict):
    # print(tree)
    if isinstance(tree, str):
        # print(tree)
        if rules.get("text"):
            tree = rules["text"](tree)
        return tree
    elif not isinstance(tree, dict):
        return tree
    new_tree = {}
    k, v = next(iter(tree.items()))
    new_tree[k] = {
        "attrs": v["attrs"],
        "children": [tranform_tree(c, rules) for c in v["children"]],
    }
    return new_tree


def tree_to_htpy(tree):
    from hypie.experimental.templates import For

    if not isinstance(tree, dict):
        return tree
    k, v = next(iter(tree.items()))
    if k == "_for":
        _for = For(**v["attrs"])
        _for.body = [tree_to_htpy(b) for b in v["children"]]
        return _for
    children = []
    for c in v["children"]:
        children.append(tree_to_htpy(c))
    return (
        htpy.Element(k, children=children, attrs_str=v["attrs"])
        if k != "_fragment"
        else htpy.fragment[children]
    )

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
    if "data-hypie-component" in v.get("attrs", ""):
        return el
    return {
        k: {
            "children": v["children"],
            "attrs": v["attrs"] + f' data-hypie-component="{component_name}"',
        }
    }
