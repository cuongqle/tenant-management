from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(
        _request: Request,
        exc: IntegrityError,
    ) -> JSONResponse:
        detail = str(exc.orig) if exc.orig is not None else str(exc)
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": detail},
        )
