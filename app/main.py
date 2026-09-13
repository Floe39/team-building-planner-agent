import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .schemas import TeamBuildingPlan, TeamBuildingRequest
from .service import TeamBuildingPlannerService

app = FastAPI(title="Team Building Planner Agent API", version="0.1.0")
service = TeamBuildingPlannerService()
logger = logging.getLogger(__name__)


@app.middleware("http")
async def request_logging(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    started = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    logger.info("request_id=%s path=%s status=%s duration_ms=%d", request_id, request.url.path, response.status_code, (time.perf_counter() - started) * 1000)
    return response


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"code": "VALIDATION_ERROR", "message": exc.errors()[0]["msg"], "request_id": request.headers.get("X-Request-ID", str(uuid.uuid4()))})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/team-buildings/plan", response_model=TeamBuildingPlan)
def create_plan(payload: TeamBuildingRequest, request: Request) -> TeamBuildingPlan:
    return service.plan(payload, request.headers.get("X-Request-ID"))
