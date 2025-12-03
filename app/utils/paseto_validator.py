"""
Validador de tokens PASETO v4.local.

Este módulo proporciona funcionalidad para validar tokens PASETO emitidos
por siscom-admin-api para compartir ubicaciones de forma pública.
"""

import base64
import json
import logging
from datetime import UTC, datetime
from typing import Any

import pyseto
from pyseto import Key

from app.core.config import settings

logger = logging.getLogger(__name__)


class InvalidToken(Exception):
    """Errores genéricos de token inválido o corrupto."""

    pass


class ExpiredToken(Exception):
    """El token es válido pero ya expiró."""

    pass


class PasetoValidator:
    """
    Valida tokens PASETO v4.local emitidos por siscom-admin-api.

    Attributes:
        key: Objeto Key de pyseto para validar tokens
    """

    def __init__(self):
        """
        Inicializa el validador con la clave secreta del entorno.

        Raises:
            RuntimeError: Si PASETO_SECRET_KEY no está configurada
        """
        # Cargar clave secreta
        key_b64 = settings.PASETO_SECRET_KEY
        if not key_b64:
            raise RuntimeError("PASETO_SECRET_KEY not set in environment")

        try:
            key_bytes = base64.b64decode(key_b64)
            # Crear objeto Key de pyseto para v4.local
            self.key = Key.new(version=4, purpose="local", key=key_bytes)
        except Exception as e:
            raise RuntimeError(f"Invalid PASETO_SECRET_KEY format: {e}") from e

    def validate(self, token: str) -> dict[str, Any]:
        """
        Valida el token PASETO y regresa el payload si es válido.

        Args:
            token: Token PASETO v4.local a validar

        Returns:
            dict: Payload del token con los campos validados

        Raises:
            InvalidToken: Si el token es inválido, corrupto o tiene campos incorrectos
            ExpiredToken: Si el token ha expirado
        """
        try:
            # Decodificar el token usando el objeto Key
            decoded = pyseto.decode(self.key, token)
            # El payload viene como bytes, necesitamos deserializarlo
            raw_payload = decoded.payload  # bytes
            payload = json.loads(raw_payload.decode("utf-8"))  # dict
        except Exception as e:
            logger.warning(f"Token inválido o malformado: {e}")
            raise InvalidToken(f"Invalid or malformed token: {e}") from e

        # Verificar que el payload sea un diccionario
        if not isinstance(payload, dict):
            raise InvalidToken("Payload is not a valid dict")

        # Confirmar los campos esperados
        if payload.get("scope") != "public-location-share":
            raise InvalidToken("Invalid token scope")

        if "unit_id" not in payload:
            raise InvalidToken("Missing unit_id in token")

        if "exp" not in payload:
            raise InvalidToken("Missing exp in token")

        # Validación de expiración
        try:
            exp = datetime.fromisoformat(payload["exp"])
        except Exception as e:
            raise InvalidToken("Invalid exp format") from e

        now = datetime.now(UTC)
        if now >= exp:
            logger.info(f"Token expirado. Exp: {exp}, Now: {now}")
            raise ExpiredToken("Token expired")

        logger.info(
            f"Token validado exitosamente para unit_id: {payload.get('unit_id')}"
        )
        return payload


# Instancia global del validador
paseto_validator = PasetoValidator()
