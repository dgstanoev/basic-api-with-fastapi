from sqlalchemy import MetaData, Table, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from databases import Database
from app.config import settings

db = Database(f'{settings.db_driver}://{settings.db_user}:{settings.db_password}@{settings.db_hostname}:'
              f'{settings.db_port}/{settings.db_name}')
metadata = MetaData()


posts_table = Table(
    "posts",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(length=100)),
    Column("content", String(length=100)),
    Column("published", Boolean, server_default='TRUE', nullable=False),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=text('now()')),
    Column("owner_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
)

users_table = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, nullable=False),
    Column("email", String, nullable=False, unique=True),
    Column("password", String, nullable=False),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
)

votes_table = Table(
    "votes",
    metadata,
    Column("post_id", Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)

# import sqlalchemy
# import os
# from dotenv import load_dotenv
#
# load_dotenv()
# engine = sqlalchemy.create_engine(os.environ.get('SYNC_DB'))
# posts_table.drop(engine)
# votes_table.create(engine)
