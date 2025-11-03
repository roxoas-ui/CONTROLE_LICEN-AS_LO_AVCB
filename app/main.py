from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import OperationalError
from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html

from app.api import api_router
from app.frontend import router as frontend_router
from app.config import get_settings
from app.database import Base, engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError as exc:
        raise RuntimeError("Falha ao conectar ao banco de dados") from exc
    yield


app = FastAPI(
    title="Controle de Licenças Ambientais",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)
settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(frontend_router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    html_content = (
        "<html><head>"
        '<link href="https://cdn.jsdelivr.net/npm/tailwindcss@3.4.4/dist/tailwind.min.css" rel="stylesheet" />'
        "<style>"
        "body{background:linear-gradient(135deg,#363636,#4f4f4f);color:#f5f5f5;min-height:100vh;display:flex;align-items:center;justify-content:center;font-family:'Inter',sans-serif;}"
        ".card{background:rgba(54,54,54,0.9);border:1px solid rgba(0,0,0,0.35);box-shadow:0 20px 45px rgba(0,0,0,0.45);border-radius:24px;padding:48px;max-width:560px;text-align:center;}"
        ".card img{width:120px;height:auto;margin:0 auto 20px auto;display:block;filter:drop-shadow(0 6px 18px rgba(0,0,0,0.45));}"
        ".card h1{font-size:2.25rem;margin-bottom:16px;color:#fefefe;}"
        ".card p{color:#d0d0d0;margin-bottom:28px;font-size:1rem;}"
        ".card a{display:inline-flex;align-items:center;justify-content:center;padding:12px 28px;background:#6b8e23;color:#fff;border-radius:9999px;font-weight:600;letter-spacing:0.02em;text-decoration:none;box-shadow:0 12px 25px rgba(107,142,35,0.35);transition:transform 120ms ease,box-shadow 120ms ease;}"
        ".card a:hover{transform:translateY(-2px);box-shadow:0 16px 35px rgba(107,142,35,0.45);}"
        "</style>"
        "</head><body><div class='card'>"
        "<img src='/static/img/logo.png' alt='Logotipo Ekozen'>"
        "<h1>Controle de Licenças Ambientais</h1>"
        "<p>Backend FastAPI ativo. Utilize a interface web em /ui/dashboard ou consulte a documentação interativa no Swagger.</p>"
        "<a href='/docs'>Abrir Swagger</a>"
        "</div></body></html>"
    )
    return HTMLResponse(content=html_content)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui() -> HTMLResponse:
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-overrides.css",
        oauth2_redirect_url="/docs/oauth2-redirect",
    )


@app.get("/docs/oauth2-redirect", include_in_schema=False)
async def swagger_ui_redirect() -> HTMLResponse:
    return get_swagger_ui_oauth2_redirect_html()
