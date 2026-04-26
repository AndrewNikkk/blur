from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, Response

from app.core.config import settings as app_settings
from app.core.create_db import init_db
from app.routers import auth, chat, external, files, profile
from app.routers import settings as settings_router


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
app.include_router(settings_router.router)
app.include_router(chat.router)
app.include_router(external.router)


@app.get("/")
def read_root():
    return {"message": "Hello, world"}


@app.get("/robots.txt", response_class=PlainTextResponse)
def robots_txt():
    frontend_origin = app_settings.FRONTEND_URL.rstrip("/")
    return (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /login\n"
        "Disallow: /register\n"
        "Disallow: /forgot-password\n"
        "Disallow: /profile\n"
        "Disallow: /settings\n"
        f"Sitemap: {frontend_origin}/sitemap.xml\n"
    )


@app.get("/sitemap.xml")
def sitemap_xml():
    frontend_origin = app_settings.FRONTEND_URL.rstrip("/")
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        "<url>"
        f"<loc>{frontend_origin}/</loc>"
        "<changefreq>daily</changefreq>"
        "<priority>1.0</priority>"
        "</url>"
        "</urlset>"
    )
    return Response(content=xml, media_type="application/xml")
