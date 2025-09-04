from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def register_exception_handlers(app: FastAPI):
  @app.exception_handler(RequestValidationError)
  async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Collect all errors in a readable format
    errors = [
      {
        "type": e["type"],
        "loc": e["loc"],
        "msg": e["msg"],
        "input": e.get("input"),
        "ctx": e.get("ctx"),
      }
      for e in exc.errors()
    ]
    return JSONResponse(
      status_code=422, content={"error": errors[0]["msg"], "status": 422}
    )

  @app.exception_handler(StarletteHTTPException)
  async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
      status_code=exc.status_code,
      content={"error": exc.detail, "status": exc.status_code},
    )

  @app.exception_handler(Exception)
  async def generic_exception_handler(request: Request, exc: Exception):
    # For unexpected errors
    return JSONResponse(status_code=500, content={"error": str(exc), "status": 500})
