from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app import jwt_token
from app.schemas import Token
from app.tables import db, users_table
from app.utils import verify_password

router = APIRouter(tags=['Authentication'])


@router.post('/login', response_model=Token)
@db.transaction()
async def login(user_credentials: OAuth2PasswordRequestForm = Depends()):
    query = users_table.select().where(users_table.c.email == user_credentials.username)
    user = await db.fetch_one(query=query)

    if not user or not verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')

    access_token = jwt_token.create_access_token(data={'user_id': user.id})

    return {'access_token': access_token, 'token_type': 'Bearer'}
