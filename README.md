# Algorithm Visualizer

Interactive visualizer for interview-style algorithm problems, focused on graph/grid patterns.

The app serves a browser UI where you can:
- pick a problem by topic/subtopic,
- run it with default parameters,
- step through execution snapshots,
- track active source-code lines,
- inspect an execution log.

## Current status

- Language/runtime: Python 3 + Flask backend, vanilla JS frontend
- Rendering modes implemented: `board`, `graph`, `array`
- Problems implemented: 12
- Guide alignment source: `graph-problems-guide.md` (42 problems total in your guide)

## Features

- Auto-discovery of problems (`problems/*.py`) via subclass scanning
- Unified `Step` snapshot model for all visualizers
- Playback controls: start/back/play/forward/end + speed slider
- Click-to-seek progress bar
- Keyboard controls on visualizer screen:
  - `Space`: play/pause
  - `Left` / `Right`: previous/next step
  - `Home` / `End`: first/last step
  - `Esc`: back to problem list
- Side code panel with syntax highlighting and active-line tracking
- Collapsible log drawer

## Project structure

```text
visualize_algo/
  main.py                     # Flask app + API
  requirements.txt
  core/
    step.py                   # Step payload schema
    tracer.py                 # Mutable tracers -> snapshots
  problems/
    base_problem.py           # Problem interface
    registry.py               # Dynamic discovery
    *.py                      # Individual problem implementations
  templates/
    index.html                # App shell
  static/
    css/style.css
    js/
      app.js                  # App orchestration + API wiring
      player.js               # Playback engine
      code_panel.js           # Source viewer + line highlight
      renderers/
        board.js
        graph.js
        array.js
```

## Quick start

### 1) Create/activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Run app

```bash
python3 main.py
```

Default URL: `http://localhost:5050`

`main.py` opens the browser automatically when run directly.

## Backend API

### `GET /api/problems`
Returns available problems and metadata:
- `name`, `topic`, `subtopic`
- `description`, `long_description`
- `renderer_type`
- `default_params`

### `POST /api/run`
Request body:

```json
{
  "problem": "Number of Islands",
  "params": {
    "grid": 2
  }
}
```

Response includes:
- `source_code` (string shown in code panel)
- `renderer_type`
- `steps` (serialized `Step[]`)

## Core architecture

### Problem contract
Each problem class extends `Problem` in `problems/base_problem.py` and implements:
- metadata methods (`name`, `topic`, `subtopic`, `description`, `long_description`)
- `source_code()`
- `renderer_type()`
- `generate_steps(**kwargs)`

`registry.discover_problems()` imports `problems/*.py` and registers subclasses automatically.

### Step model
`core/step.py` defines snapshot entities:
- Board: `CellState[][]`
- Array: `ArrayCell[]`
- Graph: `GraphNode[]`, `GraphEdge[]`

Each step also carries:
- `line_number` (1-indexed into `source_code()`)
- `description`
- `log_messages`

### Tracers
`core/tracer.py` provides mutable tracer helpers:
- `Board2DTracer`
- `Array1DTracer`
- `GraphTracer`

You mutate tracer state (`select`, `patch`, `mark_error`, `set_value`, etc.) and call `snapshot(line, description)` to append a frozen step.

## Implemented problems

