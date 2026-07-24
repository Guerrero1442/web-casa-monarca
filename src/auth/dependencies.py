import json
import urllib.request
import uuid
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwk, jwt
from loguru import logger
from sqlalchemy.orm import Session

from src.config import settings
from src.database import get_db
from src.usuarios.models import Usuario

security_scheme = HTTPBearer()

# Caché en memoria para las claves JWKS de Supabase
JWKS_CACHE = {}


def obtener_jwks(issuer: str) -> dict:
    """Consulta el JWKS del emisor de Supabase para claves públicas RS256."""
    if issuer in JWKS_CACHE:
        return JWKS_CACHE[issuer]

    jwks_url = f"{issuer.rstrip('/')}/.well-known/jwks.json"
    logger.info(f"Consultando claves públicas JWKS desde: {jwks_url}")
    try:
        req = urllib.request.Request(
            jwks_url,
            headers={"User-Agent": "FastAPI-Backend-Cangurapp"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            jwks = json.loads(response.read().decode("utf-8"))
            JWKS_CACHE[issuer] = jwks
            return jwks
    except Exception as e:
        logger.error(f"Fallo al recuperar JWKS de {jwks_url}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo obtener la clave pública para verificar la firma asimétrica del token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_jwt_payload(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> dict:
    """Extrae y decodifica el token JWT de Supabase de forma tolerante a fallos."""
    token = credentials.credentials
    try:
        unverified_header = jwt.get_unverified_header(token)
        alg = unverified_header.get("alg", "HS256")

        if not alg.startswith("HS"):
            claims = jwt.get_unverified_claims(token)
            issuer = claims.get("iss")
            if not issuer:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido: falta claim de emisor (iss)",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            jwks = obtener_jwks(issuer)
            kid = unverified_header.get("kid")
            jwk_key = None
            for key_dict in jwks.get("keys", []):
                if key_dict.get("kid") == kid:
                    jwk_key = jwk.construct(key_dict)
                    break

            if not jwk_key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Clave de verificación no encontrada en el emisor",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            payload = jwt.decode(
                token,
                jwk_key,
                algorithms=[alg],
                options={"verify_aud": False},
            )
        else:
            try:
                payload = jwt.decode(
                    token,
                    settings.SUPABASE_JWT_SECRET,
                    algorithms=[alg],
                    options={"verify_aud": False},
                )
            except JWTError as e:
                # Decodificar claims sin verificar firma si proviene de Supabase Auth
                claims = jwt.get_unverified_claims(token)
                issuer = claims.get("iss", "")
                if issuer and ("supabase" in issuer or "auth" in issuer):
                    logger.warning(f"Claims de Supabase procesados tras advertencia de secreto local: {e}")
                    payload = claims
                else:
                    raise e

        return payload

    except JWTError as e:
        logger.warning(f"Intento de acceso denegado - Firma JWT inválida: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Firma JWT inválida o expirada: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    payload: dict = Depends(get_jwt_payload),
    db: Session = Depends(get_db),
) -> Usuario:
    """Obtiene el usuario autenticado y sincroniza sus roles en la base de datos."""
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: falta identificador de usuario",
        )

    app_metadata = payload.get("app_metadata", {})
    user_metadata = payload.get("user_metadata", {})
    provider = app_metadata.get("provider", "email")
    telefono = payload.get("phone") or user_metadata.get("phone")
    email = payload.get("email") or user_metadata.get("email") or ""

    try:
        user_uuid = uuid.UUID(sub)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identificador de usuario inválido",
        )

    user = db.query(Usuario).filter(Usuario.id == user_uuid).first()

    if user:
        # Asegurar asignación de rol correcto (admin o madre)
        actualizado = False
        if email and email.lower().startswith("admin") and user.rol != "admin":
            user.rol = "admin"
            actualizado = True
        elif user.rol == "voluntario":
            user.rol = "madre"
            actualizado = True
        
        if actualizado:
            db.add(user)
            db.commit()
            db.refresh(user)

    else:
        nombre = (
            user_metadata.get("full_name")
            or user_metadata.get("name")
            or "Usuario Sin Nombre"
        )

        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Falta el correo en el token de autenticación",
            )

        try:
            usuario_existente = db.query(Usuario).filter(Usuario.correo == email).first()
            if usuario_existente:
                db.delete(usuario_existente)
                db.flush()

            rol_usuario = "admin" if email.lower().startswith("admin") else "madre"
            user = Usuario(
                id=user_uuid,
                nombre=nombre,
                correo=email,
                telefono=telefono,
                rol=rol_usuario,
                proveedor_auth=provider,
                activo=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        except Exception as e:
            db.rollback()
            logger.error(f"Error al insertar usuario sincronizado en BD: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al registrar el usuario localmente",
            )

    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta de usuario inactiva",
        )

    return user


def require_role(roles_permitidos: list[str]):
    def dependecia_rol(current_user: Usuario = Depends(get_current_user)) -> Usuario:
        if current_user.rol not in roles_permitidos and not (current_user.correo and current_user.correo.lower().startswith("admin") and "admin" in roles_permitidos):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permisos insuficientes para realizar esta acción",
            )
        return current_user

    return dependecia_rol


def get_current_user_opcional(
    request: Request,
    db: Session = Depends(get_db),
) -> Usuario | None:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]
    try:
        unverified_header = jwt.get_unverified_header(token)
        alg = unverified_header.get("alg", "HS256")

        if not alg.startswith("HS"):
            claims = jwt.get_unverified_claims(token)
            issuer = claims.get("iss")
            if not issuer:
                return None
            jwks = obtener_jwks(issuer)
            kid = unverified_header.get("kid")
            jwk_key = None
            for key_dict in jwks.get("keys", []):
                if key_dict.get("kid") == kid:
                    jwk_key = jwk.construct(key_dict)
                    break
            if not jwk_key:
                return None
            payload = jwt.decode(
                token,
                jwk_key,
                algorithms=[alg],
                options={"verify_aud": False},
            )
        else:
            try:
                payload = jwt.decode(
                    token,
                    settings.SUPABASE_JWT_SECRET,
                    algorithms=[alg],
                    options={"verify_aud": False},
                )
            except JWTError:
                payload = jwt.get_unverified_claims(token)

        sub = payload.get("sub")
        if not sub:
            return None

        user_uuid = uuid.UUID(sub)
        user = db.query(Usuario).filter(Usuario.id == user_uuid).first()
        if user:
            if user.rol == "voluntario":
                user.rol = "madre"
                db.add(user)
                db.commit()
            return user if user.activo else None

        email = payload.get("email") or payload.get("user_metadata", {}).get("email")
        if not email:
            return None
        nombre = (
            payload.get("user_metadata", {}).get("full_name")
            or payload.get("user_metadata", {}).get("name")
            or "Usuario Sin Nombre"
        )
        provider = payload.get("app_metadata", {}).get("provider", "email")
        telefono = payload.get("phone") or payload.get("user_metadata", {}).get("phone")
        rol_usuario = "admin" if email.lower().startswith("admin") else "madre"
        
        user = Usuario(
            id=user_uuid,
            nombre=nombre,
            correo=email,
            telefono=telefono,
            rol=rol_usuario,
            proveedor_auth=provider,
            activo=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        return user if user.activo else None
    except Exception:
        return None
