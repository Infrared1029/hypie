import importlib
import pathlib
import sys
import inspect

import argparse
from pathlib import Path

from hypie.experimental.components import Component
from hypie.experimental.templates import Template
from hypie.experimental.client_components import ClientComponent
from hypie.experimental.hyperscript import HyperScript

import watchfiles
from contextlib import contextmanager


def find_components_register_artifacts(in_path, out_path, out_files_prefix=""):
    IGNORE_LIST = [".venv", ".pyc", ".pyo"]
    MODULES = set()

    COMPONENTS: set[Component] = set()
    TEMPLATES: set[Template] = set()
    CLIENT_COMPONENTS: set[ClientComponent] = set()
    HYPERSCRIPT: set[HyperScript] = set()

    path = pathlib.Path(in_path).resolve()
    if not path.exists():
        raise Exception("Input path does not exist")
    # print(path, path.parent.resolve())
    outdir = pathlib.Path(out_path).resolve()
    if outdir.is_file():
        raise Exception("--output must be a dir")
    outdir.mkdir(exist_ok=True, parents=True)
    # print(outdir)
    sys.path.insert(0, str(path.parent.resolve()))
    path_parts_len = len(path.parts)
    python_files = pathlib.Path(path).glob("**/*.py")
    for file_path in python_files:
        if any(p in file_path.parts for p in IGNORE_LIST):
            continue
        module_name_parts = list(file_path.parts[path_parts_len - 1 : -1]) + [
            file_path.stem
        ]
        module_name = ".".join(module_name_parts)
        mod = importlib.import_module(module_name)
        MODULES.add(module_name)
        for _, obj in inspect.getmembers(mod):
            if hasattr(obj, "_hs_dsl_component") and obj._hs_dsl_component == True:
                COMPONENTS.add(obj)
            elif hasattr(obj, "_hs_dsl_template") and obj._hs_dsl_template == True:
                TEMPLATES.add(obj)
            elif (
                hasattr(obj, "_hs_dsl_client_component")
                and obj._hs_dsl_client_component == True
            ):
                CLIENT_COMPONENTS.add(obj)
            elif (
                hasattr(obj, "_hs_dsl_hyperscript") and obj._hs_dsl_hyperscript == True
            ):
                HYPERSCRIPT.add(obj)

    # create css files
    styles = []
    scripts = []
    hs_files = []
    html = []
    print(
        f"Done Proccessing: {len(COMPONENTS)} Component, {len(TEMPLATES)} Templates, {len(CLIENT_COMPONENTS)} Client Components {len(HYPERSCRIPT)} HS Scripts"
    )
    for c in COMPONENTS:
        style = c.generate_style(with_style_tags=False)
        if style:
            styles.append(style)

    for c_comp in CLIENT_COMPONENTS:
        template = c_comp.register_template()
        if template:
            html.append(str(template))

    for h in HYPERSCRIPT:
        script = h.register_hyperscript()
        if script:
            hs_files.append(script)

    style_contents = "\n".join(styles)
    if style_contents:
        with open(outdir / f"{out_files_prefix}_hypie_styles.css", "w") as f:
            f.write(style_contents)

    html_contents = "\n".join(html)
    if html_contents:
        with open(outdir / f"{out_files_prefix}_hypie_templates.html", "w") as f:
            f.write(html_contents)

    hs_contents = "\n".join(h.render() for h in hs_files)
    if hs_contents:
        with open(outdir / f"{out_files_prefix}_hypie_hyperscript._hs", "w") as f:
            f.write(hs_contents)

    # clean up
    sys.path.pop(0)
    for mod_name in MODULES:
        del sys.modules[mod_name]


def main():
    cli_parser = argparse.ArgumentParser(prog="hypie")

    subparsers = cli_parser.add_subparsers(dest="command", required=True)
    build_parser = subparsers.add_parser("build", help="Build components")
    build_parser.add_argument(
        "--input", "-i", type=Path, required=True, help="Path to components dir"
    )
    build_parser.add_argument(
        "--output", "-o", type=Path, required=True, help="Output path for file"
    )
    build_parser.add_argument(
        "--prefix",
        "-p",
        type=str,
        required=False,
        default="",
        help="output files prefix",
    )
    build_parser.add_argument(
        "--watch",
        "-w",
        action="store_true",
        required=False,
        default=False,
        help="watch dir and re-run build",
    )
    args = cli_parser.parse_args()

    if args.command == "build":
        find_components_register_artifacts(
            out_files_prefix=args.prefix, in_path=args.input, out_path=args.output
        )
        if args.watch:
            print("[hypie]: waiting for changes...")
            for _ in watchfiles.watch(args.input):
                print("[hypie]: detected changes, re-running build...")
                find_components_register_artifacts(
                    out_files_prefix=args.prefix,
                    in_path=args.input,
                    out_path=args.output,
                )
                print("[hypie]: waiting for changes...")
