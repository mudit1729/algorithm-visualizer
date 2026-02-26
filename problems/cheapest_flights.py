from __future__ import annotations

from core.step import Step
from core.tracer import GraphTracer
from problems.base_problem import Problem

_SOURCE = """\
def findCheapestPrice(n, flights, src, dst, k):
    INF = float('inf')
    prices = [INF] * n
    prices[src] = 0

    for i in range(k + 1):
        tmp = prices[:]
        for u, v, w in flights:
            if prices[u] != INF:
                if prices[u] + w < tmp[v]:
                    tmp[v] = prices[u] + w
        prices = tmp

    return prices[dst] if prices[dst] != INF else -1"""


class CheapestFlights(Problem):
    @staticmethod
    def name() -> str:
        return "Cheapest Flights Within K Stops"

    @staticmethod
    def topic() -> str:
        return "Shortest Path"

    @staticmethod
    def subtopic() -> str:
        return "BFS / Bellman-Ford"

    @staticmethod
    def description() -> str:
        return "LeetCode #787: Find cheapest price from src to dst with at most K stops."

    @staticmethod
    def long_description() -> str:
        return (
            "There are `n` cities connected by `flights` where "
            "`flights[i] = [from, to, price]`. Given `src`, `dst`, and `k`, "
            "return the **cheapest price** from `src` to `dst` with at most "
            "`k` stops. If no such route exists, return `-1`.\n\n"
            "This is solved using a modified Bellman-Ford algorithm that runs "
            "exactly `k + 1` relaxation rounds (one for each allowed hop).\n\n"
            "Example 1:\n"
            "Input: `n = 4`, `flights = [[0,1,100],[1,2,100],[2,0,100],"
            "[1,3,600],[2,3,200]]`, `src = 0`, `dst = 3`, `k = 1`\n"
            "Output: `700`\n\n"
            "Constraints:\n\n"
            "- `1 <= n <= 100`\n"
            "- `0 <= flights.length <= n * (n - 1) / 2`\n"
            "- `0 <= src, dst, k < n`"
        )

    @staticmethod
    def source_code() -> str:
        return _SOURCE

    @staticmethod
    def renderer_type() -> str:
        return "graph"

    @staticmethod
    def default_params() -> dict[str, object]:
        return {"preset": 1}

    @staticmethod
    def theory() -> str:
        return """Approach: Find the cheapest flight path with at most K stops. This is a modified Bellman-Ford / BFS problem. Run at most K+1 relaxation rounds (since K stops means K+1 edges). Each round, relax all edges using the distances from the previous round to avoid using too many edges.

Time Complexity: O(K × E) where K is the max stops and E is the number of flights.

Space Complexity: O(V) for the distance array.

Key Insight: Unlike standard Dijkstra's, we can't just greedily expand the closest node because the hop limit constraint means a longer-distance path with fewer hops might be better. Using a copy of the distance array per round prevents counting extra hops.

Interview Tip: Three approaches work: modified Bellman-Ford (simplest), BFS with pruning, or Dijkstra's with a state of (cost, node, stops_remaining)."""

    @staticmethod
    def generate_steps(**kwargs: object) -> list[Step]:
        preset = int(kwargs.get("preset", 1))

        presets = {
            1: (
                8,
                [
                    (0, 1, 100), (0, 2, 500), (1, 2, 100), (1, 3, 200),
                    (2, 4, 50), (3, 4, 150), (3, 5, 100), (4, 5, 80),
                    (4, 6, 200), (5, 7, 100), (6, 7, 50), (2, 6, 400),
                ],
                0,   # src
                7,   # dst
                2,   # k stops
            ),
        }

        n, flights, src, dst, k = presets.get(preset, presets[1])

        INF = float("inf")
        prices = [INF] * n
        prices[src] = 0

        tracer = GraphTracer(list(range(n)), directed=True)
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(tracer.snapshot(line, desc))

        def fmt(d: float) -> str:
            if d == INF:
                return "INF"
            return str(int(d))

        # Add all edges with weights
        for u, v, w in flights:
            tracer.add_edge(u, v, weight=w)

        # Initial state: badge src with cost 0
        tracer.set_node_badge(src, "0", "#a6e3a1")
        tracer.set_node_color(src, "#a6e3a1")
        tracer.log(
            f"Nodes: {n}, src={src}, dst={dst}, k={k} stops"
        )
        snap(4, f"src={src}, dst={dst}, k={k} stops; prices[{src}]=0")

        # Bellman-Ford with K+1 iterations
        for i in range(k + 1):
            tmp = prices[:]

            tracer.deselect_all_nodes()
            tracer.deselect_all_edges()
            tracer.log(f"--- Iteration {i} (hop {i+1}/{k+1}) ---")
            snap(7, f"Iteration {i}: begin hop {i+1}/{k+1}")

            updated_any = False
            for u, v, w in flights:
                if prices[u] == INF:
                    continue

                tracer.select_edge(u, v)
                tracer.select_node(u)
                tracer.select_node(v)

                new_cost = prices[u] + w
                if new_cost < tmp[v]:
                    old_cost = tmp[v]
                    tmp[v] = new_cost

                    tracer.set_edge_class(u, v, "relaxed")
                    tracer.set_node_badge(v, fmt(new_cost), "#89b4fa")
                    tracer.set_node_color(v, "#89b4fa")
                    tracer.log(
                        f"  Relax {u}->{v}: {fmt(old_cost)} -> {fmt(new_cost)}"
                    )
                    snap(
                        12,
                        f"Relax {u}->{v}: cost {fmt(new_cost)}",
                    )
                    updated_any = True

                tracer.deselect_edge(u, v)
                tracer.deselect_node(u)
                tracer.deselect_node(v)
                tracer.set_edge_class(u, v, "")

            prices = tmp

            # Update all badges to current prices
            for node in range(n):
                if prices[node] != INF:
                    tracer.set_node_badge(node, fmt(prices[node]), "#a6e3a1")

            if not updated_any:
                tracer.log(f"  No updates in iteration {i}, early stop")
                snap(14, f"No updates, early termination")
                break

            tracer.log(f"End iteration {i}: prices={[fmt(p) for p in prices]}")
            snap(14, f"End iteration {i}")

        # Final result
        tracer.deselect_all_nodes()
        tracer.deselect_all_edges()
        result = prices[dst] if prices[dst] != INF else -1

        if result != -1:
            tracer.select_node(dst)
            tracer.set_node_color(dst, "#a6e3a1")
            tracer.set_node_badge(dst, fmt(result), "#a6e3a1")

        tracer.log(f"Result: cheapest price = {result}")
        snap(14, f"Cheapest price src={src} to dst={dst}: {result}")
        return steps
