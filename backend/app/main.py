"""Run with python -m uvicorn app.main:app --port 8000."""
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .database import Database, default_database_path
from .schemas import Contact, ContactInput, ContactList, FavoriteInput
from .services import contacts

logger = logging.getLogger(__name__)


def create_app(database_path: str | Path | None = None) -> FastAPI:
    database = Database(database_path if database_path is not None else default_database_path())

    @asynccontextmanager
    async def lifespan(application):
        database.initialize()
        yield

    application = FastAPI(title="有联通讯录 API", version="1.0.0", lifespan=lifespan)
    application.state.database = database
    origins = [value.strip() for value in os.getenv("CORS_ORIGINS", "").split(",") if value.strip()]
    if origins:
        application.add_middleware(CORSMiddleware, allow_origins=origins,
                                   allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
                                   allow_headers=["Content-Type"],
                                   expose_headers=["Content-Disposition"])

    @application.exception_handler(Exception)
    async def unexpected_error(request: Request, error: Exception):
        logger.exception("Unhandled request error")
        return JSONResponse(status_code=500, content={"detail": "服务器内部错误，请稍后重试"})

    @application.get("/api/health", tags=["health"])
    def health():
        return {"status": "ok"}

    @application.get("/api/contacts", response_model=ContactList, tags=["contacts"])
    def contact_list(q: str = Query(default="", max_length=2000), favorite: bool | None = None):
        return contacts.list_contacts(database, q, favorite)

    @application.post("/api/contacts", response_model=Contact, status_code=201, tags=["contacts"])
    def contact_create(contact: ContactInput):
        return contacts.create_contact(database, contact)

    @application.get("/api/contacts/{contact_id}", response_model=Contact, tags=["contacts"])
    def contact_detail(contact_id: int):
        return contacts.get_contact(database, contact_id)

    @application.put("/api/contacts/{contact_id}", response_model=Contact, tags=["contacts"])
    def contact_update(contact_id: int, contact: ContactInput):
        return contacts.update_contact(database, contact_id, contact)

    @application.patch("/api/contacts/{contact_id}/favorite", response_model=Contact, tags=["contacts"])
    def contact_favorite(contact_id: int, value: FavoriteInput):
        return contacts.set_favorite(database, contact_id, value.isFavorite)

    @application.delete("/api/contacts/{contact_id}", status_code=204, tags=["contacts"])
    def contact_delete(contact_id: int):
        contacts.delete_contact(database, contact_id)
        return Response(status_code=204)

    return application


app = create_app()
