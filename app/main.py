import logging

from fastapi import FastAPI

from app.routers.note import note_router

logger = logging.getLogger(__name__)

def create_application() -> FastAPI:

    log_level = logging.WARNING
    logging.basicConfig(level=log_level)


    app = FastAPI(
        title="NotesAI API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.include_router(note_router, prefix="/notes", tags=["Notes"])

    return app

app = create_application()

@app.on_event("startup")
async def startup():
    message = "🟢Starting up application🟢"
    logger.info(message)
    print(message)


@app.on_event("shutdown")
async def shutdown():
    message = "🔴Shutting down application🔴"
    logger.info(message)
    print(message)


@app.get("/")
async def root_message():
    return {"message": "Hello world!"}
