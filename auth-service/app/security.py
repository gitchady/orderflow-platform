from datetime import UTC, datetime, timedelta
import jwt
from pwdlib import PasswordHash

from .config import settings
from .models import User


password_hash = PasswordHash.recommended()


def hash_password(password: str):
    return password_hash.hash(password)


def verify_password(password, encoded_password):
    return password_hash.verify(password, hash=encoded_password)


def create_access_token(user: User):
    now = datetime.now(UTC)
    expires_in = now + timedelta(seconds=3600)
    payload = {
        "user_id": user.id,
        "email": user.email,
        "role": "user",
        "exp": expires_in
    }

    token = jwt.encode(
        payload,
        key=settings.jwt_secret.get_secret_value(),
        algorithm=settings.jwt_algorithm
    )
    return token
