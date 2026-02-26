from __future__ import annotations

from core.step import Step
from core.tracer import DSUTracer
from problems.base_problem import Problem

_SOURCE = """\
def accountsMerge(accounts):
    parent = list(range(len(accounts)))
    rank = [0] * len(accounts)

    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx == ry:
            return False
        if rank[rx] < rank[ry]:
            rx, ry = ry, rx
        parent[ry] = rx
        if rank[rx] == rank[ry]:
            rank[rx] += 1
        return True

    email_to_id = {}
    for i, account in enumerate(accounts):
        for email in account[1:]:
            if email in email_to_id:
                union(i, email_to_id[email])
            email_to_id[email] = i

    groups = {}
    for i in range(len(accounts)):
        root = find(i)
        groups.setdefault(root, []).append(i)

    return groups"""


class AccountsMerge(Problem):
    @staticmethod
    def name() -> str:
        return "Accounts Merge"

    @staticmethod
    def topic() -> str:
        return "Union Find"

    @staticmethod
    def subtopic() -> str:
        return "Grouping"

    @staticmethod
    def description() -> str:
        return "LeetCode #721: Merge accounts that share emails using Union-Find."

    @staticmethod
    def long_description() -> str:
        return (
            "Given a list of accounts where each account has a name and a set of "
            "emails, merge accounts belonging to the same person. Two accounts "
            "belong to the same person if they share at least one common email.\n\n"
            "Example:\n"
            "Input: `[[\"Alice\",\"a@mail\",\"b@mail\"],[\"Bob\",\"c@mail\"],"
            "[\"Alice\",\"b@mail\",\"d@mail\"]]`\n"
            "Output: Accounts 0 and 2 merge (share `b@mail`), account 1 stays separate.\n\n"
            "Constraints:\n\n"
            "- `1 <= accounts.length <= 1000`\n"
            "- `1 <= accounts[i].length <= 10`\n"
            "- All emails are valid and lowercase"
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
    def theory() -> str:
        return """Approach: Merge accounts that share at least one common email using Union-Find. For each account, union all its emails together. Then group emails by their root representative to form merged accounts. Sort emails within each group.

Time Complexity: O(N × L × α(N)) where N is total emails and L is the average email length (for hashing), α is the inverse Ackermann function.

Space Complexity: O(N × L) for the Union-Find mapping and merged accounts.

Key Insight: This is a connected components problem — two accounts are connected if they share an email. Union-Find efficiently merges these sets. Map emails to a representative, then group by representative.

Interview Tip: DFS/BFS on an email graph also works but Union-Find is cleaner. Remember to track which name belongs to each email — the first account that mentions an email determines the name."""

    @staticmethod
    def generate_steps(**kwargs: object) -> list[Step]:
        preset = int(kwargs.get("preset", 1))

        presets = {
            1: [
                ["Alice", "a1@m", "a2@m"],
                ["Bob", "b1@m"],
                ["Alice", "a2@m", "a3@m"],
                ["Carol", "c1@m", "c2@m"],
                ["Dave", "d1@m"],
                ["Carol", "c2@m", "d1@m"],
                ["Eve", "e1@m"],
                ["Frank", "e1@m", "f1@m"],
            ],
        }

        accounts = presets.get(preset, presets[1])
        n = len(accounts)

        parent = list(range(n))
        rank = [0] * n

        dsu = DSUTracer(list(range(n)))
        steps: list[Step] = []

        # Set labels to account names with index
        for i in range(n):
            dsu.set_label(i, f"{i}:{accounts[i][0]}")

        def snap(line: int, desc: str = "") -> None:
            steps.append(dsu.snapshot(line, desc))

        def find(x: int) -> int:
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        def union(x: int, y: int) -> bool:
            rx, ry = find(x), find(y)
            if rx == ry:
                return False
            if rank[rx] < rank[ry]:
                rx, ry = ry, rx
            parent[ry] = rx
            if rank[rx] == rank[ry]:
                rank[rx] += 1
            # Update DSU tracer to reflect parent change
            dsu.set_parent(ry, rx)
            dsu.set_rank(rx, rank[rx])
            return True

        def sync_dsu() -> None:
            """Sync all parents in DSU tracer after path compression."""
            for i in range(n):
                root = find(i)
                if root != i:
                    dsu.set_parent(i, root)
                else:
                    dsu.set_parent(i, i)

        accts_str = ", ".join(f"{i}:{a[0]}" for i, a in enumerate(accounts))
        dsu.log(f"Accounts: {accts_str}")
        snap(1, f"{n} accounts, each its own group")

        # Process emails
        email_to_id: dict[str, int] = {}

        for i, account in enumerate(accounts):
            name = account[0]
            emails = account[1:]

            dsu.deselect_all()
            dsu.select(i)
            dsu.log(f"Process account {i} ({name}): {emails}")
            snap(28, f"Process account {i} ({name})")

            for email in emails:
                if email in email_to_id:
                    j = email_to_id[email]
                    dsu.select(j)
                    dsu.log(f"  Email '{email}' shared with account {j}")
                    snap(30, f"'{email}' links {i} and {j}")

                    ri, rj = find(i), find(j)
                    if ri != rj:
                        union(i, j)
                        sync_dsu()
                        # Patch all nodes in the merged group
                        dsu.depatch_all()
                        for k in range(n):
                            if find(k) == find(i):
                                dsu.patch(k)
                        dsu.log(f"  Union accounts {i} and {j}")
                        snap(31, f"Union {i} and {j}")
                    else:
                        dsu.log(f"  Already in same group")
                        snap(13, f"Already merged")

                    dsu.deselect(j)
                else:
                    dsu.log(f"  New email '{email}' -> account {i}")

                email_to_id[email] = i

            dsu.deselect(i)

        # Final grouping
        dsu.deselect_all()
        dsu.depatch_all()
        groups: dict[int, list[int]] = {}
        for i in range(n):
            root = find(i)
            groups.setdefault(root, []).append(i)

        # Patch each group
        for root, members in groups.items():
            for m in members:
                dsu.patch(m)

        group_str = ", ".join(
            f"{{{','.join(str(m) for m in members)}}}"
            for members in groups.values()
        )
        dsu.log(f"Final groups: {group_str}")
        snap(33, f"Result: {len(groups)} merged groups")
        return steps
