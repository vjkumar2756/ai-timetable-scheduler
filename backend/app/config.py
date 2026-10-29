"""
backend/app/config.py
Configuration and environment management for SchedulAI.
"""
import os
from pydantic import BaseModel

class AppSettings(BaseModel):
    # App
    APP_NAME: str = "SchedulAI"
    VERSION: str = "2.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./timetable.db")
    
    # CSP & Solver Defaults
    DEFAULT_SEED: int = 42
    DEFAULT_TIMEOUT_SECONDS: float = 30.0
    DEFAULT_MAX_NODES: int = 50000
    
    # Soft Constraint Penalty Weights (Unified Configuration)
    # S1: Gaps in student class schedule
    WEIGHT_S1_GAPS: int = 2
    # S2: Duplicate subject in same day
    WEIGHT_S2_DAILY_REPEAT: int = 3
    # S3: Broken or non-consecutive practical labs
    WEIGHT_S3_BROKEN_LAB: int = 5
    # S4: Teacher non-preferred slot
    WEIGHT_S4_TEACHER_PREF: int = 2
    # S5: Teacher >2 consecutive lectures
    WEIGHT_S5_TEACHER_CONSECUTIVE: int = 2
    
    # Hard violation penalty multiplier
    HARD_VIOLATION_PENALTY: int = 1000

settings = AppSettings()
