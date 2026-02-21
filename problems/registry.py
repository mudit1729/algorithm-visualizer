from __future__ import annotations

import importlib
import pkgutil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from problems.base_problem import Problem


def discover_problems() -> dict[str, type[Problem]]:
    """Scan the problems package and return all Problem subclasses."""
    from problems.base_problem import Problem as BaseProblem

    import problems as pkg

    result: dict[str, type[Problem]] = {}
    for _importer, modname, _ispkg in pkgutil.iter_modules(pkg.__path__):
        if modname.startswith("_") or modname in ("base_problem", "registry"):
            continue
        module = importlib.import_module(f"problems.{modname}")
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, BaseProblem)
                and attr is not BaseProblem
            ):
                result[attr.name()] = attr
    return result
