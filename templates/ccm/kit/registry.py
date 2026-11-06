"""Every section type the kit can render, found on disk.

A type is a module in kit/sections. It states its NAME, whether it needs a
title, the order it takes on the guide, the fields the guide's table names,
how it renders, and one specimen. Nothing lists the types, so a new type is
one new file.
"""
import importlib
import pkgutil

from . import sections


def load():
    modules, files = [], {}
    for found in pkgutil.iter_modules(sections.__path__):
        module = importlib.import_module(f'{sections.__name__}.{found.name}')
        # Two modules with one NAME would take the same key, and the second
        # would quietly replace the first: the report would render the type
        # the sort order happened to put last. The build stops instead and
        # names both files.
        if module.NAME in files:
            raise ValueError(
                f'two section modules state the name {module.NAME!r}: '
                f'{files[module.NAME]}.py and {found.name}.py. A section type '
                f'is one module, so rename one of them or give it its own NAME'
            )
        files[module.NAME] = found.name
        modules.append(module)
    # The order is stated by the module and broken by the name, so the guide
    # reads the same on every machine.
    modules.sort(key=lambda module: (getattr(module, 'ORDER', 50), module.NAME))
    return {module.NAME: module for module in modules}


REGISTRY = load()
# Every section type that renders a heading and a contents link needs a title.
TITLED = tuple(name for name, module in REGISTRY.items() if module.TITLE_REQUIRED)