### DFS / BFS grid
- Flood Fill (#733)
- Number of Islands (#200)
- Rotting Oranges (#994)
- Shortest Path in Binary Matrix (#1091)
- Surrounded Regions (#130)
- Walls and Gates (#286)
- N-Queens (backtracking)

### Graph / topological / union-find
- Course Schedule (#207)
- Course Schedule II (#210)
- Is Graph Bipartite? (#785)
- Number of Provinces (#547)
- Redundant Connection (#684)

## Add a new problem

1. Create `problems/<new_problem>.py`.
2. Add a class extending `Problem`.
3. Add `_SOURCE` string with the algorithm code shown in UI.
4. Implement `generate_steps()` using the right tracer.
5. Return snapshots with accurate `line_number` mapping to `_SOURCE`.
6. Start app; discovery is automatic.

Minimal skeleton:

```python
from core.step import Step
from core.tracer import Board2DTracer
from problems.base_problem import Problem

_SOURCE = """\
def solve(...):
    ...
"""

class MyProblem(Problem):
    @staticmethod
    def name() -> str:
        return "My Problem"

    @staticmethod
    def topic() -> str:
        return "Graph / DFS"

    @staticmethod
    def subtopic() -> str:
        return "Custom"

    @staticmethod
    def description() -> str:
        return "One-line summary"

    @staticmethod
    def source_code() -> str:
        return _SOURCE

    @staticmethod
    def renderer_type() -> str:
        return "board"

    @staticmethod
    def generate_steps(**kwargs: object) -> list[Step]:
        tracer = Board2DTracer(3, 3)
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(tracer.snapshot(line, desc))

        # mutate tracer...
        snap(1, "Start")
        return steps
```

## Gap to full graph guide

Your guide contains 42 problems. Current app covers 12, so 30 remain.

Not yet implemented from the guide:
- Word Ladder
- Open the Lock
- Alien Dictionary
- Parallel Courses
- Accounts Merge
- Network Delay Time
- Cheapest Flights Within K Stops
- Path with Minimum Effort
- Min Cost to Connect All Points
- Critical Connections in a Network
- Max Area of Island
- Pacific Atlantic Water Flow
- 01 Matrix
- Clone Graph
- Graph Valid Tree
- Number of Connected Components in an Undirected Graph
- Evaluate Division
- Bus Routes
- Minimum Knight Moves
- Minimum Genetic Mutation
- Find Eventual Safe States
- Keys and Rooms
- Number of Enclaves
- Number of Closed Islands
- Detect Cycles in 2D Grid
- Making A Large Island
- Word Search
- Word Search II
- Word Ladder II
- Reconstruct Itinerary
- Sort Items by Groups Respecting Dependencies

## Additional visual elements needed for full coverage

To add all remaining guide problems with strong visual quality, current renderers need to be extended with these primitives.

### 1) Weighted-edge graph visuals
Needed for Dijkstra/MST/flight-cost/equation-ratio style problems.

Add:
- Edge weight labels
- Dist/cost badge per node
- Edge state variants: explored, relaxed, chosen-in-MST, rejected
- Support curved/parallel edges where needed

Code touch points:
- `core/step.py`: extend `GraphEdge` with `weight`, optional `label`, `state`
- `core/tracer.py`: weighted edge setters and relax/accept markers
- `static/js/renderers/graph.js`: draw edge labels and extra state styles

### 2) Frontier data-structure panels
Needed for BFS/0-1 BFS/Dijkstra/topological workflows.

Add side-panel visual data blocks for:
- Queue / deque
- Priority queue (min-heap)
- Stack
- Visited set / level map / parent map

Code touch points:
- `core/step.py`: add generic `aux_panels` payload (key-value/table/list)
- `static/js/app.js` + `templates/index.html`: render auxiliary panel region

### 3) Grid distance/path overlays
Needed for 01 Matrix, Pacific Atlantic, path-with-effort, knight moves.

Add:
- Per-cell distance/effort text overlay
- Direction arrows / parent pointer overlay
- Optional heatmap mode (distance gradient)
- Path reconstruction highlight layer

Code touch points:
- `core/step.py`: optional cell metadata (`meta`, `distance`, `parent_dir`)
- `static/js/renderers/board.js`: text/arrow/heatmap overlay rendering

### 4) DSU internals view
Needed for Accounts Merge / Valid Tree / components variants.

Add:
- Parent array view
- Rank/size array view
- Component grouping summary panel
- Optional forest/tree view for parent pointers

Code touch points:
- `core/step.py`: `dsu_state` payload (`parent`, `rank`, `components`)
- `core/tracer.py`: `DSUTracer`
- frontend auxiliary panel rendering

### 5) Trie/state-space visuals
Needed for Word Search II and large implicit-state BFS problems.

Add:
- Trie node/edge render mode (compact)
- Current trie cursor highlight
- Dynamic state graph mode (nodes created as discovered)

Code touch points:
- new renderer(s): `static/js/renderers/trie.js`, optional `state_graph.js`
- `app.js`: renderer switch updates

### 6) Tarjan (bridges/articulation) overlays
Needed for Critical Connections.

Add:
- Node annotations: discovery time `tin`, low-link `low`
- Edge classification: tree edge vs back edge vs bridge

Code touch points:
- `GraphNode` metadata fields for `tin/low`
- graph renderer annotations near nodes/edges

### 7) Hierarchical/grouped DAG rendering
Needed for Sort Items by Groups Respecting Dependencies.

Add:
- Group cluster boxes containing item nodes
- Cross-group dependency edge routing

Code touch points:
- new grouped graph renderer or graph renderer extension with clusters

## Recommended implementation order for remaining 30

1. Extend graph renderer for weighted edges + node labels + edge states.
2. Add auxiliary data-structure panel payload and UI.
3. Add grid distance/path overlays.
4. Add DSU tracer + DSU panel.
5. Add Tarjan annotations.
6. Add trie/state-space renderer for word-heavy problems.
7. Add grouped DAG renderer.

This sequence unlocks most missing problems without repeated UI rewrites.

## Known limitations

- No UI controls for overriding `default_params` yet.
- No automated tests currently.
- Large traces (for example N-Queens with `n=8`) can produce heavy payloads and slower playback.

## Notes for maintainers

- Keep `Step.line_number` in sync with `_SOURCE` line numbers.
- Keep snapshot granularity consistent: enough to teach, not so dense that playback becomes unusable.
- Prefer deterministic presets for reproducible demos.

