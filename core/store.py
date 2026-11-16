"""
Central In-Memory Database Store for SchedulAI.
Provides persistence of classes, teachers, subjects, rooms, settings, and sessions.
"""
from backend.app.database.store import db_store, DataStore

__all__ = ["db_store", "DataStore"]
