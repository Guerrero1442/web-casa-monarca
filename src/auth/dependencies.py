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

# Caché en memoria para las claves JWKS de Supabase y evitar peticiones repetidas
JWKS_CACHE = {}


def obtener_jwks(issuer: str) -> dict:
    """Consulta el JWKS (JSON Web Key Set) del emisor de Supabase para obtener

    las claves públicas de verificación de firmas asimétricas (ej. RS256).
    """
    if issuer in JWKS_CACHE:
        return JWKS_CACHE[issuer]

    jwks_url = f"{issuer.rstrip('/')}/.well-known/jwks.json"
    logger.info(f"Consultando claves públicas JWKS desde: {jwks_url}")
    try:
        req = urllib.request.Request(
            jwks_url,
            headers={"User-Agent": "FastAPI-Backend-Casa-Monarca"}
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
    """Extrae y decodifica el token JWT de Supabase de forma segura.

    Soporta verificación simétrica (HS256 con SUPABASE_JWT_SECRET) y
    verificación asimétrica dinámica (RS256/RS384/RS512 mediante JWKS
    obtenido del claim 'iss' del token).
    """
    token = credentials.credentials
    try:
        # 1. Obtener la cabecera no verificada para validar el algoritmo
        unverified_header = jwt.get_unverified_header(token)
        alg = unverified_header.get("alg", "HS256")
        
        logger.info(f"VERIFICANDO JWT - Algoritmo: {alg} - Headers: {unverified_header}")

        # 2. Si el algoritmo es asimétrico (cualquiera que no empiece con HS, ej. RS256, ES256, EdDSA), usar JWKS
        if not alg.startswith("HS"):
            claims = jwt.get_unverified_claims(token)
            issuer = claims.get("iss")
            logger.info(f"JWT Asimétrico detectado. Emisor (iss): {issuer}")
            if not issuer:
                logger.warning("Token asimétrico carece del claim 'iss' obligatorio.")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido: falta claim de emisor (iss)",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Obtener las claves del emisor
            jwks = obtener_jwks(issuer)
            kid = unverified_header.get("kid")

            # Buscar la clave correspondiente al 'kid' del token
            jwk_key = None
            for key_dict in jwks.get("keys", []):
                if key_dict.get("kid") == kid:
                    jwk_key = jwk.construct(key_dict)
                    break

            if not jwk_key:
                logger.warning(f"No se encontró clave con kid '{kid}' en el JWKS.")
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
            # 3. Si es simétrico (HS256/HS384/HS512), validar con el secreto de Supabase local
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=[alg],
                options={"verify_aud": False},
            )

        return payload

    except JWTError as e:
        logger.warning(
            f"Intento de acceso denegado - Firma JWT inválida o expirada: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Firma JWT inválida o expirada: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    payload: dict = Depends(get_jwt_payload),
    db: Session = Depends(get_db),
) -> Usuario:
    """Obtiene el usuario autenticado.

    Si el usuario no existe localmente, lo sincroniza extrayendo sus datos del
    JWT.
    """
    sub = payload.get("sub")
    if not sub:
        logger.warning(
            "JWT decodificado con exito pero carece de identificador de usuario ('sub')."
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: falta identificador de usuario",
        )

    # Extraer metadatos de OAuth de Supabase
    app_metadata = payload.get("app_metadata", {})
    user_metadata = payload.get("user_metadata", {})
    provider = app_metadata.get("provider", "email")

    # Obtener el teléfono del payload de Supabase
    telefono = payload.get("phone") or user_metadata.get("phone")

    # Log de nivel WARNING si el payload de Google/Facebook no contiene teléfono
    if provider in ["google", "facebook"] and not telefono:
        logger.warning(
            f"Trazabilidad OAuth - El payload de {provider} para el usuario ID {sub} no contiene el campo 'telefono'."
        )

    # Validar que sub sea un UUID válido
    try:
        user_uuid = uuid.UUID(sub)
    except ValueError:
        logger.warning(
            f"El identificador 'sub' del JWT no es un UUID valido: {sub}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identificador de usuario inválido",
        )

    # Buscar usuario en la base de datos local
    user = db.query(Usuario).filter(Usuario.id == user_uuid).first()

    if not user:
        # Sincronización automática de nuevos usuarios OAuth
        email = payload.get("email") or user_metadata.get("email")
        nombre = (
            user_metadata.get("full_name")
            or user_metadata.get("name")
            or "Usuario Sin Nombre"
        )

        if not email:
            logger.warning(
                f"Sincronizacion OAuth fallida - El payload del usuario {sub} carece de correo electronico."
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Falta el correo en el token de autenticación",
            )

        try:
            # Verificar colisión de correo (recreación de usuario en Supabase con mismo email pero distinto ID)
            usuario_existente = db.query(Usuario).filter(Usuario.correo == email).first()
            if usuario_existente:
                logger.warning(
                    f"Colision de identidad detectada: El correo {email} ya existe en PostgreSQL con ID {usuario_existente.id} "
                    f"pero Supabase envio una firma con nuevo ID {user_uuid}. Limpiando registro obsoleto..."
                )
                db.delete(usuario_existente)
                db.flush()  # Liberar el índice único de correo en la BD antes del commit

            logger.info(
                f"Sincronizando nuevo usuario {email} con ID {sub} desde OAuth provider '{provider}'."
            )
            rol_usuario = "admin" if email.lower().startswith("admin") else "voluntario"
            user = Usuario(
                id=user_uuid,
                nombre=nombre,
                correo=email,
                telefono=telefono,  # Guardar si viene del proveedor
                rol=rol_usuario,
                proveedor_auth=provider,
                activo=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        except Exception as e:
            db.rollback()
            logger.error(
                f"Error al insertar o resolver colision del usuario sincronizado en BD: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al registrar el usuario localmente o resolver colisión de identidad",
            )

    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta de usuario inactiva",
        )

    return user


def require_role(roles_permitidos: list[str]):
    """Dependencia parametrizada para el control de acceso basado en roles

    (RBAC).
    """

    def dependecia_rol(current_user: Usuario = Depends(get_current_user)) -> Usuario:
        if current_user.rol not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permisos insuficientes para realizar esta acción",
            )
        return current_user

    return dependecia_rol


def require_phone_verified(
    current_user: Usuario = Depends(get_current_user),
) -> Usuario:
    """Aplica la Restricción OAuth:

    Bloquea las inscripciones si el usuario de Google/Facebook no tiene un
    teléfono registrado.
    """
    if current_user.proveedor_auth in ["google", "facebook"]:
        if not current_user.telefono:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado: Captura obligatoria de telefono en perfil.",
            )
    return current_user


def get_current_user_opcional(
    request: Request,
    db: Session = Depends(get_db),
) -> Usuario | None:
    """Extrae y valida el JWT si la cabecera Authorization está presente,

    pero no falla si no lo está. Sincroniza al usuario si es nuevo.
    """
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
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=[alg],
                options={"verify_aud": False},
            )

        sub = payload.get("sub")
        if not sub:
            return None

        user_uuid = uuid.UUID(sub)
        user = db.query(Usuario).filter(Usuario.id == user_uuid).first()
        if not user:
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
            rol_usuario = "admin" if email.lower().startswith("admin") else "voluntario"
            
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

