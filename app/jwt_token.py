from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from app.tables import db, users_table
from app.schemas import TokenPayload
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

SECRET = settings.secret
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})

    encoded_jwt = jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])

        user_id: int = payload.get('user_id')

        if user_id is None:
            raise credentials_exception

        token_payload = TokenPayload(id=user_id)
    except JWTError:
        raise credentials_exception

    return token_payload


@db.transaction()
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials",
                                          headers={'WWW-Authenticate': 'Bearer'})
    token_payload = verify_access_token(token, credentials_exception)
    user = await db.fetch_one(query=users_table.select().where(users_table.c.id == token_payload.id))

    return user
