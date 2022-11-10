from fastapi import APIRouter, HTTPException, status
from app.tables import db, users_table
from app.schemas import UserCreate, UserResponse
from app.utils import hash_password

router = APIRouter(prefix='/users', tags=['Users'])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
@db.transaction()
async def create_user(user: UserCreate):
    hashed_password = hash_password(user.password)
    user.password = hashed_password
    query = users_table.insert()
    created_user_id = await db.execute(query=query, values=user.dict())
    return await db.fetch_one(query=users_table.select().where(users_table.c.id == created_user_id))


@router.get("/{user_id}", response_model=UserResponse)
@db.transaction()
async def get_user(user_id: int):
    query = users_table.select().where(users_table.c.id == user_id)
    user = await db.fetch_one(query=query)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User was not found!')
    return user
