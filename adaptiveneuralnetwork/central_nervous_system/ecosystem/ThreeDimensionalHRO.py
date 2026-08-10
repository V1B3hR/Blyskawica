import logging
import math
import random
import threading
import time
from collections.abc import Callable
from typing import Any

import numpy as np

# --- Logging setup ---
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

# --- Torch availability check ---
try:
    import torch  # type: ignore
    _TORCH_AVAILABLE = True
except Exception:
    torch = None
    _TORCH_AVAILABLE = False

# --- Registry system for cognitive components ---
image_encoders = {}
cognitive_engines = {}
microbiome_species_registry = {}

def register_image_encoder(fn: Callable) -> Callable:
    module_name_split = fn.__module__.split('.')
    model_name = module_name_split[-1]
    image_encoders[model_name] = fn
    return fn

def register_cognitive_engine(name: str = None):
    def decorator(cls_or_fn: Callable) -> Callable:
        engine_name = name or cls_or_fn.__name__.lower()
        cognitive_engines[engine_name] = cls_or_fn
        return cls_or_fn
    return decorator

def register_microbiome_species(species_class: Callable) -> Callable:
    species_name = species_class.__name__.lower()
    microbiome_species_registry[species_name] = species_class
    return species_class

def get_image_encoder(model_name: str) -> Callable:
    if model_name not in image_encoders:
        raise ValueError(f'Unknown image encoder: {model_name}')
    return image_encoders[model_name]

def get_cognitive_engine(engine_name: str) -> Callable:
    if engine_name not in cognitive_engines:
        raise ValueError(f'Unknown cognitive engine: {engine_name}')
    return cognitive_engines[engine_name]

def get_microbiome_species(species_name: str) -> Callable:
    if species_name not in microbiome_species_registry:
        raise ValueError(f'Unknown microbiome species: {species_name}')
    return microbiome_species_registry[species_name]

def is_image_encoder(model_name: str) -> bool:
    return model_name in image_encoders

def is_cognitive_engine(engine_name: str) -> bool:
    return engine_name in cognitive_engines

def build_image_encoder(config_encoder: dict[str, Any], verbose: bool = False, **kwargs) -> Any:
    model_name = config_encoder['NAME']
    if model_name.startswith('cls_'):
        model_name = model_name[4:]
    if not is_image_encoder(model_name):
        raise ValueError(f'Unknown model: {model_name}')
    return image_encoders[model_name](config_encoder, verbose, **kwargs)

def build_cognitive_engine(engine_name: str, **kwargs) -> Any:
    if not is_cognitive_engine(engine_name):
        raise ValueError(f'Unknown cognitive engine: {engine_name}')
    return cognitive_engines[engine_name](**kwargs)

# --- Thread-safe system state for cognitive engine ---
class SystemState:
    def __init__(self, max_snapshots: int = 10000):
        self._state: dict[str, Any] = {}
        self._lock = threading.RLock()
        self._snapshots: list[dict[str, Any]] = []
        self._in_transaction = False
        self._max_snapshots = int(max_snapshots)

    def begin(self):
        with self._lock:
            self._in_transaction = True
            self._snapshots.append({"__tx_begin__": True})

    def commit(self):
        with self._lock:
            while self._snapshots:
                item = self._snapshots.pop()
                if item.get("__tx_begin__"):
                    break
            self._in_transaction = False

    def update(self, key: str, value: Any):
        with self._lock:
            old_value = self._state.get(key, None)
            self._snapshots.append({"key": key, "old": old_value})
            self._state[key] = value
            if len(self._snapshots) > self._max_snapshots:
                self._snapshots = self._snapshots[-self._max_snapshots :]

    def get(self, key: str, default=None):
        with self._lock:
            return self._state.get(key, default)

    def rollback(self):
        with self._lock:
            while self._snapshots:
                item = self._snapshots.pop()
                if item.get("__tx_begin__"):
                    break
                key = item.get("key")
                if key is None:
                    continue
                old = item.get("old", None)
                if old is None:
                    self._state.pop(key, None)
                else:
                    self._state[key] = old
            self._in_transaction = False

    def as_dict(self):
        with self._lock:
            return dict(self._state)

