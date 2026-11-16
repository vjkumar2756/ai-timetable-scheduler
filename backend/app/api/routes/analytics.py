import os
import json
from fastapi import APIRouter
from backend.app.schemas.api_schemas import APIResponse
from backend.app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/analytics", tags=["Analytics & Reporting"])

@router.get("/workload", response_model=APIResponse)
def get_workload_analytics():
    data = AnalyticsService.get_teacher_workload_analytics()
    return APIResponse(success=True, message="Teacher workload statistics", data=data)

@router.get("/rooms", response_model=APIResponse)
def get_room_analytics():
    data = AnalyticsService.get_room_analytics()
    return APIResponse(success=True, message="Room utilization statistics", data=data)

@router.get("/quality", response_model=APIResponse)
def get_quality_analytics():
    data = AnalyticsService.get_constraint_quality_analytics()
    return APIResponse(success=True, message="Schedule quality and constraint compliance statistics", data=data)

@router.get("/overview", response_model=APIResponse)
def get_institutional_overview():
    data = AnalyticsService.get_institutional_overview()
    return APIResponse(success=True, message="Institutional overview", data=data)

@router.get("/benchmarks", response_model=APIResponse)
def get_benchmark_results():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(current_dir, "../../../../"))
    results_path = os.path.join(root_dir, "experiments/results/benchmark_results.json")
    if os.path.exists(results_path):
        with open(results_path, "r") as f:
            data = json.load(f)
        return APIResponse(success=True, message="Benchmark results loaded", data=data)
    return APIResponse(success=False, message="Benchmarks have not been run yet", data={})
