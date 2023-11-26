from fastapi import APIRouter, Header, Path, HTTPException
from fastapi.responses import JSONResponse

from database.models import User, UserFollow

router = APIRouter()


@router.get("/me")
async def get_user_me(
    api_key: str = Header(..., convert_underscores=True)
) -> JSONResponse:
    """
    Get information about the current user.
    :param api_key: str (header 'api-key' to select the user)
    :return: JSONResponse (information about user if it exists)
    """
    user = await User.get(api_key=api_key)
    if not user:
        raise HTTPException(
            status_code=400, detail="No such user with this api-key"
        )
    serialized_user = await user.dump()
    response = {"result": True, "user": serialized_user}
    return JSONResponse(content=response)


@router.get("/{pk}")
async def get_user(pk: int = Path(...)) -> JSONResponse:
    """
    Get information about requested user by id

    :param pk: str (primary key of user)
    :return: JSONResponse (information about user)
    """
    user = await User.get(_id=pk)
    if not user:
        raise HTTPException(
            status_code=404, detail="No such user with this id"
        )
    serialized_user = await user.dump()
    response = {"result": True, "user": serialized_user}
    return JSONResponse(content=response)


@router.post("/{pk}/follow")
async def user_follow(
    pk: int = Path(...), api_key: str = Header(..., convert_underscores=True)
):
    """
    Follow other users. Follows user with current api-key to user with pk in path.

    :param pk: int (id of user to follow)
    :param api_key: str (header api-key, identification of user)
    :return: JSONResponse (successful follow or not)
    """
    user_follower = await User.get(api_key=api_key)
    if not user_follower:
        raise HTTPException(
            status_code=400, detail="No such user with this api-key"
        )
    follow = UserFollow(
        user_follower_id=user_follower.id, user_following_id=pk
    )
    follow = await follow.add()
    if not follow:
        raise HTTPException(
            status_code=404, detail="No such user with this id"
        )
    response = {"result": True}
    return JSONResponse(content=response, status_code=201)


@router.delete("/{pk}/follow")
async def user_follow(
    pk: int = Path(...), api_key: str = Header(..., convert_underscores=True)
):
    """
    Unfollow other users. Unfollows user with current api-key from user with pk in path.

    :param pk: int (id of user to unfollow)
    :param api_key: str (header api-key, identification of user)
    :return: JSONResponse (successful unfollow or not)
    """
    user_follower = await User.get(api_key=api_key)
    if not user_follower:
        raise HTTPException(
            status_code=400, detail="No such user with this api-key"
        )
    follow = await UserFollow.get(
        user_follower_id=user_follower.id, user_following_id=pk
    )
    deleted = await follow.delete()
    if not deleted:
        raise HTTPException(
            status_code=404, detail="No such user with this id"
        )
    response = {"result": True}
    return JSONResponse(content=response)
