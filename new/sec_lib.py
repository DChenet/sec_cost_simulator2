import math
from collections import deque, defaultdict
from dataclasses import dataclass, field
from typing import Callable, Optional

# ── Module specs (pure data) ───────────────────────────────────────────────────

@dataclass
class InputModule:
    energy: float
    name: Optional[str] = None

@dataclass
class OutputModule:
    energy: float
    link_length: float
    speed: float
    name: Optional[str] = None

@dataclass
class ProcessingModule:
    ew: float    # work-induced energy consumption, J/OP
    eup: float   # uptime power consumption, J/s
    speed: float # operations per second, OP/s
    name: Optional[str] = None

Module = InputModule | OutputModule | ProcessingModule


# ── Cost functions (pure functions, no classes needed) ─────────────────────────

def input_energy_cost(m: InputModule, d: float) -> float:
    return m.energy * d

def input_time_cost(m: InputModule, d: float) -> float:
    return 0.0

def output_time_cost(m: OutputModule, d: float) -> float:
    return d / m.speed

def output_energy_cost(m: OutputModule, d: float) -> float:
    return m.energy * output_time_cost(m, d) * math.log10(m.link_length)

def processing_time_cost(m: ProcessingModule, n_op: float) -> float:
    return n_op / m.speed

def processing_energy_cost(m: ProcessingModule, din: float, n_op: float) -> float:
    t = processing_time_cost(m, n_op)
    return m.ew * din + m.eup * t


# ── Architecture (graph of modules) ───────────────────────────────────────────

@dataclass
class Architecture:
    modules: dict[str, Module] = field(default_factory=dict)
    edges: list[tuple[str, str]] = field(default_factory=list)   # (src, dst)

    def add(self, module: Module):
        self.modules[module.name] = module

    def connect(self, src: str, dst: str):
        self.edges.append((src, dst))

    def __getitem__(self, name: str) -> Module:
        return self.modules[name]

def build_architecture(config: dict) -> Architecture:
    arch = Architecture()
    for name, params in config.items():
        if "speed" in params and "link_length" in params:
            arch.add(OutputModule(**params, name=name))
        elif "speed" in params:
            arch.add(ProcessingModule(**params, name=name))
        else:
            arch.add(InputModule(**params, name=name))
    return arch


# ── Task specs (pure data) ─────────────────────────────────────────────────────

@dataclass
class SimpleTask:
    phi: float
    n_op: Callable[[float], float]
    name: Optional[str] = None

@dataclass
class SplittingTask:
    phi_vector: list[float]
    n_op: Callable[[float], float]
    name: Optional[str] = None

@dataclass
class MergingTask:
    phi_vector: list[float]
    n_op: Callable[[float], float]
    name: Optional[str] = None

Task = SimpleTask | SplittingTask | MergingTask


# ── Task functions (pure functions) ───────────────────────────────────────────

def run_simple(t: SimpleTask, d_in: float) -> tuple[float, float]:
    return d_in * t.phi, t.n_op(d_in)

def run_splitting(t: SplittingTask, d_in: float) -> tuple[list[float], float]:
    return [d_in * phi for phi in t.phi_vector], t.n_op(d_in)

def run_merging(t: MergingTask, d_in: list[float]) -> tuple[float, float]:
    return d_in[0] * t.phi_vector[0], t.n_op(sum(d_in))


# ── Algorithm (graph of tasks + data sizes on edges) ──────────────────────────

@dataclass
class Algorithm:
    tasks: dict[str, Task] = field(default_factory=dict)
    edges: list[tuple[str, str]] = field(default_factory=list)   # (src, dst)
    data_sizes: dict[tuple[str, str], float] = field(default_factory=dict)  # edge → d
    workloads: dict[str, float] = field(default_factory=dict)               # task → n_op

    def add(self, task: Task):
        self.tasks[task.name] = task

    def connect(self, src: str, dst: str):
        self.edges.append((src, dst))

    def __getitem__(self, name: str) -> Task:
        return self.tasks[name]

