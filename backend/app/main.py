import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.database.store import db_store
from backend.app.api.routes import entities, schedule, operations, analytics, io_routes

app = FastAPI(
    title="SchedulAI — AI-Based College Timetable Scheduler",
    description="Intelligent CSP and Local Search Scheduler enforcing all 9 Hard Constraints and Soft Quality Optimization",
    version="1.0.0"
)

# Enable CORS for frontend Vite dev server (and any origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(entities.router)
app.include_router(schedule.router)
app.include_router(operations.router)
app.include_router(analytics.router)
app.include_router(io_routes.router)

@app.on_event("startup")
def startup_load_default_data():
    """Load small dataset automatically on startup if store is empty"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(current_dir, "../../"))
    small_path = os.path.join(root_dir, "datasets/small_dataset.json")
    if os.path.exists(small_path) and not db_store.classes:
        with open(small_path, "r") as f:
            data = json.load(f)
        db_store.load_from_dict(data)
        print(f"[SchedulAI] Default small dataset loaded: {len(db_store.classes)} classes, {len(db_store.teachers)} teachers")

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SchedulAI Backend",
        "version": "1.0.0",
        "total_classes": len(db_store.classes),
        "total_teachers": len(db_store.teachers),
        "active_sessions": len(db_store.sessions)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