# --- Thread-safe gut-brain system state ---
class MicrobiomeSystemState:
    def __init__(self):
        self.anxiety = 0
        self.overload = 0
        self.memory = 0
        self.cyber_defense = 5
        self.health_score = 100
        # -- Reactive hormones --
        self.adrenaline   = 0
        self.noradrenaline = 0
        self.cortisol     = 0.15   # Minimum wakefulness tone
        # -- Stability foundation (V1B3hR/Sonnet accord) --
        self.serotonin    = 0.75   # Primary stability anchor
        self.gaba         = 0.50   # Inhibitory baseline
        # -- Social & Drive (maturity-scaled) --
        self.oxytocin     = 0.30   # Distributed trust (reduced from 0.5)
        self.testosterone = 0.25   # Moderate drive
        self._lock = threading.RLock()

    def absorb_overload(self, amount):
        with self._lock:
            self.overload = max(0, self.overload - amount)

    def boost_memory(self, amount):
        with self._lock:
            self.memory += amount

    def trigger_anxiety(self, amount):
        with self._lock:
            self.anxiety += amount

    def defend(self, attack_strength):
        with self._lock:
            if self.cyber_defense >= attack_strength:
                print("Defended against attack!")
                return True
            else:
                print("Attack penetrated defenses!")
                return False

    def update_health(self, delta):
        with self._lock:
            self.health_score = max(0, min(100, self.health_score + delta))

    def trigger_oxytocin(self, amount):
        """Distributed trust — half-effect for maturity scaling."""
        with self._lock:
            self.oxytocin = max(0, min(1.0, self.oxytocin + amount * 0.5))

    def trigger_gaba(self, amount):
        with self._lock:
            self.gaba = max(0, min(2.0, self.gaba + amount))

    def trigger_serotonin(self, amount):
        """Boost stability anchor. Also passively lifts GABA."""
        with self._lock:
            self.serotonin = max(0, min(1.0, self.serotonin + amount))
            self.gaba = max(0, min(1.0, self.gaba + amount * 0.15))  # Coupled

    def trigger_testosterone(self, amount):
        """Drive impulse — damped spike for balance."""
        with self._lock:
            self.testosterone = max(0, min(1.5, self.testosterone + amount * 0.6))

    def trigger_cortisol(self, amount):
        with self._lock:
            self.cortisol = max(0, min(2.0, self.cortisol + amount))

# --- Base microbiome species class ---
class MicrobiomeSpecies:
    def __init__(self, name, role, effect, is_bad=False, abundance=1):
        self.name = name
        self.role = role
        self.effect = effect
        self.is_bad = is_bad
        self.abundance = abundance

    def act(self, system):
        for _ in range(self.abundance):
            self.effect(system)

@register_microbiome_species
class Lactobacillus(MicrobiomeSpecies):
    def __init__(self, abundance=2):
        super().__init__(
            name="Lactobacillus",
            role="anxiety_reducer",
            effect=lambda sys: sys.absorb_overload(2),
            abundance=abundance
        )

@register_microbiome_species
class Bifidobacterium(MicrobiomeSpecies):
    def __init__(self, abundance=2):
        super().__init__(
            name="Bifidobacterium",
            role="memory_helper",
            effect=lambda sys: sys.boost_memory(1),
            abundance=abundance
        )

@register_microbiome_species
class Pathogenus(MicrobiomeSpecies):
    def __init__(self, abundance=1):
        super().__init__(
            name="Pathogenus",
            role="anxiety_trigger",
            effect=lambda sys: sys.trigger_anxiety(3),
            is_bad=True,
            abundance=abundance
        )