def run_algorithm(algo: Algorithm, d_start: float) -> Algorithm:
    """Topological traversal respecting split/merge data flow."""

    # Build adjacency: successors and predecessors per task
    successors   = defaultdict(list)  # task → [dst, ...]
    predecessors = defaultdict(list)  # task → [src, ...]
    for src, dst in algo.edges:
        successors[src].append(dst)
        predecessors[dst].append(src)

    # Find source tasks (no incoming edges)
    all_tasks = set(algo.tasks)
    sources = [t for t in all_tasks if not predecessors[t]]

    # edge_data[edge] = data size carried on that edge
    edge_data: dict[tuple[str, str], float] = {}

    # Seed source tasks with d_start
    for src in sources:
        # Treat an implicit incoming edge as carrying d_start
        edge_data[("__start__", src)] = d_start

    # Kahn's algorithm for topological order
    in_degree = {t: len(predecessors[t]) for t in all_tasks}
    queue = deque(sources)
    visited_order = []

    while queue:
        name = queue.popleft()
        visited_order.append(name)
        for dst in successors[name]:
            in_degree[dst] -= 1
            if in_degree[dst] == 0:
                queue.append(dst)

    if len(visited_order) != len(all_tasks):
        raise ValueError("Cycle detected in algorithm graph.")

    # Execute tasks in topological order
    for name in visited_order:
        task = algo.tasks[name]
        incoming = predecessors[name] or ["__start__"]

        # Collect data arriving at this task
        incoming_data = [edge_data[(src, name)] for src in incoming]

        if isinstance(task, SimpleTask):
            assert len(incoming_data) == 1, f"{name}: SimpleTask expects 1 input"
            d_out, n_op = run_simple(task, incoming_data[0])
            # Fan out: same output to every successor
            for dst in successors[name]:
                edge_data[(name, dst)] = d_out

        elif isinstance(task, SplittingTask):
            assert len(incoming_data) == 1, f"{name}: SplittingTask expects 1 input"
            d_outs, n_op = run_splitting(task, incoming_data[0])
            assert len(d_outs) == len(successors[name]), (
                f"{name}: SplittingTask has {len(d_outs)} outputs "
                f"but {len(successors[name])} successors"
            )
            for dst, d_out in zip(successors[name], d_outs):
                edge_data[(name, dst)] = d_out

        elif isinstance(task, MergingTask):
            d_out, n_op = run_merging(task, incoming_data)
            for dst in successors[name]:
                edge_data[(name, dst)] = d_out

        algo.workloads[name] = n_op

    # Store only real edges (exclude __start__ sentinels)
    algo.data_sizes = {e: v for e, v in edge_data.items() if e[0] != "__start__"}
    return algo


# ── Mapping & Routing (plain dicts, no classes needed) ────────────────────────

Mapping = dict[str, tuple[ProcessingModule, float, float]]  # task → (module, din, n_op)
Routing = dict[tuple[str,str], tuple[Module, float]] # edge → (module, datasize)


def mapping_cost(mapping: Mapping) -> tuple[float, float]:
    time   = sum(processing_time_cost(m, n_op)        for m, din, n_op in mapping.values())
    energy = sum(processing_energy_cost(m, din, n_op) for m, din, n_op in mapping.values())
    return time, energy

def routing_cost(routing: Routing) -> tuple[float, float]:
    time, energy = 0.0, 0.0
    for module, d in routing.values():
        if isinstance(module, InputModule):
            time   += input_time_cost(module, d)
            energy += input_energy_cost(module, d)
        elif isinstance(module, OutputModule):
            time   += output_time_cost(module, d)
            energy += output_energy_cost(module, d)
    return time, energy

def total_cost(mapping: Mapping, routing: Routing) -> tuple[float, float]:
    mt, me = mapping_cost(mapping)
    rt, re = routing_cost(routing)
    return mt + rt, me + re