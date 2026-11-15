"""The public field names match the shared frontend contract."""
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StringConstraints

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Value = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]
Label = Annotated[str, StringConstraints(strip_whitespace=True, max_length=100)]


class ContactMethod(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["phone", "email", "social", "address"]
    label: Label = ""
    value: Value


class ContactInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Name
    isFavorite: StrictBool = False
    methods: list[ContactMethod] = Field(default_factory=list, max_length=100)


class Contact(ContactInput):
    id: int


class ContactList(BaseModel):
    items: list[Contact]
    total: int


class FavoriteInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    isFavorite: StrictBool
