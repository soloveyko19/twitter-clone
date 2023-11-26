import pytest

from database.models import UserFollow, Tweet, TweetLike


async def test_get_users_me(async_client, user_test):
    headers = [("api-key", user_test.api_key)]
    response = await async_client.get("/api/users/me", headers=headers)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data.get("result")
    response_user = response_data.get("user")
    assert response_user.get("id") == user_test.id
    assert response_user.get("name") == user_test.name


async def test_get_users_id(async_client, user_test):
    response = await async_client.get(f"/api/users/{user_test.id}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data.get("result")
    response_user = response_data.get("user")
    assert response_user.get("id") == user_test.id
    assert response_user.get("name") == user_test.name


async def test_post_users_id_follow(async_client, user_test):
    headers = [("api-key", user_test.api_key)]
    response = await async_client.post(
        f"/api/users/{user_test.id + 1}/follow", headers=headers
    )
    assert response.status_code == 201
    response_data = response.json()
    assert response_data.get("result")


async def test_delete_users_id_follow(async_client, user_test, as_session):
    async with as_session() as session:
        follow = UserFollow(
            user_follower_id=user_test.id, user_following_id=user_test.id + 1
        )
        session.add(follow)
        await session.commit()
    headers = [("api-key", user_test.api_key)]
    response = await async_client.delete(
        f"/api/users/{user_test.id + 1}/follow", headers=headers
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data.get("result")
    _follow = await UserFollow.get(
        user_follower_id=user_test.id, user_following_id=user_test.id + 1
    )
    assert not _follow


async def test_get_tweets(async_client, as_session, user_test):
    async with as_session() as session:
        tweet = Tweet(
            content="Some content",
            author_id=user_test.id,
        )
        session.add(tweet)
        await session.commit()
    headers = [("api-key", user_test.api_key)]
    response = await async_client.get("/api/tweets", headers=headers)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data.get("result")
    response_tweet = response_data.get("tweets").pop()
    assert response_tweet.get("id") == tweet.id
    assert response_tweet.get("content") == tweet.content
    assert response_tweet.get("author").get("id") == tweet.author_id


async def test_post_tweets(async_client, user_test, as_session):
    headers = [("api-key", user_test.api_key)]
    data = {"tweet_data": "Some content", "tweet_media_ids": []}
    response = await async_client.post(
        "/api/tweets", headers=headers, json=data
    )
    assert response.status_code == 201
    response_data = response.json()
    assert response_data.get("result")
    tweet = await Tweet.get(pk=response_data.get("tweet_id"))
    assert tweet.id
    assert tweet.author_id == user_test.id
    assert tweet.content == data.get("tweet_data")


async def test_delete_tweets_id(async_client, as_session, user_test):
    async with as_session() as session:
        tweet = Tweet(
            content="Some content",
            author_id=user_test.id,
        )
        session.add(tweet)
        await session.commit()
    headers = [("api-key", user_test.api_key)]
    response = await async_client.delete(
        f"/api/tweets/{tweet.id}",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json().get("result")


async def test_post_tweets_pk_likes(async_client, as_session, user_test):
    async with as_session() as session:
        tweet = Tweet(
            content="Some content",
            author_id=user_test.id,
        )
        session.add(tweet)
        await session.commit()
    headers = [("api-key", user_test.api_key)]
    response = await async_client.post(
        f"/api/tweets/{tweet.id}/likes",
        headers=headers
    )
    assert response.status_code == 201
    response_data = response.json()
    assert response_data.get("result")
    like = await TweetLike.get(
        tweet_id=tweet.id,
        user_id=user_test.id
    )
    assert like.id


async def test_delete_tweets_id_likes(async_client, as_session, user_test):
    async with as_session() as session:
        tweet = Tweet(
            content="Some content",
            author_id=user_test.id,
        )
        session.add(tweet)
        await session.commit()
        like = TweetLike(
            tweet_id=tweet.id,
            user_id=user_test.id
        )
        session.add(like)
        await session.commit()
    headers = [("api-key", user_test.api_key)]
    response = await async_client.delete(
        f"/api/tweets/{tweet.id}/likes",
        headers=headers
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data.get("result")
    _like = await TweetLike.get(
        tweet_id=tweet.id,
        user_id=user_test.id
    )
    assert not _like
