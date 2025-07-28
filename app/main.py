from fastapi import FastAPI
from app.context.identity.api.routes import user_routes
from app.context.auth.api.routes import auth_routes
from app.config.database import init_db
from app.config.settings import settings
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.jwt_middleware import JWTMiddleware

init_db()

app = FastAPI(
    title="Mi API profiles",
    version="1.0.0",
    description="API PARA CREAR PERFILES PROFESIONALES",
)

app.add_middleware(    
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],    
)

app.add_middleware(JWTMiddleware)

app.include_router(user_routes.router, prefix=settings.API_PREFIX)
app.include_router(auth_routes.router, prefix=settings.API_PREFIX)

