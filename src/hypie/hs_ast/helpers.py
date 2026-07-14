import re
from typing import Iterable
import htpy
from hypie.hs_ast.expressions import Expr


def flatten_iterable(iterable):
    if not isinstance(iterable, Iterable):
        return [iterable]
    out = []
    for i in iterable:
        out.extend(flatten_iterable(i))
    return out


def kebab_case_name(name):
    return re.sub(r"(?<!^)([A-Z])", r"-\1", name).lower()


def htpy_to_tree(el: htpy.Element):
    if isinstance(el, htpy.Fragment):
        element_type = "_fragment"
        nodes = el._node or []
        children = []
        attrs = ""
    elif not isinstance(el, htpy.Element) and not hasattr(el, "_hs_dsl_component"):
        return el
    # print(type(el))
    else:
        if hasattr(el, "_hs_dsl_component") and el._hs_dsl_component == True:
            print("found component")
            try:
                el = el.__html__()
            except TypeError:
                el = el().__html__()
        nodes = getattr(el, "_children", [])
        children = []
        element_type = el._name
        attrs = el._attrs
    tree = {element_type: {"children": children, "attrs": attrs}}
    # print(tree)
    # if hasattr(el, "_children") and el._children:
    if (
        nodes is None
        or isinstance(nodes, (htpy.Element, str, int, float, bool, Expr))
        or hasattr(nodes, "_hs_dsl_component")
    ):
        children.append(htpy_to_tree(nodes))
    else:
        for c in nodes:
            # print(type(c))
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
    if not isinstance(tree, dict):
        return tree
    k, v = next(iter(tree.items()))
    children = []
    for c in v["children"]:
        children.append(tree_to_htpy(c))
    return (
        htpy.Element(k, children=children, attrs_str=v["attrs"])
        if k != "_fragment"
        else htpy.fragment[children]
    )
