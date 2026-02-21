from __future__ import annotations

from core.step import Step
from core.tracer import DSUTracer
from problems.base_problem import Problem

_SOURCE = """\
def equationsPossible(equations):
    parent = list(range(26))
    rank = [0] * 26

    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx == ry:
            return
        if rank[rx] < rank[ry]:
            rx, ry = ry, rx
        parent[ry] = rx
        if rank[rx] == rank[ry]:
            rank[rx] += 1

    for eq in equations:
        if eq[1] == '=':
            x = ord(eq[0]) - ord('a')
            y = ord(eq[3]) - ord('a')
            union(x, y)

    for eq in equations:
        if eq[1] == '!':
            x = ord(eq[0]) - ord('a')
            y = ord(eq[3]) - ord('a')
            if find(x) == find(y):
                return False

    return True"""


class EqualityEquations(Problem):
    @staticmethod
    def name() -> str:
        return "Equality Equations"

    @staticmethod
    def topic() -> str:
        return "Union Find"

    @staticmethod
    def subtopic() -> str:
        return "Constraint Satisfaction"

    @staticmethod
    def description() -> str:
        return "LeetCode #990: Check if equality and inequality constraints on variables are satisfiable."

    @staticmethod
    def long_description() -> str:
        return (
            "Given an array of strings `equations` representing relationships "
            "between variables (e.g. `\"a==b\"`, `\"b!=c\"`), determine if it is "
            "possible to assign integers to variables to satisfy all equations.\n\n"
            "Example 1:\n"
            "Input: `[\"a==b\",\"b!=a\"]`\n"
            "Output: `false`\n\n"
            "Example 2:\n"
            "Input: `[\"a==b\",\"b==c\",\"a==c\"]`\n"
            "Output: `true`\n\n"
            "Constraints:\n\n"
            "- `1 <= equations.length <= 500`\n"
            "- Each equation is 4 characters: `xi==yi` or `xi!=yi`\n"
            "- Variables are lowercase letters"
        )

    @staticmethod
    def source_code() -> str:
        return _SOURCE

    @staticmethod
    def renderer_type() -> str:
        return "dsu"

    @staticmethod
    def default_params() -> dict[str, object]:
        return {"preset": 1}

    @staticmethod
    def generate_steps(**kwargs: object) -> list[Step]:
        preset = int(kwargs.get("preset", 1))

        presets = {
            # Has a contradiction: a==b, b==c, c==d, but a!=d
            1: [
                "a==b", "b==c", "c==d", "e==f", "f==g", "g==h",
                "a!=d", "e!=h",
            ],
        }

        equations = presets.get(preset, presets[1])

        # Determine which variables are used
        used_vars: set[str] = set()
        for eq in equations:
            used_vars.add(eq[0])
            used_vars.add(eq[3])
        var_list = sorted(used_vars)
        var_to_idx = {v: i for i, v in enumerate(var_list)}
        n = len(var_list)

        parent = list(range(n))
        rank = [0] * n

        dsu = DSUTracer(list(range(n)))
        steps: list[Step] = []

        for i, v in enumerate(var_list):
            dsu.set_label(i, v)

        def snap(line: int, desc: str = "") -> None:
            steps.append(dsu.snapshot(line, desc))

        def find(x: int) -> int:
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        def union(x: int, y: int) -> None:
            rx, ry = find(x), find(y)
            if rx == ry:
                return
            if rank[rx] < rank[ry]:
                rx, ry = ry, rx
            parent[ry] = rx
            if rank[rx] == rank[ry]:
                rank[rx] += 1
            dsu.set_parent(ry, rx)
            dsu.set_rank(rx, rank[rx])

        def sync_dsu() -> None:
            for i in range(n):
                root = find(i)
                if root != i:
                    dsu.set_parent(i, root)
                else:
                    dsu.set_parent(i, i)

        eq_str = ", ".join(equations)
        dsu.log(f"Equations: {eq_str}")
        dsu.log(f"Variables: {', '.join(var_list)}")
        snap(1, f"{len(equations)} equations, {n} variables")

        # Phase 1: Process equality constraints
        dsu.log("Phase 1: Process == equations")
        snap(22, "Phase 1: equality constraints")

        for eq in equations:
            if eq[1] == "=":
                x_var, y_var = eq[0], eq[3]
                x, y = var_to_idx[x_var], var_to_idx[y_var]

                dsu.deselect_all()
                dsu.select(x)
                dsu.select(y)
                dsu.log(f"Process: {x_var}=={y_var}")
                snap(24, f"{x_var}=={y_var}")

                rx, ry = find(x), find(y)
                if rx != ry:
                    union(x, y)
                    sync_dsu()
                    # Patch the group
                    root = find(x)
                    dsu.depatch_all()
                    for i in range(n):
                        if find(i) == root:
                            dsu.patch(i)
                    dsu.log(f"  Union {x_var} and {y_var}")
                    snap(25, f"Union {x_var} and {y_var}")
                else:
                    dsu.log(f"  Already equal")
                    snap(10, f"Already in same set")

                dsu.deselect_all()

        # Phase 2: Check inequality constraints
        dsu.deselect_all()
        dsu.depatch_all()
        dsu.log("Phase 2: Check != equations")
        snap(28, "Phase 2: inequality constraints")

        result = True
        for eq in equations:
            if eq[1] == "!":
                x_var, y_var = eq[0], eq[3]
                x, y = var_to_idx[x_var], var_to_idx[y_var]

                dsu.deselect_all()
                dsu.clear_all_errors()
                dsu.select(x)
                dsu.select(y)
                dsu.log(f"Check: {x_var}!={y_var}")
                snap(30, f"Check {x_var}!={y_var}")

                if find(x) == find(y):
                    # Contradiction found
                    dsu.mark_error(x)
                    dsu.mark_error(y)
                    # Mark all in the group as error
                    root = find(x)
                    for i in range(n):
                        if find(i) == root:
                            dsu.mark_error(i)
                    dsu.log(f"  CONTRADICTION! {x_var} and {y_var} are equal")
                    snap(33, f"Contradiction: {x_var}=={y_var} but {x_var}!={y_var}")
                    result = False
                    break
                else:
                    dsu.log(f"  OK: {x_var} and {y_var} in different sets")
                    dsu.patch(x)
                    dsu.patch(y)
                    snap(32, f"OK: {x_var} != {y_var}")

                dsu.deselect_all()

        # Final result
        dsu.deselect_all()
        if result:
            dsu.clear_all_errors()
            for i in range(n):
                dsu.patch(i)
        dsu.log(f"Result: {'Satisfiable' if result else 'Not satisfiable'}")
        snap(35, f"Result: {'true' if result else 'false'}")
        return steps
