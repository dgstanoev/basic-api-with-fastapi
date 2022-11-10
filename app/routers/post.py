from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from app.tables import db, posts_table, votes_table
from app.schemas import PostCreate, PostUpdate, PostResponse
from app.jwt_token import get_current_user
from sqlalchemy import select, func

router = APIRouter(prefix='/posts', tags=['Posts'])


@router.get("/{post_id}", response_model=PostResponse)
@db.transaction()
async def get_post(post_id: int, current_user: int = Depends(get_current_user)):
    query = posts_table.select().where(posts_table.c.id == post_id)
    post = await db.fetch_one(query=query)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Post was not found!')
    return post


# @router.get("/")
@router.get("/", response_model=List[PostResponse])
@db.transaction()
async def get_posts(current_user: int = Depends(get_current_user), limit: int = 10, skip: int = 0,
                    search: Optional[str] = ''):
    query = select(posts_table, func.count(votes_table.c.post_id).label('votes')) \
        .select_from(posts_table.outerjoin(votes_table)).group_by(posts_table.c.id) \
        .where(posts_table.c.content.ilike(f'%{search}%')).limit(limit).offset(skip)
    db_posts = await db.fetch_all(query=query)
    return db_posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostResponse)
@db.transaction()
async def create_post(post: PostCreate, current_user=Depends(get_current_user)):
    query = posts_table.insert()
    created_post_id = await db.execute(query=query, values={**post.dict(), 'owner_id': current_user.id})
    return await db.fetch_one(query=posts_table.select().where(posts_table.c.id == created_post_id))


@router.put('/{post_id}', response_model=PostResponse)
@db.transaction()
async def update_post(post_id: int, post: PostUpdate, current_user: int = Depends(get_current_user)):
    find_post = posts_table.select().where(posts_table.c.id == post_id)
    post_to_update = await db.fetch_one(query=find_post)

    if not post_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Post does not exist!')

    update_query = posts_table.update().where(posts_table.c.id == post_id)
    await db.execute(query=update_query, values=post.dict())

    return await db.fetch_one(find_post)


@router.delete('/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
@db.transaction()
async def delete_post(post_id: int, current_user=Depends(get_current_user)):
    find_post = posts_table.select().where(posts_table.c.id == post_id)
    post_to_delete = await db.fetch_one(query=find_post)

    if not post_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Post does not exist!')

    if post_to_delete.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Unauthorized to perform the requested action')

    delete_query = posts_table.delete().where(posts_table.c.id == post_id)
    await db.execute(delete_query)
