import time
from typing import Dict, Any, Tuple
try:
    import constraint
    HAS_CONSTRAINT = True
except ImportError:
    HAS_CONSTRAINT = False

from backend.app.database.store import db_store
from backend.app.scheduler.constraints import ConstraintValidator

class PythonConstraintChecker:
    """
    Optional cross-check verifier using python-constraint library (Assignment Section 5.4).
    Used solely to verify constraints independently, never as the primary search engine.
    """
    @classmethod
    def verify_schedule_with_cross_check(cls) -> Tuple[bool, str, Dict[str, Any]]:
        if not HAS_CONSTRAINT:
            return False, "python-constraint library not installed", {}

        if not db_store.sessions:
            return False, "No active schedule to verify", {}

        start_time = time.time()
        
        # Build problem in python-constraint
        problem = constraint.Problem()
        session_list = list(db_store.sessions.values())
        
        # Variables: session IDs
        # Values: (day, period, room_id, teacher_id)
        domains = {}
        for s in session_list:
            domains[s.id] = [(s.day, s.period, s.room_id, s.teacher_id)]
            problem.addVariable(s.id, domains[s.id])

        # Teacher clash constraint
        def no_teacher_clash(s1_val, s2_val):
            d1, p1, r1, t1 = s1_val
            d2, p2, r2, t2 = s2_val
            if t1 == t2 and d1 == d2 and p1 == p2:
                return False
            return True

        # Room clash constraint
        def no_room_clash(s1_val, s2_val):
            d1, p1, r1, t1 = s1_val
            d2, p2, r2, t2 = s2_val
            if r1 == r2 and d1 == d2 and p1 == p2:
                return False
            return True

        # Class clash constraint
        def no_class_clash(s1_val, s2_val):
            d1, p1, r1, t1 = s1_val
            d2, p2, r2, t2 = s2_val
            if d1 == d2 and p1 == p2:
                return False
            return True

        # Add binary constraints between pairs
        for i in range(len(session_list)):
            for j in range(i + 1, len(session_list)):
                s1 = session_list[i]
                s2 = session_list[j]
                
                # Check teacher clash
                if s1.teacher_id == s2.teacher_id:
                    problem.addConstraint(no_teacher_clash, (s1.id, s2.id))
                
                # Check room clash
                if s1.room_id == s2.room_id:
                    problem.addConstraint(no_room_clash, (s1.id, s2.id))
                    
                # Check class clash
                if s1.class_id == s2.class_id:
                    problem.addConstraint(no_class_clash, (s1.id, s2.id))

        solutions = problem.getSolutions()
        elapsed = time.time() - start_time
        
        is_consistent = len(solutions) > 0
        message = (
            f"Cross-check verified: Schedule is mathematically consistent (0 clashes found in {elapsed:.4f}s)."
            if is_consistent else
            f"Cross-check warning: python-constraint identified inconsistent slot assignments."
        )

        return is_consistent, message, {
            "verified": is_consistent,
            "solution_count": len(solutions),
            "checked_sessions": len(session_list),
            "check_time_seconds": round(elapsed, 4)
        }
