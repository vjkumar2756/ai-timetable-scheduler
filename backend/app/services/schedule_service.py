import time
from typing import Dict, List, Optional, Any, Tuple
from backend.app.database.store import db_store
from backend.app.models.entities import TimetableSession, WorkingSettings
from backend.app.scheduler.csp import TimetableCSP, SlotValue, LectureVariable
from backend.app.scheduler.constraints import ConstraintValidator
from backend.app.scheduler.cost_function import CostFunction
from backend.app.scheduler.backtracking import PlainBacktrackingSolver, ImprovedBacktrackingSolver
from backend.app.scheduler.min_conflicts import MinConflictsSolver
from backend.app.scheduler.simulated_annealing import SimulatedAnnealingSolver
from backend.app.scheduler.hybrid import HybridCSPSASolver
from backend.app.scheduler.metrics import SolverResult

class ScheduleService:
    @staticmethod
    def get_csp_and_validators() -> Tuple[TimetableCSP, ConstraintValidator, CostFunction]:
        csp = TimetableCSP(
            settings=db_store.settings,
            classes=db_store.classes,
            subjects=db_store.subjects,
            teachers=db_store.teachers,
            rooms=db_store.rooms
        )
        validator = ConstraintValidator(
            settings=db_store.settings,
            classes=db_store.classes,
            subjects=db_store.subjects,
            teachers=db_store.teachers,
            rooms=db_store.rooms
        )
        cost_fn = CostFunction(
            settings=db_store.settings,
            classes=db_store.classes,
            subjects=db_store.subjects,
            teachers=db_store.teachers,
            rooms=db_store.rooms
        )
        return csp, validator, cost_fn

    @classmethod
    def generate_timetable(
        cls,
        algorithm: str = "improved_backtracking",
        time_limit_seconds: float = 20.0,
        random_seed: Optional[int] = 42
    ) -> SolverResult:
        csp, validator, cost_fn = cls.get_csp_and_validators()

        # Basic resource feasibility check
        total_required_hours = sum(
            sum(c.subject_requirements.values())
            for c in db_store.classes.values() if c.active
        )
        num_rooms = len([r for r in db_store.rooms.values() if r.active])
        working_days = len(db_store.settings.days)
        usable_periods = max(1, db_store.settings.periods_per_day - 1)  # Minus lunch
        total_room_slots = num_rooms * working_days * usable_periods

        if total_required_hours > total_room_slots:
            return SolverResult(
                algorithm=algorithm,
                success=False,
                execution_time_seconds=0.0,
                diagnostic_message=f"Mathematically infeasible: Total required hours ({total_required_hours}) exceed available room slots ({total_room_slots}). Add more rooms or reduce subject hours."
            )

        # Algorithm Selection
        algo = algorithm.lower().replace("-", "_").replace(" ", "_")
        
        if algo in ["plain_backtracking", "baseline"]:
            solver = PlainBacktrackingSolver(csp, validator, cost_fn)
            result = solver.solve(time_limit_seconds=time_limit_seconds)
        elif algo in ["min_conflicts", "local_search"]:
            solver = MinConflictsSolver(csp, validator, cost_fn, seed=random_seed)
            result = solver.solve()
        elif algo in ["simulated_annealing", "sa"]:
            solver = SimulatedAnnealingSolver(csp, validator, cost_fn, seed=random_seed)
            result = solver.solve()
        elif algo in ["hybrid", "hybrid_csp_sa"]:
            solver = HybridCSPSASolver(csp, validator, cost_fn, seed=random_seed)
            result = solver.solve()
        else:
            # Default / improved_backtracking
            solver = ImprovedBacktrackingSolver(csp, validator, cost_fn)
            result = solver.solve(time_limit_seconds=time_limit_seconds)

        # Independent Authoritative Verification
        if result.success and result.assignment:
            var_map = csp.get_variable_map()
            is_valid, hard_count, violations = validator.validate_assignment(
                result.assignment, var_map, check_completeness=True
            )
            if not is_valid:
                result.success = False
                result.hard_violations = hard_count
                result.diagnostic_message = f"Authoritative validation failed with {hard_count} violations"
            else:
                # Store resulting sessions in DataStore
                db_store.sessions.clear()
                for var_id, slot in result.assignment.items():
                    var = var_map[var_id]
                    session = TimetableSession(
                        id=var_id,
                        class_id=var.class_id,
                        subject_id=var.subject_id,
                        teacher_id=slot.teacher_id,
                        room_id=slot.room_id,
                        day=slot.day,
                        period=slot.period,
                        duration=var.duration,
                        status="scheduled"
                    )
                    db_store.sessions[var_id] = session

                db_store.current_schedule_metadata = {
                    "algorithm": result.algorithm,
                    "execution_time_seconds": result.execution_time_seconds,
                    "nodes_expanded": result.nodes_expanded,
                    "iterations": result.iterations,
                    "hard_violations": result.hard_violations,
                    "soft_penalty": result.soft_penalty,
                    "total_cost": result.total_cost,
                    "timestamp": time.time()
                }

        return result

    @classmethod
    def validate_manual_edit(
        cls,
        session_id: str,
        target_day: str,
        target_period: int,
        target_room_id: Optional[str] = None,
        target_teacher_id: Optional[str] = None
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Authoritative validation of proposed manual session move/edit.
        Returns: (is_valid, list_of_violations)
        """
        if session_id not in db_store.sessions:
            return False, [{"code": "NOT_FOUND", "message": f"Session {session_id} not found"}]

        csp, validator, _ = cls.get_csp_and_validators()
        var_map = csp.get_variable_map()

        # Build simulated assignment with the proposed change
        simulated: Dict[str, SlotValue] = {}
        for s_id, sess in db_store.sessions.items():
            if s_id == session_id:
                simulated[s_id] = SlotValue(
                    day=target_day,
                    period=target_period,
                    room_id=target_room_id or sess.room_id,
                    teacher_id=target_teacher_id or sess.teacher_id
                )
            else:
                simulated[s_id] = SlotValue(
                    day=sess.day,
                    period=sess.period,
                    room_id=sess.room_id,
                    teacher_id=sess.teacher_id
                )

        is_valid, hard_count, violations = validator.validate_assignment(
            simulated, var_map, check_completeness=True
        )
        return is_valid, violations

    @classmethod
    def apply_manual_edit(
        cls,
        session_id: str,
        target_day: str,
        target_period: int,
        target_room_id: Optional[str] = None,
        target_teacher_id: Optional[str] = None
    ) -> Tuple[bool, str]:
        is_valid, violations = cls.validate_manual_edit(
            session_id, target_day, target_period, target_room_id, target_teacher_id
        )
        if not is_valid:
            reasons = "; ".join(v["message"] for v in violations)
            return False, f"Cannot move session due to hard constraint violations: {reasons}"

        sess = db_store.sessions[session_id]
        sess.original_slot = {"day": sess.day, "period": sess.period, "room_id": sess.room_id, "teacher_id": sess.teacher_id}
        sess.day = target_day
        sess.period = target_period
        if target_room_id:
            sess.room_id = target_room_id
        if target_teacher_id:
            sess.teacher_id = target_teacher_id

        return True, "Session updated successfully"
