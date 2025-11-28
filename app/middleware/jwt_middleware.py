
from urllib import request
from fastapi import Request,  status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError, ExpiredSignatureError
from app.config.settings import settings

class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        
        public_routes = ["/api/v1/auth/access", "/api/v1/identity/register", "/health", "/docs", "/redoc", "/openapi.json"]
        
        # Permitir rutas públicas de perfil
        if request.url.path.startswith("/api/v1/identity/profile/"):
            return await call_next(request)
                
        if request.method == "OPTIONS":
            return await call_next(request)             
        
        if request.url.path in public_routes:
            return await call_next(request)
       
        authorization: str = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token missing"}
            )
        
        token = authorization.replace("Bearer ", "")
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            if not user_id:
                raise JWTError("Invalid token payload")
            request.state.user_id = int(user_id)  
        except ExpiredSignatureError:            
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token has expired", "code": "TOKEN_EXPIRED"}
            )          
        except JWTError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid token"}
            )
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": str(e)}                
            )

        return await call_next(request)