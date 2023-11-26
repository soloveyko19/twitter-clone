from fastapi import APIRouter, Header, HTTPException, Path
from fastapi.responses import JSONResponse
from database.models import Tweet, TweetMedia, User, TweetLike
from database.schemas import TweetIn

router = APIRouter()


@router.post("")
async def post_add_new_tweet(
    _tweet: TweetIn, api_key: str = Header(..., convert_underscores=True)
) -> JSONResponse:
    user = await User.get(api_key=api_key)
    if not user:
        raise HTTPException(
            status_code=404, detail="No such user with this api-key"
        )
    tweet = Tweet(content=_tweet.tweet_data, author_id=user.id)
    tweet = await tweet.add()
    if _tweet.tweet_media_ids:
        medias = await TweetMedia.add_many(
            tweet_id=tweet.id, media_ids=_tweet.tweet_media_ids
        )
        if not medias:
            raise HTTPException(
                status_code=400, detail="Medias with this id is not exists"
            )
    response = {"result": True, "tweet_id": tweet.id}
    return JSONResponse(content=response, status_code=201)


@router.delete("/{pk}")
async def delete_tweet(
    pk: int = Path(...), api_key: str = Header(..., convert_underscores=True)
) -> JSONResponse:
    user = await User.get(api_key=api_key)
    tweet = await Tweet.get(pk=pk)
    if not user:
        raise HTTPException(
            status_code=400, detail="No such user with this api-key"
        )
    if not tweet:
        raise HTTPException(
            status_code=404, detail="No such tweet with this id"
        )
    if not tweet.author.id == user.id:
        raise HTTPException(
            status_code=403, detail="No such permission for this action"
        )
    await tweet.delete()
    response = {"result": True}
    return JSONResponse(content=response)


@router.get("")
async def get_user_feed(
    api_key: str = Header(..., convert_underscores=True)
) -> JSONResponse:
    user = await User.get(api_key=api_key)
    if not user:
        raise HTTPException(
            status_code=400, detail="No such user with this api-key"
        )
    feed = await user.get_feed()
    serialized_tweet = [
        {
            "id": tweet.id,
            "content": tweet.content,
            "author": {"id": tweet.author.id, "name": tweet.author.name},
            "attachments": [media.media_path for media in tweet.medias],
            "likes": [
                {"id": user.id, "name": user.name} for user in tweet.likes
            ],
        }
        for tweet in feed
    ]
    response = {"result": True, "tweets": serialized_tweet}
    return JSONResponse(content=response)


@router.post("/{pk}/likes")
async def post_set_like(
    pk: int = Path(...), api_key: str = Header(..., convert_underscores=True)
) -> JSONResponse:
    user = await User.get(api_key=api_key)
    tweet = await Tweet.get(pk=pk)
    if not user:
        raise HTTPException(
            status_code=403, detail="No such user with this api key"
        )
    if not tweet:
        raise HTTPException(
            status_code=404, detail="No such tweet with this api key"
        )
    _like = await TweetLike.get(user_id=user.id, tweet_id=tweet.id)
    if _like:
        raise HTTPException(status_code=403, detail="Like already set")
    like = TweetLike(user_id=user.id, tweet_id=tweet.id)
    await like.add()
    response = {"result": True}
    return JSONResponse(content=response, status_code=201)


@router.delete("/{pk}/likes")
async def delete_like(
    pk: int = Path(...), api_key: str = Header(..., convert_underscores=True)
) -> JSONResponse:
    user = await User.get(api_key=api_key)
    tweet = await Tweet.get(pk=pk)
    if not user:
        raise HTTPException(
            status_code=403, detail="No such user with this api key"
        )
    if not tweet:
        raise HTTPException(
            status_code=404, detail="No such tweet with this api key"
        )
    like = await TweetLike.get(user_id=user.id, tweet_id=tweet.id)
    if not like:
        raise HTTPException(status_code=403, detail="Like is not set")
    await like.delete()
    response = {"result": True}
    return JSONResponse(content=response)
