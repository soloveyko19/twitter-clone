from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base, relationship, joinedload
from sqlalchemy import Column, Integer, String, ForeignKey, Text, select, and_
from sqlalchemy.exc import IntegrityError

from typing import Optional, List, Iterable
from conf import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_DB


url = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
engine = create_async_engine(url)
Base = declarative_base()
async_session = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50))
    api_key = Column(String(50), unique=True)
    followers = relationship(
        "User",
        secondary="users_follow",
        primaryjoin="User.id == UserFollow.user_following_id",
        secondaryjoin="User.id == UserFollow.user_follower_id",
        backref="following",
        lazy="joined",
    )

    @classmethod
    async def get(
        cls, api_key: str = None, _id: int = None
    ) -> Optional["User"]:
        if api_key:
            query = (
                select(User)
                .options(
                    joinedload(User.followers), joinedload(User.following)
                )
                .filter(User.api_key == api_key)
            )
        elif _id:
            query = (
                select(User)
                .options(
                    joinedload(User.followers), joinedload(User.following)
                )
                .filter(User.id == _id)
            )
        else:
            raise ValueError("One of arguments (api_key, _id) must be set")
        async with async_session() as session:
            user = await session.execute(query)
            return user.scalar()

    async def get_feed(self) -> Iterable["Tweet"]:
        async with async_session() as session:
            following_user_ids = [user.id for user in self.following]
            following_user_ids.append(self.id)
            query = (
                select(Tweet)
                .filter(Tweet.author_id.in_(following_user_ids))
                .order_by(Tweet.id.desc())
            )
            feed = await session.execute(query)
            return feed.scalars().unique()

    async def add(self):
        async with async_session() as session:
            session.add(self)
            await session.commit()
            return self

    async def dump(self):
        schema = {
            "id": self.id,
            "name": self.name,
            "followers": [
                {"id": f_user.id, "name": f_user.name}
                for f_user in self.followers
            ],
            "following": [
                {"id": f_user.id, "name": f_user.name}
                for f_user in self.following
            ],
        }
        return schema


class UserFollow(Base):
    __tablename__ = "users_follow"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_follower_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user_following_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    @classmethod
    async def get(
        cls, user_follower_id: int, user_following_id: int
    ) -> "UserFollow":
        async with async_session() as session:
            query = select(UserFollow).filter(
                and_(
                    UserFollow.user_follower_id == user_follower_id,
                    UserFollow.user_following_id == user_following_id,
                )
            )
            follow = await session.execute(query)
            return follow.scalar()

    async def add(self) -> "UserFollow":
        async with async_session() as session:
            try:
                session.add(self)
                await session.commit()
                return self
            except IntegrityError:
                await session.rollback()

    async def delete(self) -> bool:
        async with async_session() as session:
            try:
                await session.delete(self)
                await session.commit()
                return True
            except IntegrityError:
                pass
            return False


class Tweet(Base):
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    content = Column(Text)
    author_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    author = relationship("User", lazy="joined")
    medias = relationship("Media", secondary="tweet_medias", lazy="joined")
    likes = relationship("User", secondary="tweet_likes", lazy="joined")

    @classmethod
    async def get(cls, pk) -> "Tweet":
        async with async_session() as session:
            query = select(Tweet).filter(Tweet.id == pk)
            tweet = await session.execute(query)
            return tweet.scalar()

    async def add(self) -> "Tweet":
        async with async_session() as session:
            session.add(self)
            await session.commit()
            return self

    async def delete(self):
        async with async_session() as session:
            await session.delete(self)
            await session.commit()


class Media(Base):
    __tablename__ = "medias"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    media_path = Column(String, nullable=False)

    async def add(self) -> "Media":
        async with async_session() as session:
            session.add(self)
            await session.commit()
            return self


class TweetMedia(Base):
    __tablename__ = "tweet_medias"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tweet_id = Column(
        Integer, ForeignKey("tweets.id", ondelete="CASCADE"), nullable=False
    )
    media_id = Column(
        Integer, ForeignKey("medias.id", ondelete="CASCADE"), nullable=False
    )

    async def add(self) -> Optional["TweetMedia"]:
        async with async_session() as session:
            try:
                session.add(self)
                await session.commit()
                return self
            except IntegrityError:
                await session.rollback()

    @classmethod
    async def add_many(
        self, tweet_id: int, media_ids: List[int]
    ) -> Optional[List["TweetMedia"]]:
        instances = [
            TweetMedia(tweet_id=tweet_id, media_id=media_id)
            for media_id in media_ids
        ]
        async with async_session() as session:
            try:
                session.add_all(instances)
                await session.commit()
                return instances
            except IntegrityError:
                await session.rollback()


class TweetLike(Base):
    __tablename__ = "tweet_likes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tweet_id = Column(
        Integer, ForeignKey("tweets.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    @classmethod
    async def get(self, tweet_id: int, user_id: int):
        async with async_session() as session:
            query = select(TweetLike).filter(
                and_(
                    TweetLike.tweet_id == tweet_id,
                    TweetLike.user_id == user_id,
                )
            )
            like = await session.execute(query)
            return like.scalar()

    async def add(self):
        async with async_session() as session:
            try:
                session.add(self)
                await session.commit()
                return self
            except IntegrityError:
                await session.rollback()

    async def delete(self):
        async with async_session() as session:
            await session.delete(self)
            await session.commit()
