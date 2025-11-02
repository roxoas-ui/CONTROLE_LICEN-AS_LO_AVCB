from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import OperationalError

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


app = FastAPI(title="Controle de Licenças Ambientais", lifespan=lifespan)
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
        "</head><body class='bg-slate-100'><div class='min-h-screen flex items-center justify-center'>"
        "<div class='bg-white shadow-lg rounded-xl p-10 max-w-3xl'>"
        "<h1 class='text-3xl font-bold text-slate-900 mb-4'>Controle de Licenças Ambientais</h1>"
        "<p class='text-slate-600 mb-6'>API operante. Utilize o frontend dedicado ou o Swagger UI em /docs.</p>"
        "<a href='/docs' class='inline-flex items-center px-4 py-2 bg-emerald-600 text-white rounded-lg shadow hover:bg-emerald-500 transition'>Abrir Swagger</a>"
        "</div></div></body></html>"
    )
    return HTMLResponse(content=html_content)
