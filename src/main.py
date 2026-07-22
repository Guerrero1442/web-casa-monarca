from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.auth.router import router as auth_router
from src.eventos.router import router as eventos_router
from src.inscripciones.router import router as inscripciones_router
from src.usuarios.router import router as usuarios_router

app = FastAPI(
    title="Casa Monarca Conecta",
    description="Plataforma web para la gestión de voluntarios de ayuda humanitaria (Monterrey, México)",
    version="0.1.0",
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4321",
        "http://127.0.0.1:4321",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://web-casa-monarca-mexico.web.app",
        "https://web-casa-monarca-mexico.firebaseapp.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusión de routers
app.include_router(auth_router)
app.include_router(usuarios_router)
app.include_router(eventos_router)
app.include_router(inscripciones_router)


@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Bienvenido a la API de Casa Monarca Conecta",
    }
