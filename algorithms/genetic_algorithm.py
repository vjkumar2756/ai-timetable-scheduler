"""
Genetic Algorithm (GA) Metaheuristic Solver for Timetable Scheduling.
Employs chromosome encoding, tournament selection, class-preserving crossover, and elitism.
"""
import time
import random
from typing import Dict, List, Tuple, Any, Optional
from algorithms.base import BaseSolver
from backend.app.scheduler.csp import SlotValue
from backend.app.scheduler.metrics import SolverResult

class GeneticAlgorithmSolver(BaseSolver):
    """
    Genetic Algorithm with class-consistent crossover, mutation, and elitism.
    """
    def __init__(self, csp, validator, cost_fn, config=None, seed=42):
        super().__init__(csp, validator, cost_fn, config, seed)
        cfg = self.config
        self.pop_size = cfg.get("population_size", 24)
        self.generations = cfg.get("generations", 60)
        self.mutation_rate = cfg.get("mutation_rate", 0.15)
        self.elite_count = cfg.get("elite_count", 2)

    def solve(self, timeout_seconds: float = 30.0) -> SolverResult:
        if self.seed is not None:
            random.seed(self.seed)

        start_time = time.time()
        var_map = self.csp.get_variable_map()
        variables = self.csp.variables
        classes = list(self.csp.classes.keys())

        # 1. Initialize Population
        population: List[Dict[str, SlotValue]] = []
        for _ in range(self.pop_size):
            ind = {}
            for v in variables:
                ind[v.id] = random.choice(self.csp.domains[v.id])
            population.append(ind)

        def fitness(ind: Dict[str, SlotValue]) -> Tuple[int, int, int]:
            # Returns (total_cost, hard_violations, soft_penalty)
            _, h, _ = self.validator.validate_assignment(ind, var_map, check_completeness=False)
            s, _, _ = self.cost_fn.evaluate_soft_penalties(ind, var_map)
            cost = self.cost_fn.compute_total_cost(h, s)
            return cost, h, s

        best_ind = None
        best_cost = float("inf")
        best_h = float("inf")
        best_s = float("inf")
        cost_history = []
        evaluations = 0

        for gen in range(self.generations):
            if time.time() - start_time > timeout_seconds:
                break

            # Evaluate population
            scored_pop = []
            for ind in population:
                evaluations += 1
                c, h, s = fitness(ind)
                scored_pop.append((c, h, s, ind))
                if c < best_cost:
                    best_cost = c
                    best_h = h
                    best_s = s
                    best_ind = dict(ind)

            cost_history.append(best_cost)
            if best_h == 0 and best_s < 300:
                break

            # Sort by fitness (lowest cost is best)
            scored_pop.sort(key=lambda x: x[0])

            # Elitism: retain top individuals
            next_generation = [dict(scored_pop[i][3]) for i in range(min(self.elite_count, len(scored_pop)))]

            # Tournament Selection
            def select_parent():
                tournament = random.sample(scored_pop, 3)
                tournament.sort(key=lambda x: x[0])
                return tournament[0][3]

            # Breed new offspring
            while len(next_generation) < self.pop_size:
                p1 = select_parent()
                p2 = select_parent()

                # Class-level crossover: inherits assignments class by class
                split_classes = set(random.sample(classes, len(classes) // 2))
                child = {}
                for v in variables:
                    if v.class_id in split_classes:
                        child[v.id] = p1[v.id]
                    else:
                        child[v.id] = p2[v.id]

                # Mutation
                for v in variables:
                    if random.random() < self.mutation_rate:
                        child[v.id] = random.choice(self.csp.domains[v.id])

                next_generation.append(child)

            population = next_generation

        elapsed = time.time() - start_time
        if best_ind is None:
            best_ind = population[0]

        is_valid, final_h, _ = self.validator.validate_assignment(best_ind, var_map, check_completeness=True)
        final_s, _, _ = self.cost_fn.evaluate_soft_penalties(best_ind, var_map)

        return SolverResult(
            algorithm="Genetic Algorithm (GA)",
            success=is_valid,
            execution_time_seconds=elapsed,
            nodes_expanded=evaluations,
            iterations=evaluations,
            hard_violations=final_h,
            soft_penalty=final_s,
            total_cost=self.cost_fn.compute_total_cost(final_h, final_s),
            cost_history=cost_history,
            assignment=best_ind,
            diagnostic_message="Feasible schedule discovered by GA" if is_valid else f"GA stopped with {final_h} conflicts"
        )
