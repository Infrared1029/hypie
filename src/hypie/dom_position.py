from hypie.hs_ast.expressions import *


def next_(
    css_selector: CSSExpr,
    from_: Expr = None,
    within: Expr = None,
    with_wrapping: bool = False,
):
    return RelativetDOM(
        kind="next",
        css_selector=css_selector,
        from_=from_,
        within=within,
        with_wrapping=with_wrapping,
    )


def previous(
    css_selector: CSSExpr,
    from_: Expr = None,
    within: Expr = None,
    with_wrapping: bool = False,
):
    return RelativetDOM(
        kind="previous",
        css_selector=css_selector,
        from_=from_,
        within=within,
        with_wrapping=with_wrapping,
    )


def closest(css_selector: CSSExpr, to: Expr = None):
    return ClosestDOM(kind="closest", css_selector=css_selector, to=to)


def closest_parent(css_selector: CSSExpr, to: Expr = None):
    return ClosestDOM(kind="closest parent", css_selector=css_selector, to=to)
