from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from src.auth.router import router as auth_router
from src.eventos.router import router as eventos_router
from src.menores.router import router as menores_router
from src.solicitudes.router import router as solicitudes_router
from src.usuarios.router import router as usuarios_router

app = FastAPI(
    title="Cangurapp - Cuidado Infantil",
    description="API REST de Cangurapp para la gestión de cuidado infantil y demanda horaria en Monterrey, México",
    version="0.3.0",
)

# Configuración de CORS con soporte para la nueva URL cangurapp-mx
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4321",
        "http://127.0.0.1:4321",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://cangurapp-mx.web.app",
        "https://cangurapp-mx.firebaseapp.com",
        "https://web-casa-monarca-mexico.web.app",
        "https://web-casa-monarca-mexico.firebaseapp.com",
    ],
    allow_origin_regex=r"https://.*\.web\.app|https://.*\.firebaseapp\.com|http://localhost:\d+|http://127\.0\.0\.1:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error no capturado en ruta {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"},
    )


# Inclusión de routers
app.include_router(auth_router)
app.include_router(usuarios_router)
app.include_router(menores_router)
app.include_router(solicitudes_router)
app.include_router(eventos_router)


@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Bienvenido a la API de Cangurapp - Cuidado Infantil",
    }