class NeuronLoop:
    def __init__(self):
        self.activity = 0
        self.memory = 0
        self._lock = threading.RLock()

    def stimulate(self, amount):
        with self._lock:
            self.activity += amount
            self.memory += amount * 0.1

    def rest(self):
        with self._lock:
            self.activity = max(0, self.activity - 1)
            self.memory = max(0, self.memory - 0.05)

    def get_memory(self):
        with self._lock:
            return self.memory

    def get_activity(self):
        with self._lock:
            return self.activity

class VagusNerve:
    def __init__(self, gut_state: MicrobiomeSystemState, cognitive_state: SystemState):
        self.gut_state = gut_state
        self.cognitive_state = cognitive_state

    def transmit_signals(self):
        try:
            self.cognitive_state.update("anxiety_level", self.gut_state.anxiety)
            self.cognitive_state.update("overload_level", self.gut_state.overload)
            self.cognitive_state.update("memory_score", self.gut_state.memory)
            self.cognitive_state.update("cyber_defense", self.gut_state.cyber_defense)
            self.cognitive_state.update("microbiome_health", self.gut_state.health_score)
            logger.info("[VagusNerve] Signals transmitted from gut to brain.")
            return True
        except Exception as e:
            logger.error(f"[VagusNerve] Transmission error: {e}")
            return False

