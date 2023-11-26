import asyncio
import logging
from database.models import User, UserFollow, async_session


async def add_user(_id: int):
    user = User(name=f"user_{_id}", api_key=f"api_key_{_id}")
    await user.add()


async def add_followers(_id):
    following = UserFollow(user_follower_id=_id, user_following_id=_id - 1)
    await following.add()


async def add_test_user():
    user = User(name="Test", api_key="test")
    await user.add()


async def create_test_users():
    """
    Async function for initialize 5 test users if the table `users` is empty.
    """
    from sqlalchemy import select

    logging.info("Starting creating 5 test users")
    user = await User.get(_id=1)
    if not user:
        logging.info("Users not exists, adding...")
        users_tasks = [add_user(_id) for _id in range(1, 6)]
        await asyncio.gather(*users_tasks)
        logging.info("Users successfully added")
        following_tasks = [add_followers(_id) for _id in range(2, 6)]
        logging.info("Following successfully added")
        await asyncio.gather(*following_tasks)
        await add_test_user()
    else:
        logging.info("Users exists, skipping adding.")


if __name__ == "__main__":
    asyncio.run(create_test_users())
