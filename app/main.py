from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.create_db import init_db
from app.routers import auth, chat, files, profile, settings


app = FastAPI(
    title="Blur",
    description="API files blur",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.on_event("startup")
async def startup_event():
    init_db()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(files.router)
app.include_router(profile.router)
app.include_router(settings.router)
app.include_router(chat.router)


@app.get("/")
def read_root():
    return {"message": "Hello, world"}