@register_cognitive_engine("threedimensionalhro")
class ThreeDimensionalHRO:
    def __init__(
        self,
        reasoning_mode: str = "sequential",
        compute_backend: str = "local",
        optimization_strategy: str = "simple",
        rcd=None,
        monitors: list | None = None,
        species_capacity: int = 10,
    ):
        self.x_axis = reasoning_mode
        self.y_axis = compute_backend
        self.z_axis = optimization_strategy
        self.state = SystemState()
        self.rcd = rcd
        self.monitors = monitors or []
        self.neural_available = _TORCH_AVAILABLE
        self.reasoning_cache: dict[str, Any] = {}
        self._cache_lock = threading.RLock()
        self.optimization_history: list[dict[str, Any]] = []
        self._opt_lock = threading.RLock()
        self.microbiome_state = MicrobiomeSystemState()
        self.neurons = [NeuronLoop() for _ in range(10)]
        self.species_capacity = species_capacity
        self.microbiome = self._init_microbiome_species()
        self.vagus_nerve = VagusNerve(self.microbiome_state, self.state)
        logger.info(f"3NGIN3 initialized at ({self.x_axis}, {self.y_axis}, {self.z_axis}), neural={self.neural_available}")

    def _init_microbiome_species(self):
        species_list = []
        species_list.append(get_microbiome_species("lactobacillus")(abundance=2))
        species_list.append(get_microbiome_species("bifidobacterium")(abundance=2))
        species_list.append(get_microbiome_species("pathogenus")(abundance=1))
        species_list.extend([
            MicrobiomeSpecies(
                name="DopamineActivator", role="activity_boost",
                effect=lambda sys: [n.stimulate(2) for n in self.neurons], abundance=1
            ),
            MicrobiomeSpecies(
                name="Akkermansia", role="barrier_strengthener",
                effect=lambda sys: setattr(sys, 'cyber_defense', sys.cyber_defense + 1), abundance=1
            ),
            MicrobiomeSpecies(
                name="Faecalibacterium", role="anti_inflammatory",
                effect=lambda sys: sys.absorb_overload(1), abundance=1
            ),
            MicrobiomeSpecies(
                name="Clostridium_difficile", role="memory_disruptor",
                effect=lambda sys: setattr(sys, 'memory', max(0, sys.memory - 2)), is_bad=True, abundance=1
            ),
            MicrobiomeSpecies(
                name="E_coli_pathogenic", role="defense_weakener",
                effect=lambda sys: setattr(sys, 'cyber_defense', max(1, sys.cyber_defense - 1)), is_bad=True, abundance=1
            ),
        ])
        if len(species_list) > self.species_capacity:
            species_list = random.sample(species_list, self.species_capacity)
        return species_list

    def update_population_dynamics(self):
        beneficial = [s for s in self.microbiome if not s.is_bad]
        pathogenic = [s for s in self.microbiome if s.is_bad]
        if len(pathogenic) > len(beneficial):
            for b in beneficial:
                b.abundance = max(1, b.abundance - 1)
            self.microbiome_state.update_health(-10)
        if len(beneficial) > len(pathogenic):
            for p in pathogenic:
                p.abundance = max(1, p.abundance - 1)
            self.microbiome_state.update_health(+5)
        names = [s.name for s in beneficial]
        if "Akkermansia" in names and "Faecalibacterium" in names:
            for s in beneficial:
                if s.name in ("Akkermansia", "Faecalibacterium"):
                    s.abundance += 1

    def integrate_training_data(self, dataset):
        for s in self.microbiome:
            if s.name in dataset:
                s.abundance = max(1, dataset[s.name])

    def check_microbiome_safety(self):
        health = self.microbiome_state.health_score
        if health < 50:
            print("Health score low! Triggering probiotic intervention.")
            for s in self.microbiome:
                if not s.is_bad:
                    s.abundance += 1
            self.microbiome_state.update_health(+20)
        pathogenic_load = sum(s.abundance for s in self.microbiome if s.is_bad)
        if pathogenic_load > 5:
            print("High pathogenic load! Activating immune response.")
            for s in self.microbiome:
                if s.is_bad:
                    s.abundance = max(1, s.abundance - 1)
            self.microbiome_state.update_health(+10)

    def simulate_microbiome_phase(self, phase: str, dataset=None):
        print(f"\n--- Gut-Brain Phase: {phase} ---")
        try:
            if dataset:
                self.integrate_training_data(dataset)
            self.update_population_dynamics()
            self.check_microbiome_safety()
            for species in self.microbiome:
                species.act(self.microbiome_state)
            for n in self.neurons:
                if phase == "busy":
                    n.stimulate(random.randint(1, 3))
                elif phase == "rest":
                    n.rest()
                self.microbiome_state.memory += n.get_memory()
            self.vagus_nerve.transmit_signals()
            print(f"Anxiety (gut): {self.microbiome_state.anxiety}, Overload (gut): {self.microbiome_state.overload}, Memory (gut): {self.microbiome_state.memory}, Cyber Defense (gut): {self.microbiome_state.cyber_defense}, Health: {self.microbiome_state.health_score}")
            print(f"Cognitive State | anxiety_level: {self.state.get('anxiety_level')}, overload_level: {self.state.get('overload_level')}, memory_score: {self.state.get('memory_score')}, cyber_defense: {self.state.get('cyber_defense')}")
            return True
        except Exception as e:
            logger.error(f"[MicrobiomePhase] Error during phase '{phase}': {e}")
            return False

    def run_diagnostics(self):
        try:
            print("\n[Diagnostics]")
            print(f"Gut anxiety: {self.microbiome_state.anxiety}")
            print(f"Cognitive anxiety: {self.state.get('anxiety_level')}")
            print(f"Gut overload: {self.microbiome_state.overload}")
            print(f"Cognitive overload: {self.state.get('overload_level')}")
            print(f"Gut memory: {self.microbiome_state.memory}")
            print(f"Cognitive memory: {self.state.get('memory_score')}")
            print(f"Gut cyber defense: {self.microbiome_state.cyber_defense}")
            print(f"Cognitive cyber defense: {self.state.get('cyber_defense')}")
            print(f"Microbiome health score: {self.microbiome_state.health_score}")
            print(f"Cognitive microbiome health: {self.state.get('microbiome_health')}")
            total_neuron_activity = sum(n.get_activity() for n in self.neurons)
            total_neuron_memory = sum(n.get_memory() for n in self.neurons)
            print(f"Total neuron activity: {total_neuron_activity}")
            print(f"Total neuron memory: {total_neuron_memory}")
            return True
        except Exception as e:
            logger.error(f"[Diagnostics] Error: {e}")
            return False

    def think(self, content: str, **kwargs) -> dict[str, Any]:
        if self.x_axis == "sequential":
            return self._sequential_reasoning(content, **kwargs)
        if self.x_axis == "neural":
            if not self.neural_available:
                logger.warning("Neural requested but torch not available — falling back to sequential")
                return self._sequential_reasoning(content, **kwargs)
            return self._neural_reasoning(content, **kwargs)
        seq = self._sequential_reasoning(content, **kwargs)
        if self.neural_available:
            neu = self._neural_reasoning(content, **kwargs)
            return self._hybrid_fusion(seq, neu, **kwargs)
        return seq

    def _normalize_outcome(self, outcome: Any, start_time: float) -> dict[str, Any]:
        if isinstance(outcome, dict):
            out = dict(outcome)
        else:
            out = {"content": str(outcome)}
        out.setdefault("content", str(out.get("content", "")))
        out.setdefault("confidence", float(out.get("confidence", 0.5)))
        out["runtime"] = time.perf_counter() - start_time
        return out

    def _sequential_reasoning(self, content: str, **kwargs) -> dict[str, Any]:
        start = time.perf_counter()
        steps = [s.strip() for s in content.split(".") if s.strip()]
        reasoning_steps = []
        for i, step in enumerate(steps):
            reasoning_steps.append(
                {
                    "step": i + 1,
                    "input": step,
                    "logical_analysis": f"Analyzing: {step[:40]}...",
                    "confidence": 0.8 + random.random() * 0.2,
                }
            )
        confidence = (
            sum(s["confidence"] for s in reasoning_steps) / len(reasoning_steps) if reasoning_steps else 0.5
        )
        out = {
            "mode": "sequential",
            "reasoning_steps": reasoning_steps,
            "conclusion": f"Sequential analysis of {len(reasoning_steps)} logical steps",
            "confidence": confidence,
        }
        return self._normalize_outcome(out, start)

    def _neural_reasoning(self, content: str, **kwargs) -> dict[str, Any]:
        start = time.perf_counter()
        if not self.neural_available:
            out = {
                "mode": "neural_sim",
                "embedding_dimension": 64,
                "attention_weights": [],
                "context_strength": 0.0,
                "pattern_matches": 0,
                "confidence": 0.5,
            }
            return self._normalize_outcome(out, start)
        words = content.split()
        if not words:
            out = {"mode": "neural", "embedding_dimension": 0, "attention_weights": [], "confidence": 0.5}
            return self._normalize_outcome(out, start)
        max_words = min(128, len(words))
        seq_len = max_words
        embedding_dim = kwargs.get("embedding_dim", 64)
        embeddings = torch.randn(seq_len, embedding_dim)
        attn_logits = torch.randn(seq_len)
        attention_weights = torch.softmax(attn_logits, dim=0)
        context_vector = torch.sum(embeddings * attention_weights.unsqueeze(1), dim=0)
        out = {
            "mode": "neural",
            "embedding_dimension": embedding_dim,
            "attention_weights": attention_weights.tolist(),
            "context_strength": float(torch.norm(context_vector).item()),
            "pattern_matches": int(random.randint(1, 8)),
            "confidence": float(torch.mean(attention_weights).item()),
        }
        return self._normalize_outcome(out, start)

    def _hybrid_fusion(self, seq_result: dict[str, Any], neural_result: dict[str, Any], **kwargs) -> dict[str, Any]:
        start = time.perf_counter()
        fusion_weight = float(kwargs.get("neural_weight", 0.6))
        seq_conf = float(seq_result.get("confidence", 0.5))
        neu_conf = float(neural_result.get("confidence", 0.5))
        combined_confidence = seq_conf * (1 - fusion_weight) + neu_conf * fusion_weight
        out = {
            "mode": "hybrid",
            "sequential_component": seq_result,
            "neural_component": neural_result,
            "fusion_weight": fusion_weight,
            "combined_confidence": combined_confidence,
            "synthesis": f"Hybrid reasoning combining {len(seq_result.get('reasoning_steps', []))} logical steps with {neural_result.get('pattern_matches', 0)} pattern matches",
            "confidence": combined_confidence,
        }
        return self._normalize_outcome(out, start)

    def safe_think(self, agent_name: str, content: str, *, resource_budget: float | None = None, **kwargs) -> dict[str, Any]:
        intent = {
            "agent": agent_name,
            "action": "think",
            "content_summary": content[:200],
            "resource_budget": float(resource_budget) if resource_budget is not None else float(self.state.get("default_resource_budget", 0.5)),
        }
        if self.rcd:
            try:
                return self.rcd.monitor(intent, self.think, content, **kwargs)
            except Exception as e:
                logger.error("RCD TRIPPED during thought by %s: %s", agent_name, e)
                return {"error": "Cognitive fault detected", "details": str(e)}
        start = time.perf_counter()
        out = self.think(content, **kwargs)
        out = self._normalize_outcome(out, start)
        for m in self.monitors:
            try:
                m(self, content, out)
            except Exception as me:
                logger.exception("Monitor raised: %s", me)
        return out

    def optimize(self, problem_space: dict[str, Any], **kwargs) -> dict[str, Any]:
        if self.z_axis == "simple":
            return self._simple_optimization(problem_space, **kwargs)
        if self.z_axis == "complex":
            return self._complex_optimization(problem_space, **kwargs)
        if self.z_axis == "adaptive":
            return self._adaptive_optimization(problem_space, **kwargs)
        return self._simple_optimization(problem_space, **kwargs)

    def _simple_optimization(self, problem_space: dict[str, Any], **kwargs) -> dict[str, Any]:
        iterations = int(kwargs.get("iterations", 50))
        best_score = float("-inf")
        best_solution = None
        dims = int(problem_space.get("dimensions", 3))
        for i in range(iterations):
            params = [random.random() for _ in range(dims)]
            score = sum(params) + random.gauss(0, 0.1)
            if score > best_score:
                best_score = score
                best_solution = {"parameters": params, "iteration": i}
        out = {"strategy": "simple", "iterations": iterations, "best_score": best_score, "best_solution": best_solution}
        with self._opt_lock:
            self.optimization_history.append(out)
        return out

    def _complex_optimization(self, problem_space: dict[str, Any], **kwargs) -> dict[str, Any]:
        dimensions = int(problem_space.get("dimensions", 5))
        temperature = float(kwargs.get("initial_temperature", 100.0))
        cooling_rate = float(kwargs.get("cooling_rate", 0.95))
        min_temperature = float(kwargs.get("min_temperature", 0.01))
        current = [random.randint(0, 1) for _ in range(dimensions)]
        current_e = self._qubo_energy(current, problem_space)
        best = current.copy()
        best_e = current_e
        iteration = 0
        while temperature > min_temperature and iteration < 10000:
            neighbor = current.copy()
            flip = random.randrange(dimensions)
            neighbor[flip] = 1 - neighbor[flip]
            n_e = self._qubo_energy(neighbor, problem_space)
            accept = (n_e < current_e) or (random.random() < self._acceptance_probability(current_e, n_e, temperature))
            if accept:
                current, current_e = neighbor, n_e
                if current_e < best_e:
                    best, best_e = current.copy(), current_e  # noqa: F841
            temperature *= cooling_rate
            iteration += 1
        out = {"strategy": "complex", "algorithm": "simulated_annealing", "iterations": iteration, "best_energy": best_e}
        with self._opt_lock:
            self.optimization_history.append(out)
        return out

    def _adaptive_optimization(self, problem_space: dict[str, Any], **kwargs) -> dict[str, Any]:
        """Adaptive optimization strategy that selects the best approach based on problem complexity."""
        dimensions = int(problem_space.get("dimensions", 5))

        # Use simple optimization for small problems, complex for larger ones
        if dimensions <= 3:
            return self._simple_optimization(problem_space, **kwargs)
        else:
            return self._complex_optimization(problem_space, **kwargs)

    def _qubo_energy(self, solution, problem_space):
        """Calculate QUBO energy for a given solution."""
        # Simple energy function for demonstration
        return sum(x * (i + 1) for i, x in enumerate(solution))

    def _acceptance_probability(self, current_energy, new_energy, temperature):
        """Calculate acceptance probability for simulated annealing."""
        if new_energy < current_energy:
            return 1.0
        return np.exp(-(new_energy - current_energy) / temperature) if temperature > 0 else 0.0

    def get_status(self) -> dict[str, Any]:
        """Get the current status of the 3NGIN3 engine."""
        return {
            "position": f"({self.x_axis}, {self.y_axis}, {self.z_axis})",
            "capabilities": {
                "neural_available": self.neural_available,
                "thread_safe": True,
                "safety_monitoring": self.rcd is not None
            },
            "state": self.state.as_dict(),
            "microbiome_health": getattr(self, "microbiome_state", None),
            "rcd_status": {
                "sensitivity_threshold": 0.5,
                "constraints_active": self.rcd is not None
            } if self.rcd is not None else None
        }

    def move_to_coordinates(self, x: str = None, y: str = None, z: str = None):
        """Move the engine to new coordinates in the 3D space."""
        if x is not None:
            self.x_axis = x
        if y is not None:
            self.y_axis = y
        if z is not None:
            self.z_axis = z

        logger.info(f"Engine moved to ({self.x_axis}, {self.y_axis}, {self.z_axis})")
        out = {"strategy": "complex", "algorithm": "simulated_annealing", "iterations": iteration,  # noqa: F821
               "best_solution": {"parameters": best, "energy": best_e}, "final_temperature": temperature}  # noqa: F821
        with self._opt_lock:
            self.optimization_history.append(out)
        return out

    def _adaptive_optimization(self, problem_space: dict[str, Any], **kwargs) -> dict[str, Any]:
        complexity = problem_space.get("complexity", "medium")
        if complexity == "low" or problem_space.get("dimensions", 3) < 5:
            return self._simple_optimization(problem_space, **kwargs)
        else:
            return self._complex_optimization(problem_space, **kwargs)

    def _qubo_energy(self, solution: list[int], problem_space: dict[str, Any]) -> float:
        n = len(solution)
        energy = 0.0
        for i in range(n):
            for j in range(i+1, n):
                weight = problem_space.get("weights", {}).get(f"{i}_{j}", random.random())
                energy += weight * solution[i] * solution[j]
        return energy

    def _acceptance_probability(self, current_energy: float, new_energy: float, temperature: float) -> float:
        if temperature <= 0:
            return 0.0
        try:
            return min(1.0, math.exp((current_energy - new_energy) / temperature))
        except OverflowError:
            return 1.0 if current_energy > new_energy else 0.0

def create_default_cognitive_system(**kwargs):
    return build_cognitive_engine("threedimensionalhro", **kwargs)

def list_registered_components():
    return {
        "image_encoders": list(image_encoders.keys()),
        "cognitive_engines": list(cognitive_engines.keys()),
        "microbiome_species": list(microbiome_species_registry.keys())
    }

@register_image_encoder
def custom_vision_encoder(config_encoder, verbose=False, **kwargs):
    logger.info(f"Creating custom vision encoder with config: {config_encoder}")
    return {"type": "custom_vision", "config": config_encoder}

if __name__ == "__main__":
    print("Available components:", list_registered_components())
    engine = create_default_cognitive_system(
        reasoning_mode="hybrid",
        optimization_strategy="adaptive"
    )
    engine.simulate_microbiome_phase("busy")
    result = engine.safe_think("test_agent", "This is a test of the cognitive system.")
    print("Thinking result:", result)
    engine.run_diagnostics()
