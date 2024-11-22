from pydantic import ConfigDict, BaseModel, Field, EmailStr
from pydantic.functional_validators import BeforeValidator
from typing import Optional, List
from typing_extensions import Annotated
from datetime import datetime


PyObjectId = Annotated[str, BeforeValidator(str)]


class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    username: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    is_verified: Optional[bool] = Field(default=False)
    boards: Optional[List[PyObjectId]] = Field(default=[])
    created_At: datetime = Field(default=datetime.today())
    last_updated: Optional[datetime] = Field(default=None)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "username": "Jane Doe",
                "email": "sampleemail@gmail.com",
                "password": "233eh6fhytewfrrsfsgyuifif.eyfgftdh",
                "is_verified": False,
                "boards": ["2etdhdyjsjydy66h3", "agtdjeu7f78393hrh", "fhfyvnghyyete6fu8"],
                "created_At": "2024-10-12 11:21:12.061734",
                "last_updated": "2024-10-12 11:21:12.061734"
            },
        },
    )


class Board(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_Id: Optional[PyObjectId] = Field(default=None)
    board_url: str = Field(...)
    title: str = Field(...)
    description: str = Field(...)
    social_app: str = Field(...)
    cta: str = Field(...)
    cta_url: str = Field(...)
    is_published: Optional[bool] = Field(default=False)
    theme: Optional[dict] = Field(default={})
    posts: Optional[List[dict]] = Field(default=[])
    created_At: Optional[datetime] = Field(default=datetime.today())
    last_updated: Optional[datetime] = Field(default=None)


    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "user_Id": "670af476e240536420edf8b6",
                "board_url": "myboard",
                "title": "My new board",
                "description": "I just created this board",
                "social_app": "twitter",
                "cta": "Hire me",
                "cta_url": "https://x.com",
                "is_published": False,
                "theme": {},
                "posts": [{}],
                "created_At": "2024-10-12 11:21:12.061734",
                "last_updated": "2024-10-12 11:21:12.061734"
            },
        },
    )
