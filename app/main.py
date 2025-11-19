from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.create_db import init_db
from app.routers import auth


app = FastAPI()


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


@app.get("/")
def read_root():
    return {"message": "Hello, world"}
