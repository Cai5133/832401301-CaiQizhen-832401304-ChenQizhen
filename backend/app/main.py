"""Run with python -m uvicorn app.main:app --port 8000."""
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Query, Request, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from .database import Database, default_database_path
from .schemas import Contact, ContactInput, ContactList, FavoriteInput
from .services import contacts, excel

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

    @application.get("/api/contacts/template", tags=["excel"])
    def contact_template():
        return Response(content=excel.build_workbook(excel.sample_contacts()), media_type=excel.MIME_TYPE,
                        headers={"Content-Disposition": 'attachment; filename="contacts-template.xlsx"'})

    @application.get("/api/contacts/export", tags=["excel"])
    def contact_export():
        return Response(content=excel.export_workbook(database), media_type=excel.MIME_TYPE,
                        headers={"Content-Disposition": 'attachment; filename="contacts.xlsx"'})

    @application.post("/api/contacts/import", tags=["excel"])
    async def contact_import(file: UploadFile = File(...)):
        try:
            if not file.filename or not file.filename.lower().endswith(".xlsx"):
                raise HTTPException(status_code=400, detail="仅支持 .xlsx 文件")
            content = await file.read(excel.MAX_FILE_BYTES + 1)
            if len(content) > excel.MAX_FILE_BYTES:
                raise HTTPException(status_code=413, detail="文件不能超过 5 MB")
            return await run_in_threadpool(excel.import_workbook, database, content)
        finally:
            await file.close()

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
