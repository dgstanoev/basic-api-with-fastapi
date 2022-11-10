from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import Vote
from app.tables import db, votes_table, posts_table
from app.jwt_token import get_current_user

router = APIRouter(
    prefix='/vote',
    tags=['Votes'])


@router.post('/', status_code=status.HTTP_201_CREATED)
@db.transaction()
async def vote_post(vote: Vote, current_user=Depends(get_current_user)):
    post_query = posts_table.select().where(posts_table.c.id == vote.post_id)
    post = await db.execute(query=post_query)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post does not exist!')

    query = votes_table.select().where(votes_table.c.post_id == vote.post_id, votes_table.c.user_id ==
                                       current_user.id)
    found_vote = await db.fetch_one(query=query)
    if vote.dir == 1:
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='You have already voted on this post.')
        query = votes_table.insert()
        await db.execute(query, values={'post_id': vote.post_id, 'user_id': current_user.id})
        return {'message': 'Voted successfully!'}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Vote does not exist')
        query = votes_table.delete().where(votes_table.c.post_id == vote.post_id, votes_table.c.user_id ==
                                           current_user.id)
        await db.execute(query)
        return {'message': 'Successfully deleted vote!'}
