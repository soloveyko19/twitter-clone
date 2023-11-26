from pydantic import BaseModel
from typing import Optional, List


class TweetIn(BaseModel):
    tweet_data: str
    tweet_media_ids: Optional[List[int]]
